const fs = require('fs');
const path = require('path');
const Ajv = require('ajv');
const addFormats = require('ajv-formats');
const yaml = require('js-yaml');

class RequestValidator {
  constructor() {
    this.ajv = new Ajv();
    addFormats(this.ajv);
    this.schema = JSON.parse(fs.readFileSync(path.join(__dirname, '../config/schema.json'), 'utf8'));
    this.domainsConfig = yaml.load(fs.readFileSync(path.join(__dirname, '../config/domains.yml'), 'utf8'));
    this.validate = this.ajv.compile(this.schema);
  }

  validateRequest(requestData) {
    const errors = [];

    // 基本格式验证
    if (!this.validate(requestData)) {
      errors.push(...this.validate.errors.map(err => `Schema validation: ${err.instancePath} ${err.message}`));
    }

    // 域名启用状态检查
    const domainConfig = this.domainsConfig.domains[requestData.domain];
    if (!domainConfig || !domainConfig.enabled) {
      errors.push(`Domain ${requestData.domain} is not available for registration`);
    }

    // 记录类型检查
    if (domainConfig && !domainConfig.allowed_record_types.includes(requestData.record.type)) {
      errors.push(`Record type ${requestData.record.type} is not allowed for domain ${requestData.domain}`);
    }

    // 子域名格式检查
    if (requestData.subdomain) {
      if (requestData.subdomain.length > 63) {
        errors.push('Subdomain too long (max 63 characters)');
      }
      if (!/^[a-z0-9]([a-z0-9-]*[a-z0-9])?$/.test(requestData.subdomain)) {
        errors.push('Invalid subdomain format');
      }
      if (requestData.subdomain.includes('--')) {
        errors.push('Subdomain cannot contain consecutive hyphens');
      }
    }

    // 记录值验证
    this.validateRecordValue(requestData.record, errors);

    // 检查子域名是否已存在
    if (this.isSubdomainTaken(requestData.domain, requestData.subdomain)) {
      errors.push(`Subdomain ${requestData.subdomain}.${requestData.domain} is already taken`);
    }

    return {
      valid: errors.length === 0,
      errors: errors
    };
  }

  validateRecordValue(record, errors) {
    switch (record.type) {
      case 'A':
        if (!/^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/.test(record.value)) {
          errors.push('Invalid IPv4 address format');
        } else if (record.proxied && this.isPrivateIP(record.value)) {
          errors.push('Private IP addresses cannot be used with Cloudflare proxy (proxied: true). Either use a public IP or set proxied to false');
        }
        break;
      case 'AAAA':
        if (!/^(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$|^::1$|^::$/.test(record.value)) {
          errors.push('Invalid IPv6 address format');
        } else if (record.proxied && this.isPrivateIPv6(record.value)) {
          errors.push('Private IPv6 addresses cannot be used with Cloudflare proxy (proxied: true). Either use a public IP or set proxied to false');
        }
        break;
      case 'CNAME':
        if (!/^[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?)*\.?$/.test(record.value)) {
          errors.push('Invalid CNAME format');
        }
        break;
      case 'MX':
        if (!/^[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?)*\.?$/.test(record.value)) {
          errors.push('Invalid MX record format');
        }
        if (!record.priority || record.priority < 0 || record.priority > 65535) {
          errors.push('MX record requires valid priority (0-65535)');
        }
        break;
    }
  }

  isPrivateIP(ip) {
    const parts = ip.split('.').map(Number);
    return (
      // 10.0.0.0/8
      parts[0] === 10 ||
      // 172.16.0.0/12
      (parts[0] === 172 && parts[1] >= 16 && parts[1] <= 31) ||
      // 192.168.0.0/16
      (parts[0] === 192 && parts[1] === 168) ||
      // 127.0.0.0/8 (localhost)
      parts[0] === 127
    );
  }

  isPrivateIPv6(ip) {
    // Simplified check for common private IPv6 ranges
    return (
      ip.startsWith('::1') || // localhost
      ip.startsWith('fc') || // unique local
      ip.startsWith('fd') || // unique local
      ip.startsWith('fe80:') // link-local
    );
  }

  isSubdomainTaken(domain, subdomain) {
    const domainsDir = path.join(__dirname, '../domains', domain);
    if (!fs.existsSync(domainsDir)) {
      return false;
    }
    
    const subdomainFile = path.join(domainsDir, `${subdomain}.json`);
    return fs.existsSync(subdomainFile);
  }

  getUserSubdomainCount(username) {
    let count = 0;
    const domainsDir = path.join(__dirname, '../domains');
    
    if (!fs.existsSync(domainsDir)) {
      return count;
    }

    const domains = fs.readdirSync(domainsDir);
    for (const domain of domains) {
      const domainDir = path.join(domainsDir, domain);
      if (fs.statSync(domainDir).isDirectory()) {
        const files = fs.readdirSync(domainDir);
        for (const file of files) {
          if (file.endsWith('.json')) {
            const filePath = path.join(domainDir, file);
            const data = JSON.parse(fs.readFileSync(filePath, 'utf8'));
            if (data.owner && data.owner.username === username) {
              count++;
            }
          }
        }
      }
    }
    return count;
  }
}

module.exports = RequestValidator;

// CLI usage
if (require.main === module) {
  const validator = new RequestValidator();
  const requestFile = process.argv[2];
  
  if (!requestFile) {
    console.error('Usage: node validate-request.js <request.json>');
    process.exit(1);
  }

  try {
    const requestData = JSON.parse(fs.readFileSync(requestFile, 'utf8'));
    const result = validator.validateRequest(requestData);
    
    if (result.valid) {
      console.log('✅ Request is valid');
      process.exit(0);
    } else {
      console.log('❌ Request validation failed:');
      result.errors.forEach(error => console.log(`  - ${error}`));
      process.exit(1);
    }
  } catch (error) {
    console.error('Error:', error.message);
    process.exit(1);
  }
}
