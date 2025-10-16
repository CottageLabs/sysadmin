# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a sysadmin repository for Cottage Labs containing Ansible playbooks, configuration files, and utilities for managing infrastructure - primarily focused on DOAJ (Directory of Open Access Journals) deployment and server management using DigitalOcean.

## Repository Structure

- `ansible/` - Ansible playbooks for server provisioning and management
  - `provision/` - Server creation and initial setup playbooks
  - `ott/` - Organization-specific playbooks and upgrades
- `cloud-init_userdata/` - Cloud-init configuration files for server initialization
- `digitalocean_cli/` - DigitalOcean CLI utilities (placeholder)
- `docs/` - Documentation
- `doaj` - Symlink to ansible/ directory

## Key Infrastructure Components

### Server Types
- **App Servers**: DOAJ application servers (`create_app_server.yml`)
- **Load Balancer**: Load balancing server (`create_lb_server.yml`)
- **Test Servers**: Development/testing environments (`create_test_server.yml`)
- **Static Servers**: Static content servers
- **Kibana Systems**: Log analysis and monitoring

### Environment Requirements
- DigitalOcean token must be set as `DIGITALOCEAN_TOKEN` environment variable
- SSH keys are predefined in playbooks (IDs: "30242381", "40223915")
- Default region: `lon1` (London)
- Default OS: `ubuntu-22-04-x64`

## Common Commands

### Server Provisioning
```bash
# Create new app server
ansible-playbook ansible/provision/create_app_server.yml

# Create load balancer
ansible-playbook ansible/provision/create_lb_server.yml

# Create test server
ansible-playbook ansible/provision/create_test_server.yml
```

### Server Management
```bash
# Update production site
ansible-playbook ansible/update-site.yml

# Update test site
ansible-playbook ansible/update-test-site.yml

# Restart services
ansible-playbook ansible/restart.yml

# Reboot metrics servers
ansible-playbook ansible/reboot-metrics.yml
```

### Initial Server Setup
```bash
# Setup with specific parameters
ansible-playbook -i IP_ADDRESS, ansible/provision/server_initial_setup.yml \
  -e "server_name=SERVER_NAME install_es=false git_branch=master ansible_user=cloo" \
  --private-key=~/.ssh/id_rsa
```

## Server Configuration

### Default User
- Username: `cloo`
- Sudo access: Full NOPASSWD privileges
- SSH key authentication only (password auth disabled)

### Standard Packages
- Development: git, python3-dev, python3-pip, gcc
- Monitoring: htop, tree, ncdu
- Web: nginx, certbot, python3-certbot-nginx
- Process management: supervisor
- Dependencies: libxml2-dev, libxslt-dev, lib32z1-dev

### Domain Configuration
- Production: `doaj.org`
- Test servers: `{server_name}.doaj.cottagelabs.com`
- Load balancer: `loadbalancer.doaj.cottagelabs.com`

## Ansible Configuration

### Required Collections
- `digitalocean.cloud` - DigitalOcean provider

### Common Variables
- `deploy_env`: "test" or "production"
- `git_branch`: Target branch to deploy (default: "develop" for test, "master" for production)
- `ansible_user`: "cloo"
- `certbot_domain`: Auto-configured based on server name and environment

### Supervisor Tasks
- App tasks: `doaj`
- Background tasks: `huey-long-running`, `huey-main`, `huey-events`, `huey-scheduled-long`, `huey-scheduled-short`

## Security Notes

- SSH keys are hardcoded in cloud-init configuration
- SSL certificates managed via Let's Encrypt/Certbot
- Firewall tags: `doaj`, `firewall-doaj-app`
- All servers assigned to DOAJ DigitalOcean project (ID: f7668431-327e-47d8-9d7e-73e713fe1d4d)