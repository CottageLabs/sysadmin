## Create, Destroy, and View DigitalOcean resources

It's handy to have the yaml callback for readability. Example command:

    ANSIBLE_STDOUT_CALLBACK=yaml ansible-playbook -i localhost, -c local create_app_server.yml -v