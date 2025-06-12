# 项目架构说明

## 1. 工作流程

1. **配置域名**
   - 管理员在 `config/domains.json` 中添加可申请的域名及其 Cloudflare `zone_id`。
2. **提交申请**
   - 用户 Fork 仓库并在 `domains/<domain>.json` 中添加申请条目。
   - 用户提交 Pull Request，PR 标题需遵循 `Add subdomain <name> for domain <domain>`。
3. **自动校验**
   - GitHub Action 或定时任务触发 `bot.py` 执行校验。
   - 校验 PR 标题、修改文件、JSON Schema、子域名唯一性等。
4. **管理员审批**
   - Bot 在 PR 中留言通过或拒绝。
   - 管理员合并通过的 PR。
5. **应用 DNS**
   - 合并 PR 后触发 `bot.py --apply`，通过 Cloudflare API 创建 DNS 记录。

## 2. 关键模块

- **bot.py**
  - `check_pr(pr)`: 校验 PR 合规性。
  - `apply_pr(pr_number)`: 处理合并后的 PR，通过 Cloudflare API 创建解析。
  - `create_cloudflare_record(data, domain)`: 调用 Cloudflare API 创建记录。

- **config/domains.json**
  - 定义可申请的域名列表及状态。

- **config/schema.json**
  - 定义申请文件 JSON 格式。

- **domains/**
  - 存放各域名的申请记录 JSON 文件。

## 3. 安全及权限

- GitHub Actions 使用 `pull_request_target` 来确保有权限关闭或评论 PR。
- Cloudflare API Token 权限仅限 DNS 编辑。

## 4. 扩展性

- 支持更多 DNS 记录类型，已在 `schema.json` 中定义。
- 可扩展到其他 DNS 提供商，只需实现相应的 API 操作模块。

