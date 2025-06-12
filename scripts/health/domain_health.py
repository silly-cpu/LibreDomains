#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
域名健康检查模块

此模块提供了检查域名健康状态的功能。
"""

import json
import os
import socket
import sys
import time
import datetime
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Any, Optional, Tuple

import requests

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))


def load_config(config_path: str = None) -> Dict[str, Any]:
    """
    加载配置文件
    
    Args:
        config_path: 配置文件路径 (可选，默认为项目根目录下的 config/domains.json)
    
    Returns:
        配置信息字典
    """
    if config_path is None:
        config_path = os.path.join(os.path.dirname(__file__), '../../config/domains.json')
    
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_domain_files(domain: str, domains_dir: str = None) -> List[str]:
    """
    获取域名目录下的所有 JSON 文件
    
    Args:
        domain: 域名
        domains_dir: 域名目录路径 (可选，默认为项目根目录下的 domains/)
    
    Returns:
        文件路径列表
    """
    if domains_dir is None:
        domains_dir = os.path.join(os.path.dirname(__file__), '../../domains')
    
    domain_dir = os.path.join(domains_dir, domain)
    
    if not os.path.isdir(domain_dir):
        return []
    
    return [os.path.join(domain_dir, f) for f in os.listdir(domain_dir) if f.endswith('.json') and f != 'example.json']


def load_domain_config(file_path: str) -> Optional[Dict[str, Any]]:
    """
    加载域名配置文件
    
    Args:
        file_path: 配置文件路径
    
    Returns:
        配置信息字典，如果加载失败则为 None
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return None


def get_record_fqdn(domain: str, subdomain: str, record: Dict[str, Any]) -> str:
    """
    获取记录的完整域名
    
    Args:
        domain: 主域名
        subdomain: 子域名
        record: 记录信息
    
    Returns:
        完整域名
    """
    name = record.get('name', '@')
    
    if name == '@':
        if subdomain == '@':
            return domain
        return f"{subdomain}.{domain}"
    else:
        if subdomain == '@':
            return f"{name}.{domain}"
        return f"{name}.{subdomain}.{domain}"


