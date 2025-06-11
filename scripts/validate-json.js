const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');

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

function validateJson(filePath) {
  try {
    const data = JSON.parse(fs.readFileSync(filePath, 'utf8'));
    const config = loadConfig();
    
    // 检查必需字段
    const requiredKeys = ['domain', 'type', 'content'];
    const missingKeys = requiredKeys.filter(key => !data.hasOwnProperty(key));
    if (missingKeys.length > 0) {
      console.error(`验证失败: 缺少必需字段: ${missingKeys.join(', ')}`);
      process.exit(1);
    }

    // 验证域名格式
    const domain = data.domain;
    const enabledDomains = config.domains.filter(d => d.enabled).map(d => d.name);
    const domainSuffix = enabledDomains.find(suffix => domain.endsWith('.' + suffix));
    
    if (!domainSuffix) {
      console.error(`验证失败: 域名 "${domain}" 不属于允许的域名后缀: ${enabledDomains.join(', ')}`);
      process.exit(1);
    }

    // 验证记录类型
    if (!config.settings.allowed_record_types.includes(data.type)) {
      console.error(`验证失败: 不支持的记录类型 "${data.type}". 允许的类型: ${config.settings.allowed_record_types.join(', ')}`);
      process.exit(1);
    }

    // 检查重复域名
    const allFiles = fs.readdirSync(path.join(__dirname, '../subdomains'));
    const existingDomains = allFiles.map(file => {
      try {
        if (!file.endsWith('.json') || file === 'template.json') return null;
        const fileData = JSON.parse(fs.readFileSync(path.join(__dirname, '../subdomains', file), 'utf8'));
        return fileData.domain;
      } catch (error) {
        return null;
      }
    }).filter(Boolean);

    if (existingDomains.includes(domain)) {
      console.error(`验证失败: 域名 "${domain}" 已存在`);
      process.exit(1);
    }

    // 验证内容格式
    if (data.type === 'A' && !/^(\d{1,3}\.){3}\d{1,3}$/.test(data.content)) {
      console.error(`验证失败: A记录的内容必须是有效的IPv4地址`);
      process.exit(1);
    }

    if (data.type === 'AAAA' && !/^([0-9a-fA-F]{0,4}:){1,7}[0-9a-fA-F]{0,4}$/.test(data.content)) {
      console.error(`验证失败: AAAA记录的内容必须是有效的IPv6地址`);
      process.exit(1);
    }

    console.log("JSON验证通过");
  } catch (error) {
    console.error(`验证失败: ${error.message}`);
    process.exit(1);
  }
}

if (require.main === module) {
  const sha = process.argv[2];
  exec(`git show --name-only ${sha}`, (error, stdout, stderr) => {
    if (error) {
      console.error(`Failed to execute git command: ${error.message}`);
      process.exit(1);
    }
    const fileNames = stdout.trim().split('\n');
    if (fileNames.length === 0) {
      console.error(`Validation failed: No files were modified in this commit.`);
      process.exit(1);
    }
    const filePath = path.resolve(__dirname, '..', 'subdomains', fileNames[0]);
    validateJson(filePath);
  });
}