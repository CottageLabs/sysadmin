---
tags: [infrastructure, host]
---

# cl-docker

Shared Cottage Labs host running several internal services as Docker containers, fronted by a single nginx. A [[DigitalOcean]] virtual machine, per our general hosting pattern for internal projects. Ubuntu 20.04 LTS — **past EOL (April 2025)**, see [[vm-os-inventory]]. Should be prioritised for an upgrade given how much runs on it.

## DNS pattern

[[GoDaddy]] → `cl-docker` nginx → container (per service, path-routed or by subdomain)

## Runs

- [[Mattermost]] — `~/mattermost`, `docker compose -f docker-compose.yml -f docker-compose.without-nginx.yml up -d`
- [[Passbolt]] — `~/passbolt`, `docker compose -f docker-compose-ce.yaml up -d`
- [[SWORD Wordpress]]

## Related

- [[DigitalOcean]]
- [[GoDaddy]]
