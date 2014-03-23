#!/bin/bash
if [ $# -ne 1 ]
then
    echo "Usage: $0 http://<server running ES>:<ES port>"
    echo "E.g.: $0 http://yonce:9200"
    exit 1
fi

echo -n "The whole DOAJ index: "; curl "$1""/doaj/_count" ; echo
echo -n "Accounts: "; curl "$1""/doaj/account/_count" ; echo
echo -n "Articles: "; curl "$1""/doaj/article/_count" ; echo
echo -n "Journals: "; curl "$1""/doaj/journal/_count" ; echo
echo -n "Suggestions: "; curl "$1""/doaj/suggestion/_count" ; echo
echo -n "Uploads: "; curl "$1""/doaj/upload/_count" ; echo
echo -n "Cache: "; curl "$1""/doaj/cache/_count" ; echo
echo -n "ToC-s: "; curl "$1""/doaj/toc/_count" ; echo
