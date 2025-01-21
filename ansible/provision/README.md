## Create, Destroy, and View DigitalOcean resources

Install required collections

    ansible-galaxy collection install -r requirements.yml

## TODO:

 -[ ] Refactor sub-tasks into roles / tasks
 -[ ] Make better use of secrets and templates
 -[ ] more TODOs

## Provisioning machines

To interact with DigitalOcean resources you will need an access token - our playbooks expect it to be stored in an environment variable:

    export DIGITALOCEAN_TOKEN=dop_v1_...

Then e.g. create the maintenance page server:

    ansible-playbook create_maintenance_page_server.yml --private-key=~/.ssh/cl_ed25519

It can also be handy to use the yaml output callback for readability. Example command:

    ANSIBLE_STDOUT_CALLBACK=yaml ansible-playbook -i localhost, -c local create_app_server.yml -v