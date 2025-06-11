import fs from 'fs';
import path from 'path';

export default function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { domain, type, content, ttl, proxied } = req.body;

  // 验证输入
  if (!domain || !type || !content) {
    return res.status(400).json({ error: '缺少必要参数' });
  }

  // 验证域名格式
  const domainRegex = /^[a-zA-Z0-9-]+\.[a-zA-Z0-9.-]+$/;
  if (!domainRegex.test(domain)) {
    return res.status(400).json({ error: '域名格式不正确' });
  }

  try {
    // 检查子域名是否已存在
    const subdomainsDir = path.join(process.cwd(), 'subdomains');
    const filename = `${domain.replace(/\./g, '_')}.json`;
    const filePath = path.join(subdomainsDir, filename);

    if (fs.existsSync(filePath)) {
      return res.status(400).json({ error: '子域名已存在' });
    }

    // 创建子域名记录
    const subdomainData = {
      domain,
      type,
      content,
      ttl: ttl || 300,
      proxied: proxied || false,
      approved: false,
      created_at: new Date().toISOString(),
      description: `${type} 记录指向 ${content}`
    };

    // 确保目录存在
    if (!fs.existsSync(subdomainsDir)) {
      fs.mkdirSync(subdomainsDir, { recursive: true });
    }

    // 写入文件
    fs.writeFileSync(filePath, JSON.stringify(subdomainData, null, 2));

    res.status(200).json({ 
      success: true, 
      message: '子域名申请提交成功，等待审核' 
    });

  } catch (error) {
    console.error('申请处理失败:', error);
    res.status(500).json({ error: '申请处理失败' });
  }
}
