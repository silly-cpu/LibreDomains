# LibreDomains - 自由域名分发服务

LibreDomains 是一个开源的二级域名分发服务，允许用户通过 GitHub Pull Request 来申请和管理二级域名。

## 可用域名

目前，本项目提供以下域名：

| 域名 | 状态 | 描述 |
|------|------|------|
| ciao.su | ✅ 可用 | 主要域名 |
| ciallo.de | ⏸️ 暂停开放 | 备用域名 |

## 申请域名

### 申请步骤

1. Fork 本仓库
2. 在 `domains/[域名]/` 目录下创建一个以你想要申请的子域名命名的 JSON 文件
   - 例如: `domains/ciao.su/mysubdomain.json`
3. 按照下面的格式填写 JSON 文件
4. 提交 Pull Request
5. 等待自动检查和审核
6. Pull Request 被合并后，你的域名记录将在几分钟内生效

### JSON 格式

```json
{
  "owner": {
    "name": "你的名字",
    "github": "你的GitHub用户名",
    "email": "你的邮箱（可选）"
  },
  "records": [
    {
      "type": "A",
      "name": "@",
      "content": "185.199.108.153",
      "ttl": 3600,
      "proxied": true
    },
    {
      "type": "CNAME",
      "name": "www",
      "content": "你的GitHub用户名.github.io",
      "ttl": 3600,
      "proxied": true
    }
  ]
}
```

### 支持的 DNS 记录类型

- `A` - IPv4 地址
- `AAAA` - IPv6 地址
- `CNAME` - 别名
- `TXT` - 文本记录
- `MX` - 邮件交换记录

### 规则

1. 子域名必须由小写字母、数字和连字符组成
2. 子域名长度在 2-63 个字符之间
3. 子域名不能以连字符开头或结尾
4. 一个 GitHub 用户最多可以申请 3 个子域名
5. 每个子域名最多可以有 10 个 DNS 记录
6. 不允许申请以下保留的子域名:
   - `www`, `mail`, `email`, `webmail`, `api`, `dev`, `blog`, `app`, `admin`, `ns`, `dns`

## 管理域名

成功创建你的域名后，若要更新记录:

1. 编辑你之前创建的 JSON 文件
2. 提交新的 Pull Request
3. 等待自动检查和审核
4. Pull Request 被合并后，更新将在几分钟内生效

## 贡献代码

欢迎提交 Pull Request 来改进本项目！

1. Fork 本仓库
2. 创建你的特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交你的更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 提交 Pull Request

## 技术实现

- Python 脚本处理域名验证和部署
- GitHub Actions 用于自动化 PR 检查和部署
- Cloudflare API 进行 DNS 记录管理

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件
