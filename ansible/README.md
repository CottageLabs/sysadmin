## Ansible tasks for DOAJ

The symlink in the root `doaj -> ansible/` is for backward compatibility for old aliases

---

You'll need to have ansible installed. Tested on version 2.15.1

For tasks that set up new machines, you'll need the digitalocean ansible collection:

	ansible-galaxy collection install -r requirements.yml

For this you'll also need your Digital Ocean personal access token,
https://docs.digitalocean.com/reference/api/create-personal-access-token/
and set the environment variable on your local machine `$DIGITALOCEAN_TOKEN`.

See the documentation https://docs.digitalocean.com/reference/ansible/reference/ for more info.

---

* Deploy new updates on the master branch to servers:

	ansible-playbook -i doaj-hosts.ini update-site.yml

* Deploy new configuration on AWS secrets manager to app machines (runs the deploy script only)

	ansible-playbook -i doaj-hosts.ini update-config.yml

* Restart the service without code or config changes

	ansible-playbook -i doaj-hosts.ini restart.yml

* Reboot metrics and APM on all machines

	ansible-playbook -i doaj-hosts.ini reboot-metrics.yml


## Useful tasks we expect to only run once

These are in the directory ott

* Install the updated digital ocean monitoring agent on production machiens
  (see https://github.com/andrewsomething/ansible-role-do-agent)

        ansible-galaxy install andrewsomething.do-agent
        ansible-playbook -i doaj-hosts.ini ott/reinstall-monitoring.yml

* Upload a new SSH access key to all of our hosts
  set the path for file lookup in the yml file to its path on your local machine.
  todo: can we read this from CLI?

        ansible-playbook -i doaj-hosts.ini ott/upload_ssh_key.yml
