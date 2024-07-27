import os
import json
import requests

# 从环境变量中获取 Cloudflare 相关配置
CLOUDFLARE_API_TOKEN = os.getenv('CLOUDFLARE_API_TOKEN')
ZONE_ID = os.getenv('CLOUDFLARE_ZONE_ID')

if not CLOUDFLARE_API_TOKEN or not ZONE_ID:
    print("Error: CLOUDFLARE_API_TOKEN or ZONE_ID is not set")
    exit(1)

headers = {
    "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
    "Content-Type": "application/json"
}

def update_dns_record(file_path):
    with open(file_path) as f:
        record = json.load(f)
    url = f"https://api.cloudflare.com/client/v4/zones/{ZONE_ID}/dns_records"
    response = requests.post(url, headers=headers, json=record)
    if response.status_code == 200:
        print(f"Successfully updated DNS record for {record['name']}")
    else:
        print(f"Failed to update DNS record for {record['name']}: {response.text}")

def main():
    for root, dirs, files in os.walk('domains'):
        for file in files:
            if file.endswith('.json'):
                update_dns_record(os.path.join(root, file))

if __name__ == "__main__":
    main()