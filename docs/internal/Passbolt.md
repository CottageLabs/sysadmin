---
tags: [internal]
status: active
---

# Passbolt

Team password manager, containerised on [[cl-docker]]. Source of truth for most credentials referenced elsewhere in this vault.

## Infrastructure & Access

- DNS: [[GoDaddy]] → `cl-docker` nginx → container
- Path: `/home/cloo/passbolt`
- Start: `docker compose -f docker-compose-ce.yaml up -d`
- Runs alongside [[Mattermost]] on the same host, with the same pattern — a `sysadmin@cottagelabs.com` user has full control so Steve's own account stays unprivileged.

## Deploy / Release Process

Runs containerised on [[cl-docker]]. No separate release process — upgraded in place.

## Backup & Disaster Recovery

Backups stored in `~/passbolt/backups/` on [[cl-docker]] and synced to S3 bucket `cl-passbolt` (see [[AWS]]). Each daily backup produces three items:

- `passbolt-YYYYMMDD.sql` — full database dump
- `gpg-YYYYMMDD/` — server GPG key pair
- `jwt-YYYYMMDD/` — JWT key pair (for API/browser extension auth)

**Restore on a fresh host:**

**1. Start only the database container**

```bash
docker compose -f ~/passbolt/docker-compose-ce.yaml up -d db
```

**2. Restore the database**

```bash
docker cp ~/passbolt/backups/passbolt-YYYYMMDD.sql passbolt-db-1:/tmp/
docker exec passbolt-db-1 bash -c 'mysql -u passbolt -p<PASSWORD> passbolt < /tmp/passbolt-YYYYMMDD.sql'
```

**3. Restore the GPG keys**

```bash
docker cp ~/passbolt/backups/gpg-YYYYMMDD/. passbolt-passbolt-1:/etc/passbolt/gpg/
```

**4. Restore the JWT keys**

```bash
docker cp ~/passbolt/backups/jwt-YYYYMMDD/. passbolt-passbolt-1:/etc/passbolt/jwt/
```

**5. Bring up the full stack**

```bash
docker compose -f ~/passbolt/docker-compose-ce.yaml up -d
```

## Monitoring

TODO

## Admin Tasks & Contacts

- Provisioning new users
- Setting up shared directories
- Resetting user passwords

## Related

- [[cl-docker]]
- [[GoDaddy]]
- [[AWS]]
- [[Mattermost]]
