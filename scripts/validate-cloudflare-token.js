const axios = require('axios');

class CloudflareTokenValidator {
  constructor() {
    this.apiToken = process.env.CLOUDFLARE_API_TOKEN;
    this.baseURL = 'https://api.cloudflare.com/client/v4';
  }

  async validateToken() {
    if (!this.apiToken) {
      throw new Error('CLOUDFLARE_API_TOKEN environment variable is required');
    }

    if (!this.apiToken.match(/^[A-Za-z0-9_-]{40}$/)) {
      throw new Error('Invalid Cloudflare API token format. Token should be 40 characters long.');
    }

    try {
      // Verify token
      const verifyResponse = await axios.get(
        `${this.baseURL}/user/tokens/verify`,
        {
          headers: {
            'Authorization': `Bearer ${this.apiToken}`,
            'Content-Type': 'application/json'
          },
          timeout: 10000
        }
      );

      if (!verifyResponse.data.success) {
        throw new Error(`Token verification failed: ${JSON.stringify(verifyResponse.data.errors)}`);
      }

      console.log('✅ Token is valid and active');
      
      // Check permissions
      const token = verifyResponse.data.result;
      console.log(`📋 Token ID: ${token.id}`);
      console.log(`📋 Status: ${token.status}`);
      
      return true;
    } catch (error) {
      if (error.response?.status === 401) {
        throw new Error('Invalid or expired Cloudflare API token');
      }
      if (error.response?.status === 403) {
        throw new Error('Cloudflare API token lacks required permissions');
      }
      throw error;
    }
  }
}

module.exports = CloudflareTokenValidator;

// CLI usage
if (require.main === module) {
  (async () => {
    try {
      const validator = new CloudflareTokenValidator();
      await validator.validateToken();
      console.log('✅ Cloudflare API token validation successful');
      process.exit(0);
    } catch (error) {
      console.error('❌ Cloudflare API token validation failed:', error.message);
      process.exit(1);
    }
  })();
}
