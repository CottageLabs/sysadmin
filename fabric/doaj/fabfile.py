from fabric.api import env, run, sudo, cd, abort, roles, execute

env.use_ssh_config = True  # username, identity file (key), hostnames for machines will all be loaded from ~/.ssh/config
# This means that you run this script like this:
# fab -H <host1,host2> <task_name>

# E.g.:
# Update DOAJ app to HEAD of current git master:
# fab update_doaj
# This will update it on all servers specified later in this file
# (the 2 application servers and the gateway for now).

# If you want to specify which hosts to update it on:
# fab -H doaj,cl2,doajgate update_doaj
    # (replace ssh names with the ones you would use yourself on the command
    # line with ssh - they come from your own ~/.ssh/config)
    # You can also use IP addresses, of course.

# Switch DOAJ from running on one server to another.
# fab switch_doaj:from_=cl2,to_=doaj
# This would cause the DOAJ Gateway to direct traffic to the DOAJ server
# and away from CL2, the OAG server.
# Obviously, make sure the application config is actually the way you want it on both servers. You will be asked about all the important bits.

    # WARNING: If git pull pulls any changes to python code (including
    # configuration!), or if YOU change the app config, make sure to
    # reload the application by sending a HUP signal to the gunicorn 
    # master process before the final step of this task!
    
    # On the DOAJ machine, this happens just by doing
    # kill -HUP $(sudo supervisorctl pid doaj)

    # On the OAG machine, do ps -ef | grep gunicorn and look for the one
    # that says "gunicorn: master [portality.app:app]", get its PID, and
    # just do kill -HUP <the PID you got> 
    # Then send me a passive aggressive reminder email to upgrade
    # supervisord on that server.

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


DOAJ_IP = '93.93.135.219'
CL2_IP = '93.93.131.41'
DOAJGATE_IP = '95.85.56.138'
APP_SERVER_NAMES = {'DOAJ': DOAJ_IP, 'CL2': CL2_IP}  # the gateway nginx config files are named after which app server the gateway directs traffic to

env.hosts = [DOAJGATE_IP]

DOAJ_PATH_SRC = '/opt/doaj/src/doaj'  # path on remote servers to the DOAJ app
DOAJ_APP_PORT = 5550  # servers can access the application directly at 5550, the normal port is 5050
                      # access to 5550 is restricted to the server IP-s by the firewall however
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
            'app': [DOAJ_IP, CL2_IP], 
            'gate': [DOAJGATE_IP]
        }
)

def switch_doaj(from_, to_, dont_sync_suggestions=None):
    FROM, source_host, TO, target_host = _get_hosts(from_, to_)

    # set the hosts to the 2 application servers passed in
    # saves us from having to wrap each single command in
    # execute(command, hosts=[host1,host2])
    # it does mean we have to wrap SOME commands, which run only on one
    # host, or which run on all the hosts incl. the gateway

    # TODO: fix this calling of tasks with execute everywhere
    app_servers = [source_host, target_host]

    execute(update_doaj, hosts=app_servers + [DOAJGATE_IP])
    raw_input('Everything OK, no unexpected changes or commits present? Press <Enter>. If not, press Ctrl+C to terminate now.')
    if not dont_sync_suggestions:
        sync_suggestions(from_, to_)
    # sync xml uploads
    execute(push_xml_uploads, hosts=[source_host])
    execute(pull_xml_uploads, hosts=[target_host])
    print
    print '-- Check the article and journal counts are the same on all app servers now.'
    print 
    execute(count_journals, hosts=app_servers)
    execute(count_articles, hosts=app_servers)
    raw_input('Journal and article counts equal? Press <Enter>. If not, press Ctrl+C to terminate now.')
    execute(check_doaj_running, hosts=app_servers)
    raw_input('Is the app running on port {app_port} on all app servers as needed by nginx? Press <Enter>. If not, press Ctrl+C to terminate now.'
            .format(app_port=DOAJ_USER_APP_PORT)
    )
    execute(print_doaj_app_config, hosts=app_servers)
    raw_input('Is the config correct for all application servers? Press <Enter>. If not, go fix it and *then* press <Enter>. Or Ctrl+C to terminate now.')
    execute(gate_switch_doaj, from_=from_, to_=to_, hosts=[DOAJGATE_IP])
    # TODO reload application itself by sending HUP to gunicorn! Need to
    # upgrade supervisord on CL2 first though.

