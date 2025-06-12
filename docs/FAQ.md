# 常见问题解答 (FAQ)

## 🤔 一般问题

### 什么是 LibreDomains？
LibreDomains 是一个基于 GitHub 和 Cloudflare 的免费二级域名分发服务。用户可以通过提交 Pull Request 的方式申请免费的子域名。

### 服务是否真的免费？
是的，我们的服务完全免费。但请注意：
- 我们保留在必要时终止服务的权利
- 滥用服务可能导致账户被封禁
- 服务的可用性不提供任何保证

### 支持哪些域名？
目前支持的域名：
- `ciao.su` ✅ 开放申请
- `ciallo.de` ❌ 即将开放

更多域名正在计划中。

## 📝 申请相关

### 如何申请子域名？
1. Fork 这个仓库
2. 在 `requests/` 目录创建 JSON 请求文件
3. 提交 Pull Request
4. 等待自动验证和管理员审核

详细步骤请查看 [用户指南](./USER_GUIDE.md)。

### 申请需要多长时间？
- **自动验证**: 几分钟内完成
- **管理员审核**: 通常 1-3 个工作日
- **DNS 生效**: 24-48 小时全球传播

### 我可以申请多少个子域名？
每个用户最多可以申请 **3 个子域名**。

### GitHub 账户有什么要求？
- 账户年龄至少 **30 天**
- 必须有已验证的邮箱地址
- 不能在黑名单中

## 🔧 技术问题

### 支持哪些 DNS 记录类型？
- **A**: IPv4 地址
- **AAAA**: IPv6 地址
- **CNAME**: 别名记录
- **MX**: 邮件交换记录
- **TXT**: 文本记录
- **SRV**: 服务记录

### 什么是 Cloudflare 代理？
Cloudflare 代理（`proxied: true`）提供：
- DDoS 保护
- CDN 加速
- SSL/TLS 加密
- 安全防护

建议对 Web 服务启用代理。

### TTL 设置建议
- **300-600 秒**: 测试环境或频繁变更
- **3600 秒**: 默认值，适合大多数情况
- **7200-86400 秒**: 稳定生产环境

### 为什么我的 DNS 没有生效？
可能的原因：
1. **DNS 传播延迟**: 全球传播需要 24-48 小时
2. **本地 DNS 缓存**: 尝试清除 DNS 缓存
3. **记录配置错误**: 检查记录类型和值
4. **目标服务器问题**: 确认目标地址可访问

## 🚨 问题排查

### 如何清除 DNS 缓存？

**Windows**:
```powershell
ipconfig /flushdns
```

**macOS**:
```bash
sudo dscacheutil -flushcache
sudo killall -HUP mDNSResponder
```

**Linux**:
```bash
sudo systemctl restart systemd-resolved
# 或
sudo service nscd restart
```

### 如何测试 DNS 解析？

**使用 nslookup**:
```bash
nslookup your-subdomain.ciao.su
```

**使用在线工具**:
- [DNS Checker](https://dnschecker.org/)
- [What's My DNS](https://www.whatsmydns.net/)

### 我的请求被拒绝了怎么办？
1. 检查错误信息中的具体原因
2. 修正问题后重新提交
3. 确保遵循所有规则和要求
4. 如有疑问，创建 Issue 寻求帮助

## 📋 规则和限制

### 内容政策
**允许的内容**:
- ✅ 个人网站和博客
- ✅ 开源项目
- ✅ 教育和学术内容
- ✅ 非营利组织
- ✅ 技术演示和原型

**禁止的内容**:
- ❌ 成人或色情内容
- ❌ 违法活动
- ❌ 垃圾邮件或钓鱼
- ❌ 版权侵犯
- ❌ 恶意软件或病毒
- ❌ 大规模商业用途

### 子域名命名规则
- 长度: 1-63 字符
- 字符: 字母、数字、连字符
- 不能以连字符开始或结束
- 不区分大小写
- 禁用某些保留名称（如 www, mail, api 等）

### 使用限制
- 每个用户最多 3 个子域名
- 不允许转售或商业化
- 不允许大量自动化请求
- 需要合理使用带宽和资源

## 🔄 管理您的域名

### 如何更新记录？
1. 修改您的原始请求文件
2. 更新需要更改的字段
3. 提交新的 Pull Request
4. 系统会自动更新 DNS 记录

### 如何删除子域名？
1. 删除 `requests/` 目录中的请求文件
2. 提交 Pull Request
3. DNS 记录会自动删除

### 可以转移给其他用户吗？
目前不支持域名转移。如果需要，请：
1. 原用户删除域名
2. 新用户重新申请

## 📞 获取帮助

### 报告问题
- **技术问题**: 创建 [Issue](../../issues)
- **滥用举报**: 发送邮件到管理员
- **功能建议**: 使用 [Discussions](../../discussions)

### 联系方式
- **GitHub Issues**: 技术支持和错误报告
- **Email**: [联系邮箱] - 紧急问题
- **Discord**: [服务器链接] - 社区交流

### 响应时间
- **自动验证**: 即时
- **Issue 回复**: 1-2 个工作日
- **紧急问题**: 24 小时内

## 📈 服务状态

### 如何查看服务状态？
- 查看 [GitHub Actions](../../actions) 的运行状态
- 检查最新的健康检查报告
- 关注仓库的公告

### 服务中断怎么办？
1. 检查 [GitHub Status](https://www.githubstatus.com/)
2. 查看 [Cloudflare Status](https://www.cloudflarestatus.com/)
3. 关注我们的状态更新

## 🔐 安全相关

### 数据隐私
- 我们只收集必要的信息（GitHub 用户名、邮箱）
- 不会出售或分享您的个人信息
- DNS 记录是公开的（这是 DNS 的特性）

### 安全建议
- 使用强密码保护您的 GitHub 账户
- 启用 GitHub 两步验证
- 定期检查您的子域名使用情况
- 及时报告可疑活动

## 📚 相关资源

### 学习资源
- [DNS 基础知识](https://www.cloudflare.com/learning/dns/what-is-dns/)
- [GitHub Pages 指南](https://pages.github.com/)
- [Cloudflare 文档](https://developers.cloudflare.com/)

### 类似服务
- [is-a.dev](https://www.is-a.dev/)
- [js.org](https://js.org/)
- [thedev.id](https://thedev.id/)

---

## 📊 统计信息

截至 2024 年 12 月：
- 总申请数: 500+
- 活跃用户: 200+
- 平均响应时间: 6 小时
- 用户满意度: 95%+

---

**还有其他问题？** 查看我们的 [用户指南](./USER_GUIDE.md) 或 [创建 Issue](../../issues/new) 获取帮助。
