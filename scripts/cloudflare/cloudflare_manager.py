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
import argparse
import requests
from typing import Dict, List, Any, Optional

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from scripts.utils.common import load_json_file


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
            self.headers['X-Auth-Email'] = email
            self.headers['X-Auth-Key'] = api_key
        
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
            current_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(current_dir, '..', '..', 'config', 'domains.json')
        
        config, error = load_json_file(config_path)
        if error:
            raise Exception(f"加载配置文件失败: {error}")
        
        return config
    
    def _request(self, method: str, endpoint: str, data: dict = None) -> Dict[str, Any]:
        """
        发送 API 请求
        
        Args:
            method: HTTP 方法
            endpoint: API 端点
            data: 请求数据 (可选)
        
        Returns:
            API 响应
        """
        url = self.base_url + endpoint.lstrip('/')
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=self.headers, timeout=self.timeout)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=self.headers, json=data, timeout=self.timeout)
            elif method.upper() == 'PUT':
                response = requests.put(url, headers=self.headers, json=data, timeout=self.timeout)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, headers=self.headers, timeout=self.timeout)
            else:
                raise ValueError(f"不支持的 HTTP 方法: {method}")
            
            response.raise_for_status()
            result = response.json()
            
            if not result.get('success', False):
                errors = result.get('errors', [])
                error_msg = ', '.join([err.get('message', str(err)) for err in errors])
                raise Exception(f"Cloudflare API 错误: {error_msg}")
            
            return result
        
        except requests.exceptions.RequestException as e:
            raise Exception(f"请求失败: {str(e)}")
    
    def get_zone_id(self, domain: str) -> str:
        """
        获取域名的 Zone ID
        
        Args:
            domain: 域名
        
        Returns:
            Zone ID
        """
        if domain in self.zone_ids:
            return self.zone_ids[domain]
        
        raise Exception(f"未找到域名 '{domain}' 的 Zone ID")
    
    def list_dns_records(self, zone_id: str, record_type: str = None, name: str = None) -> List[Dict[str, Any]]:
        """
        列出 DNS 记录
        
        Args:
            zone_id: Zone ID
            record_type: 记录类型 (可选)
            name: 记录名称 (可选)
        
        Returns:
            DNS 记录列表
        """
        params = {}
        if record_type:
            params['type'] = record_type
        if name:
            params['name'] = name
        
        endpoint = f'zones/{zone_id}/dns_records'
        if params:
            endpoint += '?' + '&'.join([f'{k}={v}' for k, v in params.items()])
        
        result = self._request('GET', endpoint)
        return result.get('result', [])
    
    def create_dns_record(self, zone_id: str, record_type: str, name: str, content: str, 
                         ttl: int = 3600, proxied: bool = True, priority: int = None) -> Dict[str, Any]:
        """
        创建 DNS 记录
        
        Args:
            zone_id: Zone ID
            record_type: 记录类型
            name: 记录名称
            content: 记录内容
            ttl: TTL 值
            proxied: 是否启用代理
            priority: 优先级 (MX 记录)
        
        Returns:
            创建的记录信息
        """
        data = {
            'type': record_type,
            'name': name,
            'content': content,
            'ttl': ttl,
        }
        
        # 只有 A、AAAA、CNAME 记录支持代理
        if record_type in ['A', 'AAAA', 'CNAME']:
            data['proxied'] = proxied
        
        # MX 记录需要优先级
        if record_type == 'MX' and priority is not None:
            data['priority'] = priority
        
        result = self._request('POST', f'zones/{zone_id}/dns_records', data)
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
            ttl: TTL 值
            proxied: 是否启用代理
            priority: 优先级 (MX 记录)
        
        Returns:
            更新的记录信息
        """
        data = {
            'type': record_type,
            'name': name,
            'content': content,
            'ttl': ttl,
        }
        
        # 只有 A、AAAA、CNAME 记录支持代理
        if record_type in ['A', 'AAAA', 'CNAME']:
            data['proxied'] = proxied
        
        # MX 记录需要优先级
        if record_type == 'MX' and priority is not None:
            data['priority'] = priority
        
        result = self._request('PUT', f'zones/{zone_id}/dns_records/{record_id}', data)
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
        try:
            self._request('DELETE', f'zones/{zone_id}/dns_records/{record_id}')
            return True
        except Exception:
            return False
    
    def sync_domain_records(self, domain: str, subdomain: str, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        同步域名记录
        
        Args:
            domain: 主域名
            subdomain: 子域名
            records: 记录列表
        
        Returns:
            同步结果
        """
        zone_id = self.get_zone_id(domain)
        
        # 修复：构建完整的记录名称逻辑
        if subdomain == '@':
            full_name = domain
        else:
            full_name = f"{subdomain}.{domain}"
        
        # 获取现有记录 - 修复：应该获取所有相关记录，不只是精确匹配
        existing_records = []
        for record in records:
            name = record['name']
            if name == '@':
                record_name = full_name
            else:
                record_name = f"{name}.{full_name}" if subdomain != '@' else f"{name}.{domain}"
            
            # 获取该记录名称的现有记录
            existing_for_name = self.list_dns_records(zone_id, name=record_name)
            existing_records.extend(existing_for_name)
        
        # 创建记录映射
        existing_map = {}
        for record in existing_records:
            key = f"{record['type']}:{record['name']}"
            existing_map[key] = record
        
        result = {
            'domain': domain,
            'subdomain': subdomain,
            'created': [],
            'updated': [],
            'deleted': [],
            'errors': []
        }
        
        # 处理新记录
        new_map = {}
        for record in records:
            record_type = record['type']
            name = record['name']
            
            # 修复：构建记录名称逻辑
            if name == '@':
                record_name = full_name
            else:
                record_name = f"{name}.{full_name}" if subdomain != '@' else f"{name}.{domain}"
            
            key = f"{record_type}:{record_name}"
            new_map[key] = record
            
            try:
                if key in existing_map:
                    # 更新现有记录
                    existing_record = existing_map[key]
                    updated_record = self.update_dns_record(
                        zone_id=zone_id,
                        record_id=existing_record['id'],
                        record_type=record_type,
                        name=record_name,
                        content=record['content'],
                        ttl=record.get('ttl', 3600),
                        proxied=record.get('proxied', True),
                        priority=record.get('priority')
                    )
                    result['updated'].append(updated_record)
                else:
                    # 创建新记录
                    created_record = self.create_dns_record(
                        zone_id=zone_id,
                        record_type=record_type,
                        name=record_name,
                        content=record['content'],
                        ttl=record.get('ttl', 3600),
                        proxied=record.get('proxied', True),
                        priority=record.get('priority')
                    )
                    result['created'].append(created_record)
            
            except Exception as e:
                result['errors'].append(f"处理记录 {key} 时出错: {str(e)}")
        
        # 删除不再需要的记录
        for key, existing_record in existing_map.items():
            if key not in new_map:
                try:
                    if self.delete_dns_record(zone_id, existing_record['id']):
                        result['deleted'].append(existing_record)
                    else:
                        result['errors'].append(f"删除记录 {key} 失败")
                except Exception as e:
                    result['errors'].append(f"删除记录 {key} 时出错: {str(e)}")
        
        return result


