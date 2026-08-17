---
tags: [moc]
---

# Ops Handbook

Index for Cottage Labs operations documentation. Every project and shared piece of infrastructure below is its own note — open **Graph view** to browse the whole picture as a map, or follow `[[links]]` from here.

> [!todo] Export the entirety of the `cottage labs/` password directory into Passbolt.

## Projects

Client-facing work.

- [[DOAJ]]
- [[RKI MEx]]
- [[uChicago]]
- [[JCT]]
- [[SWORD Wordpress]]
- [[DeepGreen]]
- [[EMLO]]
- [[Imperial Helix]]

[[DeepGreen]], [[EMLO]], and [[Imperial Helix]] are placeholder notes — details haven't been written up yet. Fill them in as you touch each project.

## Internal Infrastructure

Services we run for ourselves rather than for a client.

- [[CL Website]]
- [[Mattermost]]
- [[Passbolt]]
- [[The All Seeing Eye]]

[[CL Website]] and [[The All Seeing Eye]] are placeholder notes — details haven't been written up yet.

## Where Hosting Occurs

Who owns the account matters as much as which provider — some projects run entirely under our control, others sit inside a client's own cloud subscription.

| Project | Hosting | Whose account |
|---|---|---|
| [[DOAJ]] | [[DigitalOcean]] | Ours — full control |
| [[RKI MEx]] | RKI's own Kubernetes cluster | Client's — `kubectl` access only |
| [[uChicago]] | [[AWS]] (EKS) | Ours — full control |
| [[Imperial Helix]] | [[Azure]] | Client's own subscription |
| [[JCT]] | [[DigitalOcean]] | Ours |
| [[SWORD Wordpress]] | [[DigitalOcean]] (via [[cl-docker]]) | Ours |
| [[Mattermost]] | [[DigitalOcean]] (via [[cl-docker]]) | Ours |
| [[Passbolt]] | [[DigitalOcean]] (via [[cl-docker]]) | Ours |
| [[CL Website]] | [[DigitalOcean]] (assumed) | Ours — unconfirmed host |
| [[DeepGreen]] | Unknown | Unknown |
| [[EMLO]] | Unknown | Unknown |
| [[The All Seeing Eye]] | [[DigitalOcean]] (assumed) | Ours — unconfirmed host |

Rule of thumb: **client-run infrastructure** (RKI, Imperial) means we work inside their cloud account under their terms; **our infrastructure** (everything else) means we provision, patch, and pay for it — mostly [[DigitalOcean]] for smaller/internal projects, with [[AWS]] used where a project needs its own dedicated account.

## Shared Infrastructure

- [[DigitalOcean]]
- [[AWS]]
- [[Azure]]
- [[Cloudflare]]
- [[GoDaddy]]
- [[cl-docker]]
- [[Ansible sysadmin repo]]
- [[CircleCI]]
- [[GitHub Actions]]
- [[Kibana]]
- [[UptimeRobot]]
- [[Sentry]]
- **Google Admin Console** — Cottage Labs Google Workspace accounts, no dedicated note yet

## Company Docs

- [[vm-os-inventory]]
- [[cyber_essentials_cl_guidance]]
- [[remote_worker_hardware_inventory]]
