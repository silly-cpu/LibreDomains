# LibreDomains User Guide

This guide will help you request and manage your free subdomains.

## 🚀 Quick Start

### Step 1: Fork the Repository

1. Go to [LibreDomains-beta](https://github.com/bestZwei/LibreDomains-beta)
2. Click the **Fork** button in the top right
3. Clone your fork locally

### Step 2: Create Your Request

1. Create a new file in the `requests/` directory
2. Name it `your-subdomain-name.json`
3. Use the template below

### Step 3: Submit Pull Request

1. Commit your request file
2. Push to your fork
3. Create a Pull Request to the main repository

## 📝 Request Template

```json
{
  "domain": "ciao.su",
  "subdomain": "mysite",
  "owner": {
    "username": "your-github-username",
    "email": "your-email@example.com"
  },
  "record": {
    "type": "A",
    "value": "192.168.1.1",
    "ttl": 3600,
    "proxied": false
  },
  "description": "Brief description of your subdomain usage"
}
```

## 🎯 Record Types

### A Record (IPv4)
```json
"record": {
  "type": "A",
  "value": "203.0.113.10",
  "ttl": 3600,
  "proxied": true
}
```

### AAAA Record (IPv6)
```json
"record": {
  "type": "AAAA",
  "value": "2001:db8::1",
  "ttl": 3600,
  "proxied": false
}
```

### CNAME Record
```json
"record": {
  "type": "CNAME",
  "value": "username.github.io",
  "ttl": 3600,
  "proxied": false
}
```

### MX Record
```json
"record": {
  "type": "MX",
  "value": "mail.example.com",
  "priority": 10,
  "ttl": 3600,
  "proxied": false
}
```

### TXT Record
```json
"record": {
  "type": "TXT",
  "value": "v=spf1 include:_spf.google.com ~all",
  "ttl": 3600,
  "proxied": false
}
```

## 🛡️ Rules and Requirements

### GitHub Account Requirements
- Account must be at least **30 days old**
- Must have a verified email address
- Maximum **3 subdomains** per user

### Subdomain Requirements
- 1-63 characters long
- Only letters, numbers, and hyphens
- Cannot start or end with hyphen
- Must be unique across the domain

### Content Policy
- ✅ Personal websites and portfolios
- ✅ Open source projects
- ✅ Educational content
- ✅ Non-commercial APIs
- ❌ Adult content
- ❌ Illegal activities
- ❌ Spam or phishing
- ❌ Commercial services

## 🔧 Common Use Cases

### GitHub Pages Website
Perfect for personal portfolios and project documentation.

```json
{
  "domain": "ciao.su",
  "subdomain": "portfolio",
  "owner": {
    "username": "johndoe",
    "email": "john@example.com"
  },
  "record": {
    "type": "CNAME",
    "value": "johndoe.github.io",
    "ttl": 3600,
    "proxied": false
  },
  "description": "Personal portfolio website showcasing my development projects"
}
```

### API Endpoint
For hosting APIs and web services.

```json
{
  "domain": "ciao.su",
  "subdomain": "api",
  "owner": {
    "username": "developer",
    "email": "dev@example.com"
  },
  "record": {
    "type": "A",
    "value": "203.0.113.100",
    "ttl": 3600,
    "proxied": true
  },
  "description": "REST API for my mobile application with user management"
}
```

## ⚡ Tips and Best Practices

### Choosing Record Types
- **A/AAAA**: When you have a direct IP address
- **CNAME**: When pointing to another domain (like GitHub Pages)
- **MX**: For email services
- **TXT**: For verification and configuration

### TTL Settings
- **300-600**: For testing or frequently changing records
- **3600** (default): Good balance for most use cases
- **7200-86400**: For stable, rarely changing records

### Cloudflare Proxy
- **Enable** (`proxied: true`) for:
  - DDoS protection
  - Better performance (CDN)
  - SSL termination
- **Disable** (`proxied: false`) for:
  - Private IP addresses
  - Non-web services
  - Direct DNS resolution needed

## 🚨 Troubleshooting

### Request Rejected
- Check if subdomain is already taken
- Verify your GitHub account meets requirements
- Ensure request follows the schema

### DNS Not Resolving
- Wait 24-48 hours for global DNS propagation
- Check if you're using the correct record type
- Verify your target server is accessible

### Record Update Needed
- Create a new request file with updated information
- The system will automatically update existing records

## 📞 Getting Help

- **Issues**: Report bugs or problems
- **Discussions**: Ask questions and get community help
- **Email**: Contact maintainers for urgent issues

## 🔄 Updating Your Records

To update an existing subdomain:

1. Modify your original request file
2. Update the values you want to change
3. Submit a new Pull Request
4. The system will automatically update the DNS record

## 🗑️ Removing Your Subdomain

To remove your subdomain:

1. Delete your request file from the `requests/` directory
2. Submit a Pull Request
3. The DNS record will be automatically removed

---

**Need more help?** Check our [FAQ](FAQ.md) or [create an issue](https://github.com/bestZwei/LibreDomains-beta/issues/new).
