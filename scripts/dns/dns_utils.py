#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
DNS 工具函数模块

此模块提供了 DNS 记录相关的工具函数。
"""

import socket
import time
from typing import Dict, List, Any, Optional, Union, Tuple

try:
    import dns.resolver
    DNS_RESOLVER_AVAILABLE = True
except ImportError:
    DNS_RESOLVER_AVAILABLE = False


def resolve_a_record(domain: str, timeout: int = 5) -> Tuple[List[str], Optional[str]]:
    """
    解析 A 记录
    
    Args:
        domain: 域名
        timeout: 超时时间 (秒)
    
    Returns:
        (IP列表, 错误信息)
    """
    try:
        if DNS_RESOLVER_AVAILABLE:
            resolver = dns.resolver.Resolver()
            resolver.timeout = timeout
            resolver.lifetime = timeout
            answers = resolver.resolve(domain, 'A')
            return [str(answer) for answer in answers], None
        else:
            # 使用标准库
            socket.setdefaulttimeout(timeout)
            addresses = socket.gethostbyname_ex(domain)[2]
            return addresses, None
    except Exception as e:
        return [], f"解析 A 记录错误: {str(e)}"


def resolve_aaaa_record(domain: str, timeout: int = 5) -> Tuple[List[str], Optional[str]]:
    """
    解析 AAAA 记录
    
    Args:
        domain: 域名
        timeout: 超时时间 (秒)
    
    Returns:
        (IPv6列表, 错误信息)
    """
    try:
        if DNS_RESOLVER_AVAILABLE:
            resolver = dns.resolver.Resolver()
            resolver.timeout = timeout
            resolver.lifetime = timeout
            answers = resolver.resolve(domain, 'AAAA')
            return [str(answer) for answer in answers], None
        else:
            # 使用标准库
            socket.setdefaulttimeout(timeout)
            # 获取 IPv6 地址
            addresses = []
            try:
                infos = socket.getaddrinfo(domain, None, socket.AF_INET6)
                addresses = [info[4][0] for info in infos]
            except socket.gaierror:
                pass
            return addresses, None
    except Exception as e:
        return [], f"解析 AAAA 记录错误: {str(e)}"


def resolve_cname_record(domain: str, timeout: int = 5) -> Tuple[List[str], Optional[str]]:
    """
    解析 CNAME 记录
    
    Args:
        domain: 域名
        timeout: 超时时间 (秒)
    
    Returns:
        (CNAME列表, 错误信息)
    """
    try:
        if DNS_RESOLVER_AVAILABLE:
            resolver = dns.resolver.Resolver()
            resolver.timeout = timeout
            resolver.lifetime = timeout
            answers = resolver.resolve(domain, 'CNAME')
            return [str(answer.target) for answer in answers], None
        else:
            # 使用标准库
            socket.setdefaulttimeout(timeout)
            try:
                cname = socket.gethostbyname_ex(domain)[0]
                return [cname] if cname != domain else [], None
            except socket.gaierror:
                return [], None
    except Exception as e:
        return [], f"解析 CNAME 记录错误: {str(e)}"


def resolve_txt_record(domain: str, timeout: int = 5) -> Tuple[List[str], Optional[str]]:
    """
    解析 TXT 记录
    
    Args:
        domain: 域名
        timeout: 超时时间 (秒)
    
    Returns:
        (TXT列表, 错误信息)
    """
    if not DNS_RESOLVER_AVAILABLE:
        return [], "DNS 解析库不可用，无法解析 TXT 记录"
        
    try:
        resolver = dns.resolver.Resolver()
        resolver.timeout = timeout
        resolver.lifetime = timeout
        answers = resolver.resolve(domain, 'TXT')
        return [str(answer).strip('"') for answer in answers], None
    except Exception as e:
        return [], f"解析 TXT 记录错误: {str(e)}"


def resolve_mx_record(domain: str, timeout: int = 5) -> Tuple[List[Dict[str, Union[str, int]]], Optional[str]]:
    """
    解析 MX 记录
    
    Args:
        domain: 域名
        timeout: 超时时间 (秒)
    
    Returns:
        (MX记录列表, 错误信息)
    """
    if not DNS_RESOLVER_AVAILABLE:
        return [], "DNS 解析库不可用，无法解析 MX 记录"
        
    try:
        resolver = dns.resolver.Resolver()
        resolver.timeout = timeout
        resolver.lifetime = timeout
        answers = resolver.resolve(domain, 'MX')
        
        mx_records = []
        for answer in answers:
            mx_records.append({
                'exchange': str(answer.exchange),
                'preference': answer.preference
            })
        
        return mx_records, None
    except Exception as e:
        return [], f"解析 MX 记录错误: {str(e)}"


def check_dns_propagation(domain: str, record_type: str, expected_value: str, timeout: int = 5, max_retries: int = 10, retry_delay: int = 30) -> Tuple[bool, Optional[str]]:
    """
    检查 DNS 记录传播
    
    Args:
        domain: 域名
        record_type: 记录类型
        expected_value: 预期值
        timeout: 超时时间 (秒)
        max_retries: 最大重试次数
        retry_delay: 重试延迟 (秒)
    
    Returns:
        (是否传播完成, 错误信息)
    """
    for i in range(max_retries):
        if i > 0:
            time.sleep(retry_delay)
        
        try:
            if record_type == 'A':
                values, error = resolve_a_record(domain, timeout)
                if error:
                    continue
                if expected_value in values:
                    return True, None
                
            elif record_type == 'AAAA':
                values, error = resolve_aaaa_record(domain, timeout)
                if error:
                    continue
                if expected_value in values:
                    return True, None
                
            elif record_type == 'CNAME':
                values, error = resolve_cname_record(domain, timeout)
                if error:
                    continue
                
                expected = expected_value[:-1] if expected_value.endswith('.') else expected_value
                for value in values:
                    actual = value[:-1] if value.endswith('.') else value
                    if expected.lower() == actual.lower():
                        return True, None
                
            elif record_type == 'TXT':
                values, error = resolve_txt_record(domain, timeout)
                if error:
                    continue
                if expected_value in values:
                    return True, None
                
            elif record_type == 'MX':
                records, error = resolve_mx_record(domain, timeout)
                if error:
                    continue
                
                expected = expected_value[:-1] if expected_value.endswith('.') else expected_value
                for record in records:
                    exchange = record['exchange']
                    exchange = exchange[:-1] if exchange.endswith('.') else exchange
                    if expected.lower() == exchange.lower():
                        return True, None
        
        except Exception as e:
            continue
    
    return False, f"DNS 记录传播超时，未找到预期值 '{expected_value}'"


def get_record_fqdn(domain: str, subdomain: str, name: str = '@') -> str:
    """
    获取记录的完整域名
    
    Args:
        domain: 主域名
        subdomain: 子域名
        name: 记录名称
    
    Returns:
        完整域名
    """
    if name == '@':
        if subdomain == '@':
            return domain
        return f"{subdomain}.{domain}"
    else:
        if subdomain == '@':
            return f"{name}.{domain}"
        return f"{name}.{subdomain}.{domain}"
