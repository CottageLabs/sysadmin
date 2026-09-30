---
tags: [internal]
status: active
---

# CL Website

The `cottagelabs.com` marketing/company website.

## Infrastructure & Access

- DNS: [[GoDaddy]] (NS) → [[Cloudflare]] → `cl-docker` nginx → site
- Runs on [[cl-docker]], but not containerised — it's a plain static HTML site (built with Pelican) served directly. Source: [github.com/CottageLabs/website](https://github.com/CottageLabs/website), see that repo's README for the Pelican build/deploy details.

## Deploy / Release Process

Deployed via a git hook against a headless repo on the server: pushing to the `production` remote (`git push production master`) from a dev machine triggers the deploy.

## Backup & Disaster Recovery

No separate backup process — the git repo itself is the backup, since the site holds no database/dynamic data.

## Monitoring

- [[UptimeRobot]] — external uptime checks

## Admin Tasks & Contacts

Steve and Richard.

## Related

- [[GoDaddy]]
- [[Cloudflare]]
- [[cl-docker]]
- [[DigitalOcean]]
- [[UptimeRobot]]
