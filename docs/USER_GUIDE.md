# User Guide

This guide explains how to request a free subdomain using the LibreDomains system.

## Prerequisites

-   A GitHub account.

## How to Request a Subdomain

1.  **Fork this Repository**: Click the "Fork" button at the top right of this page to create your own copy of this repository.

2.  **Choose a Domain**: Check the `domains/available_domains.json` file in the main repository to see which parent domains are currently enabled for subdomain registration.

3.  **Create a Request File**:
    *   In your forked repository, navigate to the `requests/` directory.
    *   Create a new JSON file. The filename should be your desired subdomain and the parent domain, separated by a dot, followed by `.json`. For example, if you want `myapp.ciao.su`, your filename should be `myapp.ciao.su.json`.
    *   The content of the JSON file should specify your desired DNS records. Here's an example for `myapp.ciao.su` pointing to an IP address:

        ```json
        {
          "owner": "your_github_username",
          "records": [
            {
              "type": "A",
              "value": "192.0.2.1",
              "proxied": true
            }
          ]
        }
        ```

    *   **Supported Record Types**: A, AAAA, CNAME, MX, TXT, SRV, CAA, etc. (NS records are not permitted).
    *   **`owner`**: Your GitHub username. This helps in tracking and communication.
    *   **`records`**: An array of DNS records.
        *   **`type`**: The DNS record type (e.g., "A", "CNAME", "MX").
        *   **`value`**: The value for the record (e.g., IP address for A/AAAA, hostname for CNAME, mail server for MX).
        *   **`proxied`** (Optional, default: `false`): Set to `true` to enable Cloudflare's proxy (orange cloud). This is only applicable for A, AAAA, and CNAME records.
        *   **`priority`** (Required for MX records): The priority of the MX record.
        *   **`data`** (Required for SRV records): An object containing `service`, `proto`, `name`, `priority`, `weight`, `port`, `target`.
        *   **`data`** (Required for CAA records): An object containing `flags`, `tag`, `value`.

4.  **Commit and Push**: Commit the new JSON file to your forked repository and push the changes.

5.  **Create a Pull Request (PR)**:
    *   Go back to the main LibreDomains repository on GitHub.
    *   You should see a prompt to create a Pull Request from your recently pushed branch. Click it.
    *   Provide a clear title and description for your PR (e.g., "Request subdomain myapp.ciao.su").
    *   Submit the Pull Request.

6.  **Automated Checks**: A bot will automatically check your PR for:
    *   Correct JSON format.
    *   Whether the requested subdomain is already taken or reserved.
    *   Compliance with any other defined rules.
    *   If there are issues, the bot will comment on your PR. You may need to fix the issues in your forked repository and push the changes again (your PR will update automatically).

7.  **Approval and Merge**: If all checks pass, a repository administrator will review your request. If approved, your PR will be merged.

8.  **DNS Propagation**: Once merged, another automated process will update the DNS records on Cloudflare. This may take a few minutes to propagate globally.

## Rules and Limitations

-   Do not request NS records.
-   Subdomain requests are subject to approval by administrators.
-   Abuse of the service may lead to your subdomain being revoked.
-   Specific parent domains might have additional rules; check the `domains/available_domains.json` file or announcements in the repository.

## Troubleshooting

-   **PR Check Fails**: Carefully read the bot's comments on your PR. Make the necessary corrections in your JSON file in your forked repository and push the changes.
-   **Subdomain Not Working**: DNS propagation can take time. If it's still not working after a reasonable period, double-check your record configuration or create an issue in the main repository.
