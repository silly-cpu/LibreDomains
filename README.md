# LibreDomains Beta

Free subdomain distribution service powered by GitHub and Cloudflare.

## 🌟 Features

- **Free subdomains** for multiple domains
- **Automated validation** and deployment
- **Cloudflare integration** with proxy support
- **Multiple DNS record types** (A, AAAA, CNAME, MX, TXT, SRV)
- **GitHub-based management** - no servers needed
- **Anti-abuse protection** with user verification

## 📋 Available Domains

| Domain | Status | Description |
|--------|--------|-------------|
| `ciao.su` | ✅ Available | Free subdomain service |
| `ciallo.de` | ❌ Coming Soon | Currently not accepting applications |

## 🚀 Quick Start

### For Users

1. **Fork this repository**
2. **Create your request file** in `requests/` directory
3. **Submit a Pull Request**
4. **Wait for approval** and automatic deployment

### Example Requests

Check out these example request files in the `requests/` directory:

- **Personal Website**: [`example-personal-website.json`](requests/example-personal-website.json) - GitHub Pages site using CNAME
- **API Service**: [`example-api-service.json`](requests/example-api-service.json) - REST API using A record
- **Mail Server**: [`example-mail-server.json`](requests/example-mail-server.json) - Email server using MX record
- **IPv6 Website**: [`example-ipv6-website.json`](requests/example-ipv6-website.json) - IPv6 site using AAAA record

### Basic Request Template

Create a file `requests/your-subdomain.json`:

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
  "description": "My personal website"
}
```

### Supported Record Types

- **A**: IPv4 address
- **AAAA**: IPv6 address  
- **CNAME**: Canonical name
- **MX**: Mail exchange (requires priority)
- **TXT**: Text record
- **SRV**: Service record

## 📖 Documentation

- [User Guide](docs/USER_GUIDE.md) - How to request subdomains
- [Admin Guide](docs/ADMIN_GUIDE.md) - How to manage the service
- [Contributing Guide](CONTRIBUTING.md) - How to contribute to the project

## 🛡️ Rules and Restrictions

- GitHub account must be at least 30 days old
- Maximum 3 subdomains per user
- No adult content, illegal activities, or spam
- Subdomain must be 1-63 characters, alphanumeric and hyphens only
- Cannot start or end with hyphen

## 🛠️ Development

### Setup

```bash
git clone https://github.com/your-username/LibreDomains-beta.git
cd LibreDomains-beta
npm install
```

### Scripts

```bash
# Validate a request
npm run validate requests/example-personal-website.json

# Check GitHub user
npm run check-user username

# Generate statistics
node scripts/generate-stats.js
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md).

Types of contributions:
- 🐛 Bug reports and fixes
- ✨ New features
- 📚 Documentation improvements
- 🎨 UI/UX improvements

## 📊 Statistics

Generate current usage statistics:

```bash
node scripts/generate-stats.js
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Cloudflare](https://cloudflare.com) for DNS services
- [GitHub Actions](https://github.com/features/actions) for automation
- Inspired by [is-a.dev](https://github.com/is-a-dev/register) and [js.org](https://github.com/js-org/js.org)

## 📞 Support

- [Issues](https://github.com/your-username/LibreDomains-beta/issues) - Report bugs or request features
- [Discussions](https://github.com/your-username/LibreDomains-beta/discussions) - Community support

---

Made with ❤️ by the LibreDomains team
