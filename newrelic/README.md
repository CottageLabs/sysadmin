NOTE: all relative paths in these instructions are relative to this README file.

Main newrelic system monitor (server monitor called newrelic-sysmond): follow instructions on newrelic website, no modifications needed.

Of course, you need to install that successfully first before installing the MeetMe plugin
(elasticsearch, nginx, memcached, redis and lots of other monitoring supported).

Elasticsearch and nginx plugins:

1. follow instructions on RPM (the newrelic control panel) to install the newrelic_plugin_agent via pip
2. sudo cp ./newrelic_plugin_agent.cfg /etc/newrelic/
3. sudo vim /etc/newrelic/newrelic_plugin_agent.cfg  # put the Newrelic license key on the line which says INSERT LICENSE KEY HERE
4. make sure the elasticsearch and nginx configs are correct

    a. elasticsearch should be running on localhost:9200
    
    b. nginx's "default" site which responds to http://localhost
    (i.e. port 80, no domain name) should be linked to from sites-enabled and
    should have the nginx stats module activated - see
    ../config/nginx/default for an example "default" site file)

5. Alright, just test it now.

    # first, let ourselves run the newrelic plugin as the newrelic user would run it when it's a service
    sudo usermod -a -G newrelic cloo
    sudo chown newrelic:newrelic /var/log/newrelic
    sudo chown newrelic:newrelic /var/run/newrelic

    # alright, now test the config - won't run as a daemon, just outputs to terminal
    newrelic_plugin_agent -c /etc/newrelic/newrelic_plugin_agent.cfg -f
    # there should be no errors - if there are, check the config is correct YAML,
    # check your nginx http status path and ES settings, check the nginx error log and the ES error log as needed

6. Set it up as a service if everything is OK and you start seeing data in a couple of minuts on the Newrelic RPM control panel:

    sudo cp /opt/newrelic_plugin_agent/newrelic_plugin_agent.deb /etc/init.d/newrelic_plugin_agent
    sudo chmod a+x /etc/init.d/newrelic_plugin_agent
    sudo update-rc.d newrelic_plugin_agent defaults 95 05
    sudo sysv-rc-conf --list | grep newrelic  # should return something like newrelic-plu (as well as newrelic-sys, the main newrelic monitor)
