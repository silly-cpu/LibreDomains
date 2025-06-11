const axios = require('axios');
const fs = require('fs');
const path = require('path');
const yaml = require('js-yaml');

class CloudflareAPI {
  constructor() {
    this.apiToken = process.env.CLOUDFLARE_API_TOKEN;
    this.baseURL = 'https://api.cloudflare.com/client/v4';
    this.domainsConfig = yaml.load(fs.readFileSync(path.join(__dirname, '../config/domains.yml'), 'utf8'));
    
    if (!this.apiToken) {
      throw new Error('CLOUDFLARE_API_TOKEN environment variable is required');
    }
  }

  async createDNSRecord(domain, subdomain, record) {
    const domainConfig = this.domainsConfig.domains[domain];
    if (!domainConfig) {
      throw new Error(`Domain ${domain} not found in configuration`);
    }

    const zoneId = domainConfig.cloudflare_zone_id;
    const recordName = subdomain ? `${subdomain}.${domain}` : domain;

    const recordData = {
      type: record.type,
      name: recordName,
      content: record.value,
      ttl: record.ttl || 3600,
      proxied: record.proxied || false
    };

    if (record.type === 'MX' && record.priority) {
      recordData.priority = record.priority;
    }

    try {
      const response = await axios.post(
        `${this.baseURL}/zones/${zoneId}/dns_records`,
        recordData,
        {
          headers: {
            'Authorization': `Bearer ${this.apiToken}`,
            'Content-Type': 'application/json'
          }
        }
      );

      if (response.data.success) {
        return response.data.result;
      } else {
        throw new Error(`Cloudflare API error: ${JSON.stringify(response.data.errors)}`);
      }
    } catch (error) {
      if (error.response?.status === 400 && error.response?.data?.errors) {
        const cfError = error.response.data.errors[0];
        
        // Handle proxied record with private IP error
        if (cfError.code === 9003 && recordData.proxied) {
          console.log(`⚠️  Private IP detected with proxy enabled, retrying without proxy...`);
          recordData.proxied = false;
          
          try {
            const retryResponse = await axios.post(
              `${this.baseURL}/zones/${zoneId}/dns_records`,
              recordData,
              {
                headers: {
                  'Authorization': `Bearer ${this.apiToken}`,
                  'Content-Type': 'application/json'
                }
              }
            );

            if (retryResponse.data.success) {
              console.log(`✅ Record created successfully without proxy`);
              return retryResponse.data.result;
            }
          } catch (retryError) {
            console.error(`❌ Retry failed:`, retryError.response?.data || retryError.message);
          }
        }
        
        throw new Error(`Cloudflare API error (${cfError.code}): ${cfError.message}`);
      }
      
      if (error.response) {
        throw new Error(`Cloudflare API error: ${error.response.status} - ${JSON.stringify(error.response.data)}`);
      }
      throw error;
    }
  }

  async updateDNSRecord(domain, subdomain, record, recordId) {
    const domainConfig = this.domainsConfig.domains[domain];
    const zoneId = domainConfig.cloudflare_zone_id;
    const recordName = subdomain ? `${subdomain}.${domain}` : domain;

    const recordData = {
      type: record.type,
      name: recordName,
      content: record.value,
      ttl: record.ttl || 3600,
      proxied: record.proxied || false
    };

    if (record.type === 'MX' && record.priority) {
      recordData.priority = record.priority;
    }

    try {
      const response = await axios.put(
        `${this.baseURL}/zones/${zoneId}/dns_records/${recordId}`,
        recordData,
        {
          headers: {
            'Authorization': `Bearer ${this.apiToken}`,
            'Content-Type': 'application/json'
          }
        }
      );

      if (response.data.success) {
        return response.data.result;
      } else {
        throw new Error(`Cloudflare API error: ${JSON.stringify(response.data.errors)}`);
      }
    } catch (error) {
      if (error.response?.status === 400 && error.response?.data?.errors) {
        const cfError = error.response.data.errors[0];
        
        // Handle proxied record with private IP error
        if (cfError.code === 9003 && recordData.proxied) {
          console.log(`⚠️  Private IP detected with proxy enabled, retrying without proxy...`);
          recordData.proxied = false;
          
          try {
            const retryResponse = await axios.put(
              `${this.baseURL}/zones/${zoneId}/dns_records/${recordId}`,
              recordData,
              {
                headers: {
                  'Authorization': `Bearer ${this.apiToken}`,
                  'Content-Type': 'application/json'
                }
              }
            );

            if (retryResponse.data.success) {
              console.log(`✅ Record updated successfully without proxy`);
              return retryResponse.data.result;
            }
          } catch (retryError) {
            console.error(`❌ Retry failed:`, retryError.response?.data || retryError.message);
          }
        }
        
        throw new Error(`Cloudflare API error (${cfError.code}): ${cfError.message}`);
      }
      
      if (error.response) {
        throw new Error(`Cloudflare API error: ${error.response.status} - ${JSON.stringify(error.response.data)}`);
      }
      throw error;
    }
  }

  async deleteDNSRecord(domain, recordId) {
    const domainConfig = this.domainsConfig.domains[domain];
    const zoneId = domainConfig.cloudflare_zone_id;

    try {
      const response = await axios.delete(
        `${this.baseURL}/zones/${zoneId}/dns_records/${recordId}`,
        {
          headers: {
            'Authorization': `Bearer ${this.apiToken}`,
            'Content-Type': 'application/json'
          }
        }
      );

      return response.data.success;
    } catch (error) {
      if (error.response) {
        throw new Error(`Cloudflare API error: ${error.response.status} - ${JSON.stringify(error.response.data)}`);
      }
      throw error;
    }
  }

  async getDNSRecords(domain, subdomain = null) {
    const domainConfig = this.domainsConfig.domains[domain];
    const zoneId = domainConfig.cloudflare_zone_id;
    const recordName = subdomain ? `${subdomain}.${domain}` : domain;

    try {
      const response = await axios.get(
        `${this.baseURL}/zones/${zoneId}/dns_records?name=${recordName}`,
        {
          headers: {
            'Authorization': `Bearer ${this.apiToken}`,
            'Content-Type': 'application/json'
          }
        }
      );

      if (response.data.success) {
        return response.data.result;
      } else {
        throw new Error(`Cloudflare API error: ${JSON.stringify(response.data.errors)}`);
      }
    } catch (error) {
      if (error.response) {
        throw new Error(`Cloudflare API error: ${error.response.status} - ${JSON.stringify(error.response.data)}`);
      }
      throw error;
    }
  }
}

module.exports = CloudflareAPI;
