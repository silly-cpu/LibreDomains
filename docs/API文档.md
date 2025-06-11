# LibreDomains API 文档

本文档描述了 LibreDomains 系统提供的 API 接口。

## 基础信息

- **Base URL**: `https://your-domain.pages.dev/api`
- **数据格式**: JSON
- **字符编码**: UTF-8

## 公开 API

### 1. 获取可用域名

获取当前可申请的域名列表。

**请求**
```http
GET /api/domains
```

**响应**
```json
{
  "domains": [
    {
      "name": "ciao.su",
      "enabled": true,
      "description": "主要域名"
    }
  ],
  "settings": {
    "max_subdomains_per_user": 5,
    "allowed_record_types": ["A", "AAAA", "CNAME", "TXT"]
  }
}
```

### 2. 申请子域名

提交子域名申请。

**请求**
```http
POST /api/subdomains/apply
Content-Type: application/json

{
  "domain": "example.ciao.su",
  "type": "A",
  "content": "192.0.2.1",
  "ttl": 300,
  "proxied": false
}
```

**请求参数**

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| domain | string | ✅ | 完整的子域名 |
| type | string | ✅ | DNS 记录类型 (A/AAAA/CNAME/TXT) |
| content | string | ✅ | 记录内容 |
| ttl | number | ❌ | 生存时间，默认 300 秒 |
| proxied | boolean | ❌ | 是否启用 Cloudflare 代理，默认 false |

**成功响应**
```json
{
  "message": "申请提交成功，等待管理员审核",
  "domain": "example.ciao.su"
}
```

**错误响应**
```json
{
  "error": "域名已存在"
}
```

**可能的错误**

| HTTP 状态码 | 错误信息 | 说明 |
|-------------|----------|------|
| 400 | 缺少必要字段 | 请求参数不完整 |
| 400 | 域名必须以允许的后缀结尾 | 域名格式不正确 |
| 400 | 不支持的记录类型 | 记录类型不在允许列表中 |
| 400 | 域名已存在 | 该子域名已被申请 |
| 500 | 申请处理失败 | 服务器内部错误 |

## 管理员 API

所有管理员 API 都需要认证，请在请求头中包含认证令牌：

```http
Authorization: Bearer your_admin_token
```

### 1. 管理员登录

获取管理员访问令牌。

**请求**
```http
POST /api/admin/login
Content-Type: application/json

{
  "password": "admin_password"
}
```

**成功响应**
```json
{
  "token": "64_character_hex_token",
  "message": "Login successful"
}
```

**错误响应**
```json
{
  "error": "Invalid password"
}
```

### 2. 域名管理

#### 获取所有域名配置

**请求**
```http
GET /api/admin/domains
Authorization: Bearer your_admin_token
```

**响应**
```json
{
  "domains": [
    {
      "name": "ciao.su",
      "enabled": true,
      "description": "主要域名",
      "cloudflare_zone_id": "zone_id_here"
    }
  ],
  "admin": {
    "email": "admin@example.com",
    "github_username": "admin"
  },
  "settings": {
    "auto_approve": false,
    "max_subdomains_per_user": 5,
    "allowed_record_types": ["A", "AAAA", "CNAME", "TXT"]
  }
}
```

#### 添加新域名

**请求**
```http
POST /api/admin/domains
Authorization: Bearer your_admin_token
Content-Type: application/json

{
  "name": "example.com",
  "description": "新域名",
  "cloudflare_zone_id": "zone_id_here",
  "enabled": true
}
```

**成功响应**
```json
{
  "message": "Domain added successfully"
}
```

#### 更新域名配置

**请求**
```http
PUT /api/admin/domains
Authorization: Bearer your_admin_token
Content-Type: application/json

{
  "index": 0,
  "updates": {
    "enabled": false
  }
}
```

**请求参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| index | number | 域名在配置数组中的索引 |
| updates | object | 要更新的字段 |

**成功响应**
```json
{
  "message": "Domain updated successfully"
}
```

### 3. 子域名管理

#### 获取所有子域名

**请求**
```http
GET /api/admin/subdomains
Authorization: Bearer your_admin_token
```

**响应**
```json
{
  "subdomains": [
    {
      "domain": "example.ciao.su",
      "type": "A",
      "content": "192.0.2.1",
      "ttl": 300,
      "proxied": false,
      "approved": false,
      "created_at": "2025-01-01T00:00:00.000Z",
      "ip": "192.0.2.100"
    }
  ]
}
```

#### 删除子域名

**请求**
```http
DELETE /api/admin/subdomains
Authorization: Bearer your_admin_token
Content-Type: application/json

{
  "subdomain": "example.ciao.su"
}
```

**成功响应**
```json
{
  "message": "Subdomain deleted successfully"
}
```

### 4. 审核申请

