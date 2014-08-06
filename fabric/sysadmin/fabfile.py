from fabric.api import env, run, sudo, cd, abort, roles, execute, warn_only

import time
import sys

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

servers = {
    'yonce': '95.85.59.151',
    'clgate1': '95.85.56.138',
    'mark_test': '93.93.131.120',
    'richard_test': '188.226.208.42',
    'pinky': '188.226.153.213',
    'cl_website': '46.235.224.100',
    'arttactic': '46.235.224.107',
    'oamonitor': '188.226.213.168',
}

all_servers = []
for name, server in servers.items():
    if server not in all_servers:
        all_servers.append(server)

SYSADMIN_SRC_PATH = '/opt/sysadmin'  # path on remote servers to the sysadmin repo
ES_EXPORTER_BACKUPS_PATH = '/home/cloo/backups/elasticsearch-es-exporter'

env.roledefs.update(
        {
            'app': [servers['cl_website'], servers['arttactic'], servers['yonce']], 
            'gate': [servers['clgate1']],
            'test': [servers['mark_test'], servers['richard_test'], servers['pinky'], servers['oamonitor']]
        }
)


@roles('app', 'gate', 'test')
def update_sysadmin():
    with warn_only():
        with cd(SYSADMIN_SRC_PATH):
            run('git pull', pty=False)

@roles('app', 'gate', 'test')
def push_sysadmin():
    with warn_only():
        with cd(SYSADMIN_SRC_PATH):
            run('git push')

@roles('app', 'gate', 'test')
def create_sysadmin():
    with warn_only():
        with cd('/opt'):
            sudo('mkdir -p sysadmin')
            sudo('chown cloo:cloo sysadmin')
            run('git clone https://github.com/CottageLabs/sysadmin.git', pty=False)

@roles('app', 'gate', 'test')
def apt_install(packages):
    '''
    Install one or more software packages across all hosts.
    :param packages: A space-separated string of package names. Can be just a single name as well.
    
    This task will fail immediately if one of the servers fails to install the software and will
    not proceed with trying to install it on any more servers.
    '''
    sudo('apt-get -q -y install ' + packages, pty=False)

def _get_hosts(from_, to_):
    FROM = from_.lower()
    TO = to_.lower()
    if FROM not in servers or TO not in servers:
        abort('only the following server names are valid: ' + ', '.join(servers))
    source_host = servers[FROM]
    target_host = servers[TO]
    return FROM, source_host, TO, target_host

# call this like:
# fab transfer_index:index=doaj,from_=yonce,to_=pinky
def transfer_index(index, from_, to_, restore_only=False, scp=False, filename=None, restore_batch_size=None, restore_sleep=None):
    ''':index=,from_=,to_= - Copy an index from one machine to another. Requires elasticsearch-exporter (nodejs app) on source machine. Read src for more options.'''
    restore_only = (restore_only == True)  # all args get stringified by fabric
    scp = (scp == True)

    FROM, source_host, TO, target_host = _get_hosts(from_, to_)

    if restore_only and not filename:
        print 'You probably want to specify a specific filename to restore.'
        sys.exit(1)

    execute(update_sysadmin, hosts=[source_host, target_host])

    if not filename:
        timestamp = time.strftime('%Y-%m-%d_%H%M')
        filename = '{index}_{timestamp}'.format(index=index, timestamp=timestamp)

    if not restore_only:
        execute(backup_index_locally, index=index, directory=ES_EXPORTER_BACKUPS_PATH, filename=filename, hosts=[source_host])

    if (restore_only and scp) or not restore_only:
        try:
            execute(secure_copy, filename_pattern=filename + '*', target_host=target_host, remote_path=ES_EXPORTER_BACKUPS_PATH, hosts=[source_host])
        except SystemExit:
            print
            print 'Looks like the secure copy failed - maybe your connection timed out since you didn\'t see that the backup had finished? Trying again...'
            print
            execute(secure_copy, filename_pattern=filename + '*', target_host=target_host, remote_path=ES_EXPORTER_BACKUPS_PATH, hosts=[source_host])

        execute(__uncompress_backups, filename=filename, hosts=[target_host])

    execute(__es_bulk_restore, index=index, filename=filename, restore_batch_size=restore_batch_size, restore_sleep=restore_sleep, hosts=[target_host])

def backup_index_locally(index, directory, filename):
    with cd(directory):
        run('node --nouse-idle-notification --expose-gc ~/elasticsearch-exporter -i {index} -g {filename} -m 0.6'.format(index=index, filename=filename))

def secure_copy(filename_pattern, target_host, remote_path):
    print 'If the next command fails, you\'ll need to set up proper ssh keys on the servers so that the source can connect to the target. You will be asked for the key\'s passphrase!'
    with cd(ES_EXPORTER_BACKUPS_PATH):
        run('scp {filename_pattern} cloo@{target_host}:{remote_path}'.format(filename_pattern=filename_pattern, target_host=target_host, remote_path=remote_path))


def __es_bulk_restore(index, filename, restore_batch_size=None, restore_sleep=None):
    with cd(ES_EXPORTER_BACKUPS_PATH):
        thescript = SYSADMIN_SRC_PATH + '/backup/elasticsearch/bulk_restore.py'
        mapping_filename = ES_EXPORTER_BACKUPS_PATH + '/' + filename + '.meta'
        data_filename = ES_EXPORTER_BACKUPS_PATH + '/' + filename + '.data'
        cmd = 'python {thescript} -i {index} {mapping_filename} {data_filename}'.format(thescript=thescript, index=index, mapping_filename=mapping_filename, data_filename=data_filename)
        if restore_batch_size:
            cmd += ' -b ' + restore_batch_size
        if restore_sleep:
            cmd += ' -s ' + restore_sleep
        run(cmd)


def __uncompress_backups(filename):
    with cd(ES_EXPORTER_BACKUPS_PATH):
        run('mv {filename}.data {filename}.data.gz'.format(filename=filename))
        run('gunzip {filename}.data.gz'.format(filename=filename))
