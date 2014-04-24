#!/usr/bin/python

from datetime import datetime
import argparse
import os
import sys
import logging
from subprocess import check_output, CalledProcessError
import shlex
import time

LOG_FORMAT = '%(asctime)-15s :: %(levelname)-6s:  %(message)s'
logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)
logger = logging.getLogger(__name__)

DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 9200
DEFAULT_QUERY_SIZE = 10
DEFAULT_EXEC = ['/usr/bin/node', '--nouse-idle-notification', '--expose-gc', '/home/cloo/elasticsearch-exporter', '-m 0.3']

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
    parser.add_argument("backup_directory")
    
    for p in EXPORTER_PARAMS:
        short = p['short']; long_ = p['long']; default = p.get('default'); help_ = p.get('help');
        parser.add_argument(short, long_, default=default, help=help_)

    # UI / CLI - this param is much more rarely used (if ever), so
    # goes at the bottom of the list
    parser.add_argument("--exporter", action=StoreAsList, default=DEFAULT_EXEC, help='Which executable to use for the actual export operation. It will get all the short options. Default: "{0}"'.format(' '.join(DEFAULT_EXEC))) 

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

    os.chdir(args.backup_directory)
    try:
        output = check_output(args.exporter + exporter_args)
    except OSError as e:
        if e.errno == 2:
            fail('Cannot find the exporter executable ' + args.exporter)
        raise e
    except CalledProcessError as e:
        log(' '.join(e.cmd), 'failed with return code', str(e.returncode), "output below\n", str(e.output), severity='error')
        raise e


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
    
