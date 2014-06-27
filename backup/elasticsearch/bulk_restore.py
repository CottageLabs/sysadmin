#!/usr/bin/python

import requests
import sys
import json
from time import sleep
from datetime import datetime
import argparse

config = {}
config['ELASTIC_SEARCH_HOST'] = 'http://localhost:9200'
config['ELASTIC_SEARCH_HOST'] = config['ELASTIC_SEARCH_HOST'].rstrip('/')
config['RETRY_ES'] = 30

def put_mapping(mapping_dict):
    for index in mapping_dict:
        if not index.startswith('_'):
            # create the index first
            i = config['ELASTIC_SEARCH_HOST']
            i += '/' + index
            ri = requests.put(i)
            if ri.status_code != 200:
                print 'Failed to create Index:', index, ', HTTP Response:', ri.status_code
                print ri.text
                sys.exit(3)
            # now create each type inside the index
            for key, mapping in mapping_dict[index]['mappings'].iteritems():
                im = i + '/' + key + '/_mapping'
                exists = requests.get(im)
                # do not overwrite existing mappings
                if exists.status_code != 200:
                    themapping = {}
                    themapping[key] = mapping
                    r = requests.put(im, json.dumps(themapping))
                    if r.status_code != 200:
                        print 'Failed to do PUT mapping for Index:', index, ', Key:', key, ', HTTP Response:', r.status_code
                        sys.exit(4)
                    else:
                        print 'Mapping OK for Index:', index, ', Key:', key, ', HTTP Response:', r.status_code
                else:
                    print 'Mapping already exists for Index:', index, ', Key:', key
        else:
            print 'Ignoring {0}, no index names start with _'.format(index)

def main(argv=None):
    if not argv:
        argv = sys.argv

    parser = argparse.ArgumentParser()
    parser.add_argument("mapping_filename")
    parser.add_argument("data_filename")
    BATCH_SIZE_DEFAULT = 2000
    parser.add_argument("-i", "--index", help="Pass the index name when you are restoring a single index.")
    parser.add_argument("-b", "--batch-size", type=int, help="Size of each batch of items sent to ES. Default: {0}".format(BATCH_SIZE_DEFAULT))
    parser.add_argument("-t", "--dry-run", action="store_true")
    parser.add_argument("-y", "--destroy-all", action="store_true", help="Pass this to delete all indices in the target ES instance and skip the question this script would otherwise ask about this.")
    parser.add_argument("-n", "--no-destroy-all", action="store_true", help="Pass this to skip deleting all indices in the target ES instance and skip the question this script would otherwise ask about this. NOTE: The script will skip updating the mappings if you do not agree to delete all data. (You have to reindex after a mapping update.)")
    parser.add_argument("-s", "--sleep", type=int, help="Number of seconds to sleep between batches. Pass 0 to disable sleeping. Default: the first digit of your batch size. If sending 20 items, sleep 2 seconds between them. Same for 200 or 200'000 items. Sending 30, 3'000 (and so on) items will sleep for 3 seconds by default.")
    args=parser.parse_args(argv[1:])

    mapping_filename = args.mapping_filename
    data_filename = args.data_filename
    
    index = args.index
    batch_size = args.batch_size if args.batch_size else BATCH_SIZE_DEFAULT

    dry_run = args.dry_run

    sleep_seconds = args.sleep if args.sleep or args.sleep == 0 else int(str(batch_size)[0]) # Default case: first digit of batch size. 2 for 20 items, 2 for 2000 items, 2 for 20000 items. 3 for 30 items, 4 for 400 items.
    
    no_of_lines = batch_size * 2  # 2 actual lines get read in for every item in the batch

    if dry_run:
        print 'THIS IS A DRY RUN. No operations will actually be performed, including deleting data, updating mappings and sending data to ES in bulk.'
    if index:
        print 'INDEX:', index
    print 'BATCH SIZE:', batch_size
    print 'SLEEPING for {0} seconds between batches.'.format(sleep_seconds)

    if index:
        delete_what = 'the ' + index + ' index'
    else:
        delete_what = 'all indices'

    if args.destroy_all:
        delete = True
    else:
        if args.no_destroy_all:
            delete = False
        else:
            # we don't know, we need to ask
            print 'If you want to update the mappings you will have to reindex the data. With this in mind...'
            delete = raw_input('  Do you want to delete {delete_what} now? Enter "yes, destroy all the data" to do so, or "n" to proceed without deleting anything: '.format(delete_what=delete_what))
            delete = True if delete == "yes, destroy all the data" else False

    if delete:
        print 'DELETING all data in {delete_what}.'.format(delete_what=delete_what)
    else:
        print 'NOT DELETING any data in ES.'

    deleted = False
    if not dry_run:
        if delete:
            if index:
                r = requests.delete(config['ELASTIC_SEARCH_HOST'] + '/' + index)
            else:
                r = requests.delete(config['ELASTIC_SEARCH_HOST'])
            if r.status_code == 200:
                print '  Deleted successfully.'
            else:
                print '  ES reported a problem deleting the data.'
                print '    Status code: {0}.'.format(r.status_code)
                print '    HTTP response body:'
                print r.text
            requests.post(config['ELASTIC_SEARCH_HOST'] + '/_flush')
            sleep(5)
            deleted = True
    else:
        print '  DRY RUN: Not deleting anything.'
    
    if not deleted and not dry_run:
        print 'Skipping mappings update, you chose not to delete any data.'
    else:
        with open(mapping_filename, 'rb') as i:
            data = json.loads(i.read())
            if index:
                data = {index: data}
            if dry_run:
                print '  DRY RUN: Mapping loaded successfully from file, but not going to send it to ES.'
            else:
                put_mapping(data)
    
    started = datetime.now()

    total_counter = 0
    with open(data_filename, 'rb') as i:
        counter = 0
        while True:
            counter += 1
            print 'On batch', counter, '. Done {0} items so far.'.format(total_counter / 2.0)
            batch = []
            cur_no_of_lines = 0
            for line in i:
                cur_no_of_lines += 1
                batch.append(line)
                if cur_no_of_lines >= no_of_lines:
                    break

            if cur_no_of_lines == 0:
                break
            total_counter += len(batch)
            data = "".join(batch)

            if dry_run:
                print '  DRY RUN: Batch #{0} constructed, len(batch) = {1}, but not sending to ES.'.format(counter, len(batch))
            else:
                r = None
                count = 0
                exception = None
                while count < config['RETRY_ES']:
                    count += 1
                    try:
                        r = requests.post(config['ELASTIC_SEARCH_HOST'] + '/_bulk', data=data)
                        break
                    except Exception as e:
                        exception = e
                    time.sleep(0.5)
                        
                if exception is not None:
                    raise exception

                if r.status_code != 200:
                    print '  Batch', counter, 'error. HTTP response:', r.status_code
                    print r.text
                    sys.exit(1)
                sleep(sleep_seconds)
    print 'Total lines', total_counter
    print 'Total items', total_counter / 2.0
    print
    print 'Started:', started
    ended = datetime.now()
    print 'Ended:', ended
    print 'Time taken:', ended - started
        
if __name__ == '__main__':
    main()
