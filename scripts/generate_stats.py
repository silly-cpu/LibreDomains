#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统计生成脚本
生成项目使用统计和分析报告
"""

import os
import json
import yaml
from collections import defaultdict, Counter
from datetime import datetime, timedelta
from typing import Dict, Any, List


class StatisticsGenerator:
    """统计生成器"""
    
    def __init__(self):
        self.domains_config = None
        self.load_config()
        self.stats = {
            "generated_at": datetime.now().isoformat(),
            "summary": {},
            "domains": {},
            "users": {},
            "records": {},
            "trends": {}
        }
    
    def load_config(self):
        """加载配置文件"""
        config_path = os.path.join(os.path.dirname(__file__), "..", "config", "domains.yml")
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                self.domains_config = yaml.safe_load(f)
        except FileNotFoundError:
            print(f"❌ 配置文件不存在: {config_path}")
            return
        except yaml.YAMLError as e:
            print(f"❌ 配置文件格式错误: {e}")
            return
    
    def collect_domain_data(self) -> Dict[str, List[Dict[str, Any]]]:
        """收集所有域名数据"""
        all_records = {}
        domains_dir = os.path.join(os.path.dirname(__file__), "..", "domains")
        
        if not os.path.exists(domains_dir):
            return {}
        
        for domain_folder in os.listdir(domains_dir):
            domain_path = os.path.join(domains_dir, domain_folder)
            if not os.path.isdir(domain_path):
                continue
            
            domain_records = []
            for file in os.listdir(domain_path):
                if file.endswith(".json"):
                    file_path = os.path.join(domain_path, file)
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            record_data = json.load(f)
                            record_data["_filename"] = file
                            record_data["_subdomain"] = file[:-5]
                            domain_records.append(record_data)
                    except (json.JSONDecodeError, FileNotFoundError):
                        continue
            
            all_records[domain_folder] = domain_records
        
        return all_records
    
    def generate_summary_stats(self, all_records: Dict[str, List[Dict[str, Any]]]):
        """生成总体统计"""
        total_domains = len(all_records)
        total_subdomains = sum(len(records) for records in all_records.values())
        total_users = len(set(
            record.get("owner", {}).get("username", "").lower()
            for records in all_records.values()
            for record in records
            if record.get("owner", {}).get("username")
        ))
        
        # 记录类型统计
        record_types = Counter()
        for records in all_records.values():
            for record in records:
                record_type = record.get("record", {}).get("type", "Unknown")
                record_types[record_type] += 1
        
        self.stats["summary"] = {
            "total_domains": total_domains,
            "total_subdomains": total_subdomains,
            "total_users": total_users,
            "record_types": dict(record_types),
            "most_popular_record_type": record_types.most_common(1)[0] if record_types else ("None", 0)
        }
    
    def generate_domain_stats(self, all_records: Dict[str, List[Dict[str, Any]]]):
        """生成按域名统计"""
        for domain, records in all_records.items():
            domain_config = self.domains_config.get("domains", {}).get(domain, {})
            
            # 记录类型统计
            record_types = Counter()
            for record in records:
                record_type = record.get("record", {}).get("type", "Unknown")
                record_types[record_type] += 1
            
            # 用户统计
            users = set()
            for record in records:
                username = record.get("owner", {}).get("username", "").lower()
                if username:
                    users.add(username)
            
            # 代理统计
            proxied_count = sum(
                1 for record in records
                if record.get("record", {}).get("proxied", False)
            )
            
            self.stats["domains"][domain] = {
                "enabled": domain_config.get("enabled", False),
                "description": domain_config.get("description", ""),
                "total_subdomains": len(records),
                "unique_users": len(users),
                "record_types": dict(record_types),
                "proxied_records": proxied_count,
                "non_proxied_records": len(records) - proxied_count
            }
    
    def generate_user_stats(self, all_records: Dict[str, List[Dict[str, Any]]]):
        """生成用户统计"""
        user_records = defaultdict(list)
        
        for domain, records in all_records.items():
            for record in records:
                username = record.get("owner", {}).get("username", "").lower()
                if username:
                    user_records[username].append({
                        "domain": domain,
                        "subdomain": record["_subdomain"],
                        "record_type": record.get("record", {}).get("type", "Unknown"),
                        "deployed_at": record.get("_metadata", {}).get("deployed_at")
                    })
        
        # 用户排行榜
        user_counts = [(user, len(records)) for user, records in user_records.items()]
        user_counts.sort(key=lambda x: x[1], reverse=True)
        
        self.stats["users"] = {
            "total_users": len(user_records),
            "top_users": user_counts[:10],
            "users_with_multiple_subdomains": len([
                user for user, records in user_records.items() if len(records) > 1
            ]),
            "average_subdomains_per_user": (
                sum(len(records) for records in user_records.values()) / len(user_records)
                if user_records else 0
            )
        }
    
    def generate_record_stats(self, all_records: Dict[str, List[Dict[str, Any]]]):
        """生成记录类型统计"""
        all_records_flat = [
            record for records in all_records.values() for record in records
        ]
        
        # 记录类型分布
        record_types = Counter()
        ttl_values = Counter()
        proxied_usage = {"proxied": 0, "not_proxied": 0}
        
        for record in all_records_flat:
            record_info = record.get("record", {})
            
            # 记录类型
            record_type = record_info.get("type", "Unknown")
            record_types[record_type] += 1
            
            # TTL 值
            ttl = record_info.get("ttl", 3600)
            ttl_values[ttl] += 1
            
            # 代理使用情况
            if record_info.get("proxied", False):
                proxied_usage["proxied"] += 1
            else:
                proxied_usage["not_proxied"] += 1
        
        self.stats["records"] = {
            "total_records": len(all_records_flat),
            "record_type_distribution": dict(record_types),
            "ttl_distribution": dict(ttl_values.most_common(10)),
            "proxy_usage": proxied_usage,
            "most_common_ttl": ttl_values.most_common(1)[0] if ttl_values else (3600, 0)
        }
    
    def generate_trend_stats(self, all_records: Dict[str, List[Dict[str, Any]]]):
        """生成趋势统计"""
        # 按月统计部署数量
        monthly_deployments = defaultdict(int)
        
        for records in all_records.values():
            for record in records:
                deployed_at = record.get("_metadata", {}).get("deployed_at")
                if deployed_at:
                    try:
                        date = datetime.fromisoformat(deployed_at.replace("Z", "+00:00"))
                        month_key = date.strftime("%Y-%m")
                        monthly_deployments[month_key] += 1
                    except ValueError:
                        continue
        
        # 最近30天的活动
        recent_activity = 0
        thirty_days_ago = datetime.now() - timedelta(days=30)
        
        for records in all_records.values():
            for record in records:
                deployed_at = record.get("_metadata", {}).get("deployed_at")
                if deployed_at:
                    try:
                        date = datetime.fromisoformat(deployed_at.replace("Z", "+00:00"))
                        if date.replace(tzinfo=None) > thirty_days_ago:
                            recent_activity += 1
                    except ValueError:
                        continue
        
        self.stats["trends"] = {
            "monthly_deployments": dict(sorted(monthly_deployments.items())),
            "recent_activity_30days": recent_activity,
            "peak_month": max(monthly_deployments.items(), key=lambda x: x[1]) if monthly_deployments else ("N/A", 0)
        }
    
    def generate_all_stats(self):
        """生成所有统计数据"""
        print("📊 生成统计数据...")
        
        # 收集数据
        all_records = self.collect_domain_data()
        
        if not all_records:
            print("⚠️ 没有找到域名记录数据")
            return self.stats
        
        # 生成各类统计
        self.generate_summary_stats(all_records)
        self.generate_domain_stats(all_records)
        self.generate_user_stats(all_records)
        self.generate_record_stats(all_records)
        self.generate_trend_stats(all_records)
        
        print("✅ 统计数据生成完成")
        return self.stats
    
    def save_json_report(self, filename: str = None):
        """保存 JSON 格式报告"""
        if not filename:
            filename = f"stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self.stats, f, indent=2, ensure_ascii=False)
        
        print(f"📄 JSON 统计报告已保存: {filename}")
    
    def save_markdown_report(self, filename: str = None):
        """保存 Markdown 格式报告"""
        if not filename:
            filename = f"stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        summary = self.stats["summary"]
        domains = self.stats["domains"]
        users = self.stats["users"]
        records = self.stats["records"]
        trends = self.stats["trends"]
        
        report_content = f"""# LibreDomains 统计报告

