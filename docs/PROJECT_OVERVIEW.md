# 🌐 LibreDomains 项目完整说明

## 📖 项目概述

LibreDomains 是一个基于 GitHub 和 Cloudflare 的免费二级域名分发服务。用户通过提交 Pull Request 的方式申请子域名，系统自动验证并部署 DNS 记录。

### 🎯 项目特色

- **完全免费**: 无需任何费用
- **自动化流程**: GitHub Actions 自动验证和部署
- **多种记录类型**: 支持 A、AAAA、CNAME、MX、TXT、SRV
- **安全可靠**: Cloudflare 提供 DNS 服务和保护
- **中文支持**: 完整的中文文档和界面

## 🏗️ 系统架构

```
用户请求 → GitHub PR → 自动验证 → 管理员审核 → DNS 部署 → 全球生效
    ↓           ↓            ↓           ↓         ↓         ↓
 JSON文件   GitHub Actions  Python脚本   人工检查  Cloudflare API  DNS传播
```

### 核心组件

1. **GitHub Repository**: 代码和配置管理
2. **GitHub Actions**: 自动化工作流
3. **Python Scripts**: 核心业务逻辑
4. **Cloudflare API**: DNS 记录管理
5. **配置文件**: 域名和规则配置

## 📁 项目结构

```
LibreDomains-beta/
├── .github/workflows/           # GitHub Actions 工作流
│   ├── validate-and-deploy.yml  # 验证和部署
│   ├── pr-comments.yml         # PR 自动评论
│   ├── health-check.yml        # 健康检查
│   ├── status-update.yml       # 状态更新
│   └── test.yml               # 测试工作流
├── config/                     # 配置文件
│   ├── domains.yml            # 域名配置
│   └── schema.json            # 请求格式模式
├── docs/                      # 文档
│   ├── USER_GUIDE.md         # 用户指南
│   ├── ADMIN_GUIDE.md        # 管理员指南
│   └── FAQ.md                # 常见问题
├── domains/                   # 已部署的记录
│   ├── ciao.su/              # 域名目录
│   └── ciallo.de/
├── requests/                  # 用户请求文件
│   ├── example-*.json        # 示例文件
│   └── user-requests.json    # 用户申请
├── scripts/                   # Python 脚本
│   ├── validate_request.py    # 请求验证
│   ├── deploy_dns.py         # DNS 部署
│   ├── check_github_user.py  # 用户检查
│   ├── generate_stats.py     # 统计生成
│   ├── health_check.py       # 健康检查
│   ├── cli.py                # 命令行工具
│   └── status_generator.py   # 状态页面生成
├── tests/                     # 测试文件
├── requirements.txt           # Python 依赖
├── pytest.ini               # 测试配置
├── README.md                 # 项目说明
├── CONTRIBUTING.md           # 贡献指南
└── STATUS.md                 # 状态页面
```

## 🚀 功能特性

### 用户功能
- ✅ 免费子域名申请
- ✅ 支持多种 DNS 记录类型
- ✅ GitHub Pages 集成
- ✅ Cloudflare 代理选项
- ✅ 自动验证和部署

### 管理功能
- ✅ 自动请求验证
- ✅ GitHub 用户检查
- ✅ 滥用防护机制
- ✅ 健康状态监控
- ✅ 统计信息生成

### 技术特性
- ✅ 基于 Python 的后端逻辑
- ✅ GitHub Actions 自动化
- ✅ Cloudflare API 集成
- ✅ 完整的测试覆盖
- ✅ 命令行管理工具

## 🔧 核心脚本说明

### validate_request.py
- **功能**: 验证用户申请请求
- **检查项**: JSON 格式、域名可用性、用户限制、记录格式
- **输出**: 验证结果和错误信息

### deploy_dns.py
- **功能**: 部署和管理 DNS 记录
- **支持**: 创建、更新、删除 DNS 记录
- **集成**: Cloudflare API

### check_github_user.py
- **功能**: 检查 GitHub 用户资格
- **验证**: 账户年龄、仓库信息、历史记录
- **输出**: 用户资格状态

### generate_stats.py
- **功能**: 生成使用统计信息
- **统计**: 用户数量、域名分布、记录类型
- **格式**: JSON 和文本输出

### health_check.py
- **功能**: DNS 健康检查
- **检查**: DNS 解析、HTTP 响应、记录有效性
- **报告**: Markdown 和 JSON 格式

### cli.py
- **功能**: 命令行管理工具
- **命令**: validate、user、stats、health、deploy、list
- **用途**: 本地管理和调试

