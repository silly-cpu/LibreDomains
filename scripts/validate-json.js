const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');

function validateJson(filePath) {
  try {
    const data = JSON.parse(fs.readFileSync(filePath, 'utf8'));
    const requiredKeys = ['domain', 'type', 'content'];
    const missingKeys = requiredKeys.filter(key => !data.hasOwnProperty(key));
    if (missingKeys.length > 0) {
      console.error(`Validation failed: Missing keys: ${missingKeys.join(', ')}`);
      process.exit(1);
    }

    // Check for duplicate domains
    const domain = data.domain;
    const allFiles = fs.readdirSync(path.join(__dirname, '../subdomains'));
    const existingDomains = allFiles.map(file => {
      try {
        const fileData = JSON.parse(fs.readFileSync(path.join(__dirname, '../subdomains', file), 'utf8'));
        return fileData.domain;
      } catch (error) {
        return null;
      }
    }).filter(Boolean); // Remove any null values

    if (existingDomains.includes(domain)) {
      console.error(`Validation failed: Domain "${domain}" already exists.`);
      process.exit(1);
    }

    console.log("JSON validation passed.");
  } catch (error) {
    console.error(`Validation failed: ${error.message}`);
    process.exit(1);
  }
}

if (require.main === module) {
  const sha = process.argv[2];
  exec(`git show --name-only ${sha} | head -n 1`, (error, stdout, stderr) => {
    if (error) {
      console.error(`Failed to execute git command: ${error.message}`);
      process.exit(1);
    }
    const filePath = path.resolve(__dirname, '..', 'subdomains', stdout.trim());
    validateJson(filePath);
  });
}