const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');

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

async function checkPermission(filePath) {
  try {
    const config = loadConfig();
    const data = JSON.parse(fs.readFileSync(filePath, 'utf8'));
    const domain = data.domain;
    const prAuthor = process.env.GITHUB_ACTOR;

    // 如果是管理员，跳过权限检查
    if (prAuthor === config.admin.github_username) {
      console.log(`管理员权限检查通过: ${prAuthor}`);
      return;
    }

    // 检查文件是否已存在
    if (!fs.existsSync(filePath)) {
      console.log(`新文件权限检查通过: ${domain}`);
      return;
    }

    // 获取文件的提交历史
    try {
      const { stdout } = await execAsync(`git log --format="%an" --follow -- "${filePath}"`);
      const commitAuthors = stdout.trim().split('\n').filter(author => author.trim());
      
      if (commitAuthors.length === 0) {
        console.log(`新文件权限检查通过: ${domain}`);
        return;
      }

      const originalAuthor = commitAuthors[commitAuthors.length - 1].trim();
      
      if (prAuthor !== originalAuthor) {
        console.error(`权限检查失败: 用户 "${prAuthor}" 不是域名 "${domain}" 的原始创建者 "${originalAuthor}"`);
        process.exit(1);
      }

      console.log(`权限检查通过: ${domain} (原始创建者: ${originalAuthor})`);
    } catch (gitError) {
      console.log(`无法获取Git历史，视为新文件: ${domain}`);
    }

  } catch (error) {
    console.error(`权限检查失败: ${error.message}`);
    process.exit(1);
  }
}

if (require.main === module) {
  const sha = process.argv[2];
  const filePath = `../subdomains/$(git show --name-only ${sha} | head -n 1)`;
  checkPermission(filePath);
}