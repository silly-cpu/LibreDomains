#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub 用户检查脚本
检查 GitHub 用户信息和统计数据
"""

import os
import sys
import json
import requests
from datetime import datetime
from typing import Dict, Any, List


class GitHubUserChecker:
    """GitHub 用户检查器"""
    
    def __init__(self):
        self.github_token = os.getenv("GITHUB_TOKEN")
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "LibreDomains-Bot"
        }
        if self.github_token:
            self.headers["Authorization"] = f"token {self.github_token}"
    
    def get_user_info(self, username: str) -> Dict[str, Any]:
        """获取 GitHub 用户信息"""
        try:
            response = requests.get(
                f"https://api.github.com/users/{username}",
                headers=self.headers
            )
            
            if response.status_code == 404:
                return {"error": "用户不存在", "exists": False}
            
            response.raise_for_status()
            user_data = response.json()
            
            # 计算账户年龄
            created_at = datetime.fromisoformat(user_data["created_at"].replace("Z", "+00:00"))
            account_age_days = (datetime.now().astimezone() - created_at).days
            
            return {
                "exists": True,
                "username": user_data["login"],
                "name": user_data.get("name"),
                "email": user_data.get("email"),
                "bio": user_data.get("bio"),
                "company": user_data.get("company"),
                "location": user_data.get("location"),
                "blog": user_data.get("blog"),
                "twitter_username": user_data.get("twitter_username"),
                "public_repos": user_data["public_repos"],
                "public_gists": user_data["public_gists"],
                "followers": user_data["followers"],
                "following": user_data["following"],
                "created_at": user_data["created_at"],
                "updated_at": user_data["updated_at"],
                "account_age_days": account_age_days,
                "avatar_url": user_data["avatar_url"],
                "html_url": user_data["html_url"]
            }
        
        except requests.RequestException as e:
            return {"error": f"API 请求失败: {e}", "exists": False}
    
    def get_user_repositories(self, username: str, limit: int = 10) -> List[Dict[str, Any]]:
        """获取用户的公开仓库"""
        try:
            response = requests.get(
                f"https://api.github.com/users/{username}/repos",
                headers=self.headers,
                params={
                    "sort": "updated",
                    "direction": "desc",
                    "per_page": limit
                }
            )
            response.raise_for_status()
            
            repos = []
            for repo in response.json():
                repos.append({
                    "name": repo["name"],
                    "description": repo.get("description"),
                    "language": repo.get("language"),
                    "stars": repo["stargazers_count"],
                    "forks": repo["forks_count"],
                    "updated_at": repo["updated_at"],
                    "html_url": repo["html_url"]
                })
            
            return repos
        
        except requests.RequestException as e:
            print(f"⚠️ 获取用户仓库失败: {e}")
            return []
    
    def count_user_subdomains(self, username: str) -> Dict[str, int]:
        """统计用户的子域名数量"""
        count_by_domain = {}
        total_count = 0
        
        domains_dir = os.path.join(os.path.dirname(__file__), "..", "domains")
        
        if not os.path.exists(domains_dir):
            return {"total": 0}
        
        for domain_folder in os.listdir(domains_dir):
            domain_path = os.path.join(domains_dir, domain_folder)
            if not os.path.isdir(domain_path):
                continue
            
            domain_count = 0
            for file in os.listdir(domain_path):
                if file.endswith(".json"):
                    file_path = os.path.join(domain_path, file)
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            data = json.load(f)
                            if data.get("owner", {}).get("username", "").lower() == username.lower():
                                domain_count += 1
                                total_count += 1
                    except (json.JSONDecodeError, FileNotFoundError):
                        continue
            
            if domain_count > 0:
                count_by_domain[domain_folder] = domain_count
        
        count_by_domain["total"] = total_count
        return count_by_domain
    
    def get_user_subdomains(self, username: str) -> List[Dict[str, Any]]:
        """获取用户的所有子域名详情"""
        subdomains = []
        domains_dir = os.path.join(os.path.dirname(__file__), "..", "domains")
        
        if not os.path.exists(domains_dir):
            return []
        
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
                                subdomain_name = file[:-5]  # 移除 .json 后缀
                                subdomains.append({
                                    "domain": domain_folder,
                                    "subdomain": subdomain_name,
                                    "full_domain": f"{subdomain_name}.{domain_folder}",
                                    "record_type": data.get("record", {}).get("type"),
                                    "record_value": data.get("record", {}).get("value"),
                                    "description": data.get("description"),
                                    "deployed_at": data.get("_metadata", {}).get("deployed_at")
                                })
                    except (json.JSONDecodeError, FileNotFoundError):
                        continue
        
        return sorted(subdomains, key=lambda x: x["full_domain"])
    
    def check_user_eligibility(self, username: str, min_age_days: int = 30) -> Dict[str, Any]:
        """检查用户申请资格"""
        user_info = self.get_user_info(username)
        
        if not user_info.get("exists"):
            return {
                "eligible": False,
                "reason": user_info.get("error", "用户不存在")
            }
        
        eligibility = {
            "eligible": True,
            "reasons": [],
            "warnings": []
        }
        
        # 检查账户年龄
        if user_info["account_age_days"] < min_age_days:
            eligibility["eligible"] = False
            eligibility["reasons"].append(f"账户年龄不足 {min_age_days} 天（当前: {user_info['account_age_days']} 天）")
        
        # 检查子域名数量限制
        subdomain_count = self.count_user_subdomains(username)["total"]
        max_subdomains = 3  # 可以从配置文件读取
        
        if subdomain_count >= max_subdomains:
            eligibility["eligible"] = False
            eligibility["reasons"].append(f"已达到最大子域名数量限制 ({subdomain_count}/{max_subdomains})")
        
        # 警告信息
        if user_info["public_repos"] == 0:
            eligibility["warnings"].append("用户没有公开仓库")
        
        if not user_info.get("email"):
            eligibility["warnings"].append("用户未公开邮箱地址")
        
        return eligibility


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="检查 GitHub 用户信息")
    parser.add_argument("username", help="GitHub 用户名")
    parser.add_argument("--detailed", "-d", action="store_true", help="显示详细信息")
    parser.add_argument("--repos", "-r", action="store_true", help="显示用户仓库")
    parser.add_argument("--subdomains", "-s", action="store_true", help="显示用户子域名")
    
    args = parser.parse_args()
    
    checker = GitHubUserChecker()
    
    print(f"🔍 检查 GitHub 用户: {args.username}")
    print("=" * 50)
    
    # 获取用户基本信息
    user_info = checker.get_user_info(args.username)
    
    if not user_info.get("exists"):
        print(f"❌ {user_info.get('error', '用户不存在')}")
        sys.exit(1)
    
    print(f"✅ 用户存在: {user_info['username']}")
    if user_info.get("name"):
        print(f"📝 真实姓名: {user_info['name']}")
    if user_info.get("bio"):
        print(f"📋 个人简介: {user_info['bio']}")
    if user_info.get("location"):
        print(f"📍 位置: {user_info['location']}")
    if user_info.get("company"):
        print(f"🏢 公司: {user_info['company']}")
    if user_info.get("blog"):
        print(f"🌐 博客: {user_info['blog']}")
    
    print(f"📊 统计数据:")
    print(f"  • 公开仓库: {user_info['public_repos']}")
    print(f"  • 关注者: {user_info['followers']}")
    print(f"  • 正在关注: {user_info['following']}")
    print(f"  • 账户年龄: {user_info['account_age_days']} 天")
    print(f"  • 创建时间: {user_info['created_at']}")
    
    # 检查申请资格
    print(f"\n🎯 申请资格检查:")
    eligibility = checker.check_user_eligibility(args.username)
    
    if eligibility["eligible"]:
        print("✅ 符合申请条件")
    else:
        print("❌ 不符合申请条件")
        for reason in eligibility["reasons"]:
            print(f"  • {reason}")
    
    if eligibility["warnings"]:
        print("⚠️ 警告:")
        for warning in eligibility["warnings"]:
            print(f"  • {warning}")
    
    # 子域名统计
    subdomain_count = checker.count_user_subdomains(args.username)
    if subdomain_count["total"] > 0:
        print(f"\n📊 子域名统计:")
        print(f"  • 总数: {subdomain_count['total']}")
        for domain, count in subdomain_count.items():
            if domain != "total":
                print(f"  • {domain}: {count}")
    
    # 显示详细信息
    if args.detailed:
        print(f"\n📄 详细信息:")
        print(f"  • 头像: {user_info['avatar_url']}")
        print(f"  • 主页: {user_info['html_url']}")
        if user_info.get("email"):
            print(f"  • 邮箱: {user_info['email']}")
        if user_info.get("twitter_username"):
            print(f"  • Twitter: @{user_info['twitter_username']}")
    
    # 显示用户仓库
    if args.repos:
        print(f"\n📚 最近仓库:")
        repos = checker.get_user_repositories(args.username)
        if repos:
            for repo in repos:
                print(f"  • {repo['name']}")
                if repo.get("description"):
                    print(f"    描述: {repo['description']}")
                if repo.get("language"):
                    print(f"    语言: {repo['language']}")
                print(f"    ⭐ {repo['stars']} 🍴 {repo['forks']}")
                print()
        else:
            print("  无公开仓库或获取失败")
    
    # 显示用户子域名
    if args.subdomains:
        print(f"\n🌐 用户子域名:")
        subdomains = checker.get_user_subdomains(args.username)
        if subdomains:
            for subdomain in subdomains:
                print(f"  • {subdomain['full_domain']}")
                print(f"    类型: {subdomain['record_type']}")
                print(f"    值: {subdomain['record_value']}")
                print(f"    描述: {subdomain['description']}")
                if subdomain.get("deployed_at"):
                    print(f"    部署时间: {subdomain['deployed_at']}")
                print()
        else:
            print("  无子域名记录")


if __name__ == "__main__":
    main()
