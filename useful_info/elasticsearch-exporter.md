#Use cases
##Export an index

    cd ~/backups/elasticsearch-es-exporter
    node --nouse-idle-notification --expose-gc ~/elasticsearch-exporter -i doaj -g doaj_`date +%F_%H%M` -m 0.6

This should use no more than 60% of the remaining memory on the server (the -m parameter). Up it to 0.9 for a faster operation if the server has lots of RAM to spare.
