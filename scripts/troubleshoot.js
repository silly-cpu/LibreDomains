const fs = require('fs');
const path = require('path');
const CloudflareAPI = require('./cloudflare-api');
const yaml = require('js-yaml');

class Troubleshooter {
  constructor() {
    this.domainsConfig = yaml.load(fs.readFileSync(path.join(__dirname, '../config/domains.yml'), 'utf8'));
  }

  async diagnose() {
    console.log('🔍 LibreDomains Troubleshooting\n');
    
    // Check 1: Environment variables
    console.log('1️⃣ Checking environment variables...');
    const apiToken = process.env.CLOUDFLARE_API_TOKEN;
    if (!apiToken) {
      console.log('   ❌ CLOUDFLARE_API_TOKEN not set');
      return;
    } else {
      console.log('   ✅ CLOUDFLARE_API_TOKEN is set');
    }

    // Check 2: Cloudflare API connectivity
    console.log('\n2️⃣ Testing Cloudflare API connectivity...');
    try {
      const cloudflare = new CloudflareAPI();
      
      for (const [domain, config] of Object.entries(this.domainsConfig.domains)) {
        if (config.enabled) {
          console.log(`   Testing ${domain}...`);
          const records = await cloudflare.getDNSRecords(domain);
          console.log(`   ✅ ${domain}: ${records.length} records found`);
        }
      }
    } catch (error) {
      console.log(`   ❌ API Error: ${error.message}`);
      return;
    }

    // Check 3: Domain configuration
    console.log('\n3️⃣ Checking domain configuration...');
    for (const [domain, config] of Object.entries(this.domainsConfig.domains)) {
      console.log(`   Domain: ${domain}`);
      console.log(`     Enabled: ${config.enabled ? '✅' : '❌'}`);
      console.log(`     Zone ID: ${config.cloudflare_zone_id ? '✅' : '❌'}`);
      console.log(`     Allowed types: ${config.allowed_record_types.join(', ')}`);
    }

    // Check 4: Local domain files vs Cloudflare
    console.log('\n4️⃣ Checking sync between local files and Cloudflare...');
    await this.checkSync();

    // Check 5: Recent deployment logs
    console.log('\n5️⃣ Checking recent GitHub Actions...');
    console.log('   💡 Check: https://github.com/your-repo/actions');
    console.log('   Look for failed deploy-dns.yml workflows');

    console.log('\n✅ Troubleshooting complete!');
  }

  async checkSync() {
    const domainsDir = path.join(__dirname, '../domains');
    if (!fs.existsSync(domainsDir)) {
      console.log('   ❌ No domains directory found');
      return;
    }

    const cloudflare = new CloudflareAPI();
    const domains = fs.readdirSync(domainsDir);

    for (const domain of domains) {
      const domainDir = path.join(domainsDir, domain);
      if (fs.statSync(domainDir).isDirectory()) {
        console.log(`   Checking ${domain}...`);
        
        const files = fs.readdirSync(domainDir);
        for (const file of files) {
          if (file.endsWith('.json')) {
            const subdomain = file.replace('.json', '');
            const localData = JSON.parse(fs.readFileSync(path.join(domainDir, file), 'utf8'));
            
            try {
              const cfRecords = await cloudflare.getDNSRecords(domain, subdomain);
              if (cfRecords.length === 0) {
                console.log(`     ❌ ${subdomain}.${domain} - Missing in Cloudflare`);
              } else if (cfRecords[0].content !== localData.record.value) {
                console.log(`     ⚠️  ${subdomain}.${domain} - Value mismatch`);
                console.log(`         Local: ${localData.record.value}`);
                console.log(`         Cloudflare: ${cfRecords[0].content}`);
              } else {
                console.log(`     ✅ ${subdomain}.${domain} - Synced`);
              }
            } catch (error) {
              console.log(`     ❌ ${subdomain}.${domain} - Error: ${error.message}`);
            }
          }
        }
      }
    }
  }

  async fixRecord(domain, subdomain) {
    console.log(`🔧 Attempting to fix ${subdomain}.${domain}...`);
    
    const filePath = path.join(__dirname, '../domains', domain, `${subdomain}.json`);
    if (!fs.existsSync(filePath)) {
      console.log('❌ Local record file not found');
      return;
    }

    const localData = JSON.parse(fs.readFileSync(filePath, 'utf8'));
    const cloudflare = new CloudflareAPI();

    try {
      // Check if record exists in Cloudflare
      const cfRecords = await cloudflare.getDNSRecords(domain, subdomain);
      
      if (cfRecords.length === 0) {
        console.log('📍 Record missing in Cloudflare, creating...');
        const newRecord = await cloudflare.createDNSRecord(domain, subdomain, localData.record);
        
        // Update local file with new record ID
        localData.cloudflare_record_id = newRecord.id;
        localData.updated_at = new Date().toISOString();
        fs.writeFileSync(filePath, JSON.stringify(localData, null, 2));
        
        console.log('✅ Record created and local file updated');
      } else {
        console.log('📍 Record exists in Cloudflare, updating...');
        await cloudflare.updateDNSRecord(domain, subdomain, localData.record, cfRecords[0].id);
        
        // Update local file with correct record ID
        localData.cloudflare_record_id = cfRecords[0].id;
        localData.updated_at = new Date().toISOString();
        fs.writeFileSync(filePath, JSON.stringify(localData, null, 2));
        
        console.log('✅ Record updated');
      }
    } catch (error) {
      console.log(`❌ Failed to fix record: ${error.message}`);
    }
  }
}

module.exports = Troubleshooter;

// CLI usage
if (require.main === module) {
  const troubleshooter = new Troubleshooter();
  const action = process.argv[2];
  const domain = process.argv[3];
  const subdomain = process.argv[4];
  
  (async () => {
    try {
      if (action === 'fix' && domain && subdomain) {
        await troubleshooter.fixRecord(domain, subdomain);
      } else {
        await troubleshooter.diagnose();
      }
    } catch (error) {
      console.error('Troubleshooting failed:', error.message);
      process.exit(1);
    }
  })();
}