### status_generator.py
- **功能**: 生成状态页面
- **内容**: 服务状态、统计信息、性能指标
- **输出**: Markdown 状态页面

## 🎛️ 配置文件说明

### domains.yml
```yaml
domains:
  ciao.su:
    enabled: true                    # 是否开放申请
    cloudflare_zone_id: "zone_id"   # Cloudflare Zone ID
    description: "免费域名服务"       # 域名描述
    restrictions: [...]              # 使用限制
    allowed_record_types: [...]      # 支持的记录类型
    max_records_per_subdomain: 5     # 每个子域名最大记录数

settings:
  auto_approve: false              # 是否自动批准
  require_github_verification: true # 是否需要 GitHub 验证
  min_account_age_days: 30         # 最小账户年龄
  max_subdomains_per_user: 3       # 每用户最大子域名数
  blocked_subdomains: [...]        # 禁用的子域名
  blocked_users: [...]             # 禁用的用户
```

### schema.json
定义请求文件的 JSON Schema，包括：
- 必需字段验证
- 数据类型检查
- 格式验证规则
- 枚举值限制

## 🔄 工作流程详解

### 1. 用户申请流程
```
用户Fork仓库 → 创建请求文件 → 提交PR → 自动验证 → 管理员审核 → 合并部署
```

### 2. 自动验证流程
```
PR创建 → 文件变更检测 → JSON格式验证 → 业务规则检查 → 生成评论反馈
```

### 3. DNS部署流程
```
PR合并 → 文件变更检测 → 读取配置 → 调用Cloudflare API → 创建DNS记录 → 保存记录文件
```

### 4. 健康检查流程
```
定时触发 → 遍历所有记录 → DNS解析测试 → HTTP响应检查 → 生成健康报告
```

## 🛡️ 安全特性

### 用户验证
- GitHub 账户年龄验证
- 邮箱验证（可选）
- 用户黑名单机制
- 申请数量限制

### 内容审核
- 禁用敏感子域名
- 内容政策检查
- 滥用监控和报告
- 快速响应机制

### 系统安全
- API Token 权限最小化
- GitHub Secrets 安全存储
- 自动化安全扫描
- 依赖漏洞检查

## 📊 监控和统计

### 实时监控
- DNS 解析状态
- 服务可用性
- API 响应时间
- 错误率统计

### 统计报告
- 用户增长趋势
- 域名使用分布
- 记录类型统计
- 性能指标分析

## 🚀 部署指南

### 环境要求
- Python 3.8+
- GitHub 仓库
- Cloudflare 账户
- GitHub Actions 启用

### 配置步骤
1. **Fork 仓库**
2. **配置 Cloudflare API Token**
3. **设置 GitHub Secrets**
4. **更新域名配置**
5. **启用 GitHub Actions**

### 验证部署
```bash
# 验证配置
python scripts/cli.py validate requests/example-personal-website.json

# 检查健康状态
python scripts/cli.py health

# 生成统计信息
python scripts/cli.py stats
```

## 🤝 贡献方式

### 开发者贡献
- 🐛 错误修复
- ✨ 新功能开发
- 📚 文档改进
- 🧪 测试用例添加

### 用户贡献
- 📝 反馈问题
- 💡 功能建议
- 📖 文档翻译
- 🗣️ 社区推广

## 📈 未来规划

### 短期目标
- [ ] 添加更多域名
- [ ] 优化性能监控
- [ ] 改进用户体验
- [ ] 增强安全防护

### 长期目标
- [ ] 支持自定义域名
- [ ] 实现负载均衡
- [ ] 添加CDN功能
- [ ] 开发Web界面

## 📞 支持渠道

### 技术支持
- **GitHub Issues**: 错误报告和功能请求
- **GitHub Discussions**: 社区讨论和提问
- **文档**: 详细的使用指南和FAQ

### 社区资源
- **用户指南**: 完整的申请和使用教程
- **管理员指南**: 服务管理和维护指南
- **常见问题**: 解答常见疑惑

---

## 🎉 项目亮点

1. **全中文支持**: 完整的中文文档和界面
2. **自动化程度高**: 从申请到部署全程自动化
3. **安全可靠**: 多重验证和安全防护
4. **易于扩展**: 模块化设计，便于添加新功能
5. **开源透明**: 所有代码公开，接受社区监督

这个项目实现了一个完整的、功能齐全的二级域名分发服务，具有良好的可维护性和可扩展性。通过 GitHub 和 Cloudflare 的集成，为用户提供了免费、可靠的子域名服务。
