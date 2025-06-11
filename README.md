# LibreDomains - Free Subdomain Distribution

This project provides a system for distributing free subdomains, managed entirely through GitHub Pull Requests and automated via GitHub Actions and the Cloudflare API.

## Overview

Users can request subdomains under pre-configured parent domains by submitting a JSON file via a Pull Request. A bot (GitHub Action) validates these requests. Upon approval and merge, another GitHub Action syncs the DNS records to Cloudflare.

## Features

-   **GitHub-native**: All management and requests happen within this GitHub repository.
-   **Automated Validation**: Pull Requests are automatically checked for format, conflicts, and adherence to rules.
-   **Cloudflare Integration**: DNS records are managed automatically using the Cloudflare API.
-   **Admin-configurable Domains**: Administrators can easily add new domains for distribution and enable/disable them.
-   **Flexible Record Types**: Supports common DNS record types (A, AAAA, CNAME, MX, TXT, etc.), excluding NS records.
-   **Cloudflare Proxy Option**: Users can choose to enable Cloudflare's proxy for supported record types.

## Getting Started

-   **Users**: Please see the [User Guide](./docs/USER_GUIDE.md) for instructions on how to request a subdomain.
-   **Administrators**: Please see the [Admin Guide](./docs/ADMIN_GUIDE.md) for setup and management instructions.
-   **Project Details**: For more information on the project architecture, see [Project Overview](./docs/README.md).