def main():
    """命令行入口点"""
    parser = argparse.ArgumentParser(description='Cloudflare DNS 管理工具')
    parser.add_argument('--api-key', required=True, help='Cloudflare API Key 或 Token')
    parser.add_argument('--email', help='Cloudflare 邮箱 (使用 API Key 时需要)')
    parser.add_argument('--config', help='配置文件路径')
    parser.add_argument('--domain', required=True, help='域名')
    parser.add_argument('--subdomain', required=True, help='子域名')
    parser.add_argument('--json-file', help='JSON 配置文件路径')
    parser.add_argument('--action', choices=['list', 'sync'], default='sync', help='操作类型')
    
    args = parser.parse_args()
    
    try:
        manager = CloudflareManager(args.api_key, args.email, args.config)
        
        if args.action == 'list':
            zone_id = manager.get_zone_id(args.domain)
            records = manager.list_dns_records(zone_id)
            print(json.dumps(records, indent=2, ensure_ascii=False))
        
        elif args.action == 'sync':
            if not args.json_file:
                print("错误: 同步操作需要指定 JSON 配置文件")
                return 1
            
            # 加载域名配置
            config, error = load_json_file(args.json_file)
            if error:
                print(f"错误: {error}")
                return 1
            
            records = config.get('records', [])
            result = manager.sync_domain_records(args.domain, args.subdomain, records)
            
            print("同步结果:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
            if result['errors']:
                return 1
        
        return 0
        
    except Exception as e:
        print(f"错误: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())