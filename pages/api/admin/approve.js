import fs from 'fs';
import path from 'path';

function verifyAdmin(req) {
  const token = req.headers.authorization?.replace('Bearer ', '');
  return !!token;
}

export default function handler(req, res) {
  if (!verifyAdmin(req)) {
    return res.status(401).json({ error: '未授权' });
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { subdomain } = req.body;
  const filename = `${subdomain.replace(/\./g, '_')}.json`;
  const filePath = path.join(process.cwd(), 'subdomains', filename);

  try {
    if (fs.existsSync(filePath)) {
      const data = JSON.parse(fs.readFileSync(filePath, 'utf8'));
      data.approved = true;
      data.approved_at = new Date().toISOString();
      
      fs.writeFileSync(filePath, JSON.stringify(data, null, 2));
      
      // TODO: 这里可以添加实际的 DNS 记录创建逻辑
      // await createDNSRecord(data);
      
      res.status(200).json({ success: true });
    } else {
      res.status(404).json({ error: '子域名不存在' });
    }
  } catch (error) {
    res.status(500).json({ error: '审核失败' });
  }
}
