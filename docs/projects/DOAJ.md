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
```

Alternatively, keep the keys in a credentials-format file with a `[doaj-test]` section (your own `~/.aws/credentials` or a standalone file) and read them from there, which keeps them out of shell history:

```
ansible-playbook create_test_server.yml -e @aws_creds_from_file.yml --e="aws_profile=doaj-test aws_creds_file=/home/<you>/.aws/credentials droplet_name=3991 git_branch=feature/3991_weekly_email_alert" --private-key=~/.ssh/cl_ed25519
```

The local credentials file is:

```
[doaj-test]
aws_access_key_id = <SEE_PASSBOLT>
aws_secret_access_key = <SEE_PASSBOLT>
```

The profile must be `doaj-test`: it's the profile name `deploy.sh` uses on the server to fetch the app config. Only the credentials file is read; no local `.aws/config` is needed. The `@aws_creds_from_file.yml` must be its own `-e` and come first, so the `aws_profile` that follows overrides its default `doaj-app`. E.g.:

```
# Destroy a test server
ansible-playbook destroy_test_server.yml --e "droplet_name=3991"
```

The static pages preview server (static.doaj.cottagelabs.com) has its own playbook with its size, branch and data set built in, so only credentials are needed. After that it's deployed by a GitHub Action on push to `static_pages`. Destruction uses the same test server playbook.

```
ansible-playbook destroy_test_server.yml --e "droplet_name=static"
ansible-playbook create_static_server.yml -e @aws_creds_from_file.yml --e="aws_profile=doaj-test aws_creds_file=/home/<you>/.aws/credentials" --private-key=~/.ssh/cl_ed25519
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
