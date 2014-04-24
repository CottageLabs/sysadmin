#!/usr/bin/python

from datetime import datetime
import argparse
import os
import sys
import logging
import subprocess
import shlex
import time

LOG_FORMAT = '%(asctime)-15s :: %(levelname)-6s:  %(message)s'
logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)
logger = logging.getLogger(__name__)

DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 9200
DEFAULT_QUERY_SIZE = 10
DEFAULT_EXEC = ['node', '--nouse-idle-notification', '--expose-gc', '/home/cloo/elasticsearch-exporter', '-m 0.3']

# The following options should be (kept) the same as the nodejs app
# "elasticsearch-exporter" options related to backing up stuff.
# Easier to stay consistent - even if this script eventually has its own
# support for exporting data into bulk ES format, or starts using ES 1.x
# snapshots etc.

# all of these entries must have the "short" and "long" keys defined
# "long" is used for fetching the value passed to this script using argparse
# "short" is used when passing the argument on to the exporter

EXPORTER_PARAMS = [
    {'short': "-a", 'long': "--host", 'default': DEFAULT_HOST, 'help': "The hostname from which data is to be exported from. Default: {0}".format(DEFAULT_HOST)}, 
    {'short': "-p", 'long': "--port", 'default': DEFAULT_PORT, 'help': "The port of the source host to talk to. Default: {0}".format(DEFAULT_PORT)}, 
    {'short': "-i", 'long': "--index", 'help': "Pass the index name when you are exporting a single index. Default: export all indices"},
    {'short': "-t", 'long': "--type", 'help': "The type from which to export data from. Default: the entire index is exported"},
    {'short': "-s", 'long': "--query", 'help': "Define a query that limits what kind of documents are exported from the source. Default: all documents are exported"},
    {'short': "-z", 'long': "--size", 'default': DEFAULT_QUERY_SIZE, 'help': "The maximum number of results to be returned per query. Default: {0}".format(DEFAULT_QUERY_SIZE)}, 
    {'short': "-g", 'long': "--targetFile", 'help': "The filename base to which the data should be exported (becomes <filename>.data and <filename>.meta). The format depends on the compression flag (default = compressed). Default filename base: <host>_<timestamp> . If an index is specified, <index>_<timestamp>. If a type is specified, <index>_<type>_<timestamp>. WARNING: define a suitable filename if you're using --query!"},
]

def main(argv=None):
    if not argv:
        argv = sys.argv

    parser = argparse.ArgumentParser()
    parser.add_argument("backup_directory", help="Will be created with mkdir -p if it doesn't exist. Probably best if you ensure it exists and has the correct permissions though.")
    
    for p in EXPORTER_PARAMS:
        short = p['short']; long_ = p['long']; default = p.get('default'); help_ = p.get('help');
        parser.add_argument(short, long_, default=default, help=help_)

    # UI / CLI - this param is much more rarely used (if ever), so
    # goes at the bottom of the list
    parser.add_argument("--exporter", action=StoreAsList, default=DEFAULT_EXEC, help='Which executable to use for the actual export operation. It will get all the short options. Default: "{0}"'.format(' '.join(DEFAULT_EXEC))) 
    parser.add_argument("--s3-bucket", help="If you specify this (format: s3://BUCKET_NAME ), the resulting backup files will be put on a S3 bucket with the most restrictive access permissions. Existing files will be overwritten, so if you are also using a custom filename with -g or --targetFile, make sure to include a timestamp in it.") 

    args=parser.parse_args(argv[1:])

    filename_base = args.targetFile
    if not filename_base:
        timestamp = time.strftime('%Y-%m-%d-%H%M%S')
        filename_base_elements = []
        nohost = False
        if args.index:
            filename_base_elements.append('{index}')
            nohost = True
        if args.type:
            filename_base_elements.append('{type}')
            nohost = True

        if not nohost:
            filename_base_elements.append('{host}')

        filename_base_elements.append('{timestamp}')
        filename_base = '_'.join(filename_base_elements)
        filename_base = filename_base.format(host=args.host, index=args.index, type=args.type, timestamp=timestamp)

    exporter_args = []
    for p in EXPORTER_PARAMS:
        pname = p['long'][2:]
        argval = getattr(args, pname)

        if pname == 'targetFile':
            argval = filename_base

        if argval:
            exporter_args.append(p['short'])
            exporter_args.append(str(argval))  # remove the dashes when accessing that argument in the args Namespace obj

    logger.info('Going into {0}.'.format(args.backup_directory))
    cd(args.backup_directory)

    start = datetime.now()
    logger.info('Starting export using {exporter} at {time}'.format(exporter=' '.join(args.exporter + exporter_args), time=start))
    output = run_command(args.exporter + exporter_args)
    end = datetime.now()
    elapsed = end - start
    logger.info('Export finished at {time}'.format(time=end))
    logger.info('Export took {time}'.format(time=elapsed))

    if args.s3_bucket:
        upload_filename = filename_base + '.meta'
        logger.info('Putting {file} into S3 bucket {bucket}.'.format(file=upload_filename, bucket=args.s3_bucket))
        output = run_command(['s3cmd', 'put', '--acl-private', '-H', upload_filename, args.s3_bucket])

        upload_filename = filename_base + '.data'
        logger.info('Putting {file} into S3 bucket {bucket}.'.format(file=upload_filename, bucket=args.s3_bucket))
        output = run_command(['s3cmd', 'put', '--acl-private', '-H', upload_filename, args.s3_bucket])

    logger.info('All done.')


def cd(directory, recursion_level=0):
    if recursion_level > 2:
        fail('The attempt to change the current working directory to {0} has failed - this script keeps trying to create it and failing to cd into it repeatedly.'.format(directory))
    try:
        os.chdir(directory)
    except OSError as e:
        if e.errno == 2:
            logger.info('Directory {0} does not exist, attempting to create with mkdir -p...'.format(directory))
            output = run_command(['mkdir', '-p', directory])
            cd(directory, recursion_level=recursion_level+1)
        else:
            raise e


def run_command(arguments, *args, **kwargs):
    '''Takes a list as 1st argument and passes everything to subprocess.check_output, keeping the signature the same as subprocess.check_output.'''
    stderr = kwargs.pop('stderr', subprocess.STDOUT)  # capture stderr by default, but allow override via kwargs

    try:
        output = subprocess.check_output(arguments, *args, stderr=stderr, **kwargs)
    except OSError as e:
        if e.errno == 2:
            fail('Cannot find the executable ' + arguments[0])
        raise e
    except subprocess.CalledProcessError as e:
        log(' '.join(e.cmd), 'failed with return code', str(e.returncode), "output below\n", str(e.output), severity='error')
        raise e
    return output


def log(*args, **kwargs):
    severity = kwargs.pop('severity', 'debug')  # not allowed a keyword arg after *args
    logfunc = getattr(logger, severity)

    msg = ' '.join(args)
    logfunc(msg)


def fail(*args, **kwargs):
    log(*args, severity='error')
    sys.exit(kwargs.pop('status', 1))


class StoreAsList(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, shlex.split(values))


if __name__ == '__main__':
    main()
    
