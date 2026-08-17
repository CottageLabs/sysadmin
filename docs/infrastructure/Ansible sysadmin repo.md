---
tags: [infrastructure, tooling]
---

# Ansible sysadmin repo

This vault lives inside it: [github.com/CottageLabs/sysadmin](https://github.com/CottageLabs/sysadmin), checked out locally at `sysadmin/`. Holds Ansible playbooks, cloud-init configs, and utility scripts for provisioning and managing infrastructure — primarily [[DOAJ]] today.

## Layout

- `ansible/provision/` — server creation and initial setup playbooks ([[DigitalOcean]])
- `ansible/ott/` — one-off/organisation-specific playbooks and upgrades
- `cloud-init_userdata/` — cloud-init configs for server initialisation
- `cloudflare/` — [[Cloudflare]] zone export/import tooling
- `digitalocean_cli/` — DigitalOcean CLI utilities (placeholder)
- `docs/` — this vault

## Default server config (DOAJ playbooks)

- User: `cloo`, full NOPASSWD sudo, SSH-key auth only
- Packages: git, python3-dev, python3-pip, gcc, htop, tree, ncdu, nginx, certbot, python3-certbot-nginx, supervisor, libxml2-dev, libxslt-dev, lib32z1-dev

## Related

- [[DigitalOcean]]
- [[Cloudflare]]
- [[DOAJ]]
