#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Cloudflare DNS 管理模块

此模块提供了与 Cloudflare API 交互的功能，用于管理域名的 DNS 记录。
"""

import json
import os
import sys
import time
from typing import Dict, List, Any, Optional

import requests

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))


class CloudflareManager:
    """Cloudflare API 管理类"""

    def __init__(self, api_key: str, email: str = None, config_path: str = None):
        """
        初始化 Cloudflare 管理器
        
        Args:
            api_key: Cloudflare API 密钥或 API Token
            email: Cloudflare 账户邮箱 (使用 API Key 时需要)
            config_path: 配置文件路径 (可选，默认为项目根目录下的 config/domains.json)
        """
        self.api_key = api_key
        self.email = email
        self.base_url = "https://api.cloudflare.com/client/v4/"
        
        # 确定是使用 API Key 还是 API Token
        self.is_token = not email
        
        # 设置请求头
        self.headers = {
            'Content-Type': 'application/json',
        }
        
        if self.is_token:
            self.headers['Authorization'] = f'Bearer {api_key}'
        else:
            self.headers['X-Auth-Key'] = api_key
            self.headers['X-Auth-Email'] = email
        
        # 加载配置
        self.config = self._load_config(config_path)
        
        # 初始化域名 zone ID 映射
        self.zone_ids = {}
        for domain_config in self.config.get('domains', []):
            domain_name = domain_config.get('name')
            zone_id = domain_config.get('cloudflare_zone_id')
            if domain_name and zone_id:
                self.zone_ids[domain_name] = zone_id
        
        # 设置请求超时
        self.timeout = self.config.get('cloudflare_timeout', 30)

    def _load_config(self, config_path: str = None) -> Dict[str, Any]:
        """
        加载配置文件
        
        Args:
            config_path: 配置文件路径
        
        Returns:
            配置信息字典
        """
        if config_path is None:
            config_path = os.path.join(os.path.dirname(__file__), '../../config/domains.json')
        
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _request(self, method: str, endpoint: str, data: dict = None) -> Dict[str, Any]:
        """
        发送请求到 Cloudflare API
        
        Args:
            method: 请求方法 (GET, POST, PUT, DELETE)
            endpoint: API 端点
            data: 请求数据
        
        Returns:
            API 响应
        
        Raises:
            Exception: 如果请求失败
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=self.headers, timeout=self.timeout)
            elif method == 'POST':
                response = requests.post(url, headers=self.headers, json=data, timeout=self.timeout)
            elif method == 'PUT':
                response = requests.put(url, headers=self.headers, json=data, timeout=self.timeout)
            elif method == 'DELETE':
                response = requests.delete(url, headers=self.headers, timeout=self.timeout)
            else:
                raise ValueError(f"不支持的请求方法: {method}")
            
            response.raise_for_status()
            result = response.json()
            
            if not result.get('success'):
                errors = result.get('errors', [])
                error_msgs = [f"{e.get('code')}: {e.get('message')}" for e in errors]
                raise Exception(f"API 请求失败: {', '.join(error_msgs)}")
            
            return result
        
        except requests.exceptions.RequestException as e:
            raise Exception(f"请求错误: {str(e)}")
    
    def get_zone_id(self, domain: str) -> str:
        """
        获取域名的 Zone ID
        
        Args:
            domain: 域名
        
        Returns:
            Zone ID
        
        Raises:
            ValueError: 如果域名不在配置中
        """
        if domain in self.zone_ids:
            return self.zone_ids[domain]
        
        raise ValueError(f"未找到域名 '{domain}' 的 Zone ID，请在配置文件中添加")
    
    def list_dns_records(self, zone_id: str, record_type: str = None, name: str = None) -> List[Dict[str, Any]]:
        """
        列出 DNS 记录
        
        Args:
            zone_id: Zone ID
            record_type: 记录类型 (A, AAAA, CNAME, TXT, MX, ...)
            name: 记录名称
        
        Returns:
            记录列表
        """
        params = {}
        if record_type:
            params['type'] = record_type
        if name:
            params['name'] = name
        
        endpoint = f"zones/{zone_id}/dns_records"
        if params:
            endpoint += "?" + "&".join([f"{k}={v}" for k, v in params.items()])
        
        result = self._request('GET', endpoint)
        return result.get('result', [])
    
    def create_dns_record(self, zone_id: str, record_type: str, name: str, content: str, 
                         ttl: int = 3600, proxied: bool = True, priority: int = None) -> Dict[str, Any]:
        """
        创建 DNS 记录
        
        Args:
            zone_id: Zone ID
            record_type: 记录类型 (A, AAAA, CNAME, TXT, MX, ...)
            name: 记录名称
            content: 记录内容
            ttl: TTL (秒)
            proxied: 是否使用 Cloudflare 代理
            priority: 优先级 (仅用于 MX 和 SRV 记录)
        
        Returns:
            创建的记录
        """
        data = {
            'type': record_type,
            'name': name,
            'content': content,
            'ttl': ttl,
            'proxied': proxied if record_type in ['A', 'AAAA', 'CNAME'] else False
        }
        
        # MX 记录需要优先级
        if record_type == 'MX' and priority is not None:
            data['priority'] = priority
        
        result = self._request('POST', f"zones/{zone_id}/dns_records", data)
        return result.get('result', {})
    
    def update_dns_record(self, zone_id: str, record_id: str, record_type: str, name: str, 
                         content: str, ttl: int = 3600, proxied: bool = True, priority: int = None) -> Dict[str, Any]:
        """
        更新 DNS 记录
        
        Args:
            zone_id: Zone ID
            record_id: 记录 ID
            record_type: 记录类型
            name: 记录名称
            content: 记录内容
            ttl: TTL (秒)
            proxied: 是否使用 Cloudflare 代理
            priority: 优先级 (仅用于 MX 和 SRV 记录)
        
        Returns:
            更新后的记录
        """
        data = {
            'type': record_type,
            'name': name,
            'content': content,
            'ttl': ttl,
            'proxied': proxied if record_type in ['A', 'AAAA', 'CNAME'] else False
        }
        
        # MX 记录需要优先级
        if record_type == 'MX' and priority is not None:
            data['priority'] = priority
        
        result = self._request('PUT', f"zones/{zone_id}/dns_records/{record_id}", data)
        return result.get('result', {})
    
    def delete_dns_record(self, zone_id: str, record_id: str) -> bool:
        """
        删除 DNS 记录
        
        Args:
            zone_id: Zone ID
            record_id: 记录 ID
        
        Returns:
            是否删除成功
        """
        result = self._request('DELETE', f"zones/{zone_id}/dns_records/{record_id}")
        return result.get('success', False)
    
    def sync_domain_records(self, domain: str, subdomain: str, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        同步域名的 DNS 记录
        
        Args:
            domain: 主域名
            subdomain: 子域名
            records: 记录列表
        
        Returns:
            同步结果
        """
        zone_id = self.get_zone_id(domain)
        result = {
            'created': [],
            'updated': [],
            'deleted': [],
            'unchanged': [],
            'errors': []
        }
        
        try:
            # 获取当前记录
            current_records = {}
            for record in self.list_dns_records(zone_id):
                record_name = record.get('name', '')
                
                # 匹配子域名记录
                # 例如: subdomain.example.com 或 example.com (@)
                if (subdomain != '@' and record_name == f"{subdomain}.{domain}") or \
                   (subdomain == '@' and record_name == domain):
                    key = (record.get('type'), record.get('name'))
                    current_records[key] = record
            
            # 处理新记录
            new_record_keys = set()
            for record in records:
                record_type = record.get('type')
                record_name = record.get('name')
                
                # 根据 record_name 构建完整名称
                if record_name == '@':
                    full_name = domain
                else:
                    if subdomain == '@':
                        full_name = f"{record_name}.{domain}"
                    else:
                        full_name = f"{record_name}.{subdomain}.{domain}"
                
                key = (record_type, full_name)
                new_record_keys.add(key)
                
                # 准备记录数据
                record_data = {
                    'type': record_type,
                    'name': full_name,
                    'content': record.get('content'),
                    'ttl': record.get('ttl', 3600),
                    'proxied': record.get('proxied', True)
                }
                
                # 添加 MX 优先级
                if record_type == 'MX' and 'priority' in record:
                    record_data['priority'] = record.get('priority')
                
                # 更新或创建记录
                if key in current_records:
                    current_record = current_records[key]
                    
                    # 检查记录是否有变化
                    needs_update = False
                    if record_data['content'] != current_record.get('content'):
                        needs_update = True
                    if record_data['ttl'] != current_record.get('ttl'):
                        needs_update = True
                    if record_type in ['A', 'AAAA', 'CNAME']:
                        if record_data['proxied'] != current_record.get('proxied'):
                            needs_update = True
                    if record_type == 'MX' and 'priority' in record_data:
                        if record_data['priority'] != current_record.get('priority'):
                            needs_update = True
                    
                    if needs_update:
                        updated_record = self.update_dns_record(
                            zone_id, 
                            current_record['id'],
                            record_data['type'],
                            record_data['name'],
                            record_data['content'],
                            record_data['ttl'],
                            record_data.get('proxied', False),
                            record_data.get('priority')
                        )
                        result['updated'].append(updated_record)
                    else:
                        result['unchanged'].append(current_record)
                else:
                    created_record = self.create_dns_record(
                        zone_id,
                        record_data['type'],
                        record_data['name'],
                        record_data['content'],
                        record_data['ttl'],
                        record_data.get('proxied', False),
                        record_data.get('priority')
                    )
                    result['created'].append(created_record)
            
            # 删除不再需要的记录
            for key, record in current_records.items():
                if key not in new_record_keys:
                    success = self.delete_dns_record(zone_id, record['id'])
                    if success:
                        result['deleted'].append(record)
                    else:
                        result['errors'].append({
                            'message': f"删除记录失败: {record['id']}",
                            'record': record
                        })
            
            return result
            
        except Exception as e:
            result['errors'].append({
                'message': str(e)
            })
            return result


def main():
    """命令行入口点"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Cloudflare DNS 管理工具')
    parser.add_argument('--api-key', required=True, help='Cloudflare API Key 或 Token')
    parser.add_argument('--email', help='Cloudflare 邮箱 (使用 API Key 时需要)')
    parser.add_argument('--config', help='配置文件路径')
    parser.add_argument('--domain', required=True, help='域名')
    parser.add_argument('--subdomain', required=True, help='子域名')
    parser.add_argument('--json-file', help='JSON 配置文件路径')
    parser.add_argument('--action', choices=['list', 'sync'], default='list', help='操作类型')
    
    args = parser.parse_args()
    
    try:
        # 初始化管理器
        cf = CloudflareManager(args.api_key, args.email, args.config)
        
        if args.action == 'list':
            # 获取 Zone ID
            zone_id = cf.get_zone_id(args.domain)
            
            # 构建子域名完整名称
            if args.subdomain == '@':
                name = args.domain
            else:
                name = f"{args.subdomain}.{args.domain}"
            
            # 列出 DNS 记录
            records = cf.list_dns_records(zone_id, name=name)
            print(json.dumps(records, indent=2, ensure_ascii=False))
            
        elif args.action == 'sync':
            if not args.json_file:
                print("错误: 同步操作需要提供 JSON 配置文件路径")
                return 1
                
            # 加载 JSON 配置
            with open(args.json_file, 'r', encoding='utf-8') as f:
                domain_config = json.load(f)
            
            # 同步 DNS 记录
            result = cf.sync_domain_records(args.domain, args.subdomain, domain_config.get('records', []))
            
            # 打印结果
            print("DNS 记录同步结果:")
            print(f"- 创建: {len(result['created'])}")
            print(f"- 更新: {len(result['updated'])}")
            print(f"- 删除: {len(result['deleted'])}")
            print(f"- 未变: {len(result['unchanged'])}")
            print(f"- 错误: {len(result['errors'])}")
            
            # 如果有错误，打印错误信息并返回错误代码
            if result['errors']:
                print("\n错误详情:")
                for error in result['errors']:
                    print(f"- {error.get('message')}")
                return 1
        
        return 0
        
    except Exception as e:
        print(f"错误: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())