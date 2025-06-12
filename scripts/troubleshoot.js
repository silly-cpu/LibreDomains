const fs = require('fs');
const path = require('path');
const CloudflareAPI = require('./cloudflare-api');
const yaml = require('js-yaml');

class Troubleshooter {
  constructor() {
    this.cloudflare = new CloudflareAPI();
    this.domainsConfig = yaml.load(fs.readFileSync(path.join(__dirname, '../config/domains.yml'), 'utf8'));
  }

  async runDiagnostics() {
    console.log('🔍 Running LibreDomains troubleshooter...\n');
    
    const issues = [];
    
    // Check environment
    await this.checkEnvironment(issues);
    
    // Check configuration files
    this.checkConfiguration(issues);
    
    // Check Cloudflare connectivity
    await this.checkCloudflareAPI(issues);
    
    // Check domain records consistency
    await this.checkRecordConsistency(issues);
    
    // Summary
    console.log('\n📊 Troubleshooting Summary:');
    if (issues.length === 0) {
      console.log('✅ No issues found! System appears to be healthy.');
    } else {
      console.log(`❌ Found ${issues.length} issue(s):`);
      issues.forEach((issue, index) => {
        console.log(`${index + 1}. ${issue}`);
      });
    }
    
    return issues.length === 0;
  }

  async checkEnvironment(issues) {
    console.log('🔧 Checking environment...');
    
    // Check Node.js version
    const nodeVersion = process.version;
    console.log(`   Node.js version: ${nodeVersion}`);
    
    // Check API token
    if (!process.env.CLOUDFLARE_API_TOKEN) {
      issues.push('CLOUDFLARE_API_TOKEN environment variable is not set');
      console.log('   ❌ CLOUDFLARE_API_TOKEN: Not set');
    } else {
      console.log('   ✅ CLOUDFLARE_API_TOKEN: Set');
    }
    
    // Check required directories
    const requiredDirs = ['config', 'domains', 'requests', 'scripts'];
    for (const dir of requiredDirs) {
      const dirPath = path.join(__dirname, '..', dir);
      if (!fs.existsSync(dirPath)) {
        issues.push(`Required directory missing: ${dir}`);
        console.log(`   ❌ Directory ${dir}: Missing`);
      } else {
        console.log(`   ✅ Directory ${dir}: Exists`);
      }
    }
  }

  checkConfiguration(issues) {
    console.log('📋 Checking configuration files...');
    
    // Check schema.json
    try {
      const schemaPath = path.join(__dirname, '../config/schema.json');
      const schema = JSON.parse(fs.readFileSync(schemaPath, 'utf8'));
      console.log('   ✅ schema.json: Valid');
    } catch (error) {
      issues.push(`Invalid schema.json: ${error.message}`);
      console.log('   ❌ schema.json: Invalid');
    }
    
    // Check domains.yml
    try {
      const domains = this.domainsConfig;
      const enabledDomains = Object.keys(domains.domains).filter(d => domains.domains[d].enabled);
      console.log(`   ✅ domains.yml: Valid (${enabledDomains.length} enabled domains)`);
    } catch (error) {
      issues.push(`Invalid domains.yml: ${error.message}`);
      console.log('   ❌ domains.yml: Invalid');
    }
  }

  async checkCloudflareAPI(issues) {
    console.log('🌐 Checking Cloudflare API connectivity...');
    
    try {
      // Test API connection with a simple request
      const testDomain = Object.keys(this.domainsConfig.domains)[0];
      if (testDomain) {
        await this.cloudflare.getDNSRecords(testDomain);
        console.log('   ✅ Cloudflare API: Connected');
      }
    } catch (error) {
      issues.push(`Cloudflare API error: ${error.message}`);
      console.log('   ❌ Cloudflare API: Failed');
    }
  }

  async checkRecordConsistency(issues) {
    console.log('🔍 Checking record consistency...');
    
    const domainsDir = path.join(__dirname, '../domains');
    if (!fs.existsSync(domainsDir)) {
      console.log('   ℹ️  No domain records to check');
      return;
    }

    let totalRecords = 0;
    let inconsistentRecords = 0;

    for (const domain of fs.readdirSync(domainsDir)) {
      const domainDir = path.join(domainsDir, domain);
      if (!fs.statSync(domainDir).isDirectory()) continue;

      for (const file of fs.readdirSync(domainDir)) {
        if (!file.endsWith('.json')) continue;

        totalRecords++;
        const filePath = path.join(domainDir, file);
        const subdomain = path.basename(file, '.json');

        try {
          const recordData = JSON.parse(fs.readFileSync(filePath, 'utf8'));
          
          // Check if Cloudflare record exists
          if (recordData.cloudflare_record_id) {
            try {
              const cfRecords = await this.cloudflare.getDNSRecords(domain, subdomain);
              const cfRecord = cfRecords.find(r => r.id === recordData.cloudflare_record_id);
              
              if (!cfRecord) {
                inconsistentRecords++;
                issues.push(`Local record ${subdomain}.${domain} has Cloudflare ID but record not found in Cloudflare`);
              }
            } catch (error) {
              console.log(`   ⚠️  Could not verify ${subdomain}.${domain}: ${error.message}`);
            }
          }
        } catch (error) {
          issues.push(`Invalid local record file: ${filePath}`);
        }
      }
    }

    console.log(`   📊 Checked ${totalRecords} records, ${inconsistentRecords} inconsistencies found`);
  }

  async fixRecord(domain, subdomain) {
    console.log(`🔧 Attempting to fix record: ${subdomain}.${domain}`);
    
    const filePath = path.join(__dirname, '../domains', domain, `${subdomain}.json`);
    if (!fs.existsSync(filePath)) {
      console.log('❌ Local record file not found');
      return false;
    }

    try {
      const recordData = JSON.parse(fs.readFileSync(filePath, 'utf8'));
      
      // Check if Cloudflare record exists
      const cfRecords = await this.cloudflare.getDNSRecords(domain, subdomain);
      
      if (cfRecords.length === 0) {
        console.log('🔄 No Cloudflare record found, creating new one...');
        const newRecord = await this.cloudflare.createDNSRecord(domain, subdomain, recordData.record);
        
        // Update local file with new ID
        recordData.cloudflare_record_id = newRecord.id;
        recordData.updated_at = new Date().toISOString();
        fs.writeFileSync(filePath, JSON.stringify(recordData, null, 2));
        
        console.log('✅ Record fixed successfully');
        return true;
      } else {
        console.log('✅ Cloudflare record exists, no fix needed');
        return true;
      }
    } catch (error) {
      console.log(`❌ Failed to fix record: ${error.message}`);
      return false;
    }
  }
}

module.exports = Troubleshooter;

// CLI usage
if (require.main === module) {
  const troubleshooter = new Troubleshooter();
  const action = process.argv[2];
  
  (async () => {
    try {
      if (action === 'fix') {
        const domain = process.argv[3];
        const subdomain = process.argv[4];
        
        if (!domain || !subdomain) {
          console.error('Usage: node troubleshoot.js fix <domain> <subdomain>');
          process.exit(1);
        }
        
        const success = await troubleshooter.fixRecord(domain, subdomain);
        process.exit(success ? 0 : 1);
      } else {
        const success = await troubleshooter.runDiagnostics();
        process.exit(success ? 0 : 1);
      }
    } catch (error) {
      console.error('Troubleshooter error:', error.message);
      process.exit(1);
    }
  })();
}
