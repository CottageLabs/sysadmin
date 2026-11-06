---
tags: [infrastructure, provider]
---

# Amazon AWS

Virtual machines, some DNS, S3 buckets, Secrets Manager, IAM users. Used differently by different projects — no single shared AWS account.

## Used by

- [[DOAJ]] — test-server data import pulls anonymised data from S3 (`aws_profile=doaj-test`, credentials in Passbolt as *Test Server AWS Credentials*)
- [[uChicago]] — full control, hosted on our own AWS account using EKS (Elastic Kubernetes Service — the original notes said "AKS", which is actually Azure's Kubernetes offering; corrected here, confirm)
- [[Mattermost]] — backups synced to S3 bucket `cl-mattermost`
- [[Passbolt]] — backups synced to S3 bucket `cl-passbolt`

## Related

- [[RKI MEx]] uses RKI's own S3-equivalent block storage, not our AWS account — see that note.
