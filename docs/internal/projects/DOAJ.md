---
tags: [project]
status: active
---

# DOAJ

Directory of Open Access Journals. Steve's main role is release manager — releases need to be stable and on-time.

## Infrastructure & Access

Hosted on [[DigitalOcean]], provisioned via [[Ansible sysadmin repo|sysadmin repo]] (`ansible/provision/`). Inventory lives at `ansible/doaj-hosts.ini`, grouped by role:

- `app` / `app-readonly` — public app servers + editor + background worker
- `loadbalancer` — `doaj-lb`
- `opensearch-rw` / `opensearch-r` — search cluster (read-write and read-only nodes)
- `background` — background/task worker
- `monitor` — Kibana log analysis box
- `test` — `static` content server

See [[vm-os-inventory]] for current OS versions per host — several DOAJ boxes are approaching Ubuntu 22.04 EOL (April 2027), plenty of runway.

DNS/WAF/cache sit behind [[Cloudflare]]. Domain: `doaj.org`. Test servers: `{server_name}.doaj.cottagelabs.com`. Load balancer: `loadbalancer.doaj.cottagelabs.com`.

Supervisor manages the app process (`doaj`) and background workers (`huey-long-running`, `huey-main`, `huey-events`, `huey-scheduled-long`, `huey-scheduled-short`).

### Provisioning commands

```bash
# Create new app server
ansible-playbook ansible/provision/create_app_server.yml

# Create load balancer
ansible-playbook ansible/provision/create_lb_server.yml

# Create test server (from sysadmin/ansible/provision)
ansible-playbook create_test_server.yml --e "droplet_name=3991 install_index=true git_branch=feature/3991_weekly_email_alert aws_profile=doaj-test aws_access_key=<SEE_PASSBOLT> aws_secret_key=<SEE_PASSBOLT>" --private-key=~/.ssh/cl_ed25519

# Destroy a test server
ansible-playbook destroy_test_server.yml --e "droplet_name=3991"
```

Test server AWS credentials for the anonymised data import live in Passbolt as *Test Server AWS Credentials* — see [[AWS]].

## Deploy / Release Process

Releases go to live generally (not exclusively) on **Thursdays** — see the [How-To: Deploy code to the live server](https://github.com/DOAJ/doajPM/wiki/How-To:-Deploy-code-to-the-live-server) wiki page for the full checklist. Watch for:

- Git flow branch management
- Release freeze — prepare `develop` in advance, make sure tests pass, and eyeball it
- Hold off if anything looks unstable (TODO: flesh this criterion out)

Test servers for a branch: [How-to: Deploy a Branch to a Test Server](https://github.com/DOAJ/doajPM/wiki/How-to:-Deploy-a-Branch-to-a-Test-Server).

Production update: `ansible-playbook ansible/update-site.yml`. Test site: `ansible-playbook ansible/update-test-site.yml`. Restart services: `ansible-playbook ansible/restart.yml`.

### CircleCI / Test Suite

[[CircleCI]] runs the test suite. Steve takes it upon himself to fix broken tests periodically.

### Docs Repo

Documentation is generated/published via [[GitHub Actions]]. `STEVE_PAT` is a personal access token tied to Steve's GitHub account and DOAJ project membership, used by that workflow. Replace if he leaves, or beforehand with a better mechanism (e.g. a bot/service account token).

## Backup & Disaster Recovery

TODO — not yet documented here. Search cluster snapshot policy, database backups, etc.

## Monitoring

- [[Kibana]] — self-hosted, on its own `monitor` droplet (see Infrastructure above)
- [[UptimeRobot]] — external uptime checks

## Admin Tasks & Contacts

### Adding a new sysadmin

Their public key needs to be uploaded to all machines. An existing sysadmin runs:

```bash
ansible-playbook -i ../doaj-hosts.ini upload_ssh_key.yml
```

(edit the playbook or supply the key path as an argument — TODO)

Verify access to all machines afterwards:

```bash
ansible -i doaj-hosts.ini all -m ping
```

May need to accept host key verification, or log in directly first, before this succeeds.

## Related

- [[DigitalOcean]]
- [[Cloudflare]]
- [[AWS]]
- [[Ansible sysadmin repo]]
- [[CircleCI]]
- [[GitHub Actions]]
- [[Kibana]]
- [[UptimeRobot]]
- [[vm-os-inventory]]
