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
from typing import Dict, List, Any, Optional, Tuple

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
        
        # 验证 API Token 权限
        self._validate_token()

    def _validate_token(self):
        """验证 API Token 的有效性和权限"""
        try:
            # 测试基本的 API 访问权限
            response = requests.get(
                f"{self.base_url}user/tokens/verify",
                headers=self.headers,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success', False):
                    token_info = result.get('result', {})
                    print(f"API Token 验证成功: {token_info.get('status', 'active')}", file=sys.stderr)
                else:
                    raise Exception(f"Token 验证失败: {result.get('errors', [])}")
            else:
                raise Exception(f"Token 验证请求失败: {response.status_code} - {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"警告: 无法验证 API Token: {str(e)}", file=sys.stderr)
        except Exception as e:
            print(f"警告: Token 验证异常: {str(e)}", file=sys.stderr)

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
    
    def _request(self, method: str, endpoint: str, data: dict = None, params: dict = None) -> Dict[str, Any]:
        """
        发送 API 请求
        
        Args:
            method: HTTP 方法
            endpoint: API 端点
            data: 请求数据 (可选)
            params: URL 参数 (可选)
        
        Returns:
            API 响应
        """
        url = self.base_url + endpoint.lstrip('/')
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=self.headers, params=params, timeout=self.timeout)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=self.headers, json=data, params=params, timeout=self.timeout)
            elif method.upper() == 'PUT':
                response = requests.put(url, headers=self.headers, json=data, params=params, timeout=self.timeout)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, headers=self.headers, params=params, timeout=self.timeout)
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
        endpoint = f'zones/{zone_id}/dns_records'
        
        try:
            # 首先验证 Zone 访问权限
            zone_valid, zone_msg = self.verify_zone_access(zone_id)
            if not zone_valid:
                raise Exception(f"Zone 访问验证失败: {zone_msg}")
            
            # 构建查询参数
            params = {}
            if record_type:
                params['type'] = record_type
            
            # 修复：分步查询，避免复杂的 name 参数问题
            url = self.base_url + endpoint.lstrip('/')
            response = requests.get(url, headers=self.headers, params=params, timeout=self.timeout)
            
            response.raise_for_status()
            result = response.json()
            
            if not result.get('success', False):
                errors = result.get('errors', [])
                error_details = []
                for err in errors:
                    if isinstance(err, dict):
                        error_details.append(f"Code: {err.get('code', 'N/A')}, Message: {err.get('message', str(err))}")
                    else:
                        error_details.append(str(err))
                raise Exception(f"Cloudflare API 错误: {'; '.join(error_details)}")
            
            records = result.get('result', [])
            
            # 如果指定了 name，手动过滤结果
            if name:
                filtered_records = []
                for record in records:
                    if record.get('name', '').lower() == name.lower():
                        filtered_records.append(record)
                return filtered_records
            
            return records
            
        except requests.exceptions.RequestException as e:
            error_msg = str(e)
            
            # 提供更详细的错误分析
            if "400 Client Error" in error_msg:
                debug_info = {
                    'zone_id': zone_id,
                    'params': params,
                    'api_token_type': 'Token' if self.is_token else 'Key',
                    'error': error_msg
                }
                
                # 尝试获取响应内容以获得更多信息
                try:
                    if hasattr(e, 'response') and e.response:
                        response_text = e.response.text
                        debug_info['response_body'] = response_text
                except:
                    pass
                
                raise Exception(f"DNS 记录查询失败 (400 错误):\n"
                              f"可能原因:\n"
                              f"1. API Token 缺少 Zone:Read 权限\n"
                              f"2. Zone ID '{zone_id}' 不正确或无权访问\n"
                              f"3. API Token 已过期或被撤销\n"
                              f"4. 查询参数格式错误\n"
                              f"调试信息: {debug_info}\n"
                              f"原始错误: {error_msg}")
            elif "401" in error_msg:
                raise Exception(f"API Token 认证失败 (401 错误):\n"
                              f"请检查:\n"
                              f"1. API Token 是否正确\n"
                              f"2. Token 是否已过期\n"
                              f"3. Token 权限是否足够\n"
                              f"原始错误: {error_msg}")
            elif "403" in error_msg:
                raise Exception(f"API Token 权限不足 (403 错误):\n"
                              f"请确保 API Token 具有以下权限:\n"
                              f"1. Zone:Read\n"
                              f"2. DNS:Edit\n"
                              f"3. 对应 Zone 的访问权限\n"
                              f"原始错误: {error_msg}")
            else:
                raise Exception(f"DNS 记录查询请求失败: {error_msg}")

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
        
        result = {
            'domain': domain,
            'subdomain': subdomain,
            'created': [],
            'updated': [],
            'deleted': [],
            'errors': [],
            'debug_info': {}
        }
        
        # 添加调试信息
        try:
            debug_info = self.debug_dns_query(zone_id, full_name)
            result['debug_info'] = debug_info
            
            if not debug_info.get('zone_access', {}).get('valid', False):
                result['errors'].append(f"Zone 访问失败: {debug_info['zone_access']['message']}")
                return result
                
        except Exception as e:
            result['errors'].append(f"调试查询失败: {str(e)}")
        
        # 获取现有记录 - 修复：直接获取所有记录，然后手动过滤
        existing_records = []
        try:
            all_records = self._request('GET', f'zones/{zone_id}/dns_records')
            all_records_list = all_records.get('result', [])
            
            # 手动过滤相关记录
            for record in records:
                name = record['name']
                if name == '@':
                    record_name = full_name
                else:
                    record_name = f"{name}.{full_name}" if subdomain != '@' else f"{name}.{domain}"
                
                # 查找匹配的现有记录
                matching_records = [
                    r for r in all_records_list 
                    if r.get('name', '').lower() == record_name.lower()
                ]
                existing_records.extend(matching_records)
                
        except Exception as e:
            result['errors'].append(f"获取现有记录失败: {str(e)}")
            return result
        
        # 创建记录映射
        existing_map = {}
        for record in existing_records:
            key = f"{record['type']}:{record['name']}"
            existing_map[key] = record
        
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

    def verify_zone_access(self, zone_id: str) -> Tuple[bool, str]:
        """
        验证 Zone 访问权限
        
        Args:
            zone_id: Zone ID
            
        Returns:
            (是否有访问权限, 错误信息)
        """
        try:
            url = f"{self.base_url}zones/{zone_id}"
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success', False):
                    zone_info = result.get('result', {})
                    zone_name = zone_info.get('name', 'Unknown')
                    return True, f"Zone '{zone_name}' 访问正常"
                else:
                    errors = result.get('errors', [])
                    error_msg = '; '.join([err.get('message', str(err)) for err in errors])
                    return False, f"Zone API 返回错误: {error_msg}"
            elif response.status_code == 403:
                return False, f"Zone 访问权限不足 (403): API Token 没有访问此 Zone 的权限"
            elif response.status_code == 404:
                return False, f"Zone 不存在 (404): Zone ID '{zone_id}' 可能不正确"
            elif response.status_code == 401:
                return False, f"API Token 认证失败 (401): Token 可能无效或已过期"
            else:
                return False, f"Zone 访问失败: HTTP {response.status_code} - {response.text}"
                
        except requests.exceptions.RequestException as e:
            return False, f"Zone 访问请求异常: {str(e)}"
        except Exception as e:
            return False, f"Zone 访问验证异常: {str(e)}"

    def debug_dns_query(self, zone_id: str, name: str = None) -> Dict[str, Any]:
        """
        调试 DNS 查询，提供详细的诊断信息
        
        Args:
            zone_id: Zone ID
            name: 记录名称 (可选)
            
        Returns:
            调试信息
        """
        debug_info = {
            'zone_id': zone_id,
            'query_name': name,
            'api_token_type': 'Token' if self.is_token else 'Key',
            'base_url': self.base_url,
            'timeout': self.timeout,
            'headers_masked': {k: v if k not in ['Authorization', 'X-Auth-Key'] else '***' for k, v in self.headers.items()}
        }
        
        # 验证 Zone 访问权限
        zone_valid, zone_msg = self.verify_zone_access(zone_id)
        debug_info['zone_access'] = {
            'valid': zone_valid,
            'message': zone_msg
        }
        
        if not zone_valid:
            return debug_info
            
        # 尝试获取所有记录（不使用 name 过滤）
        try:
            records = self.list_dns_records(zone_id)
            debug_info['total_records'] = len(records)
            
            if name:
                # 手动过滤记录
                matching_records = [
                    record for record in records
                    if record.get('name', '').lower() == name.lower()
                ]
                debug_info['matching_records'] = len(matching_records)
                debug_info['matching_record_details'] = [
                    {
                        'id': record.get('id'),
                        'name': record.get('name'),
                        'type': record.get('type'),
                        'content': record.get('content')
                    }
                    for record in matching_records
                ]
            
            # 显示前5条记录作为样本
            debug_info['sample_records'] = [
                {
                    'name': record.get('name'),
                    'type': record.get('type'),
                    'content': record.get('content')[:50] + ('...' if len(record.get('content', '')) > 50 else '')
                }
                for record in records[:5]
            ]
                
        except Exception as e:
            debug_info['records_query_error'] = str(e)
            
        return debug_info


