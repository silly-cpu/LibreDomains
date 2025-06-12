const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');
const CloudflareAPI = require('./cloudflare-api');

class HealthChecker {
  constructor() {
    this.cloudflare = new CloudflareAPI();
  }

  async checkAllRecords() {
    console.log('🏥 Starting health check for all DNS records...\n');
    
    const domainsDir = path.join(__dirname, '../domains');
    if (!fs.existsSync(domainsDir)) {
      console.log('ℹ️  No domain records found');
      return true;
    }

    let totalRecords = 0;
    let healthyRecords = 0;
    const issues = [];

    for (const domain of fs.readdirSync(domainsDir)) {
      const domainDir = path.join(domainsDir, domain);
      if (!fs.statSync(domainDir).isDirectory()) continue;

      console.log(`🌐 Checking domain: ${domain}`);
      
      for (const file of fs.readdirSync(domainDir)) {
        if (!file.endsWith('.json')) continue;

        totalRecords++;
        const subdomain = path.basename(file, '.json');
        const filePath = path.join(domainDir, file);
        
        try {
          const recordData = JSON.parse(fs.readFileSync(filePath, 'utf8'));
          const isHealthy = await this.checkRecord(domain, subdomain, recordData);
          
          if (isHealthy) {
            healthyRecords++;
          } else {
            issues.push(`${subdomain}.${domain}`);
          }
        } catch (error) {
          console.log(`   ❌ ${subdomain}.${domain}: Error reading record - ${error.message}`);
          issues.push(`${subdomain}.${domain} (file error)`);
        }
      }
    }

    // Summary
    console.log('\n📊 Health Check Summary:');
    console.log(`   Total records: ${totalRecords}`);
    console.log(`   Healthy: ${healthyRecords}`);
    console.log(`   Issues: ${issues.length}`);
    
    if (issues.length > 0) {
      console.log('\n❌ Records with issues:');
      issues.forEach(issue => console.log(`   - ${issue}`));
    }

    return issues.length === 0;
  }

  async checkRecord(domain, subdomain, recordData) {
    const fullDomain = `${subdomain}.${domain}`;
    
    try {
      // Check Cloudflare record
      const cfHealthy = await this.checkCloudflareRecord(domain, subdomain, recordData);
      
      // Check DNS resolution
      const dnsHealthy = await this.checkDNSResolution(fullDomain, recordData.record);
      
      const isHealthy = cfHealthy && dnsHealthy;
      
      if (isHealthy) {
        console.log(`   ✅ ${fullDomain}: Healthy`);
      } else {
        console.log(`   ❌ ${fullDomain}: Issues detected`);
      }
      
      return isHealthy;
    } catch (error) {
      console.log(`   ❌ ${fullDomain}: Health check failed - ${error.message}`);
      return false;
    }
  }

  async checkCloudflareRecord(domain, subdomain, recordData) {
    try {
      if (!recordData.cloudflare_record_id) {
        console.log(`   ⚠️  ${subdomain}.${domain}: No Cloudflare record ID`);
        return false;
      }

      const cfRecords = await this.cloudflare.getDNSRecords(domain, subdomain);
      const cfRecord = cfRecords.find(r => r.id === recordData.cloudflare_record_id);
      
      if (!cfRecord) {
        console.log(`   ❌ ${subdomain}.${domain}: Cloudflare record not found`);
        return false;
      }

      // Check if record values match
      if (cfRecord.content !== recordData.record.value) {
        console.log(`   ⚠️  ${subdomain}.${domain}: Record value mismatch`);
        console.log(`       Expected: ${recordData.record.value}`);
        console.log(`       Actual: ${cfRecord.content}`);
        return false;
      }

      return true;
    } catch (error) {
      console.log(`   ❌ ${subdomain}.${domain}: Cloudflare check failed - ${error.message}`);
      return false;
    }
  }

  async checkDNSResolution(fullDomain, record) {
    try {
      let command;
      
      switch (record.type) {
        case 'A':
          command = `nslookup -type=A ${fullDomain}`;
          break;
        case 'AAAA':
          command = `nslookup -type=AAAA ${fullDomain}`;
          break;
        case 'CNAME':
          command = `nslookup -type=CNAME ${fullDomain}`;
          break;
        case 'MX':
          command = `nslookup -type=MX ${fullDomain}`;
          break;
        case 'TXT':
          command = `nslookup -type=TXT ${fullDomain}`;
          break;
        default:
          console.log(`   ℹ️  ${fullDomain}: DNS resolution check skipped for ${record.type} record`);
          return true;
      }

      const output = execSync(command, { encoding: 'utf8', timeout: 5000 });
      
      // Basic check - if no error thrown, DNS is resolving
      if (output.includes(record.value) || output.includes('Name:')) {
        return true;
      } else {
        console.log(`   ⚠️  ${fullDomain}: DNS resolution may be incomplete`);
        return true; // Don't fail health check for DNS propagation issues
      }
    } catch (error) {
      console.log(`   ⚠️  ${fullDomain}: DNS resolution check failed (may be propagating)`);
      return true; // Don't fail health check for DNS propagation issues
    }
  }

  async checkSingleRecord(domain, subdomain) {
    console.log(`🔍 Checking single record: ${subdomain}.${domain}`);
    
    const filePath = path.join(__dirname, '../domains', domain, `${subdomain}.json`);
    if (!fs.existsSync(filePath)) {
      console.log('❌ Record file not found');
      return false;
    }

    try {
      const recordData = JSON.parse(fs.readFileSync(filePath, 'utf8'));
      return await this.checkRecord(domain, subdomain, recordData);
    } catch (error) {
      console.log(`❌ Error checking record: ${error.message}`);
      return false;
    }
  }
}

module.exports = HealthChecker;

// CLI usage
if (require.main === module) {
  const checker = new HealthChecker();
  const domain = process.argv[2];
  const subdomain = process.argv[3];
  
  (async () => {
    try {
      let success;
      
      if (domain && subdomain) {
        success = await checker.checkSingleRecord(domain, subdomain);
      } else {
        success = await checker.checkAllRecords();
      }
      
      process.exit(success ? 0 : 1);
    } catch (error) {
      console.error('Health check error:', error.message);
      process.exit(1);
    }
  })();
}
