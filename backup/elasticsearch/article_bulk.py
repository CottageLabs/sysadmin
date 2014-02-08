import requests
import sys
import json

def usage():
    print 'Usage:', sys.argv[0], '<mapping filename>', '<data filename>', '<bulk batch size>'
    sys.exit(1)

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
    
    raw_input('Going to delete DOAJ index NOW. <Enter> to continue, Ctrl+C to stop now and preserve the index.')
    requests.delete('http://localhost:9200/doaj')
    
    with open(argv[1], 'rb') as i:
        data = json.dumps(json.loads(i.read()))  # make it obvious when the mapping is not valid JSON, this would throw an exception
        ri = requests.post('http://localhost:9200/doaj/article')
        r = requests.put('http://localhost:9200/doaj/article/_mapping', data=data)
        print 'data mapping', r.status_code
    
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
        
if __name__ == '__main__':
    main()
