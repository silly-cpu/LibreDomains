# 管理员使用文档

## 环境准备

1. 在本地安装 Python，建议版本 >= 3.8。
2. 克隆仓库并进入目录：
   ```powershell
   git clone https://github.com/yourname/LibreDomains-beta.git
   cd LibreDomains-beta
   ```
3. 安装依赖：
   ```powershell
   pip install -r requirements.txt
   ```
4. 在 GitHub 仓库设置 Secrets：
   - `GITHUB_TOKEN`：具有 repo 权限的个人访问令牌。
   - `CF_API_TOKEN`：Cloudflare API Token，具有 DNS 编辑权限。
   - `GITHUB_REPO`：形如 `yourname/LibreDomains-beta`。

5. 配置可申请域名，在 `config/domains.json` 中添加或修改条目：
   ```json
   {
     "domain": "example.com",
     "enabled": true,
     "zone_id": "<YOUR_CF_ZONE_ID>",
     "subdomains": []
   }
   ```

## 运行 Bot

- 本地检查和校验 Pull Request：
  ```powershell
  python bot.py
  ```
- 当 PR 合并后，应用 DNS 记录：
  ```powershell
  python bot.py --apply --pr-number 123
  ```

## 自动化部署（可选）

可以将 Bot 部署为 GitHub Actions：

```yaml
name: Subdomain Allocation Bot

on:
  pull_request:
    types: [opened, edited, reopened]
  pull_request_target:
    types: [closed]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.x'
      - name: Install deps
        run: pip install -r requirements.txt
      - name: Run bot validate
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          GITHUB_REPO: ${{ github.repository }}
          CF_API_TOKEN: ${{ secrets.CF_API_TOKEN }}
          CF_ZONE_IDS: '{}'
        run: python bot.py

  apply:
    if: github.event.pull_request.merged == true
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.x'
      - name: Install deps
        run: pip install -r requirements.txt
      - name: Apply DNS records
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          GITHUB_REPO: ${{ github.repository }}
          CF_API_TOKEN: ${{ secrets.CF_API_TOKEN }}
          CF_ZONE_IDS: '{}'
        run: |
          python bot.py --apply --pr-number ${{ github.event.pull_request.number }}
```
