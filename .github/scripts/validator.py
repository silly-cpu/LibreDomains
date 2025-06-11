#!/usr/bin/env python3
import os
import json
import re
import sys

# --- Configuration ---
REQUESTS_DIR = "requests"
DOMAINS_FILE = "domains/available_domains.json"
CONFIG_FILE = "config.json"

# --- Helper Functions ---
def load_json(file_path):
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        return None

def get_pr_changed_files(pr_number, github_token):
    # In a real GitHub Action, you'd get this from the event payload or API
    # For local testing, this will be harder to simulate accurately without API calls.
    # This function is a placeholder for how you might get changed files.
    # For now, we'll assume the script is run in a context where changed files are known
    # or we iterate through all files in the PR (less efficient).

    # Example: using GITHUB_EVENT_PATH
    event_path = os.environ.get('GITHUB_EVENT_PATH')
    if not event_path:
        print("::error::GITHUB_EVENT_PATH not found. Cannot determine changed files for PR.")
        return []

    try:
        with open(event_path, 'r') as f:
            event_data = json.load(f)
        
        # This path to files depends on the event type (pull_request, pull_request_target)
        # For 'pull_request', it's often not directly in the main payload, 
        # you'd typically use `actions/checkout` and then git diff, or use the API.

        # For simplicity in this script, we'll rely on the workflow path filter
        # and assume any .json file in requests/ that is part of the commit is what we need to check.
        # A more robust solution uses the GitHub API to list files in a PR:
        # GET /repos/{owner}/{repo}/pulls/{pull_number}/files
        # However, this requires an authenticated API call.

        # Let's try a simplified approach: list files in requests/ and check against base branch
        # This is still complex to do correctly without full git history here.
        # The workflow `paths` trigger is the primary filter.
        # We will iterate over all files in requests/ that are part of the current PR commit(s).
        # This part is tricky to implement generically without API calls or git commands.

        # Fallback: if PR_NUMBER is available, try to use git diff. This assumes git is available.
        if pr_number:
            print(f"Attempting to get changed files for PR #{pr_number}")
            # Ensure we have the base branch to compare against
            base_ref = os.environ.get('GITHUB_BASE_REF')
            if not base_ref:
                print("::warning::GITHUB_BASE_REF not set. Cannot reliably determine changed files via git diff.")
                return [] # Or fallback to checking all files in requests/
            
            try:
                # Fetch the base branch
                os.system(f'git fetch origin {base_ref} --depth=1')
                # Get diff
                diff_files = os.popen(f'git diff --name-only origin/{base_ref} HEAD -- {REQUESTS_DIR}/').read().splitlines()
                json_files = [f for f in diff_files if f.startswith(REQUESTS_DIR + '/') and f.endswith('.json')]
                print(f"Found changed JSON files via git diff: {json_files}")
                return json_files
            except Exception as e:
                print(f"::warning::Error using git diff to find changed files: {e}. Will check all files in PR.")
                # Fallback if git diff fails, this part is hard to do without API
                # The action should ideally pass the changed files as an input or env var.
                pass
        
        # If all else fails, and we are in a PR context, we might have to assume
        # any file in requests/ in the current checkout that is new or modified is relevant.
        # This is not ideal. The workflow `paths` filter is key.
        print("::warning::Could not reliably determine specific changed files for the PR. Will scan all files in requests/ directory of the PR branch.")
        # This will scan all files in the PR's version of requests/
        pr_files = []
        if os.path.exists(REQUESTS_DIR):
            for f_name in os.listdir(REQUESTS_DIR):
                if f_name.endswith('.json'):
                    pr_files.append(os.path.join(REQUESTS_DIR, f_name))
        return pr_files

    except Exception as e:
        print(f"::error::Could not determine changed files: {e}")
        return []

def is_subdomain_conflict(subdomain_to_check, existing_files, pr_author, current_file_path):
    """Checks for conflicts: same file name (subdomain) by a different author, or existing record."""
    for existing_file in existing_files:
        if existing_file == current_file_path: # Don't compare a file with itself (e.g. on synchronize)
            continue
        if os.path.basename(existing_file) == os.path.basename(current_file_path):
            # Same filename, check owner if possible (this is a simplified check)
            # A more robust check would look at the git history or PR author of the existing file.
            # For now, if filename is same and it's not the current PR's file, assume conflict.
            print(f"::error file={current_file_path}::Subdomain {subdomain_to_check} (file: {os.path.basename(current_file_path)}) conflicts with existing file: {existing_file}.")
            return True
    return False

