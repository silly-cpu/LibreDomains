const axios = require('axios');

class CloudflareTokenValidator {
  constructor(token) {
    this.token = token;
    this.baseURL = 'https://api.cloudflare.com/client/v4';
  }

  async validateToken() {
    if (!this.token) {
      return {
        valid: false,
        error: 'Cloudflare API token is not provided'
      };
    }

    try {
      // Test token by getting user details
      const response = await axios.get(`${this.baseURL}/user/tokens/verify`, {
        headers: {
          'Authorization': `Bearer ${this.token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.data.success) {
        const result = response.data.result;
        return {
          valid: true,
          tokenInfo: {
            id: result.id,
            status: result.status,
            permissions: result.policies?.map(p => p.permission_groups).flat() || []
          }
        };
      } else {
        return {
          valid: false,
          error: 'Token verification failed',
          details: response.data.errors
        };
      }
    } catch (error) {
      if (error.response) {
        const status = error.response.status;
        const data = error.response.data;
        
        if (status === 401) {
          return {
            valid: false,
            error: 'Invalid Cloudflare API token (401 Unauthorized)'
          };
        } else if (status === 403) {
          return {
            valid: false,
            error: 'Insufficient permissions for Cloudflare API token (403 Forbidden)'
          };
        } else {
          return {
            valid: false,
            error: `Cloudflare API error (${status})`,
            details: data?.errors || [error.message]
          };
        }
      } else {
        return {
          valid: false,
          error: `Network error: ${error.message}`
        };
      }
    }
  }

  async checkZonePermissions(zoneName) {
    if (!this.token) {
      return { hasPermission: false, error: 'No token provided' };
    }

    try {
      // Get zones to check if token has access
      const response = await axios.get(`${this.baseURL}/zones?name=${zoneName}`, {
        headers: {
          'Authorization': `Bearer ${this.token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.data.success && response.data.result.length > 0) {
        return {
          hasPermission: true,
          zone: response.data.result[0]
        };
      } else {
        return {
          hasPermission: false,
          error: `Zone ${zoneName} not found or no access permission`
        };
      }
    } catch (error) {
      return {
        hasPermission: false,
        error: `Failed to check zone permissions: ${error.message}`
      };
    }
  }
}

module.exports = CloudflareTokenValidator;

// CLI usage
if (require.main === module) {
  const token = process.env.CLOUDFLARE_API_TOKEN || process.argv[2];
  const zoneName = process.argv[3];
  
  if (!token) {
    console.error('Usage: node validate-cloudflare-token.js [token] [zone_name]');
    console.error('Or set CLOUDFLARE_API_TOKEN environment variable');
    process.exit(1);
  }

  (async () => {
    try {
      const validator = new CloudflareTokenValidator(token);
      
      console.log('🔍 Validating Cloudflare API token...');
      const tokenResult = await validator.validateToken();
      
      if (!tokenResult.valid) {
        console.error('❌ Token validation failed:', tokenResult.error);
        if (tokenResult.details) {
          console.error('Details:', tokenResult.details);
        }
        process.exit(1);
      }
      
      console.log('✅ Token is valid');
      console.log('Token info:', tokenResult.tokenInfo);
      
      if (zoneName) {
        console.log(`\n🔍 Checking permissions for zone: ${zoneName}`);
        const zoneResult = await validator.checkZonePermissions(zoneName);
        
        if (!zoneResult.hasPermission) {
          console.error('❌ Zone permission check failed:', zoneResult.error);
          process.exit(1);
        }
        
        console.log('✅ Zone access confirmed');
        console.log('Zone ID:', zoneResult.zone.id);
      }
      
      process.exit(0);
    } catch (error) {
      console.error('Error:', error.message);
      process.exit(1);
    }
  })();
}
