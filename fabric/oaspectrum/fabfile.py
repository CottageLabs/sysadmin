from fabric.api import env, run, sudo, cd, abort, roles, execute, warn_only

env.use_ssh_config = True  # username, identity file (key), hostnames for machines will all be loaded from ~/.ssh/config
# COMMON COMMANDS
# fab update_test - puts newest master on the test server
# fab deploy_live:tag=git_tag_from_repo - rolls out latest tag to live

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


OASPECTRUM_IP = '178.62.3.108'
RICHARD_TEST_IP = '178.62.191.218'
APP_SERVER_NAMES = {'OASPECTRUM': OASPECTRUM_IP}
TEST_SERVER_NAMES = {'RICHARD_TEST': RICHARD_TEST_IP}

APP_PATH_SRC = '/opt/oaspectrum/src/oaspectrum'  # path on remote servers to the OACWellcome app
TEST_APP_PATH_SRC = '/opt/oaspectrum/oaspectrum'  # path on test to the OACWellcome app
USER_APP_PORT = 5050

# Used when running tasks directly, e.g. fab update_app . Not (yet)
# used when a task is calling multiple other tasks
# programmatically. Enables us to not have to specify "which hosts" 
# all the time when running Fabric.
env.roledefs.update(
        {
            'app': [OASPECTRUM_IP], 
            'test': [RICHARD_TEST_IP],
        }
)

@roles('app')
def deploy_live(tag, branch='master'):
    update_app(branch=branch, tag=tag)
    reload_app()

@roles('app')
def update_app(env, branch='master', tag=''):

    if env == 'test':
        app_dir = TEST_APP_PATH_SRC
    else:
        app_dir = APP_PATH_SRC

    with cd(app_dir):
        run('git config user.email "us@cottagelabs.com"')
        run('git config user.name "Cottage Labs LLP"')
        stash = run('git stash')
        run('git checkout master')  # so that we have a branch we can definitely pull in
                                    # (in case we start from one that was set up for pushing only)

        run('git pull', pty=False)
        run('git branch --set-upstream-to origin/{branch}'.format(branch=branch))  # make sure we can pull here
        run('git checkout ' + branch)
        run('git pull', pty=False)
        if tag:
            run('git checkout {0}'.format(tag))
        run('git submodule update --init --recursive', pty=False)
        run('git submodule update --recursive', pty=False)
        if not 'No local changes to save' in stash:
            with warn_only():
                run('git stash apply')
    install_dependencies(env=env)

@roles('app', 'test')
def install_dependencies(env):
    sudo('sudo apt-get update -q -y')
    sudo('sudo apt-get -q -y install libxml2-dev libxslt-dev python-dev lib32z1-dev')

    if env == 'test':
        app_dir = TEST_APP_PATH_SRC
        env_path = '../env'
    else:
        app_dir = APP_PATH_SRC
        env_path = '../..'

    with cd(app_dir + '/esprit'):
        run('source ../{env_path}/bin/activate && pip install -e .'.format(env_path=env_path))

    with cd(app_dir + '/magnificent-octopus'):
        run('source ../{env_path}/bin/activate && pip install -e .'.format(env_path=env_path))

    with cd(app_dir):
        run('source {env_path}/bin/activate && pip install -e .'.format(env_path=env_path))

@roles('test')
def update_test(dev_branch="master"):
    '''Update app on the test server. Optionally takes dev_branch=<name> arg, default "master".'''
    update_app(env='test', branch=dev_branch)
    sudo('sudo supervisorctl restart spectrum-test')

@roles('app')
def check_app_running():
    run('if [ $(curl -L -s localhost:{app_port}/health | grep {check_for} | wc -l) -ge 1 ]; then echo "App running on localhost:{app_port}"; fi'
            .format(app_port=USER_APP_PORT, check_for="All OK")
    )
    # there's also /health on the app

@roles('app')
def reload_app(supervisor_task_name='oaspectrum-production'):
    sudo('kill -HUP $(sudo supervisorctl pid {0})'.format(supervisor_task_name))

@roles('app')
def deploy_live(branch='master', tag=""):
    update_app(env='production', branch=branch, tag=tag)
    execute(reload_app, hosts=env.roledefs['app'])
