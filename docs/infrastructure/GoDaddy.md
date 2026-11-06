---
tags: [infrastructure, provider]
---

# GoDaddy

Registrar for the `cottagelabs.com` domain. Since the migration to [[Cloudflare]], GoDaddy holds only the nameserver (NS) records pointing at Cloudflare — it no longer manages the zone's actual DNS records, WAF, or cache directly.

## Used by

- [[CL Website]]
- [[Mattermost]] — NS only, zone lives on [[Cloudflare]]
- [[Passbolt]] — NS only, zone lives on [[Cloudflare]]
