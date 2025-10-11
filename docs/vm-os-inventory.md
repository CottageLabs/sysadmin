# VM Operating System Inventory

Last updated: 2025-10-11

## Summary of Operating Systems Across All VMs (27 total)

Ordered by release date (newest to oldest):

- **1 server** running Ubuntu 24.10 (invenio-notify) - Released October 2024, EOL July 2025
- **2 servers** running Ubuntu 24.04 LTS (chicago-invenio, invenio) - Released April 2024, EOL April 2029
- **1 server** running Debian 12 (deepgreen) - Released June 2023, EOL ~June 2028
- **14 servers** running Ubuntu 22.04 LTS (eui-invenio-live, rivendell, sauron, emlo-edit, 3916, Kibana, doaj-background-1, doaj-editor-1, doaj-lb, doaj-public-1, doaj-public-2, doaj-index-1, doaj-index-2, static) - Released April 2022, EOL April 2027
- **5 servers** running Ubuntu 20.04 LTS **EOL** (cl-docker, noddy-JCT, noddy-JCT-dev, rdms, rdms2) - Released April 2020, EOL April 2025
- **2 servers** running Ubuntu 18.04 **EOL** (noddy-resources, doaj-kibana [obsolete]) - Released April 2018, EOL May 2023
- **2 servers** running Ubuntu 14.04 **CRITICAL EOL** (noddy-main, noddy-index) - Released April 2014, EOL April 2019

## End-of-Life Status

### Critical - Immediate Action Required
- **noddy-main** - Ubuntu 14.04 (EOL 6+ years ago)
- **noddy-index** - Ubuntu 14.04 (EOL 6+ years ago)

### EOL - Action Required
- **noddy-resources** - Ubuntu 18.04 (EOL ~2 years ago)
- **doaj-kibana** - Ubuntu 18.04 (obsolete, can be decommissioned)
- **cl-docker** - Ubuntu 20.04 LTS (EOL 6 months ago)
- **noddy-JCT** - Ubuntu 20.04 LTS (EOL 6 months ago)
- **noddy-JCT-dev** - Ubuntu 20.04 LTS (EOL 6 months ago)
- **rdms** - Ubuntu 20.04 LTS (EOL 6 months ago)
- **rdms2** - Ubuntu 20.04 LTS (EOL 6 months ago)

## Methodology for Gathering This Information

### 1. Check DigitalOcean API for Basic Information

```bash
# List all droplets with their image information
doctl compute droplet list -o json | jq -r '.[] | "\(.name)\t\(.image.slug // .image.name // .image.distribution)"' | sort -k2

# Count by OS version
doctl compute droplet list -o json | jq -r '.[] | "\(.name)\t\(.image.slug // .image.name // .image.distribution)"' | awk -F'\t' '{print $2}' | sort | uniq -c | sort -rn
```

**Note**: DigitalOcean API shows snapshot names for VMs created from custom snapshots, not the actual running OS version. These need to be verified separately.

### 2. Verify DOAJ Servers via Ansible

For servers in the ansible inventory (`ansible/doaj-hosts.ini`), we can query them directly:

```bash
# Get OS information from all DOAJ servers (excluding obsolete ones)
ansible -i ansible/doaj-hosts.ini all:!doaj-kibana -m setup -a 'filter=ansible_distribution*' 2>/dev/null | grep -E '(doaj-|Kibana|static).*SUCCESS|ansible_distribution[^_]|ansible_distribution_version|ansible_distribution_release'
```

This provides accurate, real-time OS information from the running servers.

### 3. Infer OS for Cloned Servers

Servers cloned from snapshots inherit the OS of their parent:
- **rivendell** - cloned from sauron → Ubuntu 22.04 LTS
- **rdms2** - cloned from rdms → Ubuntu 20.04 LTS

### 4. SSH into Remaining Servers

For servers not in ansible inventory or created from custom snapshots, SSH in and check directly:

```bash
# Check SSH config for host entries
grep -E "^Host (server-name)\s*$" ~/.ssh/config -A 5

# Get OS information via SSH
ssh server-name "lsb_release -a 2>/dev/null"

# Or if not in SSH config, use IP directly
ssh -i ~/.ssh/cl_ed25519 cloo@IP_ADDRESS "lsb_release -a 2>/dev/null"
```

### Summary of Approach

1. Start with DigitalOcean API for overview (but note limitations with snapshots)
2. Use Ansible for DOAJ infrastructure (most reliable)
3. Infer OS for cloned servers based on parent server
4. SSH into remaining servers to verify actual running OS

This multi-layered approach ensures accurate OS information across all VMs, accounting for:
- Servers upgraded after creation (snapshot metadata is stale)
- Servers created from custom snapshots
- Servers managed via different tools (Ansible vs manual)

## Action Items

### High Priority
- [ ] Upgrade or decommission **noddy-main** (Ubuntu 14.04)
- [ ] Upgrade or decommission **noddy-index** (Ubuntu 14.04)
- [ ] Upgrade or decommission **noddy-resources** (Ubuntu 18.04)
- [ ] Decommission **doaj-kibana** (obsolete)

### Medium Priority
- [ ] Upgrade **cl-docker** from Ubuntu 20.04 to 22.04 or 24.04 (EOL 6 months ago)
- [ ] Upgrade **noddy-JCT** from Ubuntu 20.04 to 22.04 or 24.04 (EOL 6 months ago)
- [ ] Upgrade **noddy-JCT-dev** from Ubuntu 20.04 to 22.04 or 24.04 (EOL 6 months ago)
- [ ] Upgrade **rdms** from Ubuntu 20.04 to 22.04 or 24.04 (EOL 6 months ago)
- [ ] Upgrade **rdms2** from Ubuntu 20.04 to 22.04 or 24.04 (EOL 6 months ago)

### Low Priority
- [ ] Plan upgrade path for Ubuntu 22.04 servers before April 2027
- [ ] Monitor **invenio-notify** (Ubuntu 24.10) - EOL July 2025 (consider migrating to 24.04 LTS)