def check_dns_record(domain: str, subdomain: str, record: Dict[str, Any]) -> Dict[str, Any]:
    """
    检查 DNS 记录的健康状态
    
    Args:
        domain: 主域名
        subdomain: 子域名
        record: 记录信息
    
    Returns:
        检查结果
    """
    fqdn = get_record_fqdn(domain, subdomain, record)
    record_type = record.get('type')
    expected_content = record.get('content')
    
    result = {
        'fqdn': fqdn,
        'type': record_type,
        'expected': expected_content,
        'actual': None,
        'status': 'unknown',
        'error': None,
        'latency': None
    }
    
    try:
        start_time = time.time()
        
        if record_type == 'A':
            # 检查 A 记录
            try:
                answers = socket.gethostbyname_ex(fqdn)[2]
                result['actual'] = answers
                if expected_content in answers:
                    result['status'] = 'ok'
                else:
                    result['status'] = 'mismatch'
            except socket.gaierror as e:
                result['error'] = f"DNS 解析错误: {str(e)}"
                result['status'] = 'error'
        
        elif record_type == 'AAAA':
            # IPv6 记录需要特殊处理
            # 简化处理，仅检查记录是否存在
            try:
                # 使用 socket.getaddrinfo 获取 IPv6 地址
                infos = socket.getaddrinfo(fqdn, None, socket.AF_INET6)
                ipv6_addresses = [info[4][0] for info in infos]
                result['actual'] = ipv6_addresses
                if ipv6_addresses:
                    result['status'] = 'ok'
                else:
                    result['status'] = 'mismatch'
            except socket.gaierror as e:
                result['error'] = f"DNS 解析错误: {str(e)}"
                result['status'] = 'error'
        
        elif record_type == 'CNAME':
            # 检查 CNAME 记录
            try:
                cname = socket.gethostbyname_ex(fqdn)[0]
                result['actual'] = cname
                # 简化比较，不考虑尾部的点
                expected = expected_content[:-1] if expected_content.endswith('.') else expected_content
                actual = cname[:-1] if cname.endswith('.') else cname
                
                if expected in actual:
                    result['status'] = 'ok'
                else:
                    result['status'] = 'mismatch'
            except socket.gaierror as e:
                result['error'] = f"DNS 解析错误: {str(e)}"
                result['status'] = 'error'
        
        elif record_type == 'TXT':
            # TXT 记录通常用于验证域名所有权，这里简化处理
            result['status'] = 'unchecked'
            result['error'] = "TXT 记录健康检查未实现"
        
        elif record_type == 'MX':
            # 检查 MX 记录
            try:
                # 使用标准库而不是 dns.resolver
                import subprocess
                result_cmd = subprocess.run(['nslookup', '-type=MX', fqdn], 
                                          capture_output=True, text=True, timeout=10)
                if result_cmd.returncode == 0:
                    # 简化处理，只检查是否有 MX 记录返回
                    output = result_cmd.stdout.lower()
                    if 'mail exchanger' in output or expected_content.lower() in output:
                        result['status'] = 'ok'
                        result['actual'] = ['MX records found']
                    else:
                        result['status'] = 'mismatch'
                        result['actual'] = ['No matching MX records']
                else:
                    result['status'] = 'error'
                    result['error'] = f"MX 记录查询失败: {result_cmd.stderr}"
            except Exception as e:
                result['error'] = f"MX 记录检查错误: {str(e)}"
                result['status'] = 'error'
        
        # 计算延迟
        result['latency'] = round((time.time() - start_time) * 1000)  # 毫秒
        
        # 对于 HTTP(S) 站点进行额外检查
        if record_type in ['A', 'AAAA', 'CNAME'] and result['status'] == 'ok':
            try:
                http_url = f"http://{fqdn}"
                https_url = f"https://{fqdn}"
                
                # 首先尝试 HTTPS
                try:
                    https_response = requests.get(https_url, timeout=5)
                    result['http_status'] = https_response.status_code
                    result['http_latency'] = https_response.elapsed.total_seconds() * 1000
                    result['http_url'] = https_url
                except requests.exceptions.RequestException:
                    # 如果 HTTPS 失败，尝试 HTTP
                    try:
                        http_response = requests.get(http_url, timeout=5)
                        result['http_status'] = http_response.status_code
                        result['http_latency'] = http_response.elapsed.total_seconds() * 1000
                        result['http_url'] = http_url
                    except requests.exceptions.RequestException:
                        # 两者都失败，不添加 HTTP 相关信息
                        pass
            except Exception as e:
                # 忽略 HTTP 检查错误，这不影响 DNS 记录的健康状态
                pass
        
        return result
        
    except Exception as e:
        result['error'] = f"检查错误: {str(e)}"
        result['status'] = 'error'
        return result


def check_domain_health(domain: str, subdomain: str, config: Dict[str, Any], timeout: int = 5) -> Dict[str, Any]:
    """
    检查子域名的健康状态
    
    Args:
        domain: 主域名
        subdomain: 子域名
        config: 子域名配置
        timeout: 超时时间 (秒)
    
    Returns:
        健康状态信息
    """
    result = {
        'domain': domain,
        'subdomain': subdomain,
        'owner': config.get('owner', {}),
        'records': [],
        'status': 'unknown',
        'errors': 0,
        'check_time': datetime.datetime.now().isoformat()
    }
    
    records = config.get('records', [])
    
    # 使用线程池并行检查所有记录
    with ThreadPoolExecutor(max_workers=min(10, len(records) or 1)) as executor:
        check_futures = []
        
        for record in records:
            future = executor.submit(check_dns_record, domain, subdomain, record)
            check_futures.append(future)
        
        # 收集结果
        for future in check_futures:
            try:
                record_result = future.result(timeout=timeout)
                result['records'].append(record_result)
                if record_result['status'] == 'error':
                    result['errors'] += 1
            except Exception as e:
                result['records'].append({
                    'status': 'error',
                    'error': f"检查超时或失败: {str(e)}"
                })
                result['errors'] += 1
    
    # 设置整体状态
    if result['errors'] == 0:
        if all(r['status'] == 'ok' for r in result['records']):
            result['status'] = 'healthy'
        elif any(r['status'] == 'mismatch' for r in result['records']):
            result['status'] = 'mismatch'
        else:
            result['status'] = 'partial'
    else:
        if result['errors'] == len(result['records']):
            result['status'] = 'unhealthy'
        else:
            result['status'] = 'degraded'
    
    return result


