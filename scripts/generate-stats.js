const fs = require('fs');
const path = require('path');

class StatsGenerator {
  constructor() {
    this.domainsDir = path.join(__dirname, '../domains');
  }

  generateStats() {
    const stats = {
      totalSubdomains: 0,
      activeDomains: 0,
      userCount: {},
      recordTypes: {},
      domainStats: {}
    };

    if (!fs.existsSync(this.domainsDir)) {
      return stats;
    }

    const domains = fs.readdirSync(this.domainsDir);
    
    for (const domain of domains) {
      const domainDir = path.join(this.domainsDir, domain);
      if (fs.statSync(domainDir).isDirectory()) {
        stats.activeDomains++;
        stats.domainStats[domain] = { count: 0, users: new Set() };
        
        const files = fs.readdirSync(domainDir);
        for (const file of files) {
          if (file.endsWith('.json')) {
            const filePath = path.join(domainDir, file);
            const data = JSON.parse(fs.readFileSync(filePath, 'utf8'));
            
            stats.totalSubdomains++;
            stats.domainStats[domain].count++;
            
            if (data.owner && data.owner.username) {
              const username = data.owner.username;
              stats.userCount[username] = (stats.userCount[username] || 0) + 1;
              stats.domainStats[domain].users.add(username);
            }
            
            if (data.record && data.record.type) {
              const recordType = data.record.type;
              stats.recordTypes[recordType] = (stats.recordTypes[recordType] || 0) + 1;
            }
          }
        }
        
        // Convert Set to number for JSON serialization
        stats.domainStats[domain].uniqueUsers = stats.domainStats[domain].users.size;
        delete stats.domainStats[domain].users;
      }
    }

    return stats;
  }

  printStats() {
    const stats = this.generateStats();
    
    console.log('📊 LibreDomains Statistics');
    console.log('==========================');
    console.log(`Total Subdomains: ${stats.totalSubdomains}`);
    console.log(`Active Domains: ${stats.activeDomains}`);
    console.log(`Unique Users: ${Object.keys(stats.userCount).length}`);
    console.log('');
    
    console.log('🌐 Domain Breakdown:');
    for (const [domain, domainStats] of Object.entries(stats.domainStats)) {
      console.log(`  ${domain}: ${domainStats.count} subdomains, ${domainStats.uniqueUsers} users`);
    }
    console.log('');
    
    console.log('📈 Top Users:');
    const topUsers = Object.entries(stats.userCount)
      .sort(([,a], [,b]) => b - a)
      .slice(0, 10);
    for (const [username, count] of topUsers) {
      console.log(`  ${username}: ${count} subdomain${count > 1 ? 's' : ''}`);
    }
    console.log('');
    
    console.log('📋 Record Types:');
    const totalRecords = Object.values(stats.recordTypes).reduce((a, b) => a + b, 0);
    for (const [type, count] of Object.entries(stats.recordTypes)) {
      const percentage = ((count / totalRecords) * 100).toFixed(1);
      console.log(`  ${type}: ${count} (${percentage}%)`);
    }
  }
}

module.exports = StatsGenerator;

// CLI usage
if (require.main === module) {
  const generator = new StatsGenerator();
  generator.printStats();
}
