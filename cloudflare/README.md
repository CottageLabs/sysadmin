# Cloudflare Rules Export / Import

`cloudflare_rules.py` exports and imports Cloudflare zone configuration as JSON files into the `cloudflare_rules/` directory.

## Usage

```bash
python cloudflare_rules.py export <API_TOKEN> <ZONE_ID>
python cloudflare_rules.py import <API_TOKEN> <ZONE_ID>
```

Alternatively, set environment variables and omit the arguments:

```bash
export CLOUDFLARE_API_TOKEN=your_token
export CLOUDFLARE_ZONE_ID=your_zone_id

python cloudflare_rules.py export
python cloudflare_rules.py import
```

## API Token Requirements

Create a **zone-scoped** API token (not an account token) in the Cloudflare dashboard under **My Profile > API Tokens > Create Token**.

Scope the token to the specific zone, with the following permissions:

| Category | Permission | Required for |
|----------|------------|--------------|
| Zone / DNS | Read | DNS records export/import |
| Zone / Zone Settings | Read | Zone settings export |
| Zone / Zone WAF | Edit | WAF custom rules export/import |
| Zone / Cache Rules | Edit | Cache rules export/import |
| Zone / Page Rules | Edit | Page rules export/import |

> **Note:** Import operations require Edit permissions; Read is sufficient for export-only use.

## What is exported

| File | Contents |
|------|----------|
| `dns_records.json` | All DNS records for the zone |
| `zone_settings.json` | Zone-level settings (SSL mode, security level, etc.) |
| `waf_rules.json` | WAF custom rules |
| `rate_limit_rules.json` | Rate limiting rules |
| `cache_rules.json` | Cache rules |
| `redirect_rules.json` | Dynamic redirect rules |
| `page_rules.json` | Page rules (legacy) |

Phases with no rules configured are skipped without error.
