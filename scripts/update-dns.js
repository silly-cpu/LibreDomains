const axios = require('axios');
const fs = require('fs');
const path = require('path');

const axios = require('axios');
const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');
const { promisify } = require('util');
const execAsync = promisify(exec);

// 加载配置文件
function loadConfig() {
  try {
    const configPath = path.join(__dirname, '../config/domains.json');
    return JSON.parse(fs.readFileSync(configPath, 'utf8'));
  } catch (error) {
    console.error(`无法加载配置文件: ${error.message}`);
    process.exit(1);
  }
}

async function getChangedFiles() {
  try {
    const { stdout } = await execAsync('git diff --name-only HEAD~1 HEAD');
    return stdout.trim().split('\n').filter(file => 
      file.startsWith('subdomains/') && 
      file.endsWith('.json') && 
      !file.includes('template.json')
    );
  } catch (error) {
    console.error(`获取变更文件失败: ${error.message}`);
    return [];
  }
}

async function updateDnsRecord() {
  try {
    const config = loadConfig();
    const changedFiles = await getChangedFiles();
    
    if (changedFiles.length === 0) {
      console.log("没有需要更新的DNS记录");
      return;
    }

    for (const file of changedFiles) {
      const filePath = path.join(__dirname, '..', file);
      
      if (!fs.existsSync(filePath)) {
        console.log(`文件已删除，跳过: ${file}`);
        continue;
      }

      const data = JSON.parse(fs.readFileSync(filePath, 'utf8'));
      const domain = data.domain;
      const type = data.type;
      const content = data.content;
      const ttl = data.ttl || 120;
      const proxied = data.proxied || false;

      // 找到对应的域名配置
      const domainConfig = config.domains.find(d => domain.endsWith('.' + d.name) && d.enabled);
      
      if (!domainConfig) {
        console.error(`域名 ${domain} 不属于任何启用的域名配置`);
        continue;
      }

      if (!domainConfig.cloudflare_zone_id) {
        console.error(`域名 ${domainConfig.name} 未配置 Cloudflare Zone ID`);
        continue;
      }

      await createOrUpdateDnsRecord(domainConfig.cloudflare_zone_id, {
        type,
        name: domain,
        content,
        ttl,
        proxied
      });
    }
  } catch (error) {
    console.error(`DNS更新失败: ${error.message}`);
    process.exit(1);
  }
}

async function createOrUpdateDnsRecord(zoneId, dnsRecord) {
  try {
    // 先检查记录是否存在
    const existingRecords = await axios.get(
      `https://api.cloudflare.com/client/v4/zones/${zoneId}/dns_records`,
      {
        headers: {
          'Authorization': `Bearer ${process.env.CLOUDFLARE_API_TOKEN}`,
          'Content-Type': 'application/json'
        },
        params: {
          name: dnsRecord.name,
          type: dnsRecord.type
        }
      }
    );

    if (existingRecords.data.result.length > 0) {
      // 更新现有记录
      const recordId = existingRecords.data.result[0].id;
      const response = await axios.put(
        `https://api.cloudflare.com/client/v4/zones/${zoneId}/dns_records/${recordId}`,
        dnsRecord,
        {
          headers: {
            'Authorization': `Bearer ${process.env.CLOUDFLARE_API_TOKEN}`,
            'Content-Type': 'application/json'
          }
        }
      );

      if (response.data.success) {
        console.log(`DNS记录更新成功: ${dnsRecord.name}`);
      } else {
        console.error(`DNS记录更新失败: ${response.data.errors}`);
      }
    } else {
      // 创建新记录
      const response = await axios.post(
        `https://api.cloudflare.com/client/v4/zones/${zoneId}/dns_records`,
        dnsRecord,
        {
          headers: {
            'Authorization': `Bearer ${process.env.CLOUDFLARE_API_TOKEN}`,
            'Content-Type': 'application/json'
          }
        }
      );

      if (response.data.success) {
        console.log(`DNS记录创建成功: ${dnsRecord.name}`);
      } else {
        console.error(`DNS记录创建失败: ${response.data.errors}`);
      }
    }
  } catch (error) {
    console.error(`DNS操作失败: ${error.message}`);
    throw error;
  }
}

if (require.main === module) {
  updateDnsRecord();
}