# LibreDomains Beta

基于 GitHub 和 Cloudflare 的免费二级域名分发服务。

## 🌟 功能特性

- **免费二级域名** 支持多个主域名
- **自动验证和部署** 全程自动化流程
- **Cloudflare 集成** 支持代理和各种 DNS 记录类型
- **多种 DNS 记录类型** (A, AAAA, CNAME, MX, TXT, SRV)
- **基于 GitHub 管理** 无需服务器，全程在 GitHub 完成
- **防滥用保护** 包含用户验证和限制机制

## 📋 可用域名

| 域名 | 状态 | 描述 |
|--------|--------|-------------|
| `ciao.su` | ✅ 开放申请 | 免费二级域名服务 |
| `ciallo.de` | ❌ 即将开放 | 目前不接受申请 |

## 🚀 快速开始

### 用户申请流程

1. **Fork 此仓库**
2. **在 `requests/` 目录创建请求文件**
3. **提交 Pull Request**
4. **等待审核** 和自动部署

### 申请示例

查看 `requests/` 目录中的示例请求文件：

- **个人网站**: [`example-personal-website.json`](requests/example-personal-website.json) - 使用 CNAME 指向 GitHub Pages
- **API 服务**: [`example-api-service.json`](requests/example-api-service.json) - 使用 A 记录指向服务器
- **邮件服务器**: [`example-mail-server.json`](requests/example-mail-server.json) - 使用 MX 记录配置邮件
- **IPv6 网站**: [`example-ipv6-website.json`](requests/example-ipv6-website.json) - 使用 AAAA 记录支持 IPv6

### 基本请求模板

在 `requests/` 目录创建文件 `your-subdomain.json`：

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
  "description": "我的个人网站"
}
```

### 支持的记录类型

- **A**: IPv4 地址
- **AAAA**: IPv6 地址  
- **CNAME**: 别名记录
- **MX**: 邮件交换记录（需要优先级）
- **TXT**: 文本记录
- **SRV**: 服务记录

## 📖 文档

- [用户指南](docs/USER_GUIDE.md) - 如何申请子域名
- [管理员指南](docs/ADMIN_GUIDE.md) - 如何管理服务
- [贡献指南](CONTRIBUTING.md) - 如何参与项目

## 🛡️ 规则和限制

- GitHub 账户年龄至少 30 天
- 每个用户最多申请 3 个子域名
- 禁止成人内容、违法活动或垃圾邮件
- 子域名长度 1-63 字符，只能包含字母数字和连字符
- 不能以连字符开始或结束

## 🛠️ 开发

### 环境设置

```bash
git clone https://github.com/your-username/LibreDomains-beta.git
cd LibreDomains-beta
pip install -r requirements.txt
```

### 脚本使用

```bash
# 验证请求文件
python scripts/validate_request.py requests/example-personal-website.json

# 检查 GitHub 用户
python scripts/check_github_user.py username

# 生成统计信息
python scripts/generate_stats.py

# DNS 健康检查
python scripts/health_check.py
```

## 🤝 贡献

欢迎贡献！请查看我们的 [贡献指南](CONTRIBUTING.md)。

贡献类型:
- 🐛 错误报告和修复
- ✨ 新功能
- 📚 文档改进
- 🎨 界面/体验改进

## 📊 统计信息

生成当前使用统计：

```bash
python scripts/generate_stats.py
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Cloudflare](https://cloudflare.com) for DNS services
- [GitHub Actions](https://github.com/features/actions) for automation
- Inspired by [is-a.dev](https://github.com/is-a-dev/register) and [js.org](https://github.com/js-org/js.org)

## 📞 Support

- [Issues](https://github.com/your-username/LibreDomains-beta/issues) - Report bugs or request features
- [Discussions](https://github.com/your-username/LibreDomains-beta/discussions) - Community support

---

Made with ❤️ by the LibreDomains team
