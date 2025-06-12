# LibreDomains 管理员指南

本指南面向项目维护者和管理员，介绍如何管理和维护 LibreDomains 服务。

## 🔧 系统架构

### 组件概览
- **GitHub Repository**: 存储配置和请求
- **GitHub Actions**: 自动化验证和部署
- **Cloudflare API**: DNS 记录管理
- **Python Scripts**: 核心业务逻辑

### 目录结构
```
LibreDomains-beta/
├── .github/workflows/     # GitHub Actions 工作流
├── config/               # 配置文件
│   ├── domains.yml       # 域名配置
│   └── schema.json       # 请求格式模式
├── docs/                 # 文档
├── domains/              # 已部署的记录
│   ├── ciao.su/
│   └── ciallo.de/
├── requests/             # 用户请求文件
├── scripts/              # Python 脚本
└── tests/                # 测试文件
```

## ⚙️ 环境配置

### GitHub Secrets
在仓库设置中配置以下 Secrets：

```bash
CLOUDFLARE_API_TOKEN=your_cloudflare_api_token
```

### Cloudflare API Token
需要以下权限：
- Zone:Zone:Read
- Zone:DNS:Edit
   
   **Token Configuration Steps:**
   1. Click "Create Token"
   2. Select "Custom token" template
   3. Add permissions:
      - **Zone** | **Zone** | **Read**
      - **Zone** | **DNS** | **Edit**
   4. Zone Resources:
      - **Include** | **All zones** (recommended)
      - Or **Include** | **Specific zone** for each domain you manage
   5. Optional security settings:
      - Client IP Address Filtering (add your server IPs)
      - TTL (token expiration date)
   6. Click "Continue to summary" → "Create Token"
   7. Copy the token immediately (it won't be shown again)

   **⚠️ Security Notes:**
   - Store the token securely in GitHub Secrets
   - Never commit the token to your repository
   - Consider setting an expiration date
   - Monitor token usage in Cloudflare dashboard

3. **Validate Token**
   Test your token before using it:
   ```bash
   node scripts/validate-cloudflare-token.js YOUR_TOKEN
   ```
   
   Expected output for valid token:
   ```
   ✅ Token is valid
   📊 Token info: {
     id: 'abc123...',
     status: 'active',
     permissions: ['zone:read', 'dns_records:edit'],
     expires_on: 'Never',
     hasAllPermissions: true
   }
   ```

4. **Configure Domains**
   Edit `config/domains.yml` with your domain configurations and Zone IDs

### 2. GitHub Repository Setup

1. **Fork/Clone Repository**
   ```bash
   git clone https://github.com/your-username/LibreDomains-beta.git
   cd LibreDomains-beta
   ```

2. **Install Dependencies**
   ```bash
   npm install
   ```

3. **Configure Secrets**
   - Go to Repository Settings → Secrets and Variables → Actions
   - Add secret: `CLOUDFLARE_API_TOKEN`

4. **Enable Actions**
   - Go to Actions tab
   - Enable GitHub Actions if disabled

## 🎛️ Domain Management

### Adding a New Domain

1. **Add to Cloudflare**
   - Add domain to your Cloudflare account
   - Update nameservers
   - Get Zone ID from domain overview

2. **Update Configuration**
   Edit `config/domains.yml`:
   ```yaml
   domains:
     new-domain.com:
       enabled: true
       cloudflare_zone_id: "your_zone_id"
       description: "New free subdomain service"
       restrictions:
         - "No adult content"
         - "No illegal activities"
       allowed_record_types:
         - "A"
         - "AAAA"
         - "CNAME"
         - "MX"
         - "TXT"
         - "SRV"
       max_records_per_subdomain: 5
   ```

3. **Update Schema**
   Edit `config/schema.json` to include the new domain in the enum.

### Disabling a Domain

```yaml
domains:
  example.com:
    enabled: false  # Disable new registrations
    # ... other config remains
```

### Managing Restrictions

```yaml
domains:
  example.com:
    enabled: true
    restrictions:
      - "No adult content"
      - "No illegal activities"
      - "No spam or phishing"
      - "Must be related to development"
      - "Commercial use requires approval"
```

## 👥 User Management

### User Limits Configuration

Edit `config/domains.yml`:
```yaml
settings:
  auto_approve: false
  require_github_verification: true
  min_account_age_days: 30
  max_subdomains_per_user: 3
```

### Checking User Subdomains

```bash
# Check how many subdomains a user has
node scripts/check-github-user.js username
```

### Blocking Users

Create a blocklist file `config/blocked_users.json`:
```json
{
  "blocked_users": [
    "spammer1",
    "abuser2"
  ],
  "blocked_emails": [
    "spam@example.com"
  ]
}
```

## 🔍 Monitoring and Maintenance

### Checking Domain Status

```bash
# Validate all existing domains
node scripts/check-domains.js
```

### Manual DNS Operations

```bash
# Deploy a specific request
node scripts/deploy-dns.js deploy requests/example.json

# Update existing record
node scripts/deploy-dns.js update requests/example.json

# Delete a subdomain
node scripts/deploy-dns.js delete requests/example.json
```

### Backup Management

```bash
# Backup all domain records
node scripts/backup-domains.js

# Restore from backup
node scripts/restore-domains.js backup-20231201.json
```

## 🚨 Handling Abuse

### Identifying Abuse

Signs of potential abuse:
- Multiple requests from same IP/user
- Suspicious subdomain names
- Malicious content hosting
- Spam or phishing attempts

### Removing Abusive Subdomains

1. **Immediate Action**
   ```bash
   # Delete the subdomain
   node scripts/deploy-dns.js delete domains/example.com/abusive.json
   ```

2. **Add to Blocklist**
   ```json
   {
     "blocked_users": ["abusive-user"],
     "blocked_subdomains": ["abusive", "spam", "phishing"]
   }
   ```

3. **Report to Cloudflare**
   - Use Cloudflare Security Center
   - Report abuse if needed

## 📊 Analytics and Reporting

### Usage Statistics

```bash
# Generate usage report
node scripts/generate-stats.js

# Example output:
# Total subdomains: 1,234
# Active domains: 2
# Top users: user1 (3), user2 (2)
# Record types: A (45%), CNAME (30%), AAAA (15%), others (10%)
```

### DNS Health Check

```bash
# Check all DNS records
node scripts/health-check.js

# Check specific domain
node scripts/health-check.js ciao.su
```

## 🔧 Troubleshooting

### Common Issues

**GitHub Actions Failing**
- Check API token validity
- Verify Cloudflare permissions
- Review action logs

**DNS Records Not Updating**
- Verify Zone ID is correct
- Check API token permissions
- Confirm domain is active in Cloudflare

**Validation Errors**
- Check schema.json syntax
- Verify domains.yml format
- Test with sample request

### Debug Commands

```bash
# Test API connectivity
node scripts/test-cloudflare.js

# Validate configuration
node scripts/validate-config.js

# Check specific request
node scripts/validate-request.js requests/test.json
```

## 🔒 Security Best Practices

### API Token Security
- Use minimal required permissions
- Rotate tokens regularly
- Monitor usage in Cloudflare dashboard

### Repository Security
- Require PR reviews
- Enable branch protection
- Use dependabot for updates

### DNS Security
- Enable DNSSEC where possible
- Monitor for suspicious records
- Regular security audits

## 📈 Scaling Considerations

### Performance Optimization
- Use Cloudflare caching
- Implement rate limiting
- Monitor API usage

### Infrastructure Scaling
- Consider multiple Cloudflare accounts
- Implement load balancing
- Use CDN for static content

## 🚀 Advanced Configuration

### Custom Validation Rules

Create `scripts/custom-validator.js`:
```javascript
class CustomValidator {
  validateSubdomain(subdomain, domain) {
    // Custom validation logic
    if (domain === 'special.com' && subdomain.length < 5) {
      return { valid: false, error: 'Minimum 5 characters for special.com' };
    }
    return { valid: true };
  }
}
```

### Webhook Integration

```javascript
// scripts/webhook-handler.js
const express = require('express');
const app = express();

app.post('/webhook/cloudflare', (req, res) => {
  // Handle Cloudflare webhooks
  console.log('Cloudflare webhook received:', req.body);
  res.status(200).send('OK');
});
```

### Automated Backups

```yaml
# .github/workflows/backup.yml
name: Daily Backup
on:
  schedule:
    - cron: '0 2 * * *'  # Run at 2 AM daily

jobs:
  backup:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: node scripts/backup-domains.js
      - name: Upload to S3
        # ... backup to cloud storage
```

## 📞 Support and Maintenance

### Regular Tasks
- [ ] Weekly: Review new requests
- [ ] Weekly: Check for abuse
- [ ] Monthly: Update dependencies
- [ ] Monthly: Review analytics
- [ ] Quarterly: Security audit
- [ ] Yearly: Renew domains/certificates

### Emergency Procedures
1. **Service Outage**
   - Check Cloudflare status
   - Verify API connectivity
   - Review GitHub Actions

2. **Abuse Report**
   - Investigate immediately
   - Take down if confirmed
   - Update blocklists

3. **API Limits Hit**
   - Monitor Cloudflare usage
   - Implement rate limiting
   - Consider enterprise plan

---

For technical support, contact the development team or create an issue in the repository.
