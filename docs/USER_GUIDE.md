# User Guide

This guide will help you request a free subdomain from LibreDomains.

## 📋 Prerequisites

Before requesting a subdomain, make sure you have:

- A GitHub account that is at least 30 days old
- A verified email address on GitHub
- A valid target for your subdomain (IP address, domain, etc.)

## 🚀 How to Request a Subdomain

### Step 1: Fork the Repository

1. Go to the [LibreDomains-beta repository](https://github.com/your-username/LibreDomains-beta)
2. Click the "Fork" button in the top right corner
3. This creates a copy of the repository in your account

### Step 2: Create Your Request File

1. In your forked repository, navigate to the `requests/` directory
2. Create a new file named `your-subdomain.json` (replace with your desired subdomain)
3. Use the following template:

```json
{
  "domain": "ciao.su",
  "subdomain": "your-subdomain",
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

### Step 3: Customize Your Request

#### Available Domains
- `ciao.su` - Available for registration
- `ciallo.de` - Coming soon

#### Record Types

**A Record (IPv4)**
```json
{
  "type": "A",
  "value": "192.168.1.1",
  "ttl": 3600,
  "proxied": false
}
```

**AAAA Record (IPv6)**
```json
{
  "type": "AAAA",
  "value": "2001:db8::1",
  "ttl": 3600,
  "proxied": false
}
```

**CNAME Record**
```json
{
  "type": "CNAME",
  "value": "example.com",
  "ttl": 3600,
  "proxied": false
}
```

**MX Record**
```json
{
  "type": "MX",
  "value": "mail.example.com",
  "priority": 10,
  "ttl": 3600,
  "proxied": false
}
```

**TXT Record**
```json
{
  "type": "TXT",
  "value": "v=spf1 include:_spf.google.com ~all",
  "ttl": 3600
}
```

#### Cloudflare Proxy

Set `"proxied": true` to enable Cloudflare's proxy features:
- DDoS protection
- SSL/TLS encryption
- Caching
- Bot mitigation

⚠️ **Important Proxy Limitations**:
- Only HTTP (port 80) and HTTPS (port 443) traffic can be proxied
- **DO NOT** enable proxy for:
  - Mail servers (MX records)
  - FTP servers
  - SSH servers
  - Game servers
  - Any non-HTTP services
- Records pointing to private IP addresses (RFC 1918) cannot be proxied
- If you try to proxy a private IP, the system will automatically disable proxy

💡 **When to use proxy**:
- ✅ Web applications and websites
- ✅ APIs serving HTTP/HTTPS
- ✅ Public-facing web services
- ❌ Backend services on private networks
- ❌ Email or other protocol servers

### Step 4: Submit Pull Request

1. Commit your changes with a descriptive message
2. Go to the original repository
3. Click "New Pull Request"
4. Select your forked repository and branch
5. Add a title like "Add subdomain: your-subdomain.ciao.su"
6. Click "Create Pull Request"

### Step 5: Wait for Validation

Our automated system will:
- Validate your request format
- Check if the subdomain is available
- Verify your GitHub account eligibility
- Comment on your PR with results

### Step 6: Approval and Deployment

If everything is valid:
- A maintainer will review and merge your PR
- DNS records will be automatically created
- Your subdomain will be live within minutes!

## 🔧 Updating Your Subdomain

To update your subdomain:

1. Edit your JSON file in the `requests/` directory
2. Change the record details as needed
3. Submit a new Pull Request
4. The system will update your DNS record automatically

## ❌ Deleting Your Subdomain

To delete your subdomain:

1. Delete your JSON file from the `requests/` directory
2. Submit a Pull Request
3. The DNS record will be removed automatically

## 📏 Rules and Limitations

### Subdomain Rules
- 1-63 characters long
- Only letters, numbers, and hyphens
- Cannot start or end with hyphen
- Cannot contain consecutive hyphens
- Must be unique across the domain

### Account Requirements
- GitHub account must be at least 30 days old
- Must have a verified email address
- Maximum 3 subdomains per user

### Content Restrictions
- No adult content
- No illegal activities
- No spam or phishing
- No malware or harmful content

## ❓ Troubleshooting

### Common Issues

**"Subdomain already taken"**
- Choose a different subdomain name
- Check if someone else is using it

**"Invalid subdomain format"**
- Use only letters, numbers, and hyphens
- Don't start or end with hyphen
- Keep it under 63 characters

**"GitHub account too new"**
- Wait until your account is 30 days old
- This helps prevent abuse

**"Maximum subdomains reached"**
- You can only have 3 subdomains
- Delete an existing one to request a new one

### Getting Help

If you need help:
1. Check this guide first
2. Search existing [Issues](https://github.com/your-username/LibreDomains-beta/issues)
3. Create a new issue with details
4. Join our [Discussions](https://github.com/your-username/LibreDomains-beta/discussions)

## 🎯 Examples

### Personal Website
```json
{
  "domain": "ciao.su",
  "subdomain": "john",
  "owner": {
    "username": "johnsmith",
    "email": "john@example.com"
  },
  "record": {
    "type": "CNAME",
    "value": "johnsmith.github.io",
    "proxied": true
  },
  "description": "John's personal website"
}
```

### Email Server
```json
{
  "domain": "ciao.su",
  "subdomain": "mail",
  "owner": {
    "username": "company",
    "email": "admin@company.com"
  },
  "record": {
    "type": "A",
    "value": "203.0.113.1",
    "proxied": false
  },
  "description": "Company mail server"
}
```

### API Service
```json
{
  "domain": "ciao.su",
  "subdomain": "api",
  "owner": {
    "username": "developer",
    "email": "dev@startup.com"
  },
  "record": {
    "type": "A",
    "value": "198.51.100.1",
    "proxied": true
  },
  "description": "REST API for mobile app"
}
```

---

Happy subdomaining! 🎉
