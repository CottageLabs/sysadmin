#!/usr/bin/python
# Syncs DOAJ newest records which are not present in the localhost's doaj index
# Usage: ./sync_doaj_records.py source_query_endpoint destination_query_endpoint record_type [test]
# E.g.: ./sync_doaj_records.py "http://doajtmp:9200/doaj/suggestion/_search?q=*&size=1000&sort=created_date:desc" "http://yonce:9200/doaj/suggestion/_search?q=*&size=1000&sort=created_date:desc" suggestion
# IF YOU run this script on yonce, this will copy all newest records present in doajtmp to yonce. It checks which ones to copy by querying the <destination_query_endpoint> and calculating which ones from the source are not present in there.
# Append "test" to the arguments to test the process first, see how many records would go into ES without actually putting them in

# Pay attention to your queries on the command line: make sure you're
# querying the same types of objects as the record_type you pass to this
# script. Otherwise articles may get written to the suggestion type and
# overall chaos will ensue.

# Again, this script calculates which records needs to be synced from 2
# endpoints, but it will WRITE TO LOCALHOST:9200!
import requests
import sys
import json
import time

def abort(msg):
    raise Exception(msg)

def main(argv=None):
    if not argv:
        argv=sys.argv

    src = argv[1]
    dst = argv[2]
    record_type = argv[3]

    testing = False
    if len(argv) > 4:
        if argv[4] == 'test':
            testing = True

    source_data = requests.get(src).text
    dest_data = requests.get(dst).text

    s = json.loads(source_data)
    d = json.loads(dest_data)
    
    s_total = s['hits']['total']
    s = s['hits']['hits']
    
    d_total = d['hits']['total']
    d = d['hits']['hits']

    if s_total < d_total:
        abort("Source has less docs than destination, aborting since your source and destination could be completely out of sync (both have docs than the other one does not). Investigate, fix and rerun.")

    removed = 0
    for s_hit in s[:]:
        for d_hit in d:
            if s_hit["_id"] == d_hit["_id"]:
                removed += 1
                s.remove(s_hit)

    print 'Putting', len(s), 'newest records into ES.'
    print 'You have 5 seconds to terminate this script with Ctrl+C if the number seems off.'
    time.sleep(5)

    for diff in s:
        if testing:
            print 'TESTING - would PUT', diff['_id']
        else:
            r = requests.put('http://localhost:9200/doaj/' + record_type + '/' + diff['_id'], data=json.dumps(diff['_source']))
            print diff['_id'], r.status_code
            if r.status_code not in [200, 201]:
                print 'ES error for record', diff['_id'], 'HTTP status code:', r.status_code

    print 'PUT', len(s), 'newest records into ES.'

if __name__ == '__main__':
    main()