def generate_health_report(results: List[Dict[str, Any]], config: Dict[str, Any]) -> str:
    """
    生成健康状态报告
    
    Args:
        results: 健康状态结果列表
        config: 项目配置
    
    Returns:
        Markdown 格式的报告
    """
    # 统计数据
    total_domains = len(results)
    status_counts = {
        'healthy': len([r for r in results if r['status'] == 'healthy']),
        'partial': len([r for r in results if r['status'] == 'partial']),
        'degraded': len([r for r in results if r['status'] == 'degraded']),
        'mismatch': len([r for r in results if r['status'] == 'mismatch']),
        'unhealthy': len([r for r in results if r['status'] == 'unhealthy']),
        'unknown': len([r for r in results if r['status'] == 'unknown']),
    }
    
    # 生成报告
    report = []
    report.append("# 域名健康状态报告")
    report.append("")
    report.append(f"**生成时间**: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    
    # 添加统计摘要
    report.append("## 统计摘要")
    report.append("")
    report.append(f"- 总域名数: {total_domains}")
    report.append(f"- 健康: {status_counts['healthy']} ({round(status_counts['healthy']/total_domains*100 if total_domains else 0, 1)}%)")
    report.append(f"- 部分健康: {status_counts['partial']} ({round(status_counts['partial']/total_domains*100 if total_domains else 0, 1)}%)")
    report.append(f"- 性能下降: {status_counts['degraded']} ({round(status_counts['degraded']/total_domains*100 if total_domains else 0, 1)}%)")
    report.append(f"- 配置不匹配: {status_counts['mismatch']} ({round(status_counts['mismatch']/total_domains*100 if total_domains else 0, 1)}%)")
    report.append(f"- 不健康: {status_counts['unhealthy']} ({round(status_counts['unhealthy']/total_domains*100 if total_domains else 0, 1)}%)")
    report.append(f"- 未知: {status_counts['unknown']} ({round(status_counts['unknown']/total_domains*100 if total_domains else 0, 1)}%)")
    report.append("")
    
    # 添加图标说明
    report.append("## 状态图标说明")
    report.append("")
    report.append("- ✅ 健康: 所有记录正常")
    report.append("- ⚠️ 部分健康: 部分记录正常，部分未检查")
    report.append("- 🔸 性能下降: 部分记录出错，但仍有记录正常")
    report.append("- ⚡ 配置不匹配: 记录存在但与预期不符")
    report.append("- ❌ 不健康: 所有记录均有错误")
    report.append("- ❓ 未知: 状态未知")
    report.append("")
    
    # 按域名分组
    domains = {}
    for result in results:
        domain = result['domain']
        if domain not in domains:
            domains[domain] = []
        domains[domain].append(result)
    
    # 遍历域名
    for domain, domain_results in domains.items():
        # 获取域名配置
        domain_config = None
        for d in config.get('domains', []):
            if d.get('name') == domain:
                domain_config = d
                break
        
        report.append(f"## {domain}")
        report.append("")
        if domain_config:
            report.append(f"**描述**: {domain_config.get('description', '无')}")
            report.append(f"**状态**: {'启用' if domain_config.get('enabled') else '禁用'}")
        report.append("")
        
        # 创建子域名表格
        report.append("| 子域名 | 状态 | 所有者 | 记录数 | 错误数 | 检查时间 |")
        report.append("|--------|------|-------|--------|--------|----------|")
        
        # 按状态排序: 不健康优先显示
        domain_results.sort(key=lambda r: {
            'unhealthy': 0,
            'mismatch': 1,
            'degraded': 2,
            'partial': 3,
            'unknown': 4,
            'healthy': 5
        }.get(r['status'], 6))
        
        for result in domain_results:
            subdomain = result['subdomain']
            status = result['status']
            owner = result['owner'].get('name', '未知') if result['owner'] else '未知'
            records_count = len(result['records'])
            errors_count = result['errors']
            check_time = datetime.datetime.fromisoformat(result['check_time']).strftime('%H:%M:%S')
            
            # 状态图标
            status_icon = {
                'healthy': '✅',
                'partial': '⚠️',
                'degraded': '🔸',
                'mismatch': '⚡',
                'unhealthy': '❌',
                'unknown': '❓'
            }.get(status, '❓')
            
            report.append(f"| {subdomain} | {status_icon} {status} | {owner} | {records_count} | {errors_count} | {check_time} |")
        
        report.append("")
        
        # 详细记录信息
        for result in domain_results:
            if result['status'] != 'healthy':  # 只显示有问题的域名的详细信息
                subdomain = result['subdomain']
                report.append(f"### {subdomain}.{domain}")
                report.append("")
                report.append("| 记录 | 类型 | 预期值 | 实际值 | 状态 | 延迟 |")
                report.append("|------|------|--------|--------|------|------|")
                
                for record in result['records']:
                    fqdn = record.get('fqdn', '未知')
                    record_type = record.get('type', '未知')
                    expected = record.get('expected', '未知')
                    actual = record.get('actual')
                    if isinstance(actual, list):
                        actual = ', '.join(str(a) for a in actual) if actual else '无'
                    elif actual is None:
                        actual = '无'
                    status = record.get('status', 'unknown')
                    latency = record.get('latency')
                    latency_str = f"{latency}ms" if latency is not None else '未知'
                    
                    # 状态图标
                    status_icon = {
                        'ok': '✅',
                        'mismatch': '⚡',
                        'error': '❌',
                        'unchecked': '⏳',
                        'unknown': '❓'
                    }.get(status, '❓')
                    
                    report.append(f"| {fqdn} | {record_type} | {expected} | {actual} | {status_icon} | {latency_str} |")
                
                # 添加错误信息
                errors = [r['error'] for r in result['records'] if r.get('error')]
                if errors:
                    report.append("")
                    report.append("**错误信息**:")
                    for error in errors:
                        report.append(f"- {error}")
                
                report.append("")
    
    return "\n".join(report)


def main():
    """命令行入口点"""
    import argparse
    
    parser = argparse.ArgumentParser(description='域名健康检查工具')
    parser.add_argument('--config', help='配置文件路径')
    parser.add_argument('--output', help='输出文件路径')
    parser.add_argument('--timeout', type=int, default=10, help='检查超时时间 (秒)')
    parser.add_argument('--domain', help='指定要检查的域名')
    parser.add_argument('--subdomain', help='指定要检查的子域名')
    
    args = parser.parse_args()
    
    # 加载项目配置
    config = load_config(args.config)
    
    all_results = []
    
    # 遍历所有启用的域名
    for domain_config in config.get('domains', []):
        domain = domain_config.get('name')
        
        # 跳过未启用的域名
        if not domain_config.get('enabled', True):
            continue
            
        # 如果指定了域名但不匹配，跳过
        if args.domain and args.domain != domain:
            continue
        
        print(f"检查域名: {domain}")
        
        # 获取域名目录下的所有 JSON 文件
        domain_files = get_domain_files(domain)
        
        for file_path in domain_files:
            subdomain = os.path.basename(file_path)[:-5]  # 去除 .json 后缀
            
            # 如果指定了子域名但不匹配，跳过
            if args.subdomain and args.subdomain != subdomain:
                continue
                
            print(f"  检查子域名: {subdomain}")
            
            # 加载子域名配置
            domain_config = load_domain_config(file_path)
            if domain_config is None:
                print(f"    无法加载配置文件: {file_path}")
                continue
            
            # 检查健康状态
            result = check_domain_health(domain, subdomain, domain_config, args.timeout)
            all_results.append(result)
            
            # 打印结果状态
            status_icon = {
                'healthy': '✓',
                'partial': '⚠',
                'degraded': '!',
                'mismatch': '≠',
                'unhealthy': '✗',
                'unknown': '?'
            }.get(result['status'], '?')
            print(f"    状态: {status_icon} {result['status']}")
    
    # 生成报告
    report = generate_health_report(all_results, config)
    
    # 输出报告
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"\n报告已保存至: {args.output}")
    else:
        print("\n" + report)
    
    # 返回码: 如果有任何不健康的域名，返回 1
    unhealthy_count = len([r for r in all_results if r['status'] in ['unhealthy', 'mismatch']])
    return 1 if unhealthy_count > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
