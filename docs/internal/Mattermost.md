---
tags: [internal]
status: active
---

# Mattermost

Internal chat, containerised on [[cl-docker]].

## Infrastructure & Access

- DNS: [[GoDaddy]] (NS) → [[Cloudflare]] → `cl-docker` nginx → container
- Path: `/home/cloo/mattermost`
- Start: `docker compose -f docker-compose.yml -f docker-compose.without-nginx.yml up -d`
- A `sysadmin@cottagelabs.com` user has full control of the server, so Steve's own account stays unprivileged. Login details in Passbolt.

## Deploy / Release Process

Runs containerised, automatically, on [[cl-docker]]. No separate release process — upgraded in place (tentatively, see admin tasks).

## Backup & Disaster Recovery

Backups stored in `~/mattermost/backups/` on [[cl-docker]] (database dump), and the full `~/mattermost/volumes/` tree (database files, uploads, config, plugins, logs) is synced to S3 bucket `cl-mattermost` (see [[AWS]]) via cron.

**Restore from S3:**

```bash
aws --profile cl-docker-rw-mattermost-backups s3 sync s3://cl-mattermost ~/mattermost
```

**1. Start only the database container**

```bash
docker compose -f ~/mattermost/docker-compose.yml -f ~/mattermost/docker-compose.without-nginx.yml up -d postgres
```

**2. Restore the database**

```bash
docker cp ~/mattermost/backups/mattermost-YYYYMMDD.sql mattermost-postgres-1:/tmp/
docker exec mattermost-postgres-1 bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB < /tmp/mattermost-YYYYMMDD.sql'
```

**3. Bring up the full stack**

```bash
docker compose -f ~/mattermost/docker-compose.yml -f ~/mattermost/docker-compose.without-nginx.yml up -d
```

The `volumes/` tree synced to S3 should contain all file uploads and config. The database restore plus the volumes together constitute a full recovery. **This has not been test-restored** — treat as unverified until proven.

### crontab

```
1 0 * * * docker exec mattermost-postgres-1 bash -c 'pg_dump $POSTGRES_DB -U $POSTGRES_USER > /var/lib/postgresql/data/backups/$POSTGRES_DB-$(date +%Y%m%d).sql' && docker cp mattermost-postgres-1:/var/lib/postgresql/data/backups/mattermost-$(date +%Y%m%d).sql ~/mattermost/backups/

11 0 * * * sudo aws --profile cl-docker-rw-mattermost-backups s3 sync ~/mattermost s3://cl-mattermost
```

## Monitoring

TODO

## Admin Tasks & Contacts

- Provisioning new users
- Archiving / hiding old channels
- Emoji upload
- Disabling and removing users
- Upgrading the server (tentatively)

## Related

- [[cl-docker]]
- [[GoDaddy]]
- [[Cloudflare]]
- [[AWS]]
- [[Passbolt]] — shares a host and an admin pattern with this service
