## Create, Destroy, and View DigitalOcean resources

## TODO:

 - [ ] ansible galaxy modules required - Digital Ocean and Community General for supervisorctl
 - [ ] refactor into roles
 - [ ] more TODOs

It's handy to have the yaml callback for readability. Example command:

    ANSIBLE_STDOUT_CALLBACK=yaml ansible-playbook -i localhost, -c local create_app_server.yml -v