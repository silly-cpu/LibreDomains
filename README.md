# LibreDomains - 免费二级域名分发系统

<div align="center">

![LibreDomains](https://img.shields.io/badge/LibreDomains-v1.0.0-blue.svg)
![Next.js](https://img.shields.io/badge/Next.js-14.0+-black.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

一个基于 GitHub 和 Cloudflare 的现代化免费二级域名分发系统

[在线申请](https://your-domain.pages.dev) • [使用文档](./docs/用户使用文档.md) • [管理文档](./docs/管理员使用文档.md) • [提交问题](https://github.com/yourusername/LibreDomains-beta/issues)

</div>

## ✨ 特色功能

- 🌐 **多域名支持** - 支持管理多个根域名，灵活配置启用状态
- 🎨 **现代化 UI** - 基于 Next.js 和 TailwindCSS 的美观界面
- 🔧 **管理员面板** - 完整的后台管理功能，支持域名和申请管理
- ⚡ **自动化部署** - 支持 Cloudflare Pages 一键部署
- 🚀 **GitHub 集成** - 自动化的 PR 验证和审核流程
- 🔒 **安全可靠** - 权限验证、输入校验、防重复申请
- 📱 **响应式设计** - 完美适配桌面和移动设备

## 🌍 可用域名

目前提供以下域名服务：

- ✅ **ciao.su** - 主要域名，稳定服务
- ⚠️ **test.com** - 测试域名，可能禁用

## 🚀 快速开始

### 用户申请

1. 访问 [申请页面](https://your-domain.pages.dev)
2. 填写子域名信息
3. 选择记录类型和内容
4. 提交申请等待审核

### 支持的记录类型

| 类型 | 说明 | 示例 |
|------|------|------|
| A | IPv4 地址 | `192.0.2.1` |
| AAAA | IPv6 地址 | `2001:db8::1` |
| CNAME | 域名别名 | `example.com` |
| TXT | 文本记录 | `v=spf1 include:_spf.example.com ~all` |

## 📖 文档

- 📘 [用户使用文档](./docs/用户使用文档.md) - 详细的申请和使用指南
- 📗 [管理员使用文档](./docs/管理员使用文档.md) - 部署和管理指南
- 📙 [API 文档](./docs/API文档.md) - 开发者接口说明

## 🛠️ 技术栈

- **前端**: Next.js 14, React 18, TailwindCSS
- **后端**: Next.js API Routes, Node.js
- **DNS**: Cloudflare API
- **部署**: Cloudflare Pages
- **版本控制**: GitHub + GitHub Actions
- **数据存储**: JSON 文件 (静态)

## 📦 项目结构

```
LibreDomains-beta/
├── pages/                 # Next.js 页面
│   ├── index.js          # 用户申请页面
│   ├── admin.js          # 管理员面板
│   └── api/              # API 路由
├── config/               # 配置文件
│   └── domains.json      # 域名配置
├── subdomains/           # 子域名数据
├── scripts/              # 自动化脚本
├── docs/                 # 项目文档
└── .github/workflows/    # GitHub Actions
```

## 🔧 本地开发

```bash
# 克隆项目
git clone https://github.com/yourusername/LibreDomains-beta.git
cd LibreDomains-beta

# 安装依赖
npm install

# 配置环境变量
cp .env.example .env.local
# 编辑 .env.local 填入你的配置

# 启动开发服务器
npm run dev
```

访问 `http://localhost:3000` 查看效果。

## 📋 部署要求

### 必需配置

- **Cloudflare 账户** - 用于 DNS 管理和 Pages 部署
- **域名** - 至少一个托管在 Cloudflare 的域名
- **API 令牌** - Cloudflare API 访问权限

### 可选配置

- **GitHub 仓库** - 用于 PR 自动化流程
- **自定义域名** - 替换默认的 pages.dev 域名

## 🚀 部署到 Cloudflare Pages

### 方法一：GitHub 集成 (推荐)

1. Fork 本仓库到你的 GitHub 账户
2. 在 Cloudflare Pages 中连接 GitHub 仓库
3. 设置构建配置：
   - **Framework**: Next.js (Static HTML Export)
   - **Build command**: `npm run build`
   - **Output directory**: `out`
4. 配置环境变量
5. 部署完成

### 方法二：CLI 部署

```bash
# 安装 Wrangler CLI
npm install -g wrangler

# 登录 Cloudflare
wrangler login

# 构建项目
npm run build

# 部署
wrangler pages deploy out --project-name libredomains
```

## ⚙️ 环境变量

| 变量名 | 说明 | 必需 |
|--------|------|------|
| `CLOUDFLARE_API_TOKEN` | Cloudflare API 令牌 | ✅ |
| `CLOUDFLARE_ACCOUNT_ID` | Cloudflare 账户 ID | ✅ |
| `ADMIN_PASSWORD` | 管理员面板密码 | ✅ |
| `GITHUB_TOKEN` | GitHub API 令牌 | ❌ |
| `GITHUB_REPO` | GitHub 仓库名 | ❌ |

## 🤝 贡献指南

我们欢迎所有形式的贡献！

### 报告问题
- 使用 [GitHub Issues](https://github.com/yourusername/LibreDomains-beta/issues) 报告 bug
- 提供详细的错误信息和复现步骤

### 提交代码
1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

### 改进文档
- 修正文档中的错误
- 添加使用示例
- 翻译文档到其他语言

## 📄 许可证

本项目基于 MIT 许可证开源 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [Cloudflare](https://cloudflare.com) - 提供强大的 DNS 和 CDN 服务
- [Next.js](https://nextjs.org) - 现代化的 React 框架
- [TailwindCSS](https://tailwindcss.com) - 实用优先的 CSS 框架
- [GitHub](https://github.com) - 代码托管和自动化服务

## 📞 联系我们

- 📧 邮箱: admin@example.com
- 🐛 问题反馈: [GitHub Issues](https://github.com/yourusername/LibreDomains-beta/issues)
- 💬 讨论: [GitHub Discussions](https://github.com/yourusername/LibreDomains-beta/discussions)

## 🔄 更新日志

### v1.0.0 (2025-01-01)
- 🎉 项目正式发布
- ✨ 支持多域名管理
- 🎨 现代化的用户界面
- 🔧 完整的管理员面板
- 🚀 自动化部署流程

---

<div align="center">

**如果这个项目对你有帮助，请给我们一个 ⭐️**

Made with ❤️ by LibreDomains Team

</div>