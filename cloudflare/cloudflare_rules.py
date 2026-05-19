#!/usr/bin/env python3

"""
Cloudflare Rules Export / Import Script

Usage:
    Export rules:
        python cloudflare_rules.py export <API_TOKEN> <ZONE_ID>

    Import rules:
        python cloudflare_rules.py import <API_TOKEN> <ZONE_ID>

    Dry-run import (prints payloads without making any changes):
        python cloudflare_rules.py import <API_TOKEN> <ZONE_ID> --dry-run

    Alternatively, set CLOUDFLARE_API_TOKEN and CLOUDFLARE_ZONE_ID
    environment variables and run:
        python cloudflare_rules.py export
"""

import json
import os
import sys

import requests

RULES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cloudflare_rules")


def usage():
    print("Usage: python cloudflare_rules.py {export|import} [API_TOKEN] [ZONE_ID] [--dry-run]")
    print()
    print("Arguments:")
    print("  export/import  Operation to perform")
    print("  API_TOKEN      Cloudflare API Token (optional if CLOUDFLARE_API_TOKEN env var is set)")
    print("  ZONE_ID        Cloudflare Zone ID (optional if CLOUDFLARE_ZONE_ID env var is set)")
    print("  --dry-run      Print what would be sent without making any changes (import only)")
    sys.exit(1)


def call_cloudflare(method, url, api_token, output_file=None, data_file=None, description="", dry_run=False):
    print(f"{description}...")

    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json",
    }

    data = None
    if data_file:
        if not os.path.isfile(data_file):
            print(f"Error: Data file {data_file} not found. Skipping {description}.")
            return False
        with open(data_file, "r") as f:
            data = f.read()

    if dry_run:
        print(f"  [DRY RUN] {method} {url}")
        if data:
            parsed = json.loads(data)
            print(f"  Payload: {json.dumps(parsed, indent=2)}")
        return True

    response = requests.request(method, url, headers=headers, data=data)

    if response.status_code == 404:
        try:
            errors = response.json().get("errors", [])
            if any(e.get("code") == 10003 for e in errors):
                print(f"  No rules present, skipping.")
                return True
        except Exception:
            pass

    if response.status_code < 200 or response.status_code > 299:
        print(f"Error: {description} failed with HTTP status {response.status_code}")
        if response.text:
            print(f"Response: {response.text}")
        return False

    if output_file:
        with open(output_file, "w") as f:
            f.write(response.text)

    return True


def export_dns_records(api_token, zone_id):
    print("Exporting DNS Records...")
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records"
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json",
    }

    all_records = []
    page = 1
    while True:
        response = requests.get(url, headers=headers, params={"page": page, "per_page": 100})
        if response.status_code < 200 or response.status_code > 299:
            print(f"Error: Exporting DNS Records failed with HTTP status {response.status_code}")
            if response.text:
                print(f"Response: {response.text}")
            return False

        data = response.json()
        all_records.extend(data.get("result", []))

        result_info = data.get("result_info", {})
        if page >= result_info.get("total_pages", 1):
            break
        page += 1

    with open(os.path.join(RULES_DIR, "dns_records.json"), "w") as f:
        json.dump({"result": all_records}, f, indent=2)

    print(f"  Exported {len(all_records)} DNS records.")
    return True


def import_dns_records(api_token, zone_id, dry_run=False):
    print("Importing DNS Records...")
    dns_file = os.path.join(RULES_DIR, "dns_records.json")
    if not os.path.isfile(dns_file):
        print(f"Error: Data file {dns_file} not found. Skipping DNS Records import.")
        return False

    with open(dns_file, "r") as f:
        data = json.load(f)

    records = data.get("result", [])
    if not records:
        print("No DNS records found to import.")
        return True

    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records"
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json",
    }

    exclude_fields = {"id", "zone_id", "zone_name", "created_on", "modified_on", "meta"}

    failed = False
    for i, record in enumerate(records):
        payload = {k: v for k, v in record.items() if k not in exclude_fields}
        if dry_run:
            print(f"  [DRY RUN] POST {url}")
            print(f"  Payload: {json.dumps(payload, indent=2)}")
            continue
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code < 200 or response.status_code > 299:
            print(f"Error: Importing DNS record {i} ({record.get('name', '')}) failed with HTTP status {response.status_code}")
            if response.text:
                print(f"Response: {response.text}")
            failed = True

    if failed:
        return False

    print("DNS Records imported successfully." if not dry_run else f"  {len(records)} DNS records would be imported.")
    return True


def import_zone_settings(api_token, zone_id, dry_run=False):
    print("Importing Zone Settings...")
    settings_file = os.path.join(RULES_DIR, "zone_settings.json")
    if not os.path.isfile(settings_file):
        print(f"Error: Data file {settings_file} not found. Skipping Zone Settings import.")
        return False

    with open(settings_file, "r") as f:
        data = json.load(f)

    items = [
        {"id": s["id"], "value": s["value"]}
        for s in data.get("result", [])
        if s.get("editable", False)
    ]

    if not items:
        print("No editable zone settings found to import.")
        return True

    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/settings"
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json",
    }

    if dry_run:
        print(f"  [DRY RUN] PATCH {url}")
        print(f"  Payload: {json.dumps({'items': items}, indent=2)}")
        return True

    response = requests.patch(url, headers=headers, json={"items": items})
    if response.status_code < 200 or response.status_code > 299:
        print(f"Error: Importing Zone Settings failed with HTTP status {response.status_code}")
        if response.text:
            print(f"Response: {response.text}")
        return False

    print("Zone Settings imported successfully.")
    return True


