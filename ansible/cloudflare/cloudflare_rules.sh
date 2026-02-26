#!/bin/bash

# ===============================================
# Cloudflare Rules Export / Import Script
# ===============================================
# Usage:
#   Export rules:
#       ./cloudflare_rules.sh export <API_TOKEN> <ZONE_ID>
#
#   Import rules:
#       ./cloudflare_rules.sh import <API_TOKEN> <ZONE_ID>
#
# Alternatively, set CLOUDFLARE_API_TOKEN and CLOUDFLARE_ZONE_ID
# environment variables and run:
#       ./cloudflare_rules.sh export
#
# ===============================================

# === CONFIGURATION ===
API_TOKEN="${2:-$CLOUDFLARE_API_TOKEN}"
ZONE_ID="${3:-$CLOUDFLARE_ZONE_ID}"

usage() {
    echo "Usage: $0 {export|import} [API_TOKEN] [ZONE_ID]"
    echo ""
    echo "Arguments:"
    echo "  export/import  Operation to perform"
    echo "  API_TOKEN      Cloudflare API Token (optional if CLOUDFLARE_API_TOKEN env var is set)"
    echo "  ZONE_ID        Cloudflare Zone ID (optional if CLOUDFLARE_ZONE_ID env var is set)"
    exit 1
}

if [[ -z "$API_TOKEN" || -z "$ZONE_ID" ]]; then
    echo "Error: API_TOKEN and ZONE_ID must be provided either as arguments or environment variables."
    usage
fi

BASE_URL="https://api.cloudflare.com/client/v4/zones/$ZONE_ID/rulesets"
HEADERS=(-H "Authorization: Bearer $API_TOKEN" -H "Content-Type: application/json")

# Helper to perform curl with error checking
call_cloudflare() {
    local method=$1
    local url=$2
    local output_file=$3
    local data_file=$4
    local description=$5

    echo "$description..."
    
    local curl_opts=(-s -w "\n%{http_code}" -X "$method" "$url" "${HEADERS[@]}")
    
    local full_response
    if [[ -n "$output_file" ]]; then
        # For export
        full_response=$(curl "${curl_opts[@]}" -o "$output_file")
    elif [[ -n "$data_file" ]]; then
        # For import
        if [[ ! -f "$data_file" ]]; then
            echo "Error: Data file $data_file not found. Skipping $description."
            return 1
        fi
        full_response=$(curl "${curl_opts[@]}" --data @"$data_file")
    fi

    local http_code
    http_code=$(echo "$full_response" | tail -n1)

    if [[ "$http_code" -lt 200 || "$http_code" -gt 299 ]]; then
        echo "Error: $description failed with HTTP status $http_code"
        if [[ -n "$full_response" && "$full_response" != "$http_code" ]]; then
            echo "Response: $(echo "$full_response" | head -n -1)"
        fi
        return 1
    fi
    return 0
}

# === EXPORT FUNCTION ===
export_rules() {
    local failed=0
    call_cloudflare "GET" "$BASE_URL/phases/http_request_firewall_custom/entrypoint" "waf_rules.json" "" "Exporting WAF Custom Rules" || failed=1
    call_cloudflare "GET" "$BASE_URL/phases/http_ratelimit/entrypoint" "rate_limit_rules.json" "" "Exporting Rate Limiting Rules" || failed=1
    call_cloudflare "GET" "$BASE_URL/phases/http_request_cache_settings/entrypoint" "cache_rules.json" "" "Exporting Cache Rules" || failed=1
    call_cloudflare "GET" "$BASE_URL/phases/http_request_redirect/entrypoint" "redirect_rules.json" "" "Exporting Redirect Rules" || failed=1

    if [[ $failed -eq 0 ]]; then
        echo "Export completed successfully. JSON files saved in current directory."
    else
        echo "Export completed with errors."
        exit 1
    fi
}

# === IMPORT FUNCTION ===
import_rules() {
    local failed=0
    call_cloudflare "PUT" "$BASE_URL/phases/http_request_firewall_custom/entrypoint" "" "waf_rules.json" "Importing WAF Custom Rules" || failed=1
    call_cloudflare "PUT" "$BASE_URL/phases/http_ratelimit/entrypoint" "" "rate_limit_rules.json" "Importing Rate Limiting Rules" || failed=1
    call_cloudflare "PUT" "$BASE_URL/phases/http_request_cache_settings/entrypoint" "" "cache_rules.json" "Importing Cache Rules" || failed=1
    call_cloudflare "PUT" "$BASE_URL/phases/http_request_redirect/entrypoint" "" "redirect_rules.json" "Importing Redirect Rules" || failed=1

    if [[ $failed -eq 0 ]]; then
        echo "Import completed successfully."
    else
        echo "Import completed with errors."
        exit 1
    fi
}

# === MAIN ===
case "$1" in
    export)
        export_rules
        ;;
    import)
        import_rules
        ;;
    *)
        usage
        ;;
esac
