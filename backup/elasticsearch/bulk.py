import requests
import sys
import json
from time import sleep
from datetime import datetime

config = {}
config['ELASTIC_SEARCH_HOST'] = 'http://localhost:9200'

def usage():
    print 'Usage:', sys.argv[0], '<mapping filename>', '<data filename>', '<bulk batch size>'
    sys.exit(1)

def put_mapping(mapping_dict):
    for index in mapping_dict:
        if not index.startswith('_'):
            #r = requests.put('http://localhost:9200/' + index + '/_mapping', data=json.dumps(data))

            i = str(config['ELASTIC_SEARCH_HOST']).rstrip('/')
            i += '/' + index
            ri = requests.put(i)
            if ri.status_code != 200:
                print 'Failed to create Index:', index, ', HTTP Response:', ri.status_code
                print ri.text
                sys.exit(3)
            for key, mapping in mapping_dict[index]['mappings'].iteritems():
                im = i + '/' + key + '/_mapping'
                exists = requests.get(im)
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
            print 'Ignoring {0}, no index names start with _'.format(index)

def main(argv=None):
    if not argv:
        argv = sys.argv

    if len(argv) < 4:
        usage()
    
    try:
        batch_size = int(argv[3])
    except ValueError:
        print 'ERROR: Batch size must be an integer'
        usage()
    
    no_of_lines = batch_size * 2  # 2 actual lines get read in for every item in the batch

    print 'If you want to update the mappings you will have to reindex the data. With this in mind...'
    delete = raw_input('  Do you want to delete all indices now? Enter "yes, destroy all data in ES" to do so, or "n" to proceed without deleting anything: ')
    if delete == "yes, destroy all data in ES":
        r = requests.delete('http://localhost:9200')
        if r.status_code == 200:
            print '  Deleted successfully.'
        else:
            print '  Problem deleting the data. Aborting.'
            sys.exit(2)
        requests.post('http://localhost:9200/_flush')
        sleep(5)
    
    with open(argv[1], 'rb') as i:
        data = json.loads(i.read())
        put_mapping(data)
    
    started = datetime.now()
    print 'Started:', started

    total_counter = 0
    with open(argv[2], 'rb') as i:
        counter = 0
        while True:
            counter += 1
            print 'On batch', counter
            batch = []
            cur_no_of_lines = 0
            for line in i:
                cur_no_of_lines += 1
                if cur_no_of_lines <= no_of_lines:
                    batch.append(line)
                else:
                    break

            if cur_no_of_lines == 0:
                break
            print len(batch) 
            total_counter += len(batch)
            data = "".join(batch)
            r = requests.post('http://localhost:9200/_bulk', data=data)
            if r.status_code != 200:
                print '  Batch', counter, 'error. HTTP response:', r.status_code
                print r.text
                sys.exit(1)
            sleep_seconds = int(str(batch_size)[0]) # 2 for 20 items, 2 for 2000 items, 2 for 20000 items.
            sleep(sleep_seconds)
    print 'Total lines', total_counter
    print 'Total items', total_counter / 2.0
    print
    ended = datetime.now()
    print 'Ended:', ended
    print 'Time taken:', ended - started
        
if __name__ == '__main__':
    main()
