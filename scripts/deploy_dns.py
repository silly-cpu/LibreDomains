#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DNS 记录部署脚本
负责通过 Cloudflare API 管理 DNS 记录
"""

import os
import sys
import json
import yaml
import requests
import argparse
from typing import Dict, Any, Optional
from datetime import datetime


class CloudflareAPI:
    """Cloudflare API 操作类"""
    
    def __init__(self, api_token: str):
        self.api_token = api_token
        self.base_url = "https://api.cloudflare.com/client/v4"
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }
    
    def get_zone_info(self, zone_id: str) -> Optional[Dict[str, Any]]:
        """获取域名区域信息"""
        try:
            response = requests.get(
                f"{self.base_url}/zones/{zone_id}",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json().get("result")
        except requests.RequestException as e:
            print(f"❌ 获取域名区域信息失败: {e}")
            return None
    
    def list_dns_records(self, zone_id: str, name: str = None) -> list:
        """列出 DNS 记录"""
        try:
            params = {}
            if name:
                params["name"] = name
            
            response = requests.get(
                f"{self.base_url}/zones/{zone_id}/dns_records",
                headers=self.headers,
                params=params
            )
            response.raise_for_status()
            return response.json().get("result", [])
        except requests.RequestException as e:
            print(f"❌ 获取 DNS 记录失败: {e}")
            return []
    
    def create_dns_record(self, zone_id: str, record_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """创建 DNS 记录"""
        try:
            response = requests.post(
                f"{self.base_url}/zones/{zone_id}/dns_records",
                headers=self.headers,
                json=record_data
            )
            response.raise_for_status()
            result = response.json()
            if result.get("success"):
                return result.get("result")
            else:
                print(f"❌ 创建 DNS 记录失败: {result.get('errors')}")
                return None
        except requests.RequestException as e:
            print(f"❌ 创建 DNS 记录失败: {e}")
            return None
    
    def update_dns_record(self, zone_id: str, record_id: str, record_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """更新 DNS 记录"""
        try:
            response = requests.put(
                f"{self.base_url}/zones/{zone_id}/dns_records/{record_id}",
                headers=self.headers,
                json=record_data
            )
            response.raise_for_status()
            result = response.json()
            if result.get("success"):
                return result.get("result")
            else:
                print(f"❌ 更新 DNS 记录失败: {result.get('errors')}")
                return None
        except requests.RequestException as e:
            print(f"❌ 更新 DNS 记录失败: {e}")
            return None
    
    def delete_dns_record(self, zone_id: str, record_id: str) -> bool:
        """删除 DNS 记录"""
        try:
            response = requests.delete(
                f"{self.base_url}/zones/{zone_id}/dns_records/{record_id}",
                headers=self.headers
            )
            response.raise_for_status()
            result = response.json()
            return result.get("success", False)
        except requests.RequestException as e:
            print(f"❌ 删除 DNS 记录失败: {e}")
            return False


class DNSDeployer:
    """DNS 部署器"""
    
    def __init__(self):
        self.api = None
        self.domains_config = None
        self.load_config()
    
    def load_config(self):
        """加载配置文件"""
        config_path = os.path.join(os.path.dirname(__file__), "..", "config", "domains.yml")
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                self.domains_config = yaml.safe_load(f)
        except FileNotFoundError:
            print(f"❌ 配置文件不存在: {config_path}")
            sys.exit(1)
        except yaml.YAMLError as e:
            print(f"❌ 配置文件格式错误: {e}")
            sys.exit(1)
    
    def init_api(self):
        """初始化 Cloudflare API"""
        api_token = os.getenv("CLOUDFLARE_API_TOKEN")
        if not api_token:
            print("❌ 未设置 CLOUDFLARE_API_TOKEN 环境变量")
            sys.exit(1)
        
        self.api = CloudflareAPI(api_token)
        print("✅ Cloudflare API 初始化成功")
    
    def deploy_request(self, request_file: str) -> bool:
        """部署单个请求"""
        try:
            with open(request_file, "r", encoding="utf-8") as f:
                request_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"❌ 读取请求文件失败: {e}")
            return False
        
        domain = request_data.get("domain")
        subdomain = request_data.get("subdomain")
        record = request_data.get("record")
        
        if not all([domain, subdomain, record]):
            print("❌ 请求文件缺少必要字段")
            return False
        
        # 检查域名是否可用
        domain_config = self.domains_config.get("domains", {}).get(domain)
        if not domain_config or not domain_config.get("enabled"):
            print(f"❌ 域名 {domain} 不可用")
            return False
        
        zone_id = domain_config.get("cloudflare_zone_id")
        if not zone_id:
            print(f"❌ 域名 {domain} 未配置 Zone ID")
            return False
        
        # 构建 DNS 记录数据
        full_domain = f"{subdomain}.{domain}"
        record_data = {
            "type": record["type"],
            "name": full_domain,
            "content": record["value"],
            "ttl": record.get("ttl", 3600),
            "proxied": record.get("proxied", False)
        }
        
        # MX 记录需要 priority
        if record["type"] == "MX":
            record_data["priority"] = record.get("priority", 10)
        
        # 检查是否已存在记录
        existing_records = self.api.list_dns_records(zone_id, full_domain)
        
        if existing_records:
            # 更新现有记录
            record_id = existing_records[0]["id"]
            result = self.api.update_dns_record(zone_id, record_id, record_data)
            if result:
                print(f"✅ 成功更新 DNS 记录: {full_domain}")
                self.save_domain_record(domain, subdomain, request_data)
                return True
        else:
            # 创建新记录
            result = self.api.create_dns_record(zone_id, record_data)
            if result:
                print(f"✅ 成功创建 DNS 记录: {full_domain}")
                self.save_domain_record(domain, subdomain, request_data)
                return True
        
        return False
    
    def delete_request(self, request_file: str) -> bool:
        """删除 DNS 记录"""
        try:
            with open(request_file, "r", encoding="utf-8") as f:
                request_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"❌ 读取请求文件失败: {e}")
            return False
        
        domain = request_data.get("domain")
        subdomain = request_data.get("subdomain")
        
        if not all([domain, subdomain]):
            print("❌ 请求文件缺少必要字段")
            return False
        
        domain_config = self.domains_config.get("domains", {}).get(domain)
        if not domain_config:
            print(f"❌ 域名 {domain} 不存在")
            return False
        
        zone_id = domain_config.get("cloudflare_zone_id")
        if not zone_id:
            print(f"❌ 域名 {domain} 未配置 Zone ID")
            return False
        
        full_domain = f"{subdomain}.{domain}"
        existing_records = self.api.list_dns_records(zone_id, full_domain)
        
        if not existing_records:
            print(f"⚠️ DNS 记录不存在: {full_domain}")
            return True
        
        # 删除所有匹配的记录
        success = True
        for record in existing_records:
            if not self.api.delete_dns_record(zone_id, record["id"]):
                success = False
        
        if success:
            print(f"✅ 成功删除 DNS 记录: {full_domain}")
            self.remove_domain_record(domain, subdomain)
        
        return success
    
    def save_domain_record(self, domain: str, subdomain: str, request_data: Dict[str, Any]):
        """保存域名记录到本地文件"""
        domain_dir = os.path.join(os.path.dirname(__file__), "..", "domains", domain)
        os.makedirs(domain_dir, exist_ok=True)
        
        record_file = os.path.join(domain_dir, f"{subdomain}.json")
        
        # 添加部署时间戳
        request_data["_metadata"] = {
            "deployed_at": datetime.now().isoformat(),
            "deployed_by": "github-actions"
        }
        
        with open(record_file, "w", encoding="utf-8") as f:
            json.dump(request_data, f, indent=2, ensure_ascii=False)
    
    def remove_domain_record(self, domain: str, subdomain: str):
        """删除本地域名记录文件"""
        record_file = os.path.join(os.path.dirname(__file__), "..", "domains", domain, f"{subdomain}.json")
        if os.path.exists(record_file):
            os.remove(record_file)


def main():
    parser = argparse.ArgumentParser(description="DNS 记录部署工具")
    parser.add_argument("action", choices=["deploy", "delete"], help="操作类型")
    parser.add_argument("request_file", help="请求文件路径")
    
    args = parser.parse_args()
    
    deployer = DNSDeployer()
    deployer.init_api()
    
    if args.action == "deploy":
        success = deployer.deploy_request(args.request_file)
    elif args.action == "delete":
        success = deployer.delete_request(args.request_file)
    else:
        print("❌ 未知操作类型")
        success = False
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
