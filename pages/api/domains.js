import fs from 'fs';
import path from 'path';

export default function handler(req, res) {
  const domainsPath = path.join(process.cwd(), 'config', 'domains.json');
  
  try {
    const domainsData = JSON.parse(fs.readFileSync(domainsPath, 'utf8'));
    
    if (req.method === 'GET') {
      res.status(200).json(domainsData);
    } else {
      res.status(405).json({ error: 'Method not allowed' });
    }
  } catch (error) {
    res.status(500).json({ error: '读取域名配置失败' });
  }
}
