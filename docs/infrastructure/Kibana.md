---
tags: [infrastructure, tooling]
---

# Kibana

Self-hosted log analysis and monitoring — not the SaaS product. Runs on its own [[DigitalOcean]] droplet (the `monitor` group / `Kibana` host in `ansible/doaj-hosts.ini`), provisioned via `ansible/provision/create_kibana_system.yml` and set up with `ansible/provision/kibana_setup.yml`.

## Used by

- [[DOAJ]] — the only project currently on it
