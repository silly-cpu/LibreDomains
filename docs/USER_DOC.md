# 用户使用文档

## 前提

- 用户需拥有 GitHub 账号。
- 已知目标仓库地址，如 `https://github.com/yourname/LibreDomains-beta`。

## 申请子域名步骤

1. Fork 该仓库到自己的 GitHub 账号。
2. 在本地克隆 Fork 后的仓库：
   ```powershell
   git clone https://github.com/yourname/LibreDomains-beta.git
   cd LibreDomains-beta
   ```
3. 切换到主分支并拉取最新更新：
   ```powershell
   git checkout main
   git pull upstream main
   ```
4. 在 `domains/<domain>.json` 文件中添加新的子域名申请，用以下格式：
   ```json
   {
     "name": "subdomain",
     "type": "A",
     "content": "123.123.123.123",
     "ttl": 120,
     "proxied": false
   }
   ```
5. 提交并推送你的更改：
   ```powershell
   git add domains/<domain>.json
   git commit -m "Add subdomain subdomain for domain ciao.su"
   git push origin main
   ```
6. 在 GitHub 上发起 Pull Request，并确保 PR 标题格式为：
   ```text
   Add subdomain <name> for domain <domain>
   ```
7. 等待 Bot 自动校验，通过后管理员会合并 PR，并最终在 Cloudflare 上生效。

## 注意事项

- 子域名名称只能包含小写字母、数字和短横线（-）。
- `type` 必须是常见的 DNS 类型，如 A、CNAME、TXT 等。
- `content` 字段根据记录类型填写相应内容。
- `ttl` 默认为 1（自动），可选填写大于或等于 1 的整数。
- `proxied` 字段为可选，默认为 false。