**生成时间**: {self.stats['generated_at']}

## 📊 总体概况

- **总域名数**: {summary.get('total_domains', 0)}
- **总子域名数**: {summary.get('total_subdomains', 0)}
- **总用户数**: {summary.get('total_users', 0)}
- **最受欢迎的记录类型**: {summary.get('most_popular_record_type', ['N/A', 0])[0]} ({summary.get('most_popular_record_type', ['N/A', 0])[1]} 个)

## 🌐 域名统计

"""
        
        for domain, stats in domains.items():
            status = "✅ 开放" if stats["enabled"] else "❌ 关闭"
            report_content += f"""### {domain} {status}

- **描述**: {stats['description']}
- **子域名数**: {stats['total_subdomains']}
- **用户数**: {stats['unique_users']}
- **启用代理**: {stats['proxied_records']} / 未代理: {stats['non_proxied_records']}

**记录类型分布**:
"""
            for record_type, count in stats["record_types"].items():
                report_content += f"- {record_type}: {count}\n"
            
            report_content += "\n"
        
        report_content += f"""## 👥 用户统计

- **总用户数**: {users.get('total_users', 0)}
- **拥有多个子域名的用户**: {users.get('users_with_multiple_subdomains', 0)}
- **平均每用户子域名数**: {users.get('average_subdomains_per_user', 0):.2f}

