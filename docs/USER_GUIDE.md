# LibreDomains 用户指南

本指南将帮助您申请和管理免费子域名。

## 🚀 快速开始

### 第一步：Fork 仓库

1. 访问 [LibreDomains-beta](https://github.com/bestZwei/LibreDomains-beta)
2. 点击右上角的 **Fork** 按钮
3. 将您的 fork 克隆到本地

### 第二步：创建申请请求

1. 在 `requests/` 目录中创建新文件
2. 命名为 `your-subdomain-name.json`
3. 使用下面的模板

### 第三步：提交 Pull Request

1. 提交您的请求文件
2. 推送到您的 fork
3. 向主仓库创建 Pull Request

## 📝 请求模板

```json
{
  "domain": "ciao.su",
  "subdomain": "mysite",
  "owner": {
    "username": "your-github-username",
    "email": "your-email@example.com"
  },
  "record": {
    "type": "A",
    "value": "192.168.1.1",
    "ttl": 3600,
    "proxied": false
  },
  "description": "我的网站的简短描述"
}
```

## 🎯 记录类型

### A 记录 (IPv4)
```json
"record": {
  "type": "A",
  "value": "203.0.113.10",  "ttl": 3600,
  "proxied": true
}
```

### AAAA 记录 (IPv6)
```json
"record": {
  "type": "AAAA",
  "value": "2001:db8::1",
  "ttl": 3600,
  "proxied": false
}
```

### CNAME 记录
```json
"record": {
  "type": "CNAME",
  "value": "username.github.io",
  "ttl": 3600,
  "proxied": false
}
```

### MX 记录
```json
"record": {
  "type": "MX",
  "value": "mail.example.com",
  "priority": 10,
  "ttl": 3600,
  "proxied": false
}
```

### TXT 记录
```json
"record": {
  "type": "TXT",
  "value": "v=spf1 include:_spf.google.com ~all",
  "ttl": 3600,
  "proxied": false
}
```

## 🛡️ 规则和要求

### GitHub 账户要求
- 账户年龄至少 **30 天**
- 必须有已验证的邮箱地址
- 每个用户最多 **3 个子域名**

### 子域名要求
- 长度 1-63 字符
- 只能包含字母、数字和连字符
- 不能以连字符开始或结束
- 在域名下必须唯一

### 内容政策
- ✅ 个人网站和作品集
- ✅ 开源项目
- ✅ 教育内容
- ✅ 非商业 API
- ❌ 成人内容
- ❌ 违法活动
- ❌ 垃圾邮件或钓鱼
- ❌ 商业服务

## 🔧 常见用例

### GitHub Pages 网站
适用于个人作品集和项目文档。

```json
{
  "domain": "ciao.su",
  "subdomain": "portfolio",
  "owner": {
    "username": "johndoe",
    "email": "john@example.com"
  },
  "record": {
    "type": "CNAME",
    "value": "johndoe.github.io",
    "ttl": 3600,
    "proxied": false
  },
  "description": "展示我的开发项目的个人作品集网站"
}
```

### API 端点
用于托管 API 和 Web 服务。

```json
{
  "domain": "ciao.su",
  "subdomain": "api",
  "owner": {
    "username": "developer",
    "email": "dev@example.com"
  },
  "record": {
    "type": "A",
    "value": "203.0.113.100",
    "ttl": 3600,
    "proxied": true
  },
  "description": "我的移动应用的 REST API，包含用户管理功能"
}
```

## ⚡ 提示和最佳实践

### 选择记录类型
- **A/AAAA**: 当您有直接的 IP 地址时
- **CNAME**: 当指向另一个域名时（如 GitHub Pages）
- **MX**: 用于邮件服务
- **TXT**: 用于验证和配置

### TTL 设置
- **300-600**: 用于测试或频繁更改的记录
- **3600**（默认）: 大多数用例的良好平衡
- **7200-86400**: 用于稳定、很少更改的记录

### Cloudflare 代理
- **启用** (`proxied: true`) 适用于:
  - DDoS 保护
  - 更好的性能（CDN）
  - SSL 终端
- **禁用** (`proxied: false`) 适用于:
  - 私有 IP 地址
  - 非 Web 服务
  - 需要直接 DNS 解析

## 🚨 故障排除

### 请求被拒绝
- 检查子域名是否已被占用
- 验证您的 GitHub 账户是否符合要求
- 确保请求遵循模式规范

### DNS 不解析
- 等待 24-48 小时全球 DNS 传播
- 检查是否使用了正确的记录类型
- 验证您的目标服务器是否可访问

### 需要更新记录
- 创建包含更新信息的新请求文件
- 系统将自动更新现有记录

## 📞 获取帮助

- **Issues**: 报告错误或问题
- **Discussions**: 提问并获得社区帮助
- **邮件**: 联系维护者处理紧急问题

## 🔄 更新您的记录

要更新现有子域名：

1. 修改您的原始请求文件
2. 更新您想要更改的值
3. 提交新的 Pull Request
4. 系统将自动更新 DNS 记录

## 🗑️ 删除您的子域名

要删除您的子域名：

1. 从 `requests/` 目录删除您的请求文件
2. 提交 Pull Request
3. DNS 记录将自动删除

---

**需要更多帮助？** 查看我们的 [FAQ](FAQ.md) 或 [创建 issue](https://github.com/bestZwei/LibreDomains-beta/issues/new)。
