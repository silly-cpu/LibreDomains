import fs from 'fs';
import path from 'path';

function verifyAdmin(req) {
  const token = req.headers.authorization?.replace('Bearer ', '');
  return !!token; // 简单验证，生产环境需要更严格的验证
}

export default function handler(req, res) {
  if (!verifyAdmin(req)) {
    return res.status(401).json({ error: '未授权' });
  }

  const domainsPath = path.join(process.cwd(), 'config', 'domains.json');

  try {
    if (req.method === 'GET') {
      const domainsData = JSON.parse(fs.readFileSync(domainsPath, 'utf8'));
      res.status(200).json(domainsData);
      
    } else if (req.method === 'POST') {
      const { name, description, cloudflare_zone_id, enabled } = req.body;
      const domainsData = JSON.parse(fs.readFileSync(domainsPath, 'utf8'));
      
      domainsData.domains.push({
        name,
        description,
        cloudflare_zone_id,
        enabled: enabled !== false
      });
      
      fs.writeFileSync(domainsPath, JSON.stringify(domainsData, null, 2));
      res.status(200).json({ success: true });
      
    } else if (req.method === 'PUT') {
      const { index, updates } = req.body;
      const domainsData = JSON.parse(fs.readFileSync(domainsPath, 'utf8'));
      
      if (domainsData.domains[index]) {
        Object.assign(domainsData.domains[index], updates);
        fs.writeFileSync(domainsPath, JSON.stringify(domainsData, null, 2));
        res.status(200).json({ success: true });
      } else {
        res.status(404).json({ error: '域名不存在' });
      }
      
    } else {
      res.status(405).json({ error: 'Method not allowed' });
    }
  } catch (error) {
    res.status(500).json({ error: '操作失败' });
  }
}