def validate_record(record, available_domains_config, parent_domain_name):
    """Validates a single DNS record."""
    messages = []
    is_valid = True

    required_fields = ["type", "value"]
    for field in required_fields:
        if field not in record:
            messages.append(f"Missing required field '{field}' in record.")
            is_valid = False

    if not is_valid: # Stop if basic fields are missing
        return False, messages

    record_type = record["type"].upper()

    if record_type == "NS":
        messages.append("NS records are not permitted.")
        is_valid = False

    # Basic type checks (can be expanded)
    supported_types = ["A", "AAAA", "CNAME", "MX", "TXT", "SRV", "CAA"] # Add more as needed
    if record_type not in supported_types:
        messages.append(f"Unsupported record type: {record_type}.")
        is_valid = False

    if record_type == "MX":
        if "priority" not in record or not isinstance(record["priority"], int):
            messages.append("MX records require an integer 'priority' field.")
            is_valid = False
    
    if record_type == "A":
        # Basic IPv4 regex
        if not re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", record["value"]):
            messages.append(f"Invalid IPv4 address for A record: {record['value']}")
            is_valid = False

    if record_type == "AAAA":
        # Basic IPv6 regex (simplified)
        if not re.match(r"^[0-9a-fA-F:]{3,39}$", record["value"]):
            messages.append(f"Invalid IPv6 address for AAAA record: {record['value']}")
            is_valid = False

    if record_type == "CNAME":
        # Basic hostname regex (simplified)
        if not re.match(r"^([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$", record["value"]):
            messages.append(f"Invalid hostname for CNAME record: {record['value']}")
            is_valid = False
        if record.get("proxied") not in [True, False, None]: # None is acceptable, defaults to false
             messages.append("'proxied' field for CNAME must be true or false if present.")
             is_valid = False

    if record.get("proxied") and record_type not in ["A", "AAAA", "CNAME"]:
        messages.append(f"Cloudflare proxy (proxied: true) is only supported for A, AAAA, and CNAME records. Found on {record_type}.")
        is_valid = False

    # TODO: Add more specific validation for SRV, CAA data fields as per USER_GUIDE.md

    return is_valid, messages

