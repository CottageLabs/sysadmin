
* TODO: export entirety of `cottage labs/` password directory to passbolt

Arranged by project, with general info.

## Services

A non-exhaustive list of the services I use day-to-day, the full list is at

* **DigitalOcean** - Virtual Machines (VMs), firewalls, some DNS zones
* **Amazon AWS** - Virtual Machines, some DNS, S3 buckets, Secrets Manager, IAM users.
* **Microsoft Azure** - not currently used.
* **Google Admin Console** - Cottage Labs accounts
* **Godaddy** - cottagelabs.com domain DNS

## Projects

### DOAJ

The main role I fulfil on DOAJ is release manager - I trust I don't need to expand on the full procedures here, but that means we need to take care that releases are stable and on-time.

#### [Releases to live](https://github.com/DOAJ/doajPM/wiki/How-To:-Deploy-code-to-the-live-server)

Releases are generally but not exclusively on a Thursday. There's a checklist to follow for what's necessary before a release goes out. To pay attention to:

* Git flow branch management
* Release freeze - prepare `develop` in advance and make sure the tests pass and eyeball it.
* Hold off 
#### [Test Servers](https://github.com/DOAJ/doajPM/wiki/How-to:-Deploy-a-Branch-to-a-Test-Server))

Provision commands are run from the [sysadmin repo](https://github.com/CottageLabs/sysadmin/) directory `sysadmin/ansible/provision`

The following command gets us a new test server for the branch `feature/3991_weekly_email_alert`, with all of its data pulled from the anon import:

(I can't include AWS credentials here, so they're in passbolt as *Test Server AWS Credentials*)
```
ansible-playbook create_test_server.yml --e "droplet_name=3991 install_index=true git_branch=feature/3991_weekly_email_alert aws_profile=doaj-test aws_access_key=<SEE_PASSBOLT> aws_secret_key=<SEE_PASSBOLT>" --private-key=~/.ssh/cl_ed25519
```

And to destroy it:

```
ansible-playbook destroy_test_server.yml --e "droplet_name=3991"
```

#### CircleCI / Test Suite

I take it upon myself to fix broken tests periodically.

#### Docs Repo

`STEVE_PAT` is a personal access token that requires my GH account to be active and my involvement in the DOAJ project. Replace if I leave or beforehand with a better mechanism.

### RKI

Runs on RKI's kubernetes cluster and their own block storage (S3 equivalent). We have access via `kubectl` credentials.

### uChicago

Running on our own AWS account using AKS (Amazon Kubernetes Service).

### JCT

Meteor app running in a `screen` session.
Using old index machine 

### SWORD Wordpress

Running on `cl-docker` - probably requires attention quite soon.

Sends emails via mailgun

### CL Infrastructure

#### Mattermost

DNS: Godaddy -> cl-docker nginx -> container
Path `/home/cloo/mattermost`
Exec `docker compose -f docker-compose.yml -f docker-compose.without-nginx.yml up -d`

This runs containerised, automatically on `cl-docker` and is backed up via a `cron` to S3 bucket `cl-mattermost`.
There's a sysadmin@cottagelabs.com user with full control of the server, so that my account is unprivileged. Login details are in passbolt.

Admin tasks include:
* Provisioning new users
* Archiving / hiding old channels
* Emoji upload
* Disabling and removing users
* Upgrading the server (tentatively)

**Disaster recovery:**

Backups are stored in `~/mattermost/backups/` on cl-docker (database dump) and the full `~/mattermost/volumes/` tree (database files, uploads, config, plugins, logs) is synced to S3 bucket `cl-mattermost` via cron. To restore from S3, first pull the backup down:

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

Note: the `volumes/` tree synced to S3 should contain all file uploads and config. The database restore and the volumes together constitute a full recovery. **This has not been test-restored** — treat as unverified until proven.

#### Passbolt

DNS: Godaddy -> cl-docker nginx -> container
Path `/home/cloo/passbolt`
Exec `docker compose -f docker-compose-ce.yaml up -d`

This runs on cl-docker similarly to mattermost, and the backup method is nearly the same, i.e. a cronjob that pushes to S3. Its bucket is `cl-passbolt` and there's a sysadmin user sysadmin@cottagelabs.com to manage the service. 

**Admin tasks include:**
* Provisioning new users
* Setting up shared directories
* Resetting user passwords

**Disaster recovery:**

Backups are stored in `~/passbolt/backups/` on cl-docker and synced to S3 bucket `cl-passbolt`. Each daily backup produces three items:
- `passbolt-YYYYMMDD.sql` — full database dump
- `gpg-YYYYMMDD/` — server GPG key pair
- `jwt-YYYYMMDD/` — JWT key pair (for API/browser extension auth)

To restore on a fresh host:

**1. Start only the database container**
```bash
docker compose -f ~/passbolt/docker-compose-ce.yaml up -d db
```

**2. Restore the database**
```bash
docker cp ~/passbolt/backups/passbolt-YYYYMMDD.sql passbolt-db-1:/tmp/
docker exec passbolt-db-1 bash -c 'mysql -u passbolt -peemoo5Ah-Bae3Ohyu passbolt < /tmp/passbolt-YYYYMMDD.sql'
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
