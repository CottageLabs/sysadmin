from fabric.api import env, run, sudo, cd, abort, roles, execute, warn_only

env.use_ssh_config = True  # username, identity file (key), hostnames for machines will all be loaded from ~/.ssh/config
# This means that you run this script like this:
# fab -H <host1,host2> <task_name>

# E.g.:
# Update sysadmin repo to HEAD of current git master:
# fab update_sysadmin
# This will update it on all servers specified later in this file

# If you want to specify which hosts to update it on:
# fab -H doaj,cl2,doajgate update_sysadmin
    # (replace ssh names with the ones you would use yourself on the command
    # line with ssh - they come from your own ~/.ssh/config)
    # You can also use IP addresses, of course.

# Permissions: if you do not have access to one of the servers (your key
# is not authorised), then exclude it from the task you want to run:
# fab update_sysadmin:exclude_hosts=46.235.224.100


# your local ssh config does not apply when the script is explicitly specifying which hosts to run tasks on...
# or when the script is determining which servers to run on based on
# roles in this file, i.e. you didn't specify with -H on the command line
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
MARK_TEST_IP = '93.93.131.120'
RICHARD_TEST_IP = '93.93.131.168'
CL_WEBSITE_IP = '46.235.224.100'
ARTTACTIC_IP = '46.235.224.107'

SYSADMIN_SRC_PATH = '/opt/sysadmin'  # path on remote servers to the sysadmin repo

env.roledefs.update(
        {
            'app': [CL_WEBSITE_IP, ARTTACTIC_IP, DOAJ_IP, CL2_IP], 
            'gate': [DOAJGATE_IP],
            'test': [MARK_TEST_IP, RICHARD_TEST_IP]
        }
)

@roles('app', 'gate', 'test')
def update_sysadmin():
    with warn_only():
        with cd(SYSADMIN_SRC_PATH):
            run('git pull', pty=False)

@roles('app', 'gate', 'test')
def create_sysadmin():
    with warn_only():
        with cd('/opt'):
            sudo('mkdir -p sysadmin')
            sudo('chown cloo:cloo sysadmin')
            run('git clone https://github.com/CottageLabs/sysadmin.git', pty=False)