# --- Main Validation Logic ---
def main():
    pr_number = os.environ.get('PR_NUMBER')
    pr_author = os.environ.get('PR_AUTHOR')
    github_token = os.environ.get('GITHUB_TOKEN')
    github_repository = os.environ.get('GITHUB_REPOSITORY')
    github_workspace = os.environ.get('GITHUB_WORKSPACE', '.') # Default to current dir if not in Action

    # Construct absolute paths
    requests_abs_dir = os.path.join(github_workspace, REQUESTS_DIR)
    domains_abs_file = os.path.join(github_workspace, DOMAINS_FILE)
    config_abs_file = os.path.join(github_workspace, CONFIG_FILE)

    output_messages = []
    overall_status = "success"

    if not pr_number or not pr_author:
        output_messages.append("::error::PR_NUMBER or PR_AUTHOR environment variables not set. Cannot validate.")
        overall_status = "failure"
        print("\n".join(output_messages))
        print(f"::set-output name=validation_output::{json.dumps(output_messages)}")
        print(f"::set-output name=validation_status::{overall_status}")
        sys.exit(1)

    output_messages.append(f"Validating PR #{pr_number} by @{pr_author}.")

    available_domains_config = load_json(domains_abs_file)
    if not available_domains_config or "domains" not in available_domains_config:
        output_messages.append(f"::error::Could not load or parse {DOMAINS_FILE}.")
        overall_status = "failure"
        print("\n".join(output_messages))
        print(f"::set-output name=validation_output::{json.dumps(output_messages)}")
        print(f"::set-output name=validation_status::{overall_status}")
        sys.exit(1)

    # Get files changed in this PR that are in the requests/ directory
    # This is a simplified way; a robust solution uses GitHub API or git diff against main/master
    changed_files = get_pr_changed_files(pr_number, github_token)
    if not changed_files:
        output_messages.append("::warning::No .json files found in the 'requests/' directory for this PR. Nothing to validate.")
        # This might not be an error if other files were changed, but the workflow path filter should handle this.
        print("\n".join(output_messages))
        print(f"::set-output name=validation_output::{json.dumps(output_messages)}")
        print(f"::set-output name=validation_status::{overall_status}") # Still success if nothing to do
        sys.exit(0)

    output_messages.append(f"Found changed files to validate: {changed_files}")

    # Get existing request files from the main branch to check for conflicts
    # This requires checking out the main branch or using GitHub API.
    # For simplicity, we'll list files in requests/ on the current (PR) branch
    # and assume conflict checking needs to be more robust (e.g. via a separate script or API call before merge)
    # A better approach for conflict checking: query existing files on the BASE branch.
    existing_request_files_on_base = []
    base_ref = os.environ.get('GITHUB_BASE_REF')
    if base_ref:
        try:
            print(f"Fetching base branch {base_ref} to check for existing requests...")
            os.system(f'git fetch origin {base_ref} --depth=1')
            # List files in requests/ directory of the base branch
            ls_tree_output = os.popen(f'git ls-tree -r --name-only origin/{base_ref} -- {REQUESTS_DIR}/').read().splitlines()
            existing_request_files_on_base = [f for f in ls_tree_output if f.startswith(REQUESTS_DIR + '/') and f.endswith('.json')]
            output_messages.append(f"Found {len(existing_request_files_on_base)} existing request files on base branch ({base_ref}).")
        except Exception as e:
            output_messages.append(f"::warning::Could not list files from base branch {base_ref} for conflict check: {e}. Conflict check might be incomplete.")
    else:
        output_messages.append("::warning::GITHUB_BASE_REF not set. Conflict check against base branch skipped.")


    for file_path_rel in changed_files:
        file_path_abs = os.path.join(github_workspace, file_path_rel)
        output_messages.append(f"--- Validating file: {file_path_rel} ---")

        if not file_path_rel.startswith(REQUESTS_DIR + '/') or not file_path_rel.endswith('.json'):
            output_messages.append(f"::warning::Skipping non-JSON file or file outside requests directory: {file_path_rel}")
            continue

        request_data = load_json(file_path_abs)
        if not request_data:
            output_messages.append(f"::error file={file_path_rel}::Invalid JSON format.")
            overall_status = "failure"
            continue

        # Validate owner field
        if "owner" not in request_data or request_data["owner"] != pr_author:
            output_messages.append(f"::error file={file_path_rel}::Owner field must match PR author (@{pr_author}). Found '{(request_data.get("owner"))}'.")
            overall_status = "failure"
        
        # Validate filename format (subdomain.parentdomain.tld.json)
        filename = os.path.basename(file_path_rel)
        parts = filename.split('.')
        if len(parts) < 4 or parts[-1] != 'json': # e.g., sub.domain.com.json -> [sub, domain, com, json]
            output_messages.append(f"::error file={file_path_rel}::Invalid filename format. Expected 'subdomain.parentdomain.tld.json'.")
            overall_status = "failure"
            continue
        
        requested_subdomain_part = parts[0]
        parent_domain_name = ".".join(parts[1:-1]) # e.g., domain.com

        # Check if parent domain is valid and enabled
        parent_domain_info = next((d for d in available_domains_config["domains"] if d["name"] == parent_domain_name), None)
        if not parent_domain_info:
            output_messages.append(f"::error file={file_path_rel}::Parent domain '{parent_domain_name}' is not listed in {DOMAINS_FILE}.")
            overall_status = "failure"
            continue
        if not parent_domain_info.get("enabled", False):
            output_messages.append(f"::error file={file_path_rel}::Parent domain '{parent_domain_name}' is not enabled for new requests.")
            overall_status = "failure"
            continue
        
        full_requested_domain = f"{requested_subdomain_part}.{parent_domain_name}"
        output_messages.append(f"Processing request for: {full_requested_domain}")

        # Conflict Check (against files on base branch)
        # A file with the same name on the base branch means the subdomain is already taken.
        path_on_base_to_check = os.path.join(REQUESTS_DIR, filename) # Relative path from repo root
        if path_on_base_to_check in existing_request_files_on_base:
            output_messages.append(f"::error file={file_path_rel}::Subdomain '{full_requested_domain}' (filename: {filename}) already exists in the main branch.")
            overall_status = "failure"
            continue # Skip record validation if it's a clear conflict

        # TODO: Add check for other open PRs requesting the same subdomain.
        # This requires GitHub API call to list open PRs and their files.
        # `gh pr list --json number,files --state open` and parse files.

        if "records" not in request_data or not isinstance(request_data["records"], list) or not request_data["records"]:
            output_messages.append(f"::error file={file_path_rel}::Missing or empty 'records' array.")
            overall_status = "failure"
            continue

        for i, record in enumerate(request_data["records"]):
            output_messages.append(f"  Validating record #{i+1}: Type={record.get('type')}, Value={record.get('value')}")
            is_valid, record_msgs = validate_record(record, available_domains_config, parent_domain_name)
            for msg in record_msgs:
                output_messages.append(f"::error file={file_path_rel},line={i+1}::Record #{i+1}: {msg}") # Rough line number
            if not is_valid:
                overall_status = "failure"
        
        output_messages.append(f"--- Finished validating {file_path_rel} ---")

    final_output_str = "\n".join(output_messages)
    print(final_output_str)
    
    # Set outputs for the GitHub Action
    # Escape newlines and quotes for multiline output string
    escaped_output = json.dumps(final_output_str) 
    print(f"::set-output name=validation_output::{escaped_output}")
    print(f"::set-output name=validation_status::{overall_status}")

    if overall_status == "failure":
        sys.exit(1)

if __name__ == "__main__":
    main()
