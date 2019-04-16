## Ansible tasks for DOAJ

You'll need to have ansible installed. Tested on version 2.7.0

* Deploy new updates to the master branch:

	ansible-playbook -i doaj-hosts.ini update-site.yml

* Restart the service

	ansible-playbook -i doaj-hosts.ini restart.yml

* Reboot metrics and APM

	ansible-playbook -i doaj-hosts.ini reboot-metrics.yml
