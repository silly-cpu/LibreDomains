const fs = require('fs');
const path = require('path');
const dns = require('dns').promises;
const CloudflareAPI = require('./cloudflare-api');

class HealthChecker {
  constructor() {
    this.cloudflare = new CloudflareAPI();
    this.domainsDir = path.join(__dirname, '../domains');
  }

  async checkAllRecords() {
    console.log('🏥 Starting DNS health check...\n');
    
    if (!fs.existsSync(this.domainsDir)) {
      console.log('❌ No domains directory found');
      return;
    }

    const domains = fs.readdirSync(this.domainsDir);
    let totalChecked = 0;
    let totalErrors = 0;

    for (const domain of domains) {
      const domainDir = path.join(this.domainsDir, domain);
      if (fs.statSync(domainDir).isDirectory()) {
        console.log(`🌐 Checking domain: ${domain}`);
        console.log('─'.repeat(50));
        
        const files = fs.readdirSync(domainDir);
        for (const file of files) {
          if (file.endsWith('.json')) {
            const subdomain = file.replace('.json', '');
            const result = await this.checkRecord(domain, subdomain);
            totalChecked++;
            if (!result.healthy) {
              totalErrors++;
            }
          }
        }
        console.log('');
      }
    }

    console.log('📊 Health Check Summary');
    console.log('='.repeat(30));
    console.log(`Total records checked: ${totalChecked}`);
    console.log(`Healthy records: ${totalChecked - totalErrors}`);
    console.log(`Unhealthy records: ${totalErrors}`);
    
    if (totalErrors > 0) {
      console.log(`\n⚠️  ${totalErrors} records need attention!`);
      process.exit(1);
    } else {
      console.log('\n✅ All records are healthy!');
    }
  }

  async checkRecord(domain, subdomain) {
    const filePath = path.join(this.domainsDir, domain, `${subdomain}.json`);
    const fullDomain = `${subdomain}.${domain}`;
    
    try {
      // Load local record
      const localRecord = JSON.parse(fs.readFileSync(filePath, 'utf8'));
      console.log(`  Checking ${fullDomain}...`);

      // Check Cloudflare record
      const cloudflareRecords = await this.cloudflare.getDNSRecords(domain, subdomain);
      
      if (cloudflareRecords.length === 0) {
        console.log(`    ❌ No DNS record found in Cloudflare`);
        return { healthy: false, error: 'Missing from Cloudflare' };
      }

      const cfRecord = cloudflareRecords[0];
      
      // Verify record matches
      if (cfRecord.type !== localRecord.record.type) {
        console.log(`    ❌ Record type mismatch: local=${localRecord.record.type}, cf=${cfRecord.type}`);
        return { healthy: false, error: 'Type mismatch' };
      }

      if (cfRecord.content !== localRecord.record.value) {
        console.log(`    ❌ Record value mismatch: local=${localRecord.record.value}, cf=${cfRecord.content}`);
        return { healthy: false, error: 'Value mismatch' };
      }

      // Check DNS resolution
      try {
        const resolved = await this.resolveDNS(fullDomain, localRecord.record.type);
        if (resolved) {
          console.log(`    ✅ Healthy (resolves to ${resolved})`);
        } else {
          console.log(`    ⚠️  Cloudflare OK, but not resolving yet (DNS propagation)`);
        }
      } catch (dnsError) {
        console.log(`    ⚠️  Cloudflare OK, DNS resolution failed: ${dnsError.message}`);
      }

      return { healthy: true };

    } catch (error) {
      console.log(`    ❌ Error checking ${fullDomain}: ${error.message}`);
      return { healthy: false, error: error.message };
    }
  }

  async resolveDNS(domain, recordType) {
    try {
      switch (recordType) {
        case 'A':
          const a = await dns.resolve4(domain);
          return a[0];
        case 'AAAA':
          const aaaa = await dns.resolve6(domain);
          return aaaa[0];
        case 'CNAME':
          const cname = await dns.resolveCname(domain);
          return cname[0];
        case 'MX':
          const mx = await dns.resolveMx(domain);
          return mx[0]?.exchange;
        case 'TXT':
          const txt = await dns.resolveTxt(domain);
          return txt[0]?.[0];
        default:
          return null;
      }
    } catch (error) {
      throw error;
    }
  }

  async checkSpecificDomain(domain) {
    console.log(`🏥 Checking specific domain: ${domain}\n`);
    
    const domainDir = path.join(this.domainsDir, domain);
    if (!fs.existsSync(domainDir)) {
      console.log(`❌ Domain directory not found: ${domain}`);
      return;
    }

    const files = fs.readdirSync(domainDir);
    let checked = 0;
    let errors = 0;

    for (const file of files) {
      if (file.endsWith('.json')) {
        const subdomain = file.replace('.json', '');
        const result = await this.checkRecord(domain, subdomain);
        checked++;
        if (!result.healthy) {
          errors++;
        }
      }
    }

    console.log(`\n📊 Results for ${domain}:`);
    console.log(`  Checked: ${checked}`);
    console.log(`  Healthy: ${checked - errors}`);
    console.log(`  Errors: ${errors}`);
  }
}

module.exports = HealthChecker;

// CLI usage
if (require.main === module) {
  const checker = new HealthChecker();
  const domain = process.argv[2];
  
  (async () => {
    try {
      if (domain) {
        await checker.checkSpecificDomain(domain);
      } else {
        await checker.checkAllRecords();
      }
    } catch (error) {
      console.error('Health check failed:', error.message);
      process.exit(1);
    }
  })();
}
