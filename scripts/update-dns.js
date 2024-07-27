const axios = require('axios'); // npm install axios
const fs = require('fs');
const path = require('path');

async function updateDnsRecord() {
  try {
    const filePath = `../subdomains/$(git diff --name-only HEAD~1 HEAD | grep '.json')`;
    const data = JSON.parse(fs.readFileSync(filePath, 'utf8'));
    const domain = data.domain;
    const type = data.type;
    const content = data.content;
    const ttl = data.ttl || 120;
    const proxied = data.proxied || false;

    const zoneId = await fetchZoneId(domain);

    const dnsRecord = {
      type,
      name: domain,
      content,
      ttl,
      proxied
    };

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

    if (response.status === 200) {
      console.log("DNS record updated successfully.");
    } else {
      console.error(`Failed to update DNS record: ${response.data.errors}`);
      process.exit(1);
    }
  } catch (error) {
    console.error(`Failed to update DNS record: ${error.message}`);
    process.exit(1);
  }
}

async function fetchZoneId(domain) {
  const response = await axios.get(
    'https://api.cloudflare.com/client/v4/zones',
    {
      headers: {
        'Authorization': `Bearer ${process.env.CLOUDFLARE_API_TOKEN}`,
        'Content-Type': 'application/json'
      },
      params: {
        name: domain
      }
    }
  );

  if (response.status === 200 && response.data.result.length > 0) {
    return response.data.result[0].id;
  } else {
    throw new Error(`Zone ID not found for domain: ${domain}`);
  }
}

if (require.main === module) {
  updateDnsRecord();
}