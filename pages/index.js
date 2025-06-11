import React, { useState, useEffect } from 'react';
import Head from 'next/head';

export default function Home() {
  const [domains, setDomains] = useState([]);
  const [selectedDomain, setSelectedDomain] = useState('');
  const [subdomain, setSubdomain] = useState('');
  const [recordType, setRecordType] = useState('A');
  const [content, setContent] = useState('');
  const [ttl, setTtl] = useState(300);
  const [proxied, setProxied] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    // 加载可用域名
    fetch('/api/domains')
      .then(res => res.json())
      .then(data => {
        const enabledDomains = data.domains.filter(d => d.enabled);
        setDomains(enabledDomains);
        if (enabledDomains.length > 0) {
          setSelectedDomain(enabledDomains[0].name);
        }
      })
      .catch(err => console.error('加载域名失败:', err));
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setMessage('');

    const fullDomain = `${subdomain}.${selectedDomain}`;
    
    const data = {
      domain: fullDomain,
      type: recordType,
      content,
      ttl,
      proxied
    };

    try {
      const response = await fetch('/api/subdomains/apply', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });

      const result = await response.json();
      
      if (response.ok) {
        setMessage('申请提交成功！请等待管理员审核。');
        // 重置表单
        setSubdomain('');
        setContent('');
      } else {
        setMessage(`申请失败: ${result.error}`);
      }
    } catch (error) {
      setMessage(`申请失败: ${error.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <Head>
        <title>LibreDomains - 免费二级域名申请</title>
        <meta name="description" content="免费申请二级域名服务" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <div className="container mx-auto px-4 py-8">
        <div className="max-w-2xl mx-auto">
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold text-gray-800 mb-4">
              LibreDomains
            </h1>
            <p className="text-lg text-gray-600">
              免费二级域名申请服务
            </p>
          </div>

          <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
            <h2 className="text-2xl font-semibold mb-6">申请二级域名</h2>
            
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="form-label">子域名</label>
                <div className="flex">
                  <input
                    type="text"
                    value={subdomain}
                    onChange={(e) => setSubdomain(e.target.value)}
                    className="form-input rounded-r-none"
                    placeholder="example"
                    required
                    pattern="^[a-zA-Z0-9-]+$"
                    title="只允许字母、数字和连字符"
                  />
                  <select
                    value={selectedDomain}
                    onChange={(e) => setSelectedDomain(e.target.value)}
                    className="border border-l-0 rounded-r px-3 py-2 bg-gray-50"
                  >
                    {domains.map(domain => (
                      <option key={domain.name} value={domain.name}>
                        .{domain.name}
                      </option>
                    ))}
                  </select>
                </div>
                <p className="text-sm text-gray-500 mt-1">
                  完整域名: {subdomain}.{selectedDomain}
                </p>
              </div>

              <div>
                <label className="form-label">记录类型</label>
                <select
                  value={recordType}
                  onChange={(e) => setRecordType(e.target.value)}
                  className="form-input"
                >
                  <option value="A">A (IPv4 地址)</option>
                  <option value="AAAA">AAAA (IPv6 地址)</option>
                  <option value="CNAME">CNAME (域名别名)</option>
                  <option value="TXT">TXT (文本记录)</option>
                </select>
              </div>

              <div>
                <label className="form-label">记录内容</label>
                <input
                  type="text"
                  value={content}
                  onChange={(e) => setContent(e.target.value)}
                  className="form-input"
                  placeholder={
                    recordType === 'A' ? '192.0.2.1' :
                    recordType === 'AAAA' ? '2001:db8::1' :
                    recordType === 'CNAME' ? 'example.com' :
                    'v=spf1 include:_spf.example.com ~all'
                  }
                  required
                />
                <p className="text-sm text-gray-500 mt-1">
                  {recordType === 'A' && 'IPv4 地址格式'}
                  {recordType === 'AAAA' && 'IPv6 地址格式'}
                  {recordType === 'CNAME' && '目标域名'}
                  {recordType === 'TXT' && '文本内容'}
                </p>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="form-label">TTL (秒)</label>
                  <select
                    value={ttl}
                    onChange={(e) => setTtl(Number(e.target.value))}
                    className="form-input"
                  >
                    <option value={120}>120 (2分钟)</option>
                    <option value={300}>300 (5分钟)</option>
                    <option value={600}>600 (10分钟)</option>
                    <option value={3600}>3600 (1小时)</option>
                  </select>
                </div>

                <div className="flex items-center mt-6">
                  <input
                    type="checkbox"
                    id="proxied"
                    checked={proxied}
                    onChange={(e) => setProxied(e.target.checked)}
                    className="mr-2"
                  />
                  <label htmlFor="proxied" className="text-sm text-gray-700">
                    启用 Cloudflare 代理
                  </label>
                </div>
              </div>

              <div className="pt-4">
                <button
                  type="submit"
                  disabled={isLoading || !subdomain || !content}
                  className="btn-primary w-full disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isLoading ? '提交中...' : '提交申请'}
                </button>
              </div>
            </form>

            {message && (
              <div className={`mt-4 p-4 rounded ${
                message.includes('成功') 
                  ? 'bg-green-100 text-green-700' 
                  : 'bg-red-100 text-red-700'
              }`}>
                {message}
              </div>
            )}
          </div>

          <div className="bg-white rounded-lg shadow-lg p-6">
            <h3 className="text-lg font-semibold mb-4">使用说明</h3>
            <ul className="list-disc list-inside space-y-2 text-gray-700">
              <li>子域名只能包含字母、数字和连字符</li>
              <li>申请提交后需要等待管理员审核</li>
              <li>审核通过后 DNS 记录将自动生效</li>
              <li>每个用户最多可申请 5 个子域名</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
