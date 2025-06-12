#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DNS 健康检查脚本
检查所有域名记录的可用性和正确性
"""

import os
import sys
import json
import yaml
import socket
import subprocess
from typing import Dict, Any, List
from datetime import datetime
import requests


class DNSHealthChecker:
    """DNS 健康检查器"""
    
    def __init__(self):
        self.domains_config = None
        self.load_config()
        self.report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_domains": 0,
                "total_subdomains": 0,
                "healthy_subdomains": 0,
                "unhealthy_subdomains": 0,
                "errors": []
            },
            "domain_reports": {}
        }
    
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
    
    def check_dns_resolution(self, domain: str, record_type: str) -> Dict[str, Any]:
        """检查 DNS 解析"""
        try:
            if record_type == "A":
                result = socket.gethostbyname(domain)
                return {"success": True, "result": result}
            elif record_type == "AAAA":
                result = socket.getaddrinfo(domain, None, socket.AF_INET6)
                if result:
                    return {"success": True, "result": result[0][4][0]}
            else:
                # 对于其他记录类型，使用 nslookup
                try:
                    cmd = ["nslookup", "-type=" + record_type.lower(), domain]
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        return {"success": True, "result": result.stdout}
                    else:
                        return {"success": False, "error": result.stderr}
                except subprocess.TimeoutExpired:
                    return {"success": False, "error": "DNS 查询超时"}
                except FileNotFoundError:
                    return {"success": False, "error": "nslookup 命令不可用"}
        
        except socket.gaierror as e:
            return {"success": False, "error": f"DNS 解析失败: {e}"}
        except Exception as e:
            return {"success": False, "error": f"未知错误: {e}"}
        
        return {"success": False, "error": "不支持的记录类型"}
    
    def check_http_response(self, domain: str, use_https: bool = True) -> Dict[str, Any]:
        """检查 HTTP 响应"""
        try:
            protocol = "https" if use_https else "http"
            url = f"{protocol}://{domain}"
            
            response = requests.get(url, timeout=10, allow_redirects=True)
            return {
                "success": True,
                "status_code": response.status_code,
                "response_time": response.elapsed.total_seconds(),
                "final_url": response.url
            }
        
        except requests.RequestException as e:
            if use_https:
                # HTTPS 失败时尝试 HTTP
                return self.check_http_response(domain, use_https=False)
            return {"success": False, "error": str(e)}
    
    def check_domain_records(self, domain: str) -> Dict[str, Any]:
        """检查单个域名的所有记录"""
        domain_report = {
            "domain": domain,
            "total_subdomains": 0,
            "healthy_subdomains": 0,
            "unhealthy_subdomains": 0,
            "subdomain_reports": []
        }
        
        domains_dir = os.path.join(os.path.dirname(__file__), "..", "domains", domain)
        
        if not os.path.exists(domains_dir):
            domain_report["error"] = "域名目录不存在"
            return domain_report
        
        for file in os.listdir(domains_dir):
            if not file.endswith(".json"):
                continue
            
            subdomain_name = file[:-5]
            file_path = os.path.join(domains_dir, file)
            
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    record_data = json.load(f)
                
                subdomain_report = self.check_subdomain_record(
                    domain, subdomain_name, record_data
                )
                
                domain_report["subdomain_reports"].append(subdomain_report)
                domain_report["total_subdomains"] += 1
                
                if subdomain_report["healthy"]:
                    domain_report["healthy_subdomains"] += 1
                else:
                    domain_report["unhealthy_subdomains"] += 1
            
            except (json.JSONDecodeError, FileNotFoundError) as e:
                domain_report["subdomain_reports"].append({
                    "subdomain": subdomain_name,
                    "healthy": False,
                    "error": f"读取记录文件失败: {e}"
                })
                domain_report["total_subdomains"] += 1
                domain_report["unhealthy_subdomains"] += 1
        
        return domain_report
    
    def check_subdomain_record(self, domain: str, subdomain: str, record_data: Dict[str, Any]) -> Dict[str, Any]:
        """检查单个子域名记录"""
        full_domain = f"{subdomain}.{domain}"
        record = record_data.get("record", {})
        record_type = record.get("type", "")
        
        report = {
            "subdomain": subdomain,
            "full_domain": full_domain,
            "record_type": record_type,
            "record_value": record.get("value", ""),
            "healthy": True,
            "issues": [],
            "checks": {}
        }
        
        # DNS 解析检查
        dns_check = self.check_dns_resolution(full_domain, record_type)
        report["checks"]["dns_resolution"] = dns_check
        
        if not dns_check["success"]:
            report["healthy"] = False
            report["issues"].append(f"DNS 解析失败: {dns_check.get('error', '未知错误')}")
        
        # 对于 A 和 AAAA 记录，检查 HTTP 响应
        if record_type in ["A", "AAAA"] and report["healthy"]:
            http_check = self.check_http_response(full_domain)
            report["checks"]["http_response"] = http_check
            
            if not http_check["success"]:
                report["issues"].append(f"HTTP 访问失败: {http_check.get('error', '未知错误')}")
                # HTTP 失败不一定意味着 DNS 记录有问题，所以不设置为 unhealthy
        
        # 对于 CNAME 记录，检查目标域名
        if record_type == "CNAME":
            target_domain = record.get("value", "")
            if target_domain:
                target_check = self.check_dns_resolution(target_domain, "A")
                report["checks"]["target_resolution"] = target_check
                
                if not target_check["success"]:
                    report["healthy"] = False
                    report["issues"].append(f"CNAME 目标域名解析失败: {target_check.get('error', '未知错误')}")
        
        return report
    
    def run_health_check(self) -> Dict[str, Any]:
        """运行完整的健康检查"""
        print("🔍 开始 DNS 健康检查...")
        print("=" * 50)
        
        domains = self.domains_config.get("domains", {})
        
        for domain_name in domains.keys():
            print(f"\n📊 检查域名: {domain_name}")
            print("-" * 30)
            
            domain_report = self.check_domain_records(domain_name)
            self.report["domain_reports"][domain_name] = domain_report
            
            # 更新总体统计
            self.report["summary"]["total_domains"] += 1
            self.report["summary"]["total_subdomains"] += domain_report["total_subdomains"]
            self.report["summary"]["healthy_subdomains"] += domain_report["healthy_subdomains"]
            self.report["summary"]["unhealthy_subdomains"] += domain_report["unhealthy_subdomains"]
            
            print(f"  总子域名: {domain_report['total_subdomains']}")
            print(f"  健康: {domain_report['healthy_subdomains']}")
            print(f"  异常: {domain_report['unhealthy_subdomains']}")
            
            # 显示异常的子域名
            for subdomain_report in domain_report["subdomain_reports"]:
                if not subdomain_report["healthy"]:
                    print(f"  ❌ {subdomain_report['full_domain']}: {', '.join(subdomain_report['issues'])}")
        
        # 计算健康度
        total_subdomains = self.report["summary"]["total_subdomains"]
        healthy_subdomains = self.report["summary"]["healthy_subdomains"]
        
        if total_subdomains > 0:
            health_percentage = (healthy_subdomains / total_subdomains) * 100
            self.report["summary"]["health_percentage"] = health_percentage
        else:
            self.report["summary"]["health_percentage"] = 100
        
        print(f"\n📈 总体健康度: {self.report['summary']['health_percentage']:.1f}%")
        print(f"   总域名: {self.report['summary']['total_domains']}")
        print(f"   总子域名: {self.report['summary']['total_subdomains']}")
        print(f"   健康: {self.report['summary']['healthy_subdomains']}")
        print(f"   异常: {self.report['summary']['unhealthy_subdomains']}")
        
        return self.report
    
    def generate_markdown_report(self, output_file: str = None):
        """生成 Markdown 格式的报告"""
        if not output_file:
            output_file = f"health_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        report_content = f"""# DNS 健康检查报告

