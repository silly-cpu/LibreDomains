#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LibreDomains 管理 CLI 工具
提供命令行接口来管理域名和用户
"""

import argparse
import sys
import os
import json
from typing import Dict, Any

# 添加脚本目录到路径
sys.path.append(os.path.dirname(__file__))

from validate_request import RequestValidator
from deploy_dns import DNSDeployer
from check_github_user import GitHubUserChecker
from generate_stats import StatisticsGenerator
from health_check import DNSHealthChecker


class LibreDomainsManager:
    """LibreDomains 管理器"""
    
    def __init__(self):
        self.validator = RequestValidator()
        self.user_checker = GitHubUserChecker()
        self.stats_generator = StatisticsGenerator()
        self.health_checker = DNSHealthChecker()
    
    def validate_request(self, request_file: str, verbose: bool = False) -> None:
        """验证单个请求文件"""
        print(f"🔍 验证请求文件: {request_file}")
        
        result = self.validator.validate_request(request_file)
        
        if result["valid"]:
            print("✅ 验证通过")
        else:
            print("❌ 验证失败")
            print("\n错误信息:")
            for error in result["errors"]:
                print(f"  • {error}")
        
        if result.get("warnings"):
            print("\n警告信息:")
            for warning in result["warnings"]:
                print(f"  • {warning}")
        
        if verbose:
            print(f"\n详细结果:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
    
    def check_user(self, username: str, show_repos: bool = False, 
                   show_subdomains: bool = False) -> None:
        """检查 GitHub 用户信息"""
        print(f"👤 检查用户: {username}")
        
        # 获取用户基本信息
        user_info = self.user_checker.get_user_info(username)
        if not user_info:
            print("❌ 用户不存在或无法访问")
            return
        
        print(f"\n📊 用户信息:")
        print(f"  • 用户名: {user_info['login']}")
        print(f"  • 显示名: {user_info.get('name', 'N/A')}")
        print(f"  • 邮箱: {user_info.get('email', 'N/A')}")
        print(f"  • 创建时间: {user_info['created_at']}")
        print(f"  • 公开仓库: {user_info['public_repos']}")
        print(f"  • 关注者: {user_info['followers']}")
        
        # 检查申请资格
        eligibility = self.user_checker.check_user_eligibility(username)
        print(f"\n🎯 申请资格:")
        if eligibility["eligible"]:
            print("✅ 符合申请条件")
        else:
            print("❌ 不符合申请条件")
            for reason in eligibility["reasons"]:
                print(f"  • {reason}")
        
        if eligibility.get("warnings"):
            print("⚠️ 警告:")
            for warning in eligibility["warnings"]:
                print(f"  • {warning}")
        
        # 显示仓库信息
        if show_repos:
            repos = self.user_checker.get_user_repositories(username)
            if repos:
                print(f"\n📦 仓库信息 (前10个):")
                for repo in repos[:10]:
                    print(f"  • {repo['name']}")
                    if repo.get('description'):
                        print(f"    描述: {repo['description']}")
                    print(f"    ⭐ {repo['stars']} 🍴 {repo['forks']}")
        
        # 显示子域名信息
        if show_subdomains:
            subdomains = self.user_checker.get_user_subdomains(username)
            if subdomains:
                print(f"\n🌐 用户子域名:")
                for subdomain in subdomains:
                    print(f"  • {subdomain['full_domain']}")
                    print(f"    类型: {subdomain['record_type']}")
                    print(f"    值: {subdomain['record_value']}")
                    print(f"    描述: {subdomain['description']}")
                    if subdomain.get('deployed_at'):
                        print(f"    部署时间: {subdomain['deployed_at']}")
    
    def generate_stats(self, output_file: str = None, format_json: bool = False) -> None:
        """生成统计信息"""
        print("📊 生成统计信息...")
        
        stats = self.stats_generator.generate_statistics()
        
        if format_json:
            output = json.dumps(stats, indent=2, ensure_ascii=False)
        else:
            output = self._format_stats_text(stats)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(output)
            print(f"✅ 统计信息已保存到: {output_file}")
        else:
            print(output)
    
    def _format_stats_text(self, stats: Dict[str, Any]) -> str:
        """格式化统计信息为文本"""
        summary = stats['summary']
        
        text = f"""
