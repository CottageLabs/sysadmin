---
tags: [company-docs]
---

# VM Operating System Inventory

Related: [[Ops_handbook]]

Last updated: 2026-10-23

## Summary of Operating Systems Across All VMs (34 DigitalOcean droplets)

Ordered by release date (newest to oldest). Counts use the OS image each droplet was created from as a minimum, adjusted for servers known to have been upgraded in place since (see notes below):

- **1 server** running Ubuntu 26.04 LTS (invenio-notify, upgraded from 24.10) - Released April 2026, EOL April 2031
- **11 servers** running Ubuntu 24.04 LTS (chicago-invenio, doaj-editor-a, doaj-lb, doaj-public-1, doaj-public-2, doaj-public-3, doaj-search-r1, doaj-search-r2, doaj-search-rw1, doaj-search-rw2, knowledge-rcc-sandbox) - Released April 2024, EOL May 2029
- **16 servers** running Ubuntu 22.04 LTS or later (2959, 4147, 4185, 4216, 4288, 4430, Kibana, cl-docker, doaj-background-1, doaj-editor-1, emlo-edit, emlo2, ewp, rivendell, sauron, static) - Released April 2022, EOL April 2027
- **1 server** running Debian 12 (deepgreen) - Released June 2023, EOL ~June 2028
- **5 servers** running Ubuntu 20.04 LTS with **Ubuntu Pro ESM** (noddy-JCT, noddy-JCT-dev, rdms, rdms2, noddy-index) - Released April 2020, standard support ended May 2025, ESM security updates until April 2030

### Notes
- **Upgraded in place** since creation (droplet image metadata is stale): cl-docker (from 20.04), Kibana and several other DOAJ servers, invenio-notify (24.10 to 26.04 LTS).
- **Cloned from snapshots**, OS inferred from the parent: knowledge-rcc-sandbox (from chicago-invenio), rivendell (from sauron), emlo2 (from emlo-edit), rdms2 (from rdms).
- **Ubuntu Pro ESM**: esm-infra, esm-apps and Livepatch are enabled on the five 20.04 servers via the free Ubuntu Pro subscription, which covers up to 5 machines - this allowance is now fully used.
- **Decommissioned since 2025-10-11**: noddy-main (14.04), noddy-resources (18.04), doaj-kibana (18.04).
- The `default` doctl context's token is no longer valid; this list comes from the `doaj` context.

## Kubernetes (AWS EKS)

- **chicago-invenio** (us-east-2): EKS 1.34 (standard support), managed node group `workers` with 3 worker nodes on Amazon Linux 2023 (EKS-optimised AMI, `AL2023_x86_64_STANDARD`)
- Node group updated to AMI release `1.34.12-20261019` on 2026-10-23 (previously `1.34.6-20260415`)
- Node AMIs must be kept within 14 days of release for Cyber Essentials: run a scheduled `aws eks update-nodegroup-version` (see Methodology below)

## End-of-Life Status

No servers are on an unsupported OS. The 20.04 servers depend on Ubuntu Pro ESM remaining attached.

## Methodology for Gathering This Information

### 1. Check DigitalOcean API for Basic Information

```bash
# List all droplets with their image information
doctl --context doaj compute droplet list -o json | jq -r '.[] | "\(.name)\t\(.image.slug // .image.name // .image.distribution)"' | sort -k2

# Count by OS version
doctl --context doaj compute droplet list -o json | jq -r '.[] | "\(.name)\t\(.image.slug // .image.name // .image.distribution)"' | awk -F'\t' '{print $2}' | sort | uniq -c | sort -rn
```

**Note**: DigitalOcean API shows the image a droplet was created from, not the actual running OS version, and shows snapshot names for VMs created from custom snapshots. Upgraded and cloned servers need to be verified separately.

### 2. Verify DOAJ Servers via Ansible

For servers in the ansible inventory (`ansible/doaj-hosts.ini`), we can query them directly:

```bash
# Get OS information from all DOAJ servers
ansible -i ansible/doaj-hosts.ini all -m setup -a 'filter=ansible_distribution*' 2>/dev/null | grep -E '(doaj-|Kibana|static).*SUCCESS|ansible_distribution[^_]|ansible_distribution_version|ansible_distribution_release'
```

This provides accurate, real-time OS information from the running servers.

### 3. Infer OS for Cloned Servers

Servers cloned from snapshots inherit the OS of their parent:
- **rivendell** - cloned from sauron → Ubuntu 22.04 LTS
- **emlo2** - cloned from emlo-edit → Ubuntu 22.04 LTS
- **knowledge-rcc-sandbox** - cloned from chicago-invenio → Ubuntu 24.04 LTS
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

# Check Ubuntu Pro / ESM status on the 20.04 servers
ssh server-name "pro status"
```

### 5. Check the EKS Cluster

```bash
# Cluster version and node group AMI release
aws eks describe-cluster --profile steve-admin --region us-east-2 --name chicago-invenio --query 'cluster.version'
aws eks describe-nodegroup --profile steve-admin --region us-east-2 --cluster-name chicago-invenio --nodegroup-name workers --query 'nodegroup.releaseVersion'

# Latest recommended AL2023 AMI release for the cluster version
aws ssm get-parameter --profile steve-admin --region us-east-2 --name /aws/service/eks/optimized-ami/1.34/amazon-linux-2023/x86_64/standard/recommended/release_version --query Parameter.Value --output text

# Node OS as reported by the nodes
kubectl --context chicago-invenio get nodes -o wide

# Update the node group to the latest AMI (rolling replacement of nodes)
aws eks update-nodegroup-version --profile steve-admin --region us-east-2 --cluster-name chicago-invenio --nodegroup-name workers
```

### Summary of Approach

1. Start with DigitalOcean API for overview (but note limitations with snapshots)
2. Use Ansible for DOAJ infrastructure (most reliable)
3. Infer OS for cloned servers based on parent server
4. SSH into remaining servers to verify actual running OS
5. Check the EKS node group AMI release against the latest recommended version

This multi-layered approach ensures accurate OS information across all VMs, accounting for:
- Servers upgraded after creation (snapshot metadata is stale)
- Servers created from custom snapshots
- Servers managed via different tools (Ansible vs manual)

## Action Items

### High Priority
- [ ] Schedule a regular (weekly or fortnightly) EKS node group AMI update for chicago-invenio, so nodes stay within 14 days of each AMI release

### Medium Priority
- [ ] Verify the running OS on every droplet via Ansible/SSH and replace the "or later" counts above with exact versions
- [ ] Re-authenticate or remove the stale `default` doctl context
- [ ] Plan upgrades for the five Ubuntu 20.04 ESM servers (ESM ends April 2030; the free Ubuntu Pro allowance is fully used)

### Low Priority
- [ ] Plan upgrade path for Ubuntu 22.04 servers before April 2027
