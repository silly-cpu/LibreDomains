import crypto from 'crypto';

export default function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { password } = req.body;
  const adminPassword = process.env.ADMIN_PASSWORD || 'admin123';

  if (password === adminPassword) {
    // 生成简单的token
    const token = crypto.randomBytes(32).toString('hex');
    res.status(200).json({ token });
  } else {
    res.status(401).json({ error: '密码错误' });
  }
}
