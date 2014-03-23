#!/usr/bin/python
# Syncs DOAJ newest_articles which are not present in the localhost's doaj index
# Usage: ./sync_doaj_newest_articles.py <source_query_endpoint> <destination_query_endpoint>
# E.g.: ./sync_doaj_newest_articles.py "http://doajtmp:9200/doaj/article/_search?q=admin.in_doaj:true&size=1000&sort=created_date:desc" "http://yonce:9200/doaj/article/_search?q=admin.in_doaj:true&size=1000&sort=created_date:desc"
# IF YOU run this script on yonce, this will copy all newest articles present in doajtmp to yonce. It checks which ones to copy by querying the <destination_query_endpoint> and calculating which ones from the source are not present in there.

# Again, this script calculates which articles needs to be synced from 2
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

    testing = False
    if len(argv) > 3:
        if argv[3] == 'test':
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

    print 'Putting', len(s), 'newest_articles into ES.'
    print 'You have 5 seconds to terminate this script with Ctrl+C if the number seems off.'
    time.sleep(5)

    for diff in s:
        if testing:
            print 'TESTING - would PUT', diff['_id']
        else:
            r = requests.put('http://localhost:9200/doaj/article/' + diff['_id'], data=json.dumps(diff['_source']))
            print diff['_id'], r.status_code
            if r.status_code not in [200, 201]:
                print 'ES error for record', diff['_id'], 'HTTP status code:', r.status_code

    print 'PUT', len(s), 'newest articles into ES.'

if __name__ == '__main__':
    main()
