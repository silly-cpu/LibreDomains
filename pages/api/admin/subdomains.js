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

  const subdomainsDir = path.join(process.cwd(), 'subdomains');

  try {
    if (req.method === 'GET') {
      const subdomains = [];
      
      if (fs.existsSync(subdomainsDir)) {
        const files = fs.readdirSync(subdomainsDir);
        
        for (const file of files) {
          if (file.endsWith('.json') && file !== 'template.json') {
            const filePath = path.join(subdomainsDir, file);
            const data = JSON.parse(fs.readFileSync(filePath, 'utf8'));
            subdomains.push(data);
          }
        }
      }
      
      res.status(200).json({ subdomains });
      
    } else if (req.method === 'DELETE') {
      const { subdomain } = req.body;
      const filename = `${subdomain.replace(/\./g, '_')}.json`;
      const filePath = path.join(subdomainsDir, filename);
      
      if (fs.existsSync(filePath)) {
        fs.unlinkSync(filePath);
        res.status(200).json({ success: true });
      } else {
        res.status(404).json({ error: '子域名不存在' });
      }
      
    } else {
      res.status(405).json({ error: 'Method not allowed' });
    }
  } catch (error) {
    res.status(500).json({ error: '操作失败' });
  }
}
