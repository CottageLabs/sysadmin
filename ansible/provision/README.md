## Create, Destroy, and View DigitalOcean resources

Install required collections

    ansible-galaxy collection install -r requirements.yml

## TODO:

 -[ ] more TODOs

It's handy to have the yaml callback for readability. Example command:

    ANSIBLE_STDOUT_CALLBACK=yaml ansible-playbook -i localhost, -c local create_app_server.yml -v