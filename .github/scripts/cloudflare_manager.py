#!/usr/bin/env python3
import os
import json
import requests # For Cloudflare API calls
import sys

# --- Configuration ---
# These will be set by environment variables in the GitHub Action
CLOUDFLARE_API_TOKEN = os.environ.get('CLOUDFLARE_API_TOKEN')
CONFIG_FILE_PATH = os.environ.get('CONFIG_FILE', 'config.json')
DOMAINS_FILE_PATH = os.environ.get('DOMAINS_FILE', 'domains/available_domains.json')
REQUESTS_DIR_PATH = os.environ.get('REQUESTS_DIR', 'requests')
GITHUB_WORKSPACE = os.environ.get('GITHUB_WORKSPACE', '.')

CLOUDFLARE_API_BASE_URL = "https://api.cloudflare.com/client/v4"

# --- Helper Functions ---
def load_json(file_path):
    abs_path = os.path.join(GITHUB_WORKSPACE, file_path)
    try:
        with open(abs_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"::error::File not found: {abs_path}")
        return None
    except json.JSONDecodeError as e:
        print(f"::error::Invalid JSON in {abs_path}: {e}")
        return None
    except Exception as e:
        print(f"::error::Could not load {abs_path}: {e}")
        return None

def get_cloudflare_headers():
    if not CLOUDFLARE_API_TOKEN:
        print("::error::CLOUDFLARE_API_TOKEN secret not set.")
        sys.exit(1)
    return {
        "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
        "Content-Type": "application/json"
    }

def get_zone_id(domain_name, domains_config):
    if not domains_config or "domains" not in domains_config:
        print(f"::error::Invalid or missing domains configuration in {DOMAINS_FILE_PATH}")
        return None
    for domain_entry in domains_config["domains"]:
        if domain_entry["name"] == domain_name:
            if not domain_entry.get("enabled", False):
                print(f"::warning::Parent domain '{domain_name}' is not enabled. Skipping sync for its subdomains.")
                return None # Effectively skip if not enabled
            zone_id = domain_entry.get("zoneId")
            if not zone_id or zone_id.startswith("YOUR_CLOUDFLARE_ZONE_ID"):
                print(f"::error::Missing or placeholder zoneId for domain '{domain_name}' in {DOMAINS_FILE_PATH}.")
                return None
            return zone_id
    print(f"::error::Parent domain '{domain_name}' not found in {DOMAINS_FILE_PATH}.")
    return None

