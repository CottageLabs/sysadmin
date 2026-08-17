---
tags: [project]
status: active
---

# RKI MEx

> [!todo] Sparse note — only what's in Ops_handbook.md carried over so far. Fill in overview, deploy process, backup/DR, and contacts.

## Infrastructure & Access

Runs on RKI's own Kubernetes cluster and their own block storage (S3-equivalent) — not our [[DigitalOcean]] or [[AWS]] accounts. Access is via `kubectl` credentials (in Passbolt — confirm).

Container images are built via [[GitHub Actions]] and deployed onto that cluster.

## Deploy / Release Process

TODO

## Backup & Disaster Recovery

TODO

## Monitoring

TODO

## Admin Tasks & Contacts

TODO

## Related

- [[AWS]]
- [[DigitalOcean]]
- [[GitHub Actions]]
