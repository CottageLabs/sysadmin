import requests
import sys
import json
from time import sleep

config = {}
config['ELASTIC_SEARCH_HOST'] = 'http://localhost:9200'

def usage():
    print 'Usage:', sys.argv[0], '<mapping filename>', '<data filename>', '<bulk batch size>'
    sys.exit(1)

def put_mapping(mapping_dict):
    for index in mapping_dict:
        if not index.startswith('_'):
            #r = requests.put('http://localhost:9200/' + index + '/_mapping', data=json.dumps(data))
            #print index, 'data mapping', r.status_code

            i = str(config['ELASTIC_SEARCH_HOST']).rstrip('/')
            i += '/' + index
            for key, mapping in mapping_dict[index].iteritems():
                im = i + '/' + key + '/_mapping'
                exists = requests.get(im)
                if exists.status_code != 200:
                    ri = requests.post(i)
                    r = requests.put(im, json.dumps(mapping))
                    print key, r.status_code
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
    
    #with open(argv[1], 'rb') as i:
    #    data = json.loads(i.read())
    #    put_mapping(data)
    
    with open(argv[2], 'rb') as i:
        counter = 0
        while True:
            counter += 1
            print 'On batch', counter
            batch = []
            cur_no_of_lines = 0
            for line in i:
                cur_no_of_lines += 1
                if cur_no_of_lines < no_of_lines:
                    batch.append(line)
                else:
                    break

            if cur_no_of_lines == 0:
                break
    
            data = "".join(batch)
            r = requests.post('http://localhost:9200/_bulk', data=data)
            if r.status_code != 200:
                print '  Batch', counter, 'error. HTTP response:', r.status_code
                sys.exit(1)
            sleep_seconds = int(str(batch_size)[0]) # 2 for 20 items, 2 for 2000 items, 2 for 20000 items.
            sleep(sleep_seconds)
        
if __name__ == '__main__':
    main()
