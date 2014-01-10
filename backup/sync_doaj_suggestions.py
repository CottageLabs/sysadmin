#!/usr/bin/python
# Syncs DOAJ suggestions which are not present in the localhost's doaj index
# Usage: ./sync_doaj_suggestions.py <source_query_endpoint> <destination_query_endpoint>
# E.g.: ./sync_doaj_suggestions.py "http://93.93.135.219/query/suggestion?size=15000" "http://localhost:5050/query/suggestion?size=15000"
#    if you run this on CL2, the OpenArticleGauge server, you will end up copying all suggestions from the DOAJ server to CL2
# This will copy all suggestions present in 93.93.135.219 to localhost. It checks which ones to copy by querying the <destination_query_endpoint> and calculating which ones from the source are not present in there.
import requests
import sys
import json

def abort(msg):
    raise Exception(msg)

def mock_src():
    mock = '''{
    "hits": {
        "hits": [
            {
                "_score": 1.0,
                "_type": "suggestion",
                "_id": "test",
                "_source": {
                    "index": {
                        "publisher": [
                            "Boston College Law School"
                        ],
                        "issn": [
                            "0161-6587",
                            "1930-661X"
                        ],
                        "license": [
                            null
                        ],
                        "title": [
                            "Boston College Law Review"
                        ]
                    },
                    "last_updated": "2013-12-13T22:34:05Z",
                    "admin": {
                        "notes": [
                            {
                                "date": "2013-12-13T22:34:05Z",
                                "note": "not OA, 110125/SB"
                            },
                            {
                                "date": "2013-12-13T22:34:05Z",
                                "note": "ed. informed"
                            }
                        ],
                        "contact": [
                            {
                                "name": "John Gordon",
                                "email": "john.gordon@bc.edu"
                            }
                        ],
                        "application_status": "rejected",
                        "in_doaj": false
                    },
                    "suggestion": {
                        "suggested_on": "2009-03-24 18:28:35",
                        "description": "The Boston College Law Review is the oldest scholarly publication at Boston College Law School. The Review publishes articles concerning legal issues of national interest. The Review publishes five issues each year that include articles and essays written by prominent outside authors (such as Professor Edward Imwinkelried, Reverend Jesse Jackson, and Judge Leon Higginbotham).",
                        "suggester": {
                            "name": "Deena Frazier",
                            "email": "deena.frazier@bc.edu"
                        },
                        "suggested_by_owner": false
                    },
                    "created_date": "2013-12-13T22:34:05Z",
                    "id": "test",
                    "bibjson": {
                        "publisher": "Boston College Law School",
                        "license": [
                            {
                                "open_access": false
                            }
                        ],
                        "title": "Boston College Law Review",
                        "link": [
                            {
                                "url": "http://www.bc.edu/schools/law/lawreviews/bclawreview.html",
                                "type": "homepage"
                            }
                        ],
                        "oa_end": {},
                        "provider": "Boston College Law School",
                        "oa_start": {},
                        "identifier": [
                            {
                                "type": "pissn",
                                "id": "0161-6587"
                            },
                            {
                                "type": "eissn",
                                "id": "1930-661X"
                            }
                        ]
                    }
                },
                "_index": "doaj"
            }
        ],
        "total": 14441,
        "max_score": 1.0
    },
    "_shards": {
        "successful": 5,
        "failed": 0,
        "total": 5
    },
    "took": 1585,
    "timed_out": false
}
'''
    return mock

def main(argv=None):
    if not argv:
        argv=sys.argv

    src = argv[1]
    dst = argv[2]

    testing = False
    if len(argv) > 3:
        if argv[3] == 'test':
            testing = True

    if testing:
        source_data = mock_src()
    else:
        source_data = requests.get(src).text

    s = json.loads(source_data)
    d = json.loads(requests.get(dst).text)
    
    s_total = s['hits']['total']
    s = s['hits']['hits']
    
    d_total = d['hits']['total']
    d = d['hits']['hits']

    if s_total <= d_total:
        abort("Source has less or same number of docs as destination, aborting since your source and destination could be out of sync.")

    removed = 0
    for s_hit in s[:]:
        for d_hit in d:
            if s_hit["_id"] == d_hit["_id"]:
                #print 'removing', s_hit['_id']
                removed += 1
                s.remove(s_hit)
    #print 'removed', removed

    #print s
    for diff in s:
        r = requests.put('http://localhost:9200/doaj/suggestion/' + diff['_id'], data=json.dumps(diff))
        if r.status_code not in [200, 201]:
            print 'ES error for record', diff['_id'], 'HTTP status code:', r.status_code

    print 'PUT', len(s), 'suggestions into ES.'

if __name__ == '__main__':
    main()