### 🏆 用户排行榜 (Top 10)

"""
        
        for i, (username, count) in enumerate(users.get("top_users", [])[:10], 1):
            report_content += f"{i}. **{username}**: {count} 个子域名\n"
        
        report_content += f"""

## 📋 记录统计

- **总记录数**: {records.get('total_records', 0)}
- **最常用 TTL**: {records.get('most_common_ttl', [3600, 0])[0]} 秒 ({records.get('most_common_ttl', [3600, 0])[1]} 次)

### 记录类型分布

"""
        
        for record_type, count in records.get("record_type_distribution", {}).items():
            percentage = (count / records.get('total_records', 1)) * 100
            report_content += f"- **{record_type}**: {count} ({percentage:.1f}%)\n"
        
        proxy_stats = records.get("proxy_usage", {})
        total_proxy = proxy_stats.get("proxied", 0) + proxy_stats.get("not_proxied", 0)
        if total_proxy > 0:
            proxied_pct = (proxy_stats.get("proxied", 0) / total_proxy) * 100
            report_content += f"""
### Cloudflare 代理使用情况

- **启用代理**: {proxy_stats.get('proxied', 0)} ({proxied_pct:.1f}%)
- **未启用代理**: {proxy_stats.get('not_proxied', 0)} ({100-proxied_pct:.1f}%)
"""
        
        report_content += f"""

## 📈 趋势分析

- **最近30天新增**: {trends.get('recent_activity_30days', 0)} 个子域名
- **最活跃月份**: {trends.get('peak_month', ['N/A', 0])[0]} ({trends.get('peak_month', ['N/A', 0])[1]} 个)

### 按月部署统计

"""
        
        for month, count in trends.get("monthly_deployments", {}).items():
            report_content += f"- **{month}**: {count} 个\n"
        
        report_content += f"""

---

*报告由 LibreDomains 统计系统自动生成*
"""
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write(report_content)
        
        print(f"📄 Markdown 统计报告已保存: {filename}")
    
    def print_summary(self):
        """打印统计摘要"""
        summary = self.stats["summary"]
        
        print("\n📊 LibreDomains 统计摘要")
        print("=" * 40)
        print(f"总域名数: {summary.get('total_domains', 0)}")
        print(f"总子域名数: {summary.get('total_subdomains', 0)}")
        print(f"总用户数: {summary.get('total_users', 0)}")
        print(f"最受欢迎记录类型: {summary.get('most_popular_record_type', ['N/A', 0])[0]}")
        
        print("\n📋 域名分布:")
        for domain, stats in self.stats["domains"].items():
            status = "开放" if stats["enabled"] else "关闭"
            print(f"  {domain}: {stats['total_subdomains']} 个子域名 ({status})")
        
        print(f"\n🏆 用户排行榜:")
        for i, (username, count) in enumerate(self.stats["users"].get("top_users", [])[:5], 1):
            print(f"  {i}. {username}: {count} 个")
        
        recent_activity = self.stats["trends"].get("recent_activity_30days", 0)
        print(f"\n📈 最近30天活动: {recent_activity} 个新子域名")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="生成 LibreDomains 统计报告")
    parser.add_argument("--json", "-j", help="JSON 报告输出文件名")
    parser.add_argument("--markdown", "-m", help="Markdown 报告输出文件名")
    parser.add_argument("--summary", "-s", action="store_true", help="只显示摘要")
    
    args = parser.parse_args()
    
    generator = StatisticsGenerator()
    generator.generate_all_stats()
    
    if args.summary:
        generator.print_summary()
    
    if args.json:
        generator.save_json_report(args.json)
    
    if args.markdown:
        generator.save_markdown_report(args.markdown)
    
    if not any([args.json, args.markdown, args.summary]):
        # 默认显示摘要并生成 Markdown 报告
        generator.print_summary()
        generator.save_markdown_report()


if __name__ == "__main__":
    main()
