const fs = require('fs');
const path = require('path');
const CloudflareAPI = require('./cloudflare-api');

class DNSDeployer {
  constructor() {
    this.cloudflare = new CloudflareAPI();
  }

  async deploySubdomain(domain, subdomain, requestData) {
    try {
      console.log(`Deploying ${subdomain}.${domain}...`);
      
      // 创建 DNS 记录
      const dnsRecord = await this.cloudflare.createDNSRecord(domain, subdomain, requestData.record);
      
      // 保存记录到文件系统
      const domainDir = path.join(__dirname, '../domains', domain);
      if (!fs.existsSync(domainDir)) {
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
      
      console.log(`✅ Successfully deployed ${subdomain}.${domain}`);
      return true;
    } catch (error) {
      console.error(`❌ Failed to deploy ${subdomain}.${domain}:`, error.message);
      return false;
    }
  }

  async updateSubdomain(domain, subdomain, requestData) {
    try {
      const filePath = path.join(__dirname, '../domains', domain, `${subdomain}.json`);
      const existingData = JSON.parse(fs.readFileSync(filePath, 'utf8'));
      
      console.log(`Updating ${subdomain}.${domain}...`);
      
      // 更新 DNS 记录
      const dnsRecord = await this.cloudflare.updateDNSRecord(
        domain, 
        subdomain, 
        requestData.record, 
        existingData.cloudflare_record_id
      );
      
      // 更新文件
      const recordData = {
        ...requestData,
        cloudflare_record_id: existingData.cloudflare_record_id,
        created_at: existingData.created_at,
        updated_at: new Date().toISOString(),
        status: 'active'
      };
      
      fs.writeFileSync(filePath, JSON.stringify(recordData, null, 2));
      
      console.log(`✅ Successfully updated ${subdomain}.${domain}`);
      return true;
    } catch (error) {
      console.error(`❌ Failed to update ${subdomain}.${domain}:`, error.message);
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