@roles('app', 'gate')
def update_doaj():
    with cd(DOAJ_PATH_SRC):
        run('git pull')
        run('git submodule update')

def _get_hosts(from_, to_):
    FROM = from_.upper()
    TO = to_.upper()
    if FROM not in APP_SERVER_NAMES or TO not in APP_SERVER_NAMES:
        abort('When syncing suggestions from one machine to another, only the following server names are valid: ' + ', '.join(APP_SERVER_NAMES))
    source_host = APP_SERVER_NAMES[FROM]
    target_host = APP_SERVER_NAMES[TO]
    return FROM, source_host, TO, target_host
    
def push_xml_uploads():
    # TODO: move the hardcoded dirs and files to python constants to top
    # of file .. bit pointless for now as the scheduled backups
    # themselves have those bits hardcoded too
    run("/home/cloo/backups/backup2s3.sh {doaj_path}/upload/ /home/cloo/backups/doaj-xml-uploads/ dummy s3://doaj-xml-uploads >> /home/cloo/backups/logs/doaj-xml-uploads_`date +%F_%H%M`.log 2>&1"
            .format(doaj_path=DOAJ_PATH_SRC)
    )

def pull_xml_uploads():
    # TODO: same as push_xml_uploads
    run("/home/cloo/backups/restore_from_s3.sh s3://doaj-xml-uploads {doaj_path}/upload/ /home/cloo/backups/doaj-xml-uploads/"
            .format(doaj_path=DOAJ_PATH_SRC)
    )

@roles('gate')
def gate_switch_doaj(from_, to_):
    '''Perform the actual switching of nginx configs and reload nginx on the gateway.'''
    FROM, source_host, TO, target_host = _get_hosts(from_, to_)
    with cd('/etc/nginx'):
        # determine which config file will be used
        old_nginx_conf = GATE_NGINX_CFG_PREFIX + FROM + GATE_NGINX_CFG_SUFFIX
        new_nginx_conf = GATE_NGINX_CFG_PREFIX + TO + GATE_NGINX_CFG_SUFFIX
        raw_input('Going to enable {new} and disable {old} nginx configs on the gateway. <Enter> to proceed, Ctrl+C to terminate.'
                .format(new=new_nginx_conf, old=old_nginx_conf)
        )
        sudo('ln -s ../sites-available/{new} sites-enabled/{new}'.format(new=new_nginx_conf))
        sudo('rm sites-enabled/{old}'.format(old=old_nginx_conf))
        print
        print '-- Listing all nginx configs and testing the overall nginx configuration.'
        print
        run('ls -l sites-enabled')
        sudo('nginx -t')
        raw_input('All OK? Press <Enter>. Ctrl+C to terminate now. If you proceed, the gateway nginx will reload its config and traffic will switch to your desired application server NOW.')
        sudo('nginx -s reload')

def sync_suggestions(from_, to_):
    FROM, source_host, TO, target_host = _get_hosts(from_, to_)
    execute(_sync_suggestions, FROM=FROM, hosts=[target_host])
    execute(count_suggestions, hosts=[source_host, target_host])
    raw_input('Suggestion counts OK? Press <Enter>. If not, press Ctrl+C to terminate now.')

def _sync_suggestions(FROM):
    run('/opt/sysadmin/backup/sync_doaj_suggestions.py "http://{FROM}:{app_port}/query/suggestion?size={suggestion_count}" "http://localhost:{app_port}/query/suggestion?size={suggestion_count}"'
            .format(FROM=APP_SERVER_NAMES[FROM], app_port=DOAJ_APP_PORT, suggestion_count=100000)
    )

@roles('app')
def count_suggestions():
    run('curl localhost:{app_port}/query/suggestion/_count'.format(app_port=DOAJ_APP_PORT))

@roles('app')
def count_journals():
    run('curl localhost:{app_port}/query/journal/_count'.format(app_port=DOAJ_APP_PORT))

@roles('app')
def count_articles():
    run('curl localhost:{app_port}/query/article/_count'.format(app_port=DOAJ_APP_PORT))

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
            run('grep {key} {doaj_path}/portality/{file_}'.format(file_=file_, key=key, doaj_path=DOAJ_PATH_SRC))