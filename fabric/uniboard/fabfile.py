from fabric.api import env, run, sudo, cd, abort, roles, execute, warn_only

env.use_ssh_config = True  # username, identity file (key), hostnames for machines will all be loaded from ~/.ssh/config
# This means that you run this script like this:
# fab -H <host1,host2> <task_name>

# E.g.:
# Update app to HEAD of current git master:
# fab update_app
# This will update it on all servers specified later in this file

# If you want to specify which hosts to update it on:
# fab -H host1,host2
    # (replace ssh names with the ones you would use yourself on the command
    # line with ssh - they come from your own ~/.ssh/config)
    # You can also use IP addresses, of course.

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


UNIBOARD_PILOT_IP = '95.85.52.130'
RICHARD_TEST_IP = '5.101.97.169'
APP_SERVER_NAMES = {'UNIBOARD_PILOT': UNIBOARD_PILOT_IP}  # the gateway nginx config files are named after which app server the gateway directs traffic to
TEST_SERVER_NAMES = {'RICHARD_TEST': RICHARD_TEST_IP}

APP_PATH_SRC = '/opt/uniboard/src/uniboard'  # path on remote servers to the UNIBOARD app
USER_APP_PORT = 5050

# Used when running tasks directly, e.g. fab update_app . Not (yet)
# used when a task is calling multiple other tasks
# programmatically. Enables us to not have to specify "which hosts" 
# all the time when running Fabric.
env.roledefs.update(
        {
            'app': [UNIBOARD_PILOT_IP], 
            'test': [RICHARD_TEST_IP],
        }
)

@roles('app')
def update_app(branch='master'):
    with cd(APP_PATH_SRC):
        run('git config user.email "us@cottagelabs.com"')
        run('git config user.name "Cottage Labs LLP"')
        stash = run('git stash')
        run('git pull', pty=False)
        run('git checkout ' + branch)
        run('git submodule update', pty=False)
        if not 'No local changes to save' in stash:
            with warn_only():
                run('git stash apply')
    install_dependencies()

@roles('app', 'test')
def install_dependencies():
    with cd(APP_PATH_SRC):
        run('source ../../bin/activate && pip install -r requirements.txt')

@roles('test')
def update_test(dev_branch="master"):
    '''Update app on the test server. Optionally takes dev_branch=<name> arg, default "master".'''
    update_app(dev_branch)
    sudo('sudo supervisorctl restart uniboard-test')

@roles('app')
def check_app_running():
    run('if [ $(curl -L -s localhost:{app_port}| grep {check_for} | wc -l) -ge 1 ]; then echo "Uniboard running on localhost:{app_port}"; fi'
            .format(app_port=USER_APP_PORT, check_for="UniBoard")
    )

@roles('app')
def print_app_config():
    print_keys = {
            'secret_settings.py': ['RECAPTCHA'],
            'settings.py': ['DOMAIN', 'SUPPRESS_ERROR_EMAILS', 'DEBUG']
    }
    for file_, keys in print_keys.items():
        for key in keys:
            run('grep {key} {app_path}/portality/{file_}'.format(file_=file_, key=key, app_path=APP_PATH_SRC))

@roles('app')
def reload(supervisor_task_name='uniboard'):
    sudo('kill -HUP $(sudo supervisorctl pid {0})'.format(supervisor_task_name))
