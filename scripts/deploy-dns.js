const fs = require('fs');
const path = require('path');
const CloudflareAPI = require('./cloudflare-api');

class DNSDeployer {
  constructor() {
    this.cloudflare = new CloudflareAPI();
  }

  async deploySubdomain(domain, subdomain, requestData) {
    try {
      console.log(`🚀 Deploying ${subdomain}.${domain}...`);
      
      // Check if record already exists
      try {
        const existingRecords = await this.cloudflare.getDNSRecords(domain, subdomain);
        if (existingRecords.length > 0) {
          console.log(`⚠️  Record already exists, attempting update instead...`);
          return await this.updateSubdomain(domain, subdomain, requestData);
        }
      } catch (error) {
        console.log(`ℹ️  No existing record found, proceeding with creation...`);
      }
      
      // 创建 DNS 记录
      console.log(`📡 Creating DNS record with Cloudflare...`);
      const dnsRecord = await this.cloudflare.createDNSRecord(domain, subdomain, requestData.record);
      console.log(`✅ DNS record created with ID: ${dnsRecord.id}`);
      
      // 保存记录到文件系统
      const domainDir = path.join(__dirname, '../domains', domain);
      if (!fs.existsSync(domainDir)) {
        console.log(`📁 Creating domain directory: ${domainDir}`);
        fs.mkdirSync(domainDir, { recursive: true });
      }
      
      const recordData = {
        ...requestData,
        cloudflare_record_id: dnsRecord.id,
        created_at: new Date().toISOString(),
        status: 'active'
      };
      
      const filePath = path.join(domainDir, `${subdomain}.json`);
      fs.writeFileSync(filePath, JSON.stringify(recordData, null, 2));
      console.log(`💾 Record saved to: ${filePath}`);
      
      console.log(`✅ Successfully deployed ${subdomain}.${domain}`);
      return true;
    } catch (error) {
      console.error(`❌ Failed to deploy ${subdomain}.${domain}:`);
      console.error(`   Error: ${error.message}`);
      if (error.response) {
        console.error(`   Status: ${error.response.status}`);
        console.error(`   Data: ${JSON.stringify(error.response.data, null, 2)}`);
      }
      return false;
    }
  }

  async updateSubdomain(domain, subdomain, requestData) {
    try {
      const filePath = path.join(__dirname, '../domains', domain, `${subdomain}.json`);
      
      if (!fs.existsSync(filePath)) {
        console.log(`⚠️  Local record not found, treating as new deployment...`);
        return await this.deploySubdomain(domain, subdomain, requestData);
      }
      
      const existingData = JSON.parse(fs.readFileSync(filePath, 'utf8'));
      console.log(`🔄 Updating ${subdomain}.${domain}...`);
      console.log(`   Existing record ID: ${existingData.cloudflare_record_id}`);
      
      // 更新 DNS 记录
      console.log(`📡 Updating DNS record with Cloudflare...`);
      const dnsRecord = await this.cloudflare.updateDNSRecord(
        domain, 
        subdomain, 
        requestData.record, 
        existingData.cloudflare_record_id
      );
      console.log(`✅ DNS record updated successfully`);
      
      // 更新文件
      const recordData = {
        ...requestData,
        cloudflare_record_id: existingData.cloudflare_record_id,
        created_at: existingData.created_at,
        updated_at: new Date().toISOString(),
        status: 'active'
      };
      
      fs.writeFileSync(filePath, JSON.stringify(recordData, null, 2));
      console.log(`💾 Local record updated`);
      
      console.log(`✅ Successfully updated ${subdomain}.${domain}`);
      return true;
    } catch (error) {
      console.error(`❌ Failed to update ${subdomain}.${domain}:`);
      console.error(`   Error: ${error.message}`);
      if (error.response) {
        console.error(`   Status: ${error.response.status}`);
        console.error(`   Data: ${JSON.stringify(error.response.data, null, 2)}`);
      }
      return false;
    }
  }

  async deleteSubdomain(domain, subdomain) {
    try {
      const filePath = path.join(__dirname, '../domains', domain, `${subdomain}.json`);
      const existingData = JSON.parse(fs.readFileSync(filePath, 'utf8'));
      
      console.log(`Deleting ${subdomain}.${domain}...`);
      
      // 删除 DNS 记录
      await this.cloudflare.deleteDNSRecord(domain, existingData.cloudflare_record_id);
      
      // 删除文件
      fs.unlinkSync(filePath);
      
      console.log(`✅ Successfully deleted ${subdomain}.${domain}`);
      return true;
    } catch (error) {
      console.error(`❌ Failed to delete ${subdomain}.${domain}:`, error.message);
      return false;
    }
  }
}

module.exports = DNSDeployer;

// CLI usage
if (require.main === module) {
  const deployer = new DNSDeployer();
  const action = process.argv[2];
  const requestFile = process.argv[3];
  
  if (!action || !requestFile) {
    console.error('Usage: node deploy-dns.js <deploy|update|delete> <request.json>');
    process.exit(1);
  }

  (async () => {
    try {
      const requestData = JSON.parse(fs.readFileSync(requestFile, 'utf8'));
      
      let success = false;
      switch (action) {
        case 'deploy':
          success = await deployer.deploySubdomain(requestData.domain, requestData.subdomain, requestData);
          break;
        case 'update':
          success = await deployer.updateSubdomain(requestData.domain, requestData.subdomain, requestData);
          break;
        case 'delete':
          success = await deployer.deleteSubdomain(requestData.domain, requestData.subdomain);
          break;
        default:
          console.error('Invalid action. Use: deploy, update, or delete');
          process.exit(1);
      }
      
      process.exit(success ? 0 : 1);
    } catch (error) {
      console.error('Error:', error.message);
      process.exit(1);
    }
  })();
}
