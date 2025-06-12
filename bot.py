# bot.py: GitHub Bot for managing pull requests for subdomain allocations

import os
import json
import logging
import re
import argparse

import requests
from jsonschema import validate, ValidationError

from github import Github

# Configuration
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_NAME = os.getenv("GITHUB_REPO")  # e.g., 'username/repo'
CONFIG_PATH = 'config/domains.json'
SCHEMA_PATH = 'config/schema.json'

# Cloudflare
CF_API_TOKEN = os.getenv("CF_API_TOKEN")
CF_ZONE_IDS = json.loads(os.getenv("CF_ZONE_IDS", "{}"))  # {"ciao.su": "zone_id", ...}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load config
with open(CONFIG_PATH) as f:
    domains_config = json.load(f)
with open(SCHEMA_PATH) as f:
    schema = json.load(f)

# GitHub client
g = Github(GITHUB_TOKEN)
repo = g.get_repo(REPO_NAME)

# JSON schema for subdomain request
# ...existing code...


def check_pr(pr):
    """
    Validate PR title, files, JSON schema, availability, etc.
    """
    # Check title format e.g. "Add subdomain foo for domain ciao.su"
    pattern = r"Add subdomain (?P<sub>[a-z0-9-]+) for domain (?P<domain>[a-z0-9.]+)"
    m = re.match(pattern, pr.title)
    if not m:
        pr.create_issue_comment("PR标题格式错误，应为：`Add subdomain <name> for domain <domain>`")
        pr.edit(state='closed')
        return

    sub = m.group('sub')
    domain = m.group('domain')

    # Check domain enabled
    entry = next((d for d in domains_config if d['domain'] == domain), None)
    if not entry or not entry['enabled']:
        pr.create_issue_comment(f"域名 `{domain}` 未开放申请。")
        pr.edit(state='closed')
        return

    # Ensure exactly one file modified and it's the correct JSON
    files = list(pr.get_files())
    expected_path = f"domains/{domain}.json"
    if len(files) != 1 or files[0].filename != expected_path:
        pr.create_issue_comment("一次只能修改 `domains/<domain>.json` 文件并且一次只添加一个子域名。")
        pr.edit(state='closed')
        return

    file_path = expected_path
    # Load new and old JSON lists
    try:
        new_raw = repo.get_contents(file_path, ref=pr.head.ref).decoded_content
        old_raw = repo.get_contents(file_path, ref=pr.base.ref).decoded_content
        new_list = json.loads(new_raw)
        old_list = json.loads(old_raw)
    except Exception:
        pr.create_issue_comment("无法读取或解析 JSON 文件。请检查文件格式。")
        pr.edit(state='closed')
        return

    # Determine added entries
    added = [item for item in new_list if item not in old_list]
    if len(added) != 1:
        pr.create_issue_comment("一次只能添加一个子域名申请。请确保只新增一个 JSON entry。")
        pr.edit(state='closed')
        return

    data = added[0]
    # Validate entry against schema
    try:
        validate(instance=data, schema=schema)
    except ValidationError as e:
        pr.create_issue_comment(f"JSON 校验失败: {e.message}")
        pr.edit(state='closed')
        return

    # Ensure name matches title
    if data.get('name') != sub:
        pr.create_issue_comment("JSON 中的 `name` 字段与 PR 标题中的子域名不匹配。")
        pr.edit(state='closed')
        return

    # Check subdomain availability against old list
    if any(item.get('name') == sub for item in old_list):
        pr.create_issue_comment(f"子域名 `{sub}` 已被占用。")
        pr.edit(state='closed')
        return

    # All checks passed
    pr.create_issue_comment("申请通过，等待管理员合并。")


def create_cloudflare_record(data, domain):
    entry = next((d for d in domains_config if d['domain'] == domain), None)
    zone_id = entry['zone_id']
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records"
    headers = {"Authorization": f"Bearer {CF_API_TOKEN}", "Content-Type": "application/json"}
    payload = {
        "type": data["type"],
        "name": f"{data['name']}.{domain}",
        "content": data["content"],
        "ttl": data.get("ttl", 1),
        "proxied": data.get("proxied", False)
    }
    r = requests.post(url, headers=headers, json=payload)
    if not r.ok:
        logger.error(f"Failed to create DNS record: {r.text}")
    else:
        logger.info(f"Created DNS record: {payload['name']}")


def apply_pr(pr_number):
    pr = repo.get_pull(pr_number)
    if not pr.merged:
        logger.info(f"PR #{pr_number} not merged, skipping")
        return
    for f in pr.get_files():
        m = re.match(r"domains/(?P<domain>.+)\\.json", f.filename)
        if not m:
            continue
        domain = m.group('domain')
        new_raw = repo.get_contents(f.filename, ref=pr.head.ref).decoded_content
        old_raw = repo.get_contents(f.filename, ref=pr.base.ref).decoded_content
        new_list = json.loads(new_raw)
        old_list = json.loads(old_raw)
        added = [item for item in new_list if item not in old_list]
        for entry in added:
            create_cloudflare_record(entry, domain)


def main():
    parser = argparse.ArgumentParser(description='Subdomain allocation bot')
    parser.add_argument('--apply', action='store_true', help='Apply DNS changes on merged PR')
    parser.add_argument('--pr-number', type=int, help='PR number to apply')
    args = parser.parse_args()
    if args.apply:
        apply_pr(args.pr_number)
        return

    # 对未合并的 PR 进行校验
    for pr in repo.get_pulls(state='open'):
        check_pr(pr)


if __name__ == '__main__':
    main()
