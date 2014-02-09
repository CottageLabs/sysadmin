In order to save time you should create DO droplets from images of
existing servers.

However, this means that some settings will be duplicated when both your
new server and the one which was the source of the image are both online
at the same time.

This is what to edit after bringing a new droplet into the world:

###Newrelic

    sudo vim /etc/newrelic/newrelic_plugin_agent.cfg

1. Look for "elasticsearch", change the name: bit to refer to your new
   droplet's hostname.
2. Look for "nginx", do the same.

###Nginx

###Supervisord
