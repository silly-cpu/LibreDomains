# LibreDomains Project Overview

This document provides a more detailed overview of the LibreDomains project architecture and components.

## Core Idea

The project aims to provide a simple, transparent, and automated way for users to obtain free subdomains under a set of managed parent domains. The entire process, from request to DNS record creation, is handled through GitHub.

## Directory Structure

```
LibreDomains-beta/
├── .github/
│   └── workflows/
│       ├── pr_validator.yml  # GitHub Action for validating Pull Requests
│       └── dns_sync.yml      # GitHub Action for syncing DNS to Cloudflare
├── docs/
│   ├── ADMIN_GUIDE.md
│   ├── USER_GUIDE.md
│   └── README.md           # This file (Project Overview)
├── domains/
│   └── available_domains.json # List of parent domains available for distribution
├── requests/
│   └── example.domain.com.json # Example of a user's subdomain request file
├── scripts/
│   ├── cloudflare_api.py   # Script for Cloudflare API interactions (example)
│   └── validator.py        # Script for request validation logic (example)
├── config.json             # Main project configuration
└── README.md               # Main project README (points to this overview)
```

## Components

1.  **`config.json`**:
    *   Stores global configuration like Cloudflare API token environment variable name, admin GitHub usernames, and notification emails.

2.  **`domains/available_domains.json`**:
    *   Defines the list of parent domains that are open for subdomain registration.
    *   Each domain entry includes its name, a description, an `enabled` flag, and its Cloudflare `zoneId`.

3.  **`requests/` directory**:
    *   This directory acts as the database of approved subdomain requests.
    *   Each approved subdomain has a corresponding JSON file named `subdomain.parentdomain.tld.json` (e.g., `myblog.ciao.su.json`).
    *   The JSON file contains the owner's GitHub username and the desired DNS records (type, value, proxy status, etc.).

4.  **`.github/workflows/pr_validator.yml`**:
    *   A GitHub Action triggered on `pull_request` events (when a user submits a new subdomain request or updates an existing one).
    *   **Responsibilities**:
        *   Parse the JSON file(s) in the PR.
        *   Validate the JSON schema.
        *   Check if the requested subdomain is already taken (i.e., a file for it exists in `requests/` on the main branch or in another open PR).
        *   Check for conflicts or disallowed record types (e.g., NS records).
        *   Ensure the requested parent domain is enabled in `domains/available_domains.json`.
        *   Verify the owner field matches the PR author (optional, but good practice).
        *   Comment on the PR with success or failure messages. If failed, provide clear reasons.
    *   This workflow will likely use scripts from the `scripts/` directory (e.g., `validator.py`).

5.  **`.github/workflows/dns_sync.yml`**:
    *   A GitHub Action triggered on `push` events to the main branch (typically after a PR is merged).
    *   **Responsibilities**:
        *   Scan all JSON files in the `requests/` directory.
        *   For each file, parse the DNS record definitions.
        *   Connect to the Cloudflare API using the `CLOUDFLARE_API_TOKEN` secret.
        *   Retrieve the `zoneId` for the parent domain from `domains/available_domains.json`.
        *   Create, update, or delete DNS records in the corresponding Cloudflare zone based on the JSON definitions.
            *   **Create/Update**: If a JSON file exists, ensure the DNS records in Cloudflare match.
            *   **Delete**: If a JSON file is deleted from `requests/` (meaning a subdomain is revoked), the corresponding DNS records should be removed from Cloudflare. This requires comparing the state in `requests/` with the current Cloudflare records or by tracking deletions specifically.
    *   This workflow will heavily rely on a script like `scripts/cloudflare_api.py`.

6.  **`scripts/` directory**:
    *   Contains helper scripts used by the GitHub Actions.
    *   **`validator.py` (example)**: Python script to perform complex validation logic on the request JSON files. This could include checking for blacklisted keywords, rate limits per user, etc.
    *   **`cloudflare_api.py` (example)**: Python script to interact with the Cloudflare API. It would handle:
        *   Listing existing DNS records.
        *   Creating new DNS records.
        *   Updating existing DNS records.
        *   Deleting DNS records.
        *   Error handling and retries for API calls.

## Workflow for Users

1.  User forks the repository.
2.  User creates a new JSON file in `requests/` in their fork (e.g., `myname.ciao.su.json`).
3.  User commits and pushes the file to their fork.
4.  User creates a Pull Request to the main repository.
5.  `pr_validator.yml` runs, checks the request, and comments on the PR.
6.  If checks fail, the user updates their file and pushes again.
7.  If checks pass, an admin reviews and merges the PR.
8.  `dns_sync.yml` runs, and DNS records are updated on Cloudflare.

## Workflow for Admins

1.  Configure `config.json` and `domains/available_domains.json`.
2.  Set up GitHub repository secrets (`CLOUDFLARE_API_TOKEN`).
3.  Review and merge valid Pull Requests.
4.  Monitor GitHub Actions logs for any issues.
5.  Manage parent domains by editing `domains/available_domains.json`.

## Technology Stack

-   **Version Control & Collaboration**: GitHub
-   **Automation**: GitHub Actions
-   **DNS Management**: Cloudflare API
-   **Scripting (for Actions)**: Python is a good choice due to its JSON handling and HTTP request libraries (like `requests`). Shell scripts can also be used for simpler tasks.
-   **Data Format**: JSON for configuration and requests.

## Future Enhancements

-   More sophisticated validation rules (e.g., regex for subdomains, disallowing certain patterns).
-   Rate limiting for requests per user.
-   Dashboard or status page showing currently active subdomains.
-   Notifications to users upon successful registration or issues.
-   Automated cleanup of inactive or problematic subdomains.
-   Support for internationalized domain names (IDNs).

This overview should provide a solid foundation for understanding the project. The actual implementation of the Python scripts and GitHub Action workflow YAML files will be the next major step.
