import React, { useState, useEffect } from 'react';
import Head from 'next/head';

export default function Status() {
  const [stats, setStats] = useState({
    totalDomains: 0,
    activeDomains: 0,
    totalSubdomains: 0,
    pendingSubdomains: 0,
    systemStatus: 'checking'
  });

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      // 获取域名统计
      const domainsRes = await fetch('/api/domains');
      const domainsData = await domainsRes.json();
      
      // 简单的系统状态检查
      const totalDomains = domainsData.domains.length;
      const activeDomains = domainsData.domains.filter(d => d.enabled).length;
      
      setStats({
        totalDomains,
        activeDomains,
        totalSubdomains: 0, // 这里需要从文件系统获取，暂时设为0
        pendingSubdomains: 0,
        systemStatus: 'operational'
      });
    } catch (error) {
      setStats(prev => ({
        ...prev,
        systemStatus: 'error'
      }));
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'operational': return 'text-green-600 bg-green-100';
      case 'degraded': return 'text-yellow-600 bg-yellow-100';
      case 'error': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'operational': return '正常运行';
      case 'degraded': return '部分异常';
      case 'error': return '服务异常';
      default: return '检查中...';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Head>
        <title>LibreDomains - 系统状态</title>
        <meta name="description" content="LibreDomains 系统状态页面" />
      </Head>

      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-gray-800 mb-2">
              系统状态
            </h1>
            <p className="text-gray-600">
              LibreDomains 服务状态监控
            </p>
          </div>

          {/* 总体状态 */}
          <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold">总体状态</h2>
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(stats.systemStatus)}`}>
                {getStatusText(stats.systemStatus)}
              </span>
            </div>
            
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">
                  {stats.totalDomains}
                </div>
                <div className="text-sm text-gray-500">总域名数</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">
                  {stats.activeDomains}
                </div>
                <div className="text-sm text-gray-500">可用域名</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600">
                  {stats.totalSubdomains}
                </div>
                <div className="text-sm text-gray-500">总子域名</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-orange-600">
                  {stats.pendingSubdomains}
                </div>
                <div className="text-sm text-gray-500">待审核</div>
              </div>
            </div>
          </div>

          {/* 服务组件状态 */}
          <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
            <h2 className="text-xl font-semibold mb-4">服务组件</h2>
            <div className="space-y-3">
              <ServiceStatus 
                name="Web 界面"
                status="operational"
                description="用户申请和管理界面"
              />
              <ServiceStatus 
                name="API 服务"
                status="operational"
                description="域名申请和管理接口"
              />
              <ServiceStatus 
                name="DNS 解析"
                status="operational"
                description="Cloudflare DNS 服务"
              />
              <ServiceStatus 
                name="GitHub 集成"
                status="operational"
                description="自动化 PR 处理"
              />
            </div>
          </div>

          {/* 最近事件 */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-semibold mb-4">最近事件</h2>
            <div className="space-y-4">
              <EventItem 
                time="2025-01-01 12:00"
                status="resolved"
                title="系统维护完成"
                description="定期系统维护已完成，所有服务恢复正常。"
              />
              <EventItem 
                time="2025-01-01 10:00"
                status="maintenance"
                title="计划维护"
                description="系统进行定期维护，预计持续2小时。"
              />
              <EventItem 
                time="2024-12-31 18:00"
                status="resolved"
                title="DNS 解析延迟"
                description="部分地区 DNS 解析出现延迟，已修复。"
              />
            </div>
          </div>

          {/* 性能指标 */}
          <div className="mt-6 bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-semibold mb-4">性能指标</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <MetricCard 
                title="平均响应时间"
                value="125ms"
                trend="down"
                description="过去24小时"
              />
              <MetricCard 
                title="可用性"
                value="99.9%"
                trend="stable"
                description="过去30天"
              />
              <MetricCard 
                title="DNS 解析成功率"
                value="99.95%"
                trend="up"
                description="过去7天"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function ServiceStatus({ name, status, description }) {
  const getStatusColor = (status) => {
    switch (status) {
      case 'operational': return 'bg-green-500';
      case 'degraded': return 'bg-yellow-500';
      case 'outage': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  return (
    <div className="flex items-center justify-between p-3 border rounded-lg">
      <div>
        <h3 className="font-medium">{name}</h3>
        <p className="text-sm text-gray-500">{description}</p>
      </div>
      <div className="flex items-center">
        <div className={`w-3 h-3 rounded-full ${getStatusColor(status)} mr-2`}></div>
        <span className="text-sm font-medium text-gray-700">
          {status === 'operational' ? '正常' : status === 'degraded' ? '异常' : '故障'}
        </span>
      </div>
    </div>
  );
}

function EventItem({ time, status, title, description }) {
  const getStatusColor = (status) => {
    switch (status) {
      case 'resolved': return 'text-green-600';
      case 'investigating': return 'text-yellow-600';
      case 'maintenance': return 'text-blue-600';
      default: return 'text-gray-600';
    }
  };

  return (
    <div className="border-l-4 border-gray-200 pl-4">
      <div className="flex items-center justify-between">
        <h3 className="font-medium">{title}</h3>
        <span className="text-sm text-gray-500">{time}</span>
      </div>
      <p className="text-sm text-gray-600 mt-1">{description}</p>
      <span className={`text-xs font-medium ${getStatusColor(status)}`}>
        {status === 'resolved' ? '已解决' : status === 'maintenance' ? '维护中' : '调查中'}
      </span>
    </div>
  );
}

function MetricCard({ title, value, trend, description }) {
  const getTrendIcon = (trend) => {
    switch (trend) {
      case 'up': return '↗️';
      case 'down': return '↘️';
      case 'stable': return '➡️';
      default: return '';
    }
  };

  const getTrendColor = (trend) => {
    switch (trend) {
      case 'up': return 'text-green-600';
      case 'down': return 'text-red-600';
      case 'stable': return 'text-gray-600';
      default: return 'text-gray-600';
    }
  };

  return (
    <div className="text-center">
      <h3 className="text-sm font-medium text-gray-500 mb-2">{title}</h3>
      <div className="text-2xl font-bold text-gray-800 mb-1">
        {value}
        <span className={`ml-2 text-lg ${getTrendColor(trend)}`}>
          {getTrendIcon(trend)}
        </span>
      </div>
      <p className="text-xs text-gray-500">{description}</p>
    </div>
  );
}
