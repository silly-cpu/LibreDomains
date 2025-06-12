const fs = require('fs');
const path = require('path');
const yaml = require('js-yaml');

class StatsGenerator {
  constructor() {
    this.domainsConfig = yaml.load(fs.readFileSync(path.join(__dirname, '../config/domains.yml'), 'utf8'));
  }

  generateStats() {
    console.log('📊 Generating LibreDomains Statistics\n');
    
    const stats = {
      domains: {},
      totals: {
        totalSubdomains: 0,
        activeSubdomains: 0,
        totalUsers: 0,
        recordTypes: {}
      },
      users: {},
      recordTypes: {}
    };

    const domainsDir = path.join(__dirname, '../domains');
    if (!fs.existsSync(domainsDir)) {
      console.log('ℹ️  No domain records found');
      return stats;
    }

    // Process each domain
    for (const domain of fs.readdirSync(domainsDir)) {
      const domainDir = path.join(domainsDir, domain);
      if (!fs.statSync(domainDir).isDirectory()) continue;

      stats.domains[domain] = {
        totalSubdomains: 0,
        activeSubdomains: 0,
        recordTypes: {},
        users: {}
      };

      // Process each subdomain
      for (const file of fs.readdirSync(domainDir)) {
        if (!file.endsWith('.json')) continue;

        const filePath = path.join(domainDir, file);
        try {
          const recordData = JSON.parse(fs.readFileSync(filePath, 'utf8'));
          const subdomain = path.basename(file, '.json');
          
          // Domain stats
          stats.domains[domain].totalSubdomains++;
          if (recordData.status === 'active') {
            stats.domains[domain].activeSubdomains++;
          }

          // Record type stats
          const recordType = recordData.record.type;
          stats.domains[domain].recordTypes[recordType] = (stats.domains[domain].recordTypes[recordType] || 0) + 1;
          stats.totals.recordTypes[recordType] = (stats.totals.recordTypes[recordType] || 0) + 1;

          // User stats
          if (recordData.owner && recordData.owner.username) {
            const username = recordData.owner.username;
            stats.domains[domain].users[username] = (stats.domains[domain].users[username] || 0) + 1;
            stats.users[username] = (stats.users[username] || 0) + 1;
          }

        } catch (error) {
          console.log(`⚠️  Error reading ${file}: ${error.message}`);
        }
      }

      // Update totals
      stats.totals.totalSubdomains += stats.domains[domain].totalSubdomains;
      stats.totals.activeSubdomains += stats.domains[domain].activeSubdomains;
    }

    stats.totals.totalUsers = Object.keys(stats.users).length;

    this.displayStats(stats);
    return stats;
  }

  displayStats(stats) {
    console.log('🌐 Domain Statistics:');
    console.log('═'.repeat(50));
    
    for (const [domain, domainStats] of Object.entries(stats.domains)) {
      const config = this.domainsConfig.domains[domain];
      const status = config?.enabled ? '✅ Enabled' : '❌ Disabled';
      
      console.log(`\n📋 ${domain} (${status})`);
      console.log(`   Total subdomains: ${domainStats.totalSubdomains}`);
      console.log(`   Active subdomains: ${domainStats.activeSubdomains}`);
      console.log(`   Unique users: ${Object.keys(domainStats.users).length}`);
      
      if (Object.keys(domainStats.recordTypes).length > 0) {
        console.log('   Record types:');
        for (const [type, count] of Object.entries(domainStats.recordTypes)) {
          console.log(`     ${type}: ${count}`);
        }
      }
    }

    console.log('\n📊 Overall Statistics:');
    console.log('═'.repeat(50));
    console.log(`Total subdomains: ${stats.totals.totalSubdomains}`);
    console.log(`Active subdomains: ${stats.totals.activeSubdomains}`);
    console.log(`Total users: ${stats.totals.totalUsers}`);
    
    if (Object.keys(stats.totals.recordTypes).length > 0) {
      console.log('Record type distribution:');
      for (const [type, count] of Object.entries(stats.totals.recordTypes)) {
        const percentage = ((count / stats.totals.totalSubdomains) * 100).toFixed(1);
        console.log(`  ${type}: ${count} (${percentage}%)`);
      }
    }

    // Top users
    const topUsers = Object.entries(stats.users)
      .sort(([,a], [,b]) => b - a)
      .slice(0, 10);
    
    if (topUsers.length > 0) {
      console.log('\n👥 Top Users:');
      topUsers.forEach(([username, count], index) => {
        console.log(`${index + 1}. ${username}: ${count} subdomain${count !== 1 ? 's' : ''}`);
      });
    }
  }

  exportStats(outputPath) {
    const stats = this.generateStats();
    
    if (outputPath) {
      fs.writeFileSync(outputPath, JSON.stringify(stats, null, 2));
      console.log(`\n💾 Statistics exported to: ${outputPath}`);
    }

    return stats;
  }
}

module.exports = StatsGenerator;

// CLI usage
if (require.main === module) {
  const generator = new StatsGenerator();
  const outputPath = process.argv[2];
  
  try {
    generator.exportStats(outputPath);
  } catch (error) {
    console.error('Error generating statistics:', error.message);
    process.exit(1);
  }
}
