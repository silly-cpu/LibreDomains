const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');

async function checkPermission(filePath) {
  try {
    const data = JSON.parse(fs.readFileSync(filePath, 'utf8'));
    const domain = data.domain;
    const prAuthor = process.env.GITHUB_ACTOR;

    // Fetch commit history to find the original author
    const commitHistory = await execa.stdout('git', ['log', '--format=%an', '--', filePath]);
    const originalAuthor = commitHistory.split('\n')[0];

    if (prAuthor !== originalAuthor) {
      console.error(`Permission check failed: User "${prAuthor}" is not the original author of "${domain}".`);
      process.exit(1);
    }

    console.log(`Permission check for "${domain}" passed.`);
  } catch (error) {
    console.error(`Permission check failed: ${error.message}`);
    process.exit(1);
  }
}

if (require.main === module) {
  const sha = process.argv[2];
  const filePath = `../subdomains/$(git show --name-only ${sha} | head -n 1)`;
  checkPermission(filePath);
}