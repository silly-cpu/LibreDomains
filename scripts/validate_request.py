#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
请求验证脚本
验证子域名申请的格式、内容和规则
"""

import os
import sys
import json
import yaml
import re
import requests
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import jsonschema


class RequestValidator:
    """请求验证器"""
    
    def __init__(self):
        self.domains_config = None
        self.schema = None
        self.load_config()
        self.load_schema()
    
    def load_config(self):
        """加载域名配置"""
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
    
    def load_schema(self):
        """加载 JSON Schema"""
        schema_path = os.path.join(os.path.dirname(__file__), "..", "config", "schema.json")
        try:
            with open(schema_path, "r", encoding="utf-8") as f:
                self.schema = json.load(f)
        except FileNotFoundError:
            print(f"❌ Schema 文件不存在: {schema_path}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"❌ Schema 文件格式错误: {e}")
            sys.exit(1)
    
    def validate_json_schema(self, request_data: Dict[str, Any]) -> List[str]:
        """验证 JSON Schema"""
        errors = []
        try:
            jsonschema.validate(request_data, self.schema)
        except jsonschema.ValidationError as e:
            errors.append(f"Schema 验证失败: {e.message}")
        except jsonschema.SchemaError as e:
            errors.append(f"Schema 定义错误: {e.message}")
        
        return errors
    
    def validate_domain_availability(self, domain: str) -> List[str]:
        """验证域名可用性"""
        errors = []
        
        domain_config = self.domains_config.get("domains", {}).get(domain)
        if not domain_config:
            errors.append(f"域名 {domain} 不存在于配置中")
            return errors
        
        if not domain_config.get("enabled", False):
            errors.append(f"域名 {domain} 当前不接受申请")
        
        return errors
    
    def validate_subdomain_availability(self, domain: str, subdomain: str) -> List[str]:
        """验证子域名可用性"""
        errors = []
        
        # 检查是否在禁用列表中
        blocked_subdomains = self.domains_config.get("settings", {}).get("blocked_subdomains", [])
        if subdomain.lower() in [s.lower() for s in blocked_subdomains]:
            errors.append(f"子域名 '{subdomain}' 被禁用")
        
        # 检查是否已被占用
        domain_dir = os.path.join(os.path.dirname(__file__), "..", "domains", domain)
        if os.path.exists(os.path.join(domain_dir, f"{subdomain}.json")):
            errors.append(f"子域名 '{subdomain}.{domain}' 已被占用")
        
        return errors
    
    def validate_record_format(self, record: Dict[str, Any]) -> List[str]:
        """验证 DNS 记录格式"""
        errors = []
        
        record_type = record.get("type", "").upper()
        value = record.get("value", "")
        
        if record_type == "A":
            # IPv4 地址验证
            if not self.is_valid_ipv4(value):
                errors.append(f"无效的 IPv4 地址: {value}")
        
        elif record_type == "AAAA":
            # IPv6 地址验证
            if not self.is_valid_ipv6(value):
                errors.append(f"无效的 IPv6 地址: {value}")
        
        elif record_type == "CNAME":
            # CNAME 记录验证
            if not self.is_valid_domain(value):
                errors.append(f"无效的域名: {value}")
        
        elif record_type == "MX":
            # MX 记录验证
            if not self.is_valid_domain(value):
                errors.append(f"无效的邮件服务器域名: {value}")
            if "priority" not in record:
                errors.append("MX 记录缺少 priority 字段")
        
        elif record_type == "TXT":
            # TXT 记录验证 (长度限制)
            if len(value) > 255:
                errors.append("TXT 记录值过长（最大 255 字符）")
        
        elif record_type == "SRV":
            # SRV 记录格式验证
            if not self.is_valid_srv_record(value):
                errors.append(f"无效的 SRV 记录格式: {value}")
        
        return errors
    
    def validate_user_limits(self, username: str, domain: str) -> List[str]:
        """验证用户限制"""
        errors = []
        
        # 检查用户是否被禁用
        blocked_users = self.domains_config.get("settings", {}).get("blocked_users", [])
        if username.lower() in [u.lower() for u in blocked_users]:
            errors.append(f"用户 '{username}' 已被禁用")
            return errors
        
        # 检查用户已有的子域名数量
        max_subdomains = self.domains_config.get("settings", {}).get("max_subdomains_per_user", 3)
        user_subdomains = self.count_user_subdomains(username)
        
        if user_subdomains >= max_subdomains:
            errors.append(f"用户 '{username}' 已达到最大子域名数量限制 ({max_subdomains})")
        
        return errors
    
    def validate_github_user(self, username: str, email: str) -> List[str]:
        """验证 GitHub 用户"""
        errors = []
        
        if not self.domains_config.get("settings", {}).get("require_github_verification", True):
            return errors
        
        try:
            # 获取 GitHub 用户信息
            response = requests.get(f"https://api.github.com/users/{username}")
            if response.status_code == 404:
                errors.append(f"GitHub 用户 '{username}' 不存在")
                return errors
            
            response.raise_for_status()
            user_data = response.json()
            
            # 检查账户年龄
            created_at = datetime.fromisoformat(user_data["created_at"].replace("Z", "+00:00"))
            min_age_days = self.domains_config.get("settings", {}).get("min_account_age_days", 30)
            
            if (datetime.now().astimezone() - created_at).days < min_age_days:
                errors.append(f"GitHub 账户年龄不足 {min_age_days} 天")
            
            # 检查邮箱（如果公开）
            if user_data.get("email") and user_data["email"] != email:
                errors.append("提供的邮箱与 GitHub 公开邮箱不匹配")
        
        except requests.RequestException as e:
            errors.append(f"无法验证 GitHub 用户: {e}")
        
        return errors
    
    def count_user_subdomains(self, username: str) -> int:
        """统计用户已有的子域名数量"""
        count = 0
        domains_dir = os.path.join(os.path.dirname(__file__), "..", "domains")
        
        if not os.path.exists(domains_dir):
            return 0
        
        for domain_folder in os.listdir(domains_dir):
            domain_path = os.path.join(domains_dir, domain_folder)
            if not os.path.isdir(domain_path):
                continue
            
            for file in os.listdir(domain_path):
                if file.endswith(".json"):
                    file_path = os.path.join(domain_path, file)
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            data = json.load(f)
                            if data.get("owner", {}).get("username", "").lower() == username.lower():
                                count += 1
                    except (json.JSONDecodeError, FileNotFoundError):
                        continue
        
        return count
    
    def is_valid_ipv4(self, ip: str) -> bool:
        """验证 IPv4 地址"""
        pattern = r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
        return bool(re.match(pattern, ip))
    
    def is_valid_ipv6(self, ip: str) -> bool:
        """验证 IPv6 地址"""
        try:
            import ipaddress
            ipaddress.IPv6Address(ip)
            return True
        except ValueError:
            return False
    
    def is_valid_domain(self, domain: str) -> bool:
        """验证域名格式"""
        if len(domain) > 253:
            return False
        
        pattern = r'^([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)*[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?$'
        return bool(re.match(pattern, domain))
    
    def is_valid_srv_record(self, value: str) -> bool:
        """验证 SRV 记录格式"""
        # SRV 记录格式: priority weight port target
        parts = value.split()
        if len(parts) != 4:
            return False
        
        try:
            priority = int(parts[0])
            weight = int(parts[1])
            port = int(parts[2])
            target = parts[3]
            
            return (0 <= priority <= 65535 and 
                    0 <= weight <= 65535 and 
                    0 <= port <= 65535 and 
                    self.is_valid_domain(target))
        except ValueError:
            return False
    
    def validate_request(self, request_file: str) -> Dict[str, Any]:
        """验证完整请求"""
        result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        try:
            with open(request_file, "r", encoding="utf-8") as f:
                request_data = json.load(f)
        except FileNotFoundError:
            result["valid"] = False
            result["errors"].append(f"请求文件不存在: {request_file}")
            return result
        except json.JSONDecodeError as e:
            result["valid"] = False
            result["errors"].append(f"JSON 格式错误: {e}")
            return result
        
        # JSON Schema 验证
        errors = self.validate_json_schema(request_data)
        result["errors"].extend(errors)
        
        if errors:
            result["valid"] = False
            return result
        
        domain = request_data["domain"]
        subdomain = request_data["subdomain"]
        owner = request_data["owner"]
        record = request_data["record"]
        
        # 域名可用性验证
        result["errors"].extend(self.validate_domain_availability(domain))
        
        # 子域名可用性验证
        result["errors"].extend(self.validate_subdomain_availability(domain, subdomain))
        
        # DNS 记录格式验证
        result["errors"].extend(self.validate_record_format(record))
        
        # 用户限制验证
        result["errors"].extend(self.validate_user_limits(owner["username"], domain))
        
        # GitHub 用户验证
        result["errors"].extend(self.validate_github_user(owner["username"], owner["email"]))
        
        # 如果有错误，标记为无效
        if result["errors"]:
            result["valid"] = False
        
        return result


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="验证子域名申请请求")
    parser.add_argument("request_file", help="请求文件路径")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    
    args = parser.parse_args()
    
    validator = RequestValidator()
    result = validator.validate_request(args.request_file)
    
    print(f"📄 验证文件: {args.request_file}")
    print()
    
    if result["valid"]:
        print("✅ 验证通过")
    else:
        print("❌ 验证失败")
        print()
        print("错误信息:")
        for error in result["errors"]:
            print(f"  • {error}")
        
        if result["warnings"]:
            print()
            print("警告信息:")
            for warning in result["warnings"]:
                print(f"  • {warning}")
    
    if args.verbose:
        print()
        print("详细结果:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    sys.exit(0 if result["valid"] else 1)


if __name__ == "__main__":
    main()