审核通过子域名申请并自动创建 DNS 记录。

**请求**
```http
POST /api/admin/approve
Authorization: Bearer your_admin_token
Content-Type: application/json

{
  "subdomain": "example.ciao.su"
}
```

**成功响应**
```json
{
  "message": "Subdomain approved successfully"
}
```

**错误响应**
```json
{
  "error": "Approval successful but DNS update failed"
}
```

## 数据模型

### 域名配置 (Domain)
```json
{
  "name": "string",                    // 域名
  "enabled": "boolean",                // 是否启用
  "description": "string",             // 描述
  "cloudflare_zone_id": "string"       // Cloudflare Zone ID
}
```

### 子域名记录 (Subdomain)
```json
{
  "domain": "string",                  // 完整子域名
  "type": "string",                    // 记录类型 (A/AAAA/CNAME/TXT)
  "content": "string",                 // 记录内容
  "ttl": "number",                     // 生存时间 (秒)
  "proxied": "boolean",                // 是否启用 Cloudflare 代理
  "approved": "boolean",               // 是否已审核
  "created_at": "string",              // 创建时间 (ISO 8601)
  "approved_at": "string",             // 审核时间 (ISO 8601，可选)
  "ip": "string",                      // 申请者 IP 地址
  "description": "string"              // 描述 (可选)
}
```

### 系统设置 (Settings)
```json
{
  "auto_approve": "boolean",           // 是否自动审核
  "max_subdomains_per_user": "number", // 每用户最大子域名数
  "allowed_record_types": "string[]"   // 允许的记录类型
}
```

## 错误处理

所有 API 错误都遵循统一格式：

```json
{
  "error": "错误描述信息"
}
```

### 常见 HTTP 状态码

| 状态码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 400 | 请求参数错误 |
| 401 | 认证失败或令牌无效 |
| 404 | 资源不存在 |
| 405 | 请求方法不允许 |
| 500 | 服务器内部错误 |

## 使用示例

### JavaScript/Node.js

```javascript
// 申请子域名
async function applySubdomain(data) {
  const response = await fetch('https://your-domain.pages.dev/api/subdomains/apply', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
  });
  
  const result = await response.json();
  
  if (response.ok) {
    console.log('申请成功:', result.message);
  } else {
    console.error('申请失败:', result.error);
  }
}

// 使用示例
applySubdomain({
  domain: 'mysite.ciao.su',
  type: 'A',
  content: '192.0.2.1',
  ttl: 300,
  proxied: false
});
```

### Python

```python
import requests
import json

def apply_subdomain(data):
    url = 'https://your-domain.pages.dev/api/subdomains/apply'
    headers = {'Content-Type': 'application/json'}
    
    response = requests.post(url, headers=headers, data=json.dumps(data))
    
    if response.status_code == 200:
        print('申请成功:', response.json()['message'])
    else:
        print('申请失败:', response.json()['error'])

# 使用示例
apply_subdomain({
    'domain': 'mysite.ciao.su',
    'type': 'A',
    'content': '192.0.2.1',
    'ttl': 300,
    'proxied': False
})
```

### cURL

```bash
# 申请子域名
curl -X POST https://your-domain.pages.dev/api/subdomains/apply \
  -H "Content-Type: application/json" \
  -d '{
    "domain": "mysite.ciao.su",
    "type": "A",
    "content": "192.0.2.1",
    "ttl": 300,
    "proxied": false
  }'

# 管理员登录
curl -X POST https://your-domain.pages.dev/api/admin/login \
  -H "Content-Type: application/json" \
  -d '{"password": "your_admin_password"}'

# 获取子域名列表 (需要管理员令牌)
curl https://your-domain.pages.dev/api/admin/subdomains \
  -H "Authorization: Bearer your_admin_token"
```

## 速率限制

为了防止滥用，API 实施以下限制：

- **申请接口**: 每 IP 每小时最多 10 次申请
- **管理员接口**: 每令牌每分钟最多 60 次请求
- **公开接口**: 每 IP 每分钟最多 100 次请求

超出限制时会返回 `429 Too Many Requests` 状态码。

## 安全考虑

1. **管理员令牌**：令牌在服务器重启后会失效，请妥善保管
2. **HTTPS**：所有 API 调用都应通过 HTTPS 进行
3. **输入验证**：所有用户输入都会经过严格验证
4. **权限检查**：管理员操作需要有效的认证令牌

## 更新计划

未来版本可能包含的功能：

- JWT 认证替代简单令牌
- 用户注册和登录系统
- Webhook 通知功能
- 批量操作接口
- 详细的使用统计 API

---

如有疑问，请参考 [用户使用文档](./用户使用文档.md) 或提交 [GitHub Issue](https://github.com/yourusername/LibreDomains-beta/issues)。
