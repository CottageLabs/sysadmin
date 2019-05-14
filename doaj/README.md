## Ansible tasks for DOAJ

You'll need to have ansible installed. Tested on version 2.7.0

* Deploy new updates on the master branch to servers:

	ansible-playbook -i doaj-hosts.ini update-site.yml

# Deploy new configuration on AWS secrets manager to app machines (runs the deploy script only)

	ansible-playbook -i doaj-hosts.ini update-config.yml

* Restart the service without code or config changes

	ansible-playbook -i doaj-hosts.ini restart.yml

* Reboot metrics and APM on all machines

	ansible-playbook -i doaj-hosts.ini reboot-metrics.yml
