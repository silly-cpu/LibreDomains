const axios = require('axios');
const fs = require('fs');
const path = require('path');
const yaml = require('js-yaml');

class GitHubUserChecker {
  constructor() {
    this.domainsConfig = yaml.load(fs.readFileSync(path.join(__dirname, '../config/domains.yml'), 'utf8'));
    this.settings = this.domainsConfig.settings;
  }

  async checkUser(username) {
    const errors = [];

    try {
      // 获取用户信息
      const response = await axios.get(`https://api.github.com/users/${username}`);
      const user = response.data;

      // 检查账户年龄
      if (this.settings.min_account_age_days) {
        const accountAge = Math.floor((Date.now() - new Date(user.created_at).getTime()) / (1000 * 60 * 60 * 24));
        if (accountAge < this.settings.min_account_age_days) {
          errors.push(`Account must be at least ${this.settings.min_account_age_days} days old (current: ${accountAge} days)`);
        }
      }

      // 检查是否需要验证
      if (this.settings.require_github_verification && !user.email) {
        errors.push('GitHub account must have a verified email address');
      }

      // 检查用户子域名数量限制
      const RequestValidator = require('./validate-request');
      const validator = new RequestValidator();
      const currentCount = validator.getUserSubdomainCount(username);
      
      if (currentCount >= this.settings.max_subdomains_per_user) {
        errors.push(`Maximum ${this.settings.max_subdomains_per_user} subdomains per user (current: ${currentCount})`);
      }

      return {
        valid: errors.length === 0,
        errors: errors,
        user: user
      };

    } catch (error) {
      if (error.response && error.response.status === 404) {
        errors.push('GitHub user not found');
      } else {
        errors.push(`Failed to fetch GitHub user: ${error.message}`);
      }
      
      return {
        valid: false,
        errors: errors,
        user: null
      };
    }
  }
}

module.exports = GitHubUserChecker;

// CLI usage
if (require.main === module) {
  const checker = new GitHubUserChecker();
  const username = process.argv[2];
  
  if (!username) {
    console.error('Usage: node check-github-user.js <username>');
    process.exit(1);
  }

  (async () => {
    try {
      const result = await checker.checkUser(username);
      
      if (result.valid) {
        console.log(`✅ GitHub user ${username} is valid`);
        process.exit(0);
      } else {
        console.log(`❌ GitHub user ${username} validation failed:`);
        result.errors.forEach(error => console.log(`  - ${error}`));
        process.exit(1);
      }
    } catch (error) {
      console.error('Error:', error.message);
      process.exit(1);
    }
  })();
}
