---
tags: [infrastructure, provider]
---

# DigitalOcean

Virtual machines, firewalls, and some DNS zones. The main compute provider for [[DOAJ]].

## Access

Requires a `DIGITALOCEAN_TOKEN` env var (personal access token) for the [[Ansible sysadmin repo|sysadmin repo]] provisioning playbooks. Credentials in Passbolt.

## Conventions (DOAJ project)

- Default region: `lon1` (London)
- Default OS image: `ubuntu-22-04-x64`
- SSH keys pre-registered in DigitalOcean, referenced by ID in playbooks (`30242381`, `40223915`)
- All DOAJ droplets assigned to the DOAJ DigitalOcean project (`f7668431-327e-47d8-9d7e-73e713fe1d4d`)
- Firewall tags: `doaj`, `firewall-doaj-app`

The default landing spot for our own internal and smaller client projects — anything we host end-to-end without a client-provided cloud account runs here.

## Used by

- [[DOAJ]] — app/search/lb/background/monitoring droplets, provisioned via `ansible/provision/`
- [[cl-docker]] — shared internal host, in turn running [[Mattermost]], [[Passbolt]], [[SWORD Wordpress]]
- [[JCT]] — `noddy-JCT` / `noddy-JCT-dev`
- [[CL Website]], [[The All Seeing Eye]] — likely, per the general pattern of smaller/internal projects living here — unconfirmed per-project, see each note

## Related

- [[Ansible sysadmin repo]]