def export_rules(api_token, zone_id):
    base_url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/rulesets"
    pagerules_url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/pagerules"

    os.makedirs(RULES_DIR, exist_ok=True)

    failed = False
    if not export_dns_records(api_token, zone_id):
        failed = True
    if not call_cloudflare("GET", f"https://api.cloudflare.com/client/v4/zones/{zone_id}/settings", api_token, output_file=os.path.join(RULES_DIR, "zone_settings.json"), description="Exporting Zone Settings"):
        failed = True
    if not call_cloudflare("GET", f"{base_url}/phases/http_request_firewall_custom/entrypoint", api_token, output_file=os.path.join(RULES_DIR, "waf_rules.json"), description="Exporting WAF Custom Rules"):
        failed = True
    if not call_cloudflare("GET", f"{base_url}/phases/http_ratelimit/entrypoint", api_token, output_file=os.path.join(RULES_DIR, "rate_limit_rules.json"), description="Exporting Rate Limiting Rules"):
        failed = True
    if not call_cloudflare("GET", f"{base_url}/phases/http_request_cache_settings/entrypoint", api_token, output_file=os.path.join(RULES_DIR, "cache_rules.json"), description="Exporting Cache Rules"):
        failed = True
    if not call_cloudflare("GET", f"{base_url}/phases/http_request_dynamic_redirect/entrypoint", api_token, output_file=os.path.join(RULES_DIR, "redirect_rules.json"), description="Exporting Redirect Rules"):
        failed = True
    if not call_cloudflare("GET", pagerules_url, api_token, output_file=os.path.join(RULES_DIR, "page_rules.json"), description="Exporting Page Rules"):
        failed = True

    if not failed:
        print(f"Export completed successfully. JSON files saved in {RULES_DIR}.")
    else:
        print("Export completed with errors.")
        sys.exit(1)


def import_page_rules(api_token, zone_id, dry_run=False):
    pagerules_url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/pagerules"

    print("Importing Page Rules...")
    page_rules_file = os.path.join(RULES_DIR, "page_rules.json")
    if not os.path.isfile(page_rules_file):
        print(f"Error: Data file {page_rules_file} not found. Skipping Page Rules import.")
        return False

    with open(page_rules_file, "r") as f:
        data = json.load(f)

    rules = data.get("result", [])
    if not rules:
        print("No page rules found to import.")
        return True

    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json",
    }

    page_failed = False
    for i, rule in enumerate(rules):
        payload = {
            "targets": rule["targets"],
            "actions": rule["actions"],
            "priority": rule.get("priority", i + 1),
            "status": rule.get("status", "active"),
        }

        if dry_run:
            print(f"  [DRY RUN] POST {pagerules_url}")
            print(f"  Payload: {json.dumps(payload, indent=2)}")
            continue

        response = requests.post(pagerules_url, headers=headers, json=payload)

        if response.status_code < 200 or response.status_code > 299:
            print(f"Error: Importing Page Rule {i} failed with HTTP status {response.status_code}")
            if response.text:
                print(f"Response: {response.text}")
            page_failed = True

    if page_failed:
        return False

    print("Page Rules imported successfully." if not dry_run else f"  {len(rules)} page rules would be imported.")
    return True


def import_rules(api_token, zone_id, dry_run=False):
    base_url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/rulesets"

    if dry_run:
        print("--- DRY RUN: no changes will be made ---")

    failed = False
    if not import_dns_records(api_token, zone_id, dry_run=dry_run):
        failed = True
    if not import_zone_settings(api_token, zone_id, dry_run=dry_run):
        failed = True
    if not call_cloudflare("PUT", f"{base_url}/phases/http_request_firewall_custom/entrypoint", api_token, data_file=os.path.join(RULES_DIR, "waf_rules.json"), description="Importing WAF Custom Rules", dry_run=dry_run):
        failed = True
    if not call_cloudflare("PUT", f"{base_url}/phases/http_ratelimit/entrypoint", api_token, data_file=os.path.join(RULES_DIR, "rate_limit_rules.json"), description="Importing Rate Limiting Rules", dry_run=dry_run):
        failed = True
    if not call_cloudflare("PUT", f"{base_url}/phases/http_request_cache_settings/entrypoint", api_token, data_file=os.path.join(RULES_DIR, "cache_rules.json"), description="Importing Cache Rules", dry_run=dry_run):
        failed = True
    if not call_cloudflare("PUT", f"{base_url}/phases/http_request_dynamic_redirect/entrypoint", api_token, data_file=os.path.join(RULES_DIR, "redirect_rules.json"), description="Importing Redirect Rules", dry_run=dry_run):
        failed = True
    if not import_page_rules(api_token, zone_id, dry_run=dry_run):
        failed = True

    if not failed:
        print("Dry run completed successfully." if dry_run else "Import completed successfully.")
    else:
        print("Dry run completed with errors." if dry_run else "Import completed with errors.")
        sys.exit(1)


def main():
    if len(sys.argv) < 2:
        usage()

    args = sys.argv[1:]
    dry_run = "--dry-run" in args
    args = [a for a in args if a != "--dry-run"]

    operation = args[0] if args else None
    api_token = args[1] if len(args) > 1 else os.environ.get("CLOUDFLARE_API_TOKEN", "")
    zone_id = args[2] if len(args) > 2 else os.environ.get("CLOUDFLARE_ZONE_ID", "")

    if not api_token or not zone_id:
        print("Error: API_TOKEN and ZONE_ID must be provided either as arguments or environment variables.")
        usage()

    if operation == "export":
        export_rules(api_token, zone_id)
    elif operation == "import":
        import_rules(api_token, zone_id, dry_run=dry_run)
    else:
        usage()


if __name__ == "__main__":
    main()
