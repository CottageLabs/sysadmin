import sys
from fabric.api import env, run, sudo, cd, abort, roles, execute, warn_only

env.use_ssh_config = True  # username, identity file (key), hostnames for machines will all be loaded from ~/.ssh/config
# You can run this script like this:
# fab -H <host1,host2> <task_name>

# your local ssh config does not apply when the script is explicitly specifying which hosts to run tasks on...
# so username and key path will still have to be set here, or specified on the command line using -u <username> and -i <path to key>
env.user = 'cloo'  
if not env.get('key_filename'):
    # env.setdefault does not seem to work correctly
    env.key_filename = []
env.key_filename.extend(
    [
        '~/.ssh/cl',
        # add the path to your own private key if you wish
        # you can also add the -i argument when running fabric:
        # fab -i <path to key> <task_name>:arg1=value1,arg2=value2
    ]
)


DOAJGATE_IP = '46.101.12.197'
DOAJAPP1_IP = '46.101.38.194'
DOAJ_TEST_IP = '178.62.92.200'
DOAJ_STAGING_IP = '95.85.48.213'
APP_SERVER_NAMES = {'DOAJGATE': DOAJGATE_IP}  # the gateway nginx config files are named after which app server the gateway directs traffic to
TEST_SERVER_NAMES = {'DOAJ_TEST': DOAJ_TEST_IP}
STAGING_SERVER_NAMES = {'DOAJ_STAGING': DOAJ_STAGING_IP}

env.hosts = [DOAJGATE_IP]

DOAJ_PROD_PATH_SRC = '/home/cloo/repl/apps/doaj/src/doaj'
DOAJ_TEST_PATH_SRC = '/home/cloo/repl/test/doaj/src/doaj'
DOAJ_USER_APP_PORT = 5050

# Gateway server - nginx site config filename bits (also includes the server name in the middle)
GATE_NGINX_CFG_PREFIX = 'doaj-forward-to-'
GATE_NGINX_CFG_SUFFIX = '-server-with-local-static'

# Used when running tasks directly, e.g. fab update_doaj . Not (yet)
# used when a task like switch_doaj is calling multiple other tasks
# programmatically. Enables us to not have to specify "which hosts" 
# all the time when running Fabric.
env.roledefs.update(
        {
            'app': [DOAJAPP1_IP],
            'gate': [DOAJGATE_IP],
            'test': [DOAJ_TEST_IP],
            'staging': [DOAJ_STAGING_IP]
        }
)

@roles('gate')
def update_doaj(branch='production', tag="", doajdir=DOAJ_PROD_PATH_SRC):
    if not tag and branch == 'production':
        print 'Please specify a tag to deploy to production'
        sys.exit(1)

    if doajdir == DOAJ_PROD_PATH_SRC and branch != 'production':
        print 'You\'re deploying something other than the production branch to the live DOAJ app location.'
        print 'Aborting execution. If you really want to do this edit this script and comment the guard out.'
        sys.exit(1)

    with cd(doajdir):
        run('git config user.email "us@cottagelabs.com"')
        run('git config user.name "Cottage Labs LLP"')
        run('git checkout master')  # so that we have a branch we can definitely pull in
                                    # (in case we start from one that was set up for pushing only)
        run('git pull', pty=False)  # get any new branches
        run('git checkout ' + branch)
        run('git pull', pty=False)  # again, in case the checkout actually switched the branch, pull from the remote now
        if tag:
            run('git checkout {0}'.format(tag))
        run('git submodule update --init', pty=False)
        run('deploy/{0}_doaj_deploy-gateway.sh'.format(branch))

@roles('staging')
def update_staging(branch='production'):
    '''Update the staging server with the latest live code and reload the app.'''
    execute(update_doaj, branch=branch, hosts=env.roledefs['staging'])
    execute(reload_staging)

@roles('staging')
def reload_staging():
    execute(reload_webserver, supervisor_doaj_task_name='doaj-staging', hosts=env.roledefs['staging'])

def _get_hosts(from_, to_):
    FROM = from_.upper()
    TO = to_.upper()
    if FROM not in APP_SERVER_NAMES or TO not in APP_SERVER_NAMES:
        abort('When syncing suggestions from one machine to another, only the following server names are valid: ' + ', '.join(APP_SERVER_NAMES))
    source_host = APP_SERVER_NAMES[FROM]
    target_host = APP_SERVER_NAMES[TO]
    return FROM, source_host, TO, target_host
    
@roles('app')
def push_xml_uploads():
    # TODO: move the hardcoded dirs and files to python constants to top
    # of file .. bit pointless for now as the scheduled backups
    # themselves have those bits hardcoded too
    run("/home/cloo/backups/backup2s3.sh {doaj_path}/upload/ /home/cloo/backups/doaj-xml-uploads/ dummy s3://doaj-xml-uploads >> /home/cloo/backups/logs/doaj-xml-uploads_`date +%F_%H%M`.log 2>&1"
            .format(doaj_path=DOAJ_PROD_PATH_SRC),
        pty=False
    )

@roles('app')
def pull_xml_uploads():
    # TODO: same as push_xml_uploads
    run("/home/cloo/backups/restore_from_s3.sh s3://doaj-xml-uploads {doaj_path}/upload/ /home/cloo/backups/doaj-xml-uploads/"
            .format(doaj_path=DOAJ_PROD_PATH_SRC),
        pty=False
    )

def sync_suggestions(from_, to_):
    FROM, source_host, TO, target_host = _get_hosts(from_, to_)
    execute(_sync_suggestions, FROM=FROM, hosts=[target_host])
    execute(count_suggestions, hosts=[source_host, target_host])
    raw_input('Suggestion counts OK? Press <Enter>. If not, press Ctrl+C to terminate now.')

@roles('app')
def check_doaj_running():
    run('if [ $(curl -s localhost:{app_port}| grep {check_for} | wc -l) -ge 1 ]; then echo "DOAJ running on localhost:{app_port}"; fi'
            .format(app_port=DOAJ_USER_APP_PORT, check_for="doaj")
    )

@roles('app')
def print_doaj_app_config():
    print_keys = {
            'secret_settings.py': ['RECAPTCHA'],
            'settings.py': ['DOMAIN', 'SUPPRESS_ERROR_EMAILS', 'DEBUG']
    }
    for file_, keys in print_keys.items():
        for key in keys:
            run('grep {key} {doaj_path}/portality/{file_}'.format(file_=file_, key=key, doaj_path=DOAJ_PROD_PATH_SRC))

@roles('app')
def reload_webserver(supervisor_doaj_task_name='doaj-production'):
    sudo('kill -HUP $(sudo supervisorctl pid {0})'.format(supervisor_doaj_task_name))

@roles('gate')
def deploy_live(branch='production', tag=""):
    update_doaj(branch=branch, tag=tag)
    execute(reload_webserver, hosts=env.roledefs['app'])

@roles('gate')
def deploy_test(branch='develop', tag=""):
    update_doaj(branch=branch, tag=tag, doajdir=DOAJ_TEST_PATH_SRC)
    execute(reload_webserver(supervisor_doaj_task_name='doaj-test'), hosts=env.roledefs['test'])
