---
tags: [infrastructure, provider]
---

# Cloudflare

DNS, WAF, cache and page rules for zones sitting in front of some of our projects.

## Tooling

`cloudflare/cloudflare_rules.py` in the [[Ansible sysadmin repo|sysadmin repo]] exports/imports a zone's config (DNS records, zone settings, WAF rules, rate-limit rules, cache rules, redirect rules, page rules) as JSON, using a zone-scoped API token.

```bash
python cloudflare_rules.py export <API_TOKEN> <ZONE_ID>
python cloudflare_rules.py import <API_TOKEN> <ZONE_ID>
```

There is also `ansible/purge-cloudflare.yml` for cache purges.

## Used by

- [[DOAJ]]
- [[Mattermost]] — `cottagelabs.com` zone, [[GoDaddy]] holds NS only
- [[Passbolt]] — `cottagelabs.com` zone, [[GoDaddy]] holds NS only
- [[CL Website]] — `cottagelabs.com` zone, [[GoDaddy]] holds NS only

## Related

- [[Ansible sysadmin repo]]
- [[GoDaddy]]
