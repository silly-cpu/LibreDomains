import React, { useState, useEffect } from 'react';
import Head from 'next/head';

export default function AdminPanel() {
  const [domains, setDomains] = useState([]);
  const [subdomains, setSubdomains] = useState([]);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [password, setPassword] = useState('');
  const [activeTab, setActiveTab] = useState('domains');
  const [message, setMessage] = useState('');
  const [newDomain, setNewDomain] = useState({
    name: '',
    description: '',
    cloudflare_zone_id: '',
    enabled: true
  });

  useEffect(() => {
    // 检查认证状态
    const token = localStorage.getItem('admin_token');
    if (token) {
      setIsAuthenticated(true);
      loadData();
    }
  }, []);

  const login = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch('/api/admin/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ password })
      });

      if (response.ok) {
        const { token } = await response.json();
        localStorage.setItem('admin_token', token);
        setIsAuthenticated(true);
        loadData();
        setMessage('登录成功');
      } else {
        setMessage('密码错误');
      }
    } catch (error) {
      setMessage('登录失败');
    }
  };

  const loadData = async () => {
    try {
      const [domainsRes, subdomainsRes] = await Promise.all([
        fetch('/api/admin/domains', {
          headers: { 'Authorization': `Bearer ${localStorage.getItem('admin_token')}` }
        }),
        fetch('/api/admin/subdomains', {
          headers: { 'Authorization': `Bearer ${localStorage.getItem('admin_token')}` }
        })
      ]);

      if (domainsRes.ok && subdomainsRes.ok) {
        const domainsData = await domainsRes.json();
        const subdomainsData = await subdomainsRes.json();
        setDomains(domainsData.domains);
        setSubdomains(subdomainsData.subdomains);
      }
    } catch (error) {
      console.error('加载数据失败:', error);
    }
  };

  const updateDomain = async (index, updates) => {
    try {
      const response = await fetch('/api/admin/domains', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('admin_token')}`
        },
        body: JSON.stringify({ index, updates })
      });

      if (response.ok) {
        loadData();
        setMessage('域名配置更新成功');
      } else {
        setMessage('更新失败');
      }
    } catch (error) {
      setMessage('更新失败');
    }
  };

  const addDomain = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch('/api/admin/domains', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('admin_token')}`
        },
        body: JSON.stringify(newDomain)
      });

      if (response.ok) {
        loadData();
        setNewDomain({ name: '', description: '', cloudflare_zone_id: '', enabled: true });
        setMessage('域名添加成功');
      } else {
        setMessage('添加失败');
      }
    } catch (error) {
      setMessage('添加失败');
    }
  };

  const approveSubdomain = async (subdomain) => {
    try {
      const response = await fetch('/api/admin/approve', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('admin_token')}`
        },
        body: JSON.stringify({ subdomain })
      });

      if (response.ok) {
        loadData();
        setMessage('子域名审核通过');
      } else {
        setMessage('审核失败');
      }
    } catch (error) {
      setMessage('审核失败');
    }
  };

  const deleteSubdomain = async (subdomain) => {
    if (!confirm(`确定要删除子域名 ${subdomain} 吗？`)) return;

    try {
      const response = await fetch('/api/admin/subdomains', {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('admin_token')}`
        },
        body: JSON.stringify({ subdomain })
      });

      if (response.ok) {
        loadData();
        setMessage('子域名删除成功');
      } else {
        setMessage('删除失败');
      }
    } catch (error) {
      setMessage('删除失败');
    }
  };

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="bg-white p-8 rounded-lg shadow-lg max-w-md w-full">
          <h1 className="text-2xl font-bold mb-6 text-center">管理员登录</h1>
          <form onSubmit={login}>
            <div className="mb-4">
              <label className="form-label">管理员密码</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="form-input"
                required
              />
            </div>
            <button type="submit" className="btn-primary w-full">
              登录
            </button>
          </form>
          {message && (
            <div className="mt-4 p-3 bg-red-100 text-red-700 rounded">
              {message}
            </div>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <Head>
        <title>LibreDomains - 管理员面板</title>
      </Head>

      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-800">管理员面板</h1>
          <p className="text-gray-600">管理域名和子域名申请</p>
        </div>

        {message && (
          <div className={`mb-4 p-4 rounded ${
            message.includes('成功') 
              ? 'bg-green-100 text-green-700' 
              : 'bg-red-100 text-red-700'
          }`}>
            {message}
          </div>
        )}

        <div className="mb-6">
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8">
              <button
                onClick={() => setActiveTab('domains')}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'domains'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                域名管理
              </button>
              <button
                onClick={() => setActiveTab('subdomains')}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'subdomains'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                子域名管理
              </button>
            </nav>
          </div>
        </div>

        {activeTab === 'domains' && (
          <div className="space-y-6">
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-semibold mb-4">添加新域名</h2>
              <form onSubmit={addDomain} className="grid grid-cols-2 gap-4">
                <div>
                  <label className="form-label">域名</label>
                  <input
                    type="text"
                    value={newDomain.name}
                    onChange={(e) => setNewDomain({...newDomain, name: e.target.value})}
                    className="form-input"
                    placeholder="example.com"
                    required
                  />
                </div>
                <div>
                  <label className="form-label">描述</label>
                  <input
                    type="text"
                    value={newDomain.description}
                    onChange={(e) => setNewDomain({...newDomain, description: e.target.value})}
                    className="form-input"
                    placeholder="主要域名"
                  />
                </div>
                <div>
                  <label className="form-label">Cloudflare Zone ID</label>
                  <input
                    type="text"
                    value={newDomain.cloudflare_zone_id}
                    onChange={(e) => setNewDomain({...newDomain, cloudflare_zone_id: e.target.value})}
                    className="form-input"
                    placeholder="zone_id_here"
                    required
                  />
                </div>
                <div className="flex items-center mt-6">
                  <input
                    type="checkbox"
                    id="enabled"
                    checked={newDomain.enabled}
                    onChange={(e) => setNewDomain({...newDomain, enabled: e.target.checked})}
                    className="mr-2"
                  />
                  <label htmlFor="enabled" className="text-sm text-gray-700">
                    启用域名
                  </label>
                </div>
                <div className="col-span-2">
                  <button type="submit" className="btn-primary">
                    添加域名
                  </button>
                </div>
              </form>
            </div>

            <div className="bg-white rounded-lg shadow">
              <h2 className="text-xl font-semibold p-6 border-b">现有域名</h2>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        域名
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        描述
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        状态
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        操作
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {domains.map((domain, index) => (
                      <tr key={domain.name}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {domain.name}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {domain.description}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                            domain.enabled 
                              ? 'bg-green-100 text-green-800' 
                              : 'bg-red-100 text-red-800'
                          }`}>
                            {domain.enabled ? '启用' : '禁用'}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                          <button
                            onClick={() => updateDomain(index, { enabled: !domain.enabled })}
                            className={`${
                              domain.enabled ? 'text-red-600 hover:text-red-900' : 'text-green-600 hover:text-green-900'
                            }`}
                          >
                            {domain.enabled ? '禁用' : '启用'}
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'subdomains' && (
          <div className="bg-white rounded-lg shadow">
            <h2 className="text-xl font-semibold p-6 border-b">子域名管理</h2>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      域名
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      类型
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      内容
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      状态
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      操作
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {subdomains.map((subdomain, index) => (
                    <tr key={subdomain.domain}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {subdomain.domain}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {subdomain.type}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {subdomain.content}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                          subdomain.approved 
                            ? 'bg-green-100 text-green-800' 
                            : 'bg-yellow-100 text-yellow-800'
                        }`}>
                          {subdomain.approved ? '已审核' : '待审核'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                        {!subdomain.approved && (
                          <button
                            onClick={() => approveSubdomain(subdomain.domain)}
                            className="text-green-600 hover:text-green-900"
                          >
                            审核通过
                          </button>
                        )}
                        <button
                          onClick={() => deleteSubdomain(subdomain.domain)}
                          className="text-red-600 hover:text-red-900"
                        >
                          删除
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
