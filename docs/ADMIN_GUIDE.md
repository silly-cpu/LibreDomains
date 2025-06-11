# Admin Guide

This guide is for administrators of the LibreDomains subdomain distribution system.

## Configuration

The primary configuration file is `config.json` in the root of the repository.

```json
{
  "cloudflareApiTokenEnv": "CLOUDFLARE_API_TOKEN",
  "adminGitHubUsernames": ["your_github_username", "another_admin"],
  "notificationEmail": "admin@example.com"
}
```

-   **`cloudflareApiTokenEnv`**: The name of the environment variable that holds the Cloudflare API token. This token must be set as a secret in the GitHub repository settings for Actions to use.
-   **`adminGitHubUsernames`**: A list of GitHub usernames who are administrators. This might be used by the bot for certain privileged actions or notifications (future enhancement).
-   **`notificationEmail`**: An email address for important notifications from the system (e.g., critical errors in Actions).

## Managing Parent Domains

Parent domains available for subdomain registration are managed in the `domains/available_domains.json` file.

```json
{
  "domains": [
    {
      "name": "ciao.su",
      "description": "General purpose domain.",
      "enabled": true,
      "zoneId": "your_cloudflare_zone_id_for_ciao.su"
    },
    {
      "name": "ciallo.de",
      "description": "German-focused domain (currently disabled).",
      "enabled": false,
      "zoneId": "your_cloudflare_zone_id_for_ciallo.de"
    }
  ]
}
```

-   **`name`**: The full domain name (e.g., `ciao.su`).
-   **`description`**: A brief description of the domain's purpose.
-   **`enabled`**: Set to `true` to allow users to request subdomains under this domain. Set to `false` to disable new requests for this domain.
-   **`zoneId`**: The Cloudflare Zone ID for this domain. This is required for the Cloudflare API to manage DNS records.

**To add a new domain:**

1.  Ensure the domain is managed under your Cloudflare account.
2.  Find its Zone ID in your Cloudflare dashboard.
3.  Add a new entry to the `domains` array in `domains/available_domains.json` with the required information.
4.  Commit and push the changes to the repository.

## GitHub Actions Secrets

The system relies on GitHub Actions to automate validation and DNS updates. You need to configure the following secrets in your repository settings (`Settings > Secrets and variables > Actions`):

-   **`CLOUDFLARE_API_TOKEN`**: Your Cloudflare API token. This token needs permissions to read and edit DNS records for the configured zones.
    *   Go to Cloudflare Dashboard -> My Profile -> API Tokens.
    *   Create a Custom Token.
    *   Permissions:
        *   Zone - DNS - Edit
        *   Zone - Zone - Read
    *   Zone Resources: Include all specific zones you want to manage (e.g., `ciao.su`, `ciallo.de`).
-   **`GH_TOKEN`** (Optional but Recommended): A GitHub Personal Access Token (PAT) with `repo` scope if the default `GITHUB_TOKEN` has insufficient permissions for specific actions your bot might need (e.g., more complex PR interactions or writing to other repositories if extended). For basic PR comments and checks, the default `GITHUB_TOKEN` is usually sufficient.

## Reviewing Pull Requests

1.  Users will submit Pull Requests (PRs) with their subdomain request JSON files in the `requests/` directory.
2.  The `pr_validator.yml` GitHub Action will automatically run on each PR.
    *   It will check the JSON format.
    *   It will check if the subdomain is already present in `requests/` or if a PR for it already exists.
    *   It will check for conflicts (e.g., trying to claim a subdomain that would conflict with an existing one).
    *   The bot will comment on the PR with the results of its checks.
3.  **If checks pass**: Review the request for appropriateness. If it's acceptable, merge the PR.
4.  **If checks fail**: The user will be instructed by the bot to fix their submission. Do not merge PRs that fail automated checks unless you have a specific reason to override.

## DNS Synchronization

-   Once a PR is merged into the main branch, the `dns_sync.yml` GitHub Action will trigger.
-   This action will scan the `requests/` directory for all valid JSON files.
-   It will then use the Cloudflare API to create/update the DNS records for each requested subdomain according to its JSON definition.
-   It should ideally keep a log or report of successful/failed operations.

## Manual Intervention

-   **Revoking a Subdomain**: To revoke a subdomain, delete its corresponding JSON file from the `requests/` directory and commit the change. The `dns_sync.yml` action should then detect this and remove the DNS records from Cloudflare. (This removal logic needs to be implemented in the `dns_sync.yml` script).
-   **Cloudflare Issues**: If there are issues with Cloudflare API communication, check the logs of the `dns_sync.yml` GitHub Action for error messages.

## Bot and Workflow Maintenance

-   The GitHub Actions workflows are defined in `.github/workflows/`.
-   The `pr_validator.yml` workflow handles PR checks.
-   The `dns_sync.yml` workflow handles Cloudflare DNS updates.
-   Scripts used by these workflows (e.g., for Cloudflare API interaction, validation logic) will be placed in the `scripts/` directory.
-   Regularly review and update the workflow files and scripts as needed, especially if Cloudflare API changes or new validation rules are introduced.