def get_existing_dns_records(zone_id, record_name_prefix=""):
    """Fetches all DNS records for a zone, optionally filtered by name prefix."""
    headers = get_cloudflare_headers()
    url = f"{CLOUDFLARE_API_BASE_URL}/zones/{zone_id}/dns_records"
    params = {"per_page": 100} # Max per page
    if record_name_prefix:
        params["name"] = record_name_prefix # This will fetch records starting with this full name
    
    all_records = []
    page = 1
    while True:
        params["page"] = page
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status() # Raise an exception for bad status codes
            data = response.json()
            if not data["success"]:
                print(f"::error::Cloudflare API error fetching records for zone {zone_id}: {data.get('errors')}")
                return None # Indicate error
            
            all_records.extend(data["result"])
            
            total_pages = data.get("result_info", {}).get("total_pages", 1)
            if page >= total_pages:
                break
            page += 1
        except requests.exceptions.RequestException as e:
            print(f"::error::HTTP error fetching DNS records for zone {zone_id}: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"::error::Failed to decode JSON response from Cloudflare for zone {zone_id}: {e}")
            return None
    return all_records

def create_dns_record(zone_id, record_data):
    headers = get_cloudflare_headers()
    url = f"{CLOUDFLARE_API_BASE_URL}/zones/{zone_id}/dns_records"
    try:
        response = requests.post(url, headers=headers, json=record_data)
        response.raise_for_status()
        result = response.json()
        if result["success"]:
            print(f"Successfully created DNS record: {record_data['name']} ({record_data['type']})")
            return True, result["result"]
        else:
            print(f"::error::Cloudflare API error creating record {record_data['name']}: {result.get('errors')}")
            return False, result.get('errors')
    except requests.exceptions.RequestException as e:
        print(f"::error::HTTP error creating DNS record {record_data['name']}: {e}. Response: {e.response.text if e.response else 'No response'}")
        return False, str(e)
    except json.JSONDecodeError as e:
        print(f"::error::Failed to decode JSON response from Cloudflare when creating {record_data['name']}: {e}")
        return False, str(e)

def update_dns_record(zone_id, record_id, record_data):
    headers = get_cloudflare_headers()
    url = f"{CLOUDFLARE_API_BASE_URL}/zones/{zone_id}/dns_records/{record_id}"
    try:
        response = requests.put(url, headers=headers, json=record_data)
        response.raise_for_status()
        result = response.json()
        if result["success"]:
            print(f"Successfully updated DNS record: {record_data['name']} ({record_data['type']}) ID: {record_id}")
            return True, result["result"]
        else:
            print(f"::error::Cloudflare API error updating record {record_data['name']} (ID: {record_id}): {result.get('errors')}")
            return False, result.get('errors')
    except requests.exceptions.RequestException as e:
        print(f"::error::HTTP error updating DNS record {record_data['name']} (ID: {record_id}): {e}. Response: {e.response.text if e.response else 'No response'}")
        return False, str(e)
    except json.JSONDecodeError as e:
        print(f"::error::Failed to decode JSON response from Cloudflare when updating {record_data['name']}: {e}")
        return False, str(e)

def delete_dns_record(zone_id, record_id, record_name):
    headers = get_cloudflare_headers()
    url = f"{CLOUDFLARE_API_BASE_URL}/zones/{zone_id}/dns_records/{record_id}"
    try:
        response = requests.delete(url, headers=headers)
        response.raise_for_status()
        result = response.json()
        if result["success"]:
            print(f"Successfully deleted DNS record: {record_name} (ID: {record_id})")
            return True
        else:
            print(f"::error::Cloudflare API error deleting record {record_name} (ID: {record_id}): {result.get('errors')}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"::error::HTTP error deleting DNS record {record_name} (ID: {record_id}): {e}. Response: {e.response.text if e.response else 'No response'}")
        return False
    except json.JSONDecodeError as e:
        print(f"::error::Failed to decode JSON response from Cloudflare when deleting {record_name}: {e}")
        return False

def record_matches(cf_record, desired_record, full_domain_name):
    """Check if a Cloudflare record matches a desired record definition."""
    if cf_record["type"] != desired_record["type"]: return False
    if cf_record["name"] != full_domain_name: return False # Should already be filtered, but good check
    
    # Content can vary in format (e.g. CNAMEs might have trailing dot)
    # Cloudflare API usually returns content without trailing dot for CNAMEs.
    if cf_record["type"] == "CNAME":
        if cf_record["content"].rstrip('.') != desired_record["value"].rstrip('.'): return False
    elif cf_record["type"] == "MX":
        if cf_record["content"] != desired_record["value"]: return False # MX value is the mail server
        if cf_record["priority"] != desired_record.get("priority"): return False
    elif cf_record["type"] == "TXT":
        # TXT records can be tricky due to quotes or splitting. CF API returns the raw string.
        if cf_record["content"] != desired_record["value"]: return False
    # Add more specific checks for SRV, CAA etc. if needed based on how CF stores them
    elif cf_record["content"] != desired_record["value"]: return False

    if "proxied" in desired_record and desired_record["type"] in ["A", "AAAA", "CNAME"]:
        if cf_record.get("proxied", False) != desired_record.get("proxied", False):
            return False
    return True

# --- Main Sync Logic ---
def main():
    print("Starting DNS synchronization process...")

    config = load_json(CONFIG_FILE_PATH)
    if not config:
        print(f"::error::Failed to load configuration from {CONFIG_FILE_PATH}. Exiting.")
        sys.exit(1)

    domains_config = load_json(DOMAINS_FILE_PATH)
    if not domains_config or "domains" not in domains_config:
        print(f"::error::Failed to load or parse domain configurations from {DOMAINS_FILE_PATH}. Exiting.")
        sys.exit(1)

    requests_abs_dir = os.path.join(GITHUB_WORKSPACE, REQUESTS_DIR_PATH)
    if not os.path.isdir(requests_abs_dir):
        print(f"::error::Requests directory not found: {requests_abs_dir}. Exiting.")
        sys.exit(1)

    # --- Step 1: Gather all desired records from local JSON files ---
    desired_state = {}
    print(f"Scanning request files in {requests_abs_dir}...")
    for filename in os.listdir(requests_abs_dir):
        if filename.endswith('.json'):
            file_path = os.path.join(requests_abs_dir, filename)
            record_def = load_json(file_path) # file_path is already absolute here if GITHUB_WORKSPACE is correct
            if not record_def or "records" not in record_def or "owner" not in record_def:
                print(f"::warning::Skipping invalid or incomplete request file: {filename}")
                continue

            name_parts = filename[:-5].split('.') # Remove .json and split
            if len(name_parts) < 2:
                print(f"::warning::Skipping file with invalid name format: {filename}")
                continue
            
            subdomain_part = name_parts[0]
            parent_domain_name = ".".join(name_parts[1:])
            full_domain_name = f"{subdomain_part}.{parent_domain_name}"

            zone_id = get_zone_id(parent_domain_name, domains_config)
            if not zone_id: # Error or warning already printed by get_zone_id
                continue

            if zone_id not in desired_state:
                desired_state[zone_id] = {"domain_name": parent_domain_name, "records_to_manage": {}}
            
            # Store records under their full name for easier lookup
            if full_domain_name not in desired_state[zone_id]["records_to_manage"]:
                desired_state[zone_id]["records_to_manage"][full_domain_name] = []
            
            for r_idx, record_entry in enumerate(record_def["records"]):
                # Basic validation, should have been caught by pr_validator.py but good to double check
                if not all(k in record_entry for k in ["type", "value"]):
                    print(f"::warning::Skipping malformed record #{r_idx+1} in {filename}: missing type or value.")
                    continue
                
                # Prepare record for Cloudflare API
                cf_api_record = {
                    "type": record_entry["type"].upper(),
                    "name": full_domain_name,
                    "content": record_entry["value"],
                    "ttl": record_entry.get("ttl", 1) # Default TTL to 1 (Automatic)
                }
                if "priority" in record_entry and cf_api_record["type"] == "MX":
                    cf_api_record["priority"] = record_entry["priority"]
                if "proxied" in record_entry and cf_api_record["type"] in ["A", "AAAA", "CNAME"]:
                    cf_api_record["proxied"] = record_entry["proxied"]
                
                # Handle SRV, CAA data if specified in USER_GUIDE and implemented
                # For SRV: record_entry["data"] = { "service", "proto", "name", "priority", "weight", "port", "target" }
                # Cloudflare API expects these as top-level keys in the `data` object for SRV records.
                # This part needs careful mapping based on Cloudflare's exact API requirements for these types.
                # Example for SRV (ensure your USER_GUIDE matches this structure):
                if cf_api_record["type"] == "SRV" and "data" in record_entry:
                    cf_api_record["data"] = record_entry["data"] # Pass through if structure is correct
                
                desired_state[zone_id]["records_to_manage"][full_domain_name].append(cf_api_record)

    if not desired_state:
        print("No valid request files found or no enabled domains with Zone IDs. Nothing to sync.")
        sys.exit(0)

    print(f"Desired state compiled from {len(desired_state)} zones.")

    # --- Step 2: Fetch current Cloudflare state and reconcile ---
    overall_success = True
    for zone_id, data in desired_state.items():
        parent_domain = data["domain_name"]
        print(f"--- Processing Zone: {zone_id} (Domain: {parent_domain}) ---")
        
        # Fetch ALL records for the zone to manage deletions correctly for managed subdomains
        # This is crucial: we need to know what's on Cloudflare to compare against our desired state.
        cf_records_list = get_existing_dns_records(zone_id)
        if cf_records_list is None: # Error occurred fetching records
            print(f"::error::Could not fetch existing records for zone {zone_id}. Skipping this zone.")
            overall_success = False
            continue
        
        # Organize Cloudflare records by their full name for easier lookup
        cf_records_by_name = {}
        for rec in cf_records_list:
            name = rec["name"]
            if name not in cf_records_by_name:
                cf_records_by_name[name] = []
            cf_records_by_name[name].append(rec)

        managed_subdomains_in_zone = data["records_to_manage"].keys()

        # Iterate through desired records (from files)
        for full_domain_name, desired_records_for_subdomain in data["records_to_manage"].items():
            print(f"  Syncing records for: {full_domain_name}")
            current_cf_records_for_subdomain = cf_records_by_name.get(full_domain_name, [])
            processed_cf_ids = set() # Keep track of CF records we've matched or updated

            for desired_rec_data in desired_records_for_subdomain:
                match_found = False
                for cf_rec in current_cf_records_for_subdomain:
                    if cf_rec["id"] in processed_cf_ids: # Already dealt with
                        continue
                    
                    # Check if this cf_rec matches the desired_rec_data (type, content, etc.)
                    # The `record_matches` function needs to be robust here.
                    # For simplicity, we'll compare key fields. Cloudflare API is the source of truth for exact format.
                    # A simple comparison for now, can be expanded in `record_matches`
                    if (
                        cf_rec["type"] == desired_rec_data["type"] and
                        # Name is already filtered by full_domain_name key
                        # Content comparison needs to be type-specific
                        (
                            (cf_rec["type"] == "CNAME" and cf_rec["content"].rstrip('.') == desired_rec_data["content"].rstrip('.')) or
                            (cf_rec["type"] == "MX" and cf_rec["content"] == desired_rec_data["content"] and cf_rec.get("priority") == desired_rec_data.get("priority")) or
                            (cf_rec["type"] not in ["CNAME", "MX"] and cf_rec["content"] == desired_rec_data["content"])
                        )
                    ):
                        # Potential match, now check proxied status if applicable
                        proxy_match = True
                        if desired_rec_data["type"] in ["A", "AAAA", "CNAME"]:
                            if cf_rec.get("proxied", False) != desired_rec_data.get("proxied", False):
                                proxy_match = False
                        
                        if proxy_match:
                            print(f"    Record exists and matches: {desired_rec_data['type']} {desired_rec_data['name']} -> {desired_rec_data['content']}")
                            processed_cf_ids.add(cf_rec["id"])
                            match_found = True
                            break # Found a matching CF record for this desired record
                        else:
                            # Content matches, but proxy status differs. This is an UPDATE.
                            print(f"    Record exists but proxy status differs for {desired_rec_data['name']} ({desired_rec_data['type']}). Updating.")
                            # Use the full desired_rec_data for update, as it contains all fields for CF API
                            success, _ = update_dns_record(zone_id, cf_rec["id"], desired_rec_data)
                            if success:
                                processed_cf_ids.add(cf_rec["id"])
                            else:
                                overall_success = False
                            match_found = True # Handled (attempted update)
                            break 
                
                if not match_found:
                    # No existing record matches this desired one, so create it.
                    print(f"    Creating new record: {desired_rec_data['type']} {desired_rec_data['name']} -> {desired_rec_data['content']}")
                    success, _ = create_dns_record(zone_id, desired_rec_data)
                    if not success:
                        overall_success = False
            
            # After processing all desired records for a subdomain, delete any unmatched CF records for that subdomain
            for cf_rec in current_cf_records_for_subdomain:
                if cf_rec["id"] not in processed_cf_ids:
                    print(f"    Deleting stale Cloudflare record: {cf_rec['type']} {cf_rec['name']} (ID: {cf_rec['id']})")
                    if not delete_dns_record(zone_id, cf_rec["id"], cf_rec["name"]):
                        overall_success = False
        
        # --- Step 3: Delete records for subdomains whose JSON files were removed ---
        # This means iterating through Cloudflare records and checking if a corresponding JSON file exists.
        # Only delete records that *would* be managed by this system (i.e. subdomains of parent_domain)
        print(f"  Checking for deleted subdomains in zone {zone_id} (parent: {parent_domain})...")
        for cf_full_name, cf_records_for_name in cf_records_by_name.items():
            # Check if cf_full_name belongs to the current parent_domain being processed
            if not cf_full_name.endswith("." + parent_domain):
                continue # Not a subdomain of the current parent domain

            # Is this a subdomain we expect to manage based on file structure?
            # e.g. if cf_full_name is test.ciao.su, expected file is test.ciao.su.json
            expected_request_filename = f"{cf_full_name}.json"
            expected_request_filepath = os.path.join(requests_abs_dir, expected_request_filename)

            if not os.path.exists(expected_request_filepath):
                # File does not exist, so these records should be deleted
                print(f"    Request file {expected_request_filename} not found. Deleting records for {cf_full_name}.")
                for cf_rec_to_delete in cf_records_for_name:
                    # Make sure it's not a root domain record or something unrelated we shouldn't touch
                    if cf_rec_to_delete["name"] == cf_full_name: # Ensure we are deleting the correct named records
                        print(f"      Deleting Cloudflare record: {cf_rec_to_delete['type']} {cf_rec_to_delete['name']} (ID: {cf_rec_to_delete['id']})")
                        if not delete_dns_record(zone_id, cf_rec_to_delete["id"], cf_rec_to_delete["name"]):
                            overall_success = False
            # Else: file exists, records for this name were handled in the loop above.

    if not overall_success:
        print("::error::One or more errors occurred during DNS synchronization.")
        sys.exit(1)
    
    print("DNS synchronization process completed.")

if __name__ == "__main__":
    main()
