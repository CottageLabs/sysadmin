#!/usr/bin/env python3

"""
Cloudflare Rules Export / Import Script

Usage:
    Export rules:
        python cloudflare_rules.py export <API_TOKEN> <ZONE_ID>

    Import rules:
        python cloudflare_rules.py import <API_TOKEN> <ZONE_ID>

    Alternatively, set CLOUDFLARE_API_TOKEN and CLOUDFLARE_ZONE_ID
    environment variables and run:
        python cloudflare_rules.py export
"""

import json
import os
import sys

import requests


def usage():
    print("Usage: python cloudflare_rules.py {export|import} [API_TOKEN] [ZONE_ID]")
    print()
    print("Arguments:")
    print("  export/import  Operation to perform")
    print("  API_TOKEN      Cloudflare API Token (optional if CLOUDFLARE_API_TOKEN env var is set)")
    print("  ZONE_ID        Cloudflare Zone ID (optional if CLOUDFLARE_ZONE_ID env var is set)")
    sys.exit(1)


def call_cloudflare(method, url, api_token, output_file=None, data_file=None, description=""):
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

    response = requests.request(method, url, headers=headers, data=data)

    if response.status_code < 200 or response.status_code > 299:
        print(f"Error: {description} failed with HTTP status {response.status_code}")
        if response.text:
            print(f"Response: {response.text}")
        return False

    if output_file:
        with open(output_file, "w") as f:
            f.write(response.text)

    return True


def export_rules(api_token, zone_id):
    base_url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/rulesets"
    pagerules_url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/pagerules"

    failed = False
    if not call_cloudflare("GET", f"{base_url}/phases/http_request_firewall_custom/entrypoint", api_token, output_file="waf_rules.json", description="Exporting WAF Custom Rules"):
        failed = True
    if not call_cloudflare("GET", f"{base_url}/phases/http_ratelimit/entrypoint", api_token, output_file="rate_limit_rules.json", description="Exporting Rate Limiting Rules"):
        failed = True
    if not call_cloudflare("GET", f"{base_url}/phases/http_request_cache_settings/entrypoint", api_token, output_file="cache_rules.json", description="Exporting Cache Rules"):
        failed = True
    if not call_cloudflare("GET", f"{base_url}/phases/http_request_dynamic_redirect/entrypoint", api_token, output_file="redirect_rules.json", description="Exporting Redirect Rules"):
        failed = True
    if not call_cloudflare("GET", pagerules_url, api_token, output_file="page_rules.json", description="Exporting Page Rules"):
        failed = True

    if not failed:
        print("Export completed successfully. JSON files saved in current directory.")
    else:
        print("Export completed with errors.")
        sys.exit(1)


def import_page_rules(api_token, zone_id):
    pagerules_url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/pagerules"

    print("Importing Page Rules...")
    if not os.path.isfile("page_rules.json"):
        print("Error: Data file page_rules.json not found. Skipping Page Rules import.")
        return False

    with open("page_rules.json", "r") as f:
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

        response = requests.post(pagerules_url, headers=headers, json=payload)

        if response.status_code < 200 or response.status_code > 299:
            print(f"Error: Importing Page Rule {i} failed with HTTP status {response.status_code}")
            if response.text:
                print(f"Response: {response.text}")
            page_failed = True

    if page_failed:
        return False

    print("Page Rules imported successfully.")
    return True


def import_rules(api_token, zone_id):
    base_url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/rulesets"

    failed = False
    if not call_cloudflare("PUT", f"{base_url}/phases/http_request_firewall_custom/entrypoint", api_token, data_file="waf_rules.json", description="Importing WAF Custom Rules"):
        failed = True
    if not call_cloudflare("PUT", f"{base_url}/phases/http_ratelimit/entrypoint", api_token, data_file="rate_limit_rules.json", description="Importing Rate Limiting Rules"):
        failed = True
    if not call_cloudflare("PUT", f"{base_url}/phases/http_request_cache_settings/entrypoint", api_token, data_file="cache_rules.json", description="Importing Cache Rules"):
        failed = True
    if not call_cloudflare("PUT", f"{base_url}/phases/http_request_dynamic_redirect/entrypoint", api_token, data_file="redirect_rules.json", description="Importing Redirect Rules"):
        failed = True
    if not import_page_rules(api_token, zone_id):
        failed = True

    if not failed:
        print("Import completed successfully.")
    else:
        print("Import completed with errors.")
        sys.exit(1)


def main():
    if len(sys.argv) < 2:
        usage()

    operation = sys.argv[1]
    api_token = sys.argv[2] if len(sys.argv) > 2 else os.environ.get("CLOUDFLARE_API_TOKEN", "")
    zone_id = sys.argv[3] if len(sys.argv) > 3 else os.environ.get("CLOUDFLARE_ZONE_ID", "")

    if not api_token or not zone_id:
        print("Error: API_TOKEN and ZONE_ID must be provided either as arguments or environment variables.")
        usage()

    if operation == "export":
        export_rules(api_token, zone_id)
    elif operation == "import":
        import_rules(api_token, zone_id)
    else:
        usage()


if __name__ == "__main__":
    main()