📊 LibreDomains 统计报告
{'=' * 40}

总体概况:
  • 总域名数: {summary['total_domains']}
  • 总子域名数: {summary['total_subdomains']}
  • 活跃用户数: {summary['total_users']}

域名分布:
"""
        
        for domain, count in stats['domain_usage'].items():
            text += f"  • {domain}: {count} 个子域名\n"
        
        text += "\n记录类型分布:\n"
        for record_type, count in stats['record_types'].items():
            percentage = (count / summary['total_subdomains']) * 100 if summary['total_subdomains'] > 0 else 0
            text += f"  • {record_type}: {count} 个 ({percentage:.1f}%)\n"
        
        text += "\n活跃用户 (前10名):\n"
        for user, count in list(stats['top_users'].items())[:10]:
            text += f"  • {user}: {count} 个子域名\n"
        
        return text
    
    def health_check(self, domain: str = None, output_file: str = None, 
                     format_json: bool = False) -> None:
        """运行健康检查"""
        if domain:
            print(f"🔍 检查域名: {domain}")
            report = self.health_checker.check_domain_records(domain)
            
            print(f"  总子域名: {report['total_subdomains']}")
            print(f"  健康: {report['healthy_subdomains']}")
            print(f"  异常: {report['unhealthy_subdomains']}")
            
            if report['unhealthy_subdomains'] > 0:
                print("\n❌ 异常子域名:")
                for subdomain_report in report["subdomain_reports"]:
                    if not subdomain_report["healthy"]:
                        print(f"  • {subdomain_report['full_domain']}: {', '.join(subdomain_report['issues'])}")
        else:
            print("🔍 运行完整健康检查...")
            report = self.health_checker.run_health_check()
            
            if format_json:
                output = json.dumps(report, indent=2, ensure_ascii=False)
            else:
                output = f"健康检查完成，详细信息请查看生成的报告文件"
                if output_file:
                    self.health_checker.generate_markdown_report(output_file)
            
            if output_file and format_json:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(output)
                print(f"✅ 报告已保存到: {output_file}")
            elif not output_file:
                print(output)
    
    def deploy_request(self, request_file: str, action: str = "deploy") -> None:
        """部署或删除 DNS 记录"""
        if not os.getenv("CLOUDFLARE_API_TOKEN"):
            print("❌ 未设置 CLOUDFLARE_API_TOKEN 环境变量")
            return
        
        deployer = DNSDeployer()
        deployer.init_api()
        
        if action == "deploy":
            print(f"🚀 部署 DNS 记录: {request_file}")
            success = deployer.deploy_request(request_file)
        elif action == "delete":
            print(f"🗑️ 删除 DNS 记录: {request_file}")
            success = deployer.delete_request(request_file)
        else:
            print(f"❌ 未知操作: {action}")
            return
        
        if success:
            print("✅ 操作成功")
        else:
            print("❌ 操作失败")
    
    def list_subdomains(self, domain: str = None, user: str = None) -> None:
        """列出子域名"""
        domains_dir = os.path.join(os.path.dirname(__file__), "..", "domains")
        
        if not os.path.exists(domains_dir):
            print("❌ 域名目录不存在")
            return
        
        if domain:
            domains_to_check = [domain] if domain in os.listdir(domains_dir) else []
        else:
            domains_to_check = [d for d in os.listdir(domains_dir) 
                               if os.path.isdir(os.path.join(domains_dir, d))]
        
        if not domains_to_check:
            print("❌ 未找到指定域名")
            return
        
        total_count = 0
        for domain_name in domains_to_check:
            domain_path = os.path.join(domains_dir, domain_name)
            subdomain_files = [f for f in os.listdir(domain_path) if f.endswith('.json')]
            
            print(f"\n🌐 域名: {domain_name} ({len(subdomain_files)} 个子域名)")
            print("-" * 40)
            
            for file in subdomain_files:
                subdomain_name = file[:-5]  # 移除 .json 后缀
                file_path = os.path.join(domain_path, file)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    owner_username = data.get('owner', {}).get('username', 'unknown')
                    
                    # 如果指定了用户，只显示该用户的记录
                    if user and owner_username.lower() != user.lower():
                        continue
                    
                    record = data.get('record', {})
                    description = data.get('description', 'N/A')
                    deployed_at = data.get('_metadata', {}).get('deployed_at', 'N/A')
                    
                    print(f"  • {subdomain_name}.{domain_name}")
                    print(f"    所有者: {owner_username}")
                    print(f"    类型: {record.get('type', 'N/A')}")
                    print(f"    值: {record.get('value', 'N/A')}")
                    print(f"    描述: {description}")
                    print(f"    部署时间: {deployed_at}")
                    print()
                    
                    total_count += 1
                    
                except (json.JSONDecodeError, FileNotFoundError) as e:
                    print(f"  ❌ 无法读取 {file}: {e}")
        
        print(f"📊 总计: {total_count} 个子域名")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="LibreDomains 管理工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  python cli.py validate requests/example.json
  python cli.py user github-username --repos --subdomains
  python cli.py stats --output stats.json --json
  python cli.py health --domain ciao.su
  python cli.py deploy requests/example.json
  python cli.py list --domain ciao.su
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 验证命令
    validate_parser = subparsers.add_parser('validate', help='验证请求文件')
    validate_parser.add_argument('file', help='请求文件路径')
    validate_parser.add_argument('--verbose', '-v', action='store_true', help='详细输出')
    
    # 用户检查命令
    user_parser = subparsers.add_parser('user', help='检查 GitHub 用户')
    user_parser.add_argument('username', help='GitHub 用户名')
    user_parser.add_argument('--repos', action='store_true', help='显示仓库信息')
    user_parser.add_argument('--subdomains', action='store_true', help='显示子域名信息')
    
    # 统计命令
    stats_parser = subparsers.add_parser('stats', help='生成统计信息')
    stats_parser.add_argument('--output', '-o', help='输出文件路径')
    stats_parser.add_argument('--json', action='store_true', help='JSON 格式输出')
    
    # 健康检查命令
    health_parser = subparsers.add_parser('health', help='DNS 健康检查')
    health_parser.add_argument('--domain', '-d', help='检查特定域名')
    health_parser.add_argument('--output', '-o', help='输出文件路径')
    health_parser.add_argument('--json', action='store_true', help='JSON 格式输出')
    
    # 部署命令
    deploy_parser = subparsers.add_parser('deploy', help='部署 DNS 记录')
    deploy_parser.add_argument('file', help='请求文件路径')
    deploy_parser.add_argument('--delete', action='store_true', help='删除记录')
    
    # 列表命令
    list_parser = subparsers.add_parser('list', help='列出子域名')
    list_parser.add_argument('--domain', '-d', help='指定域名')
    list_parser.add_argument('--user', '-u', help='指定用户')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    manager = LibreDomainsManager()
    
    try:
        if args.command == 'validate':
            manager.validate_request(args.file, args.verbose)
        
        elif args.command == 'user':
            manager.check_user(args.username, args.repos, args.subdomains)
        
        elif args.command == 'stats':
            manager.generate_stats(args.output, args.json)
        
        elif args.command == 'health':
            manager.health_check(args.domain, args.output, args.json)
        
        elif args.command == 'deploy':
            action = "delete" if args.delete else "deploy"
            manager.deploy_request(args.file, action)
        
        elif args.command == 'list':
            manager.list_subdomains(args.domain, args.user)
    
    except KeyboardInterrupt:
        print("\n❌ 操作被中断")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 发生错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