**检查时间**: {self.report['timestamp']}

## 📊 总体概况

- 总域名数: {self.report['summary']['total_domains']}
- 总子域名数: {self.report['summary']['total_subdomains']}
- 健康子域名: {self.report['summary']['healthy_subdomains']}
- 异常子域名: {self.report['summary']['unhealthy_subdomains']}
- 健康度: {self.report['summary']['health_percentage']:.1f}%

"""
        
        # 按域名生成详细报告
        for domain_name, domain_report in self.report["domain_reports"].items():
            report_content += f"""## 📋 域名: {domain_name}

- 子域名总数: {domain_report['total_subdomains']}
- 健康: {domain_report['healthy_subdomains']}
- 异常: {domain_report['unhealthy_subdomains']}

"""
            
            if domain_report["unhealthy_subdomains"] > 0:
                report_content += "### ❌ 异常子域名\n\n"
                
                for subdomain_report in domain_report["subdomain_reports"]:
                    if not subdomain_report["healthy"]:
                        report_content += f"#### {subdomain_report['full_domain']}\n\n"
                        report_content += f"- 记录类型: {subdomain_report['record_type']}\n"
                        report_content += f"- 记录值: {subdomain_report['record_value']}\n"
                        report_content += "- 问题:\n"
                        
                        for issue in subdomain_report["issues"]:
                            report_content += f"  - {issue}\n"
                        
                        report_content += "\n"
        
        # 保存报告
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(report_content)
        
        print(f"📄 健康检查报告已生成: {output_file}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="DNS 健康检查工具")
    parser.add_argument("--domain", "-d", help="指定检查的域名")
    parser.add_argument("--report-file", "-r", help="报告输出文件名")
    parser.add_argument("--json", action="store_true", help="输出 JSON 格式报告")
    
    args = parser.parse_args()
    
    checker = DNSHealthChecker()
    
    if args.domain:
        # 检查指定域名
        domain_report = checker.check_domain_records(args.domain)
        if args.json:
            print(json.dumps(domain_report, indent=2, ensure_ascii=False))
        else:
            print(f"域名 {args.domain} 健康检查完成")
            print(f"总子域名: {domain_report['total_subdomains']}")
            print(f"健康: {domain_report['healthy_subdomains']}")
            print(f"异常: {domain_report['unhealthy_subdomains']}")
    else:
        # 运行完整检查
        report = checker.run_health_check()
        
        if args.json:
            if args.report_file:
                with open(args.report_file, "w", encoding="utf-8") as f:
                    json.dump(report, f, indent=2, ensure_ascii=False)
            else:
                print(json.dumps(report, indent=2, ensure_ascii=False))
        else:
            if args.report_file:
                checker.generate_markdown_report(args.report_file)
        
        # 如果有异常，返回错误代码
        if report["summary"]["unhealthy_subdomains"] > 0:
            sys.exit(1)


if __name__ == "__main__":
    main()