def main():
    """命令行入口点"""
    parser = argparse.ArgumentParser(description='Cloudflare DNS 管理工具')
    parser.add_argument('--api-key', required=True, help='Cloudflare API Key 或 Token')
    parser.add_argument('--email', help='Cloudflare 邮箱 (使用 API Key 时需要)')
    parser.add_argument('--config', help='配置文件路径')
    parser.add_argument('--domain', required=True, help='域名')
    parser.add_argument('--subdomain', required=True, help='子域名')
    parser.add_argument('--json-file', help='JSON 配置文件路径')
    parser.add_argument('--action', choices=['list', 'sync', 'debug'], default='sync', help='操作类型')
    parser.add_argument('--debug', action='store_true', help='启用调试模式')
    
    args = parser.parse_args()
    
    try:
        manager = CloudflareManager(args.api_key, args.email, args.config)
        
        if args.action == 'debug':
            # 新增：调试模式
            zone_id = manager.get_zone_id(args.domain)
            full_name = f"{args.subdomain}.{args.domain}" if args.subdomain != '@' else args.domain
            
            print("=== 调试信息 ===")
            debug_info = manager.debug_dns_query(zone_id, full_name)
            print(json.dumps(debug_info, indent=2, ensure_ascii=False))
            
            return 0
        
        elif args.action == 'list':
            zone_id = manager.get_zone_id(args.domain)
            
            if args.debug:
                print("=== 调试模式启用 ===")
                debug_info = manager.debug_dns_query(zone_id)
                print("调试信息:")
                print(json.dumps(debug_info, indent=2, ensure_ascii=False))
                print("\n=== DNS 记录列表 ===")
            
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
        if args.debug:
            import traceback
            print("\n完整错误堆栈:")
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())