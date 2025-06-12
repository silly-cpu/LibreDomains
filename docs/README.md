# LibreDomains 二级域名分发项目

## 项目简介

LibreDomains 是一个基于 GitHub 仓库管理的二级域名分发系统，用户可以通过提交 Pull Request 的方式申请子域名，不需要自己部署 DNS 服务，全程在 GitHub 上通过 bot 自动化校验和 Cloudflare API 完成 DNS 解析。

## 主要功能

- 管理员在 `config/domains.json` 中配置可用域名及其是否开放申请。
- 用户通过修改 `domains/<domain>.json` 提交子域名申请，JSON 文件遵循 `config/schema.json` 规范。
- Bot 自动校验 PR 标题、文件修改范围、JSON 格式及子域名可用性。
- 管理员或自动化脚本合并 PR 后，Bot 通过 Cloudflare API 创建对应的 DNS 解析记录。

## 目录结构

```
config/              配置文件
  domains.json       可申请域名列表及状态
  schema.json        子域名申请的 JSON Schema

domains/             各域名申请记录
  ciao.su.json       已申请子域名列表
  ciallo.de.json     已申请子域名列表

bot.py               GitHub Bot 主脚本
requirements.txt     Python 依赖
scripts/             可选辅助脚本
tools/               工具代码（如部署脚本）
```
