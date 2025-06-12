#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
部署脚本测试
"""

import pytest
import json
import tempfile
import os
from unittest.mock import patch, MagicMock
import sys

# 添加脚本目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from deploy_dns import CloudflareAPI, DNSDeployer


class TestCloudflareAPI:
    """Cloudflare API 测试"""
    
    @pytest.fixture
    def api(self):
        """创建 API 实例"""
        return CloudflareAPI("test_token")
    
    @patch('requests.get')
    def test_get_zone_info_success(self, mock_get, api):
        """测试获取域名区域信息成功"""
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "result": {
                "id": "test_zone_id",
                "name": "example.com",
                "status": "active"
            }
        }
        mock_get.return_value = mock_response
        
        result = api.get_zone_info("test_zone_id")
        
        assert result is not None
        assert result["id"] == "test_zone_id"
        assert result["name"] == "example.com"
    
    @patch('requests.get')
    def test_get_zone_info_failure(self, mock_get, api):
        """测试获取域名区域信息失败"""
        mock_get.side_effect = Exception("API Error")
        
        result = api.get_zone_info("test_zone_id")
        
        assert result is None
    
    @patch('requests.get')
    def test_list_dns_records(self, mock_get, api):
        """测试列出 DNS 记录"""
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "result": [
                {
                    "id": "record_1",
                    "type": "A",
                    "name": "test.example.com",
                    "content": "192.168.1.1"
                }
            ]
        }
        mock_get.return_value = mock_response
        
        result = api.list_dns_records("test_zone_id", "test.example.com")
        
        assert len(result) == 1
        assert result[0]["type"] == "A"
        assert result[0]["content"] == "192.168.1.1"
    
    @patch('requests.post')
    def test_create_dns_record_success(self, mock_post, api):
        """测试创建 DNS 记录成功"""
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "result": {
                "id": "new_record_id",
                "type": "A",
                "name": "test.example.com"
            }
        }
        mock_post.return_value = mock_response
        
        record_data = {
            "type": "A",
            "name": "test.example.com",
            "content": "192.168.1.1",
            "ttl": 3600
        }
        
        result = api.create_dns_record("test_zone_id", record_data)
        
        assert result is not None
        assert result["id"] == "new_record_id"
    
    @patch('requests.put')
    def test_update_dns_record(self, mock_put, api):
        """测试更新 DNS 记录"""
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "result": {
                "id": "record_id",
                "type": "A",
                "content": "192.168.1.2"
            }
        }
        mock_put.return_value = mock_response
        
        record_data = {
            "type": "A",
            "content": "192.168.1.2"
        }
        
        result = api.update_dns_record("test_zone_id", "record_id", record_data)
        
        assert result is not None
        assert result["content"] == "192.168.1.2"
    
    @patch('requests.delete')
    def test_delete_dns_record(self, mock_delete, api):
        """测试删除 DNS 记录"""
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"success": True}
        mock_delete.return_value = mock_response
        
        result = api.delete_dns_record("test_zone_id", "record_id")
        
        assert result is True


class TestDNSDeployer:
    """DNS 部署器测试"""
    
    @pytest.fixture
    def deployer(self):
        """创建部署器实例"""
        with patch.object(DNSDeployer, 'load_config'), \
             patch.object(DNSDeployer, 'init_api'):
            
            deployer = DNSDeployer()
            
            # 模拟配置
            deployer.domains_config = {
                "domains": {
                    "ciao.su": {
                        "enabled": True,
                        "cloudflare_zone_id": "test_zone_id"
                    }
                }
            }
            
            # 模拟 API
            deployer.api = MagicMock()
            
            return deployer
    
    def test_deploy_request_success(self, deployer):
        """测试成功部署请求"""
        # 创建临时请求文件
        request_data = {
            "domain": "ciao.su",
            "subdomain": "test",
            "owner": {
                "username": "testuser",
                "email": "test@example.com"
            },
            "record": {
                "type": "A",
                "value": "192.168.1.1",
                "ttl": 3600,
                "proxied": False
            },
            "description": "测试网站"
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(request_data, f)
            f.flush()
            
            # 模拟 API 调用
            deployer.api.list_dns_records.return_value = []  # 没有现有记录
            deployer.api.create_dns_record.return_value = {"id": "new_record_id"}
            
            with patch.object(deployer, 'save_domain_record'):
                result = deployer.deploy_request(f.name)
            
        os.unlink(f.name)
        
        assert result is True
        deployer.api.create_dns_record.assert_called_once()
    
    def test_deploy_request_update_existing(self, deployer):
        """测试更新现有记录"""
        request_data = {
            "domain": "ciao.su",
            "subdomain": "test",
            "record": {
                "type": "A",
                "value": "192.168.1.2",
                "ttl": 3600,
                "proxied": False
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(request_data, f)
            f.flush()
            
            # 模拟现有记录
            deployer.api.list_dns_records.return_value = [{"id": "existing_record_id"}]
            deployer.api.update_dns_record.return_value = {"id": "existing_record_id"}
            
            with patch.object(deployer, 'save_domain_record'):
                result = deployer.deploy_request(f.name)
            
        os.unlink(f.name)
        
        assert result is True
        deployer.api.update_dns_record.assert_called_once()
    
    def test_deploy_request_invalid_domain(self, deployer):
        """测试部署到无效域名"""
        request_data = {
            "domain": "invalid.com",
            "subdomain": "test",
            "record": {
                "type": "A",
                "value": "192.168.1.1"
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(request_data, f)
            f.flush()
            
            result = deployer.deploy_request(f.name)
            
        os.unlink(f.name)
        
        assert result is False
    
    def test_delete_request_success(self, deployer):
        """测试成功删除请求"""
        request_data = {
            "domain": "ciao.su",
            "subdomain": "test",
            "record": {
                "type": "A",
                "value": "192.168.1.1"
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(request_data, f)
            f.flush()
            
            # 模拟现有记录
            deployer.api.list_dns_records.return_value = [{"id": "record_to_delete"}]
            deployer.api.delete_dns_record.return_value = True
            
            with patch.object(deployer, 'remove_domain_record'):
                result = deployer.delete_request(f.name)
            
        os.unlink(f.name)
        
        assert result is True
        deployer.api.delete_dns_record.assert_called_once()
    
    def test_save_domain_record(self, deployer):
        """测试保存域名记录"""
        request_data = {
            "domain": "ciao.su",
            "subdomain": "test",
            "record": {"type": "A", "value": "192.168.1.1"},
            "description": "测试"
        }
        
        with patch('os.makedirs'), \
             patch('builtins.open', create=True) as mock_open, \
             patch('json.dump') as mock_json_dump:
            
            deployer.save_domain_record("ciao.su", "test", request_data)
            
            mock_open.assert_called_once()
            mock_json_dump.assert_called_once()
            
            # 检查是否添加了元数据
            saved_data = mock_json_dump.call_args[0][0]
            assert "_metadata" in saved_data
            assert "deployed_at" in saved_data["_metadata"]


class TestRecordTypes:
    """测试不同记录类型的处理"""
    
    @pytest.fixture
    def deployer(self):
        """创建部署器实例"""
        with patch.object(DNSDeployer, 'load_config'), \
             patch.object(DNSDeployer, 'init_api'):
            
            deployer = DNSDeployer()
            deployer.domains_config = {
                "domains": {
                    "ciao.su": {
                        "enabled": True,
                        "cloudflare_zone_id": "test_zone_id"
                    }
                }
            }
            deployer.api = MagicMock()
            return deployer
    
    def test_mx_record_deployment(self, deployer):
        """测试 MX 记录部署"""
        request_data = {
            "domain": "ciao.su",
            "subdomain": "mail",
            "record": {
                "type": "MX",
                "value": "mail.example.com",
                "priority": 10,
                "ttl": 3600,
                "proxied": False
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(request_data, f)
            f.flush()
            
            deployer.api.list_dns_records.return_value = []
            deployer.api.create_dns_record.return_value = {"id": "mx_record_id"}
            
            with patch.object(deployer, 'save_domain_record'):
                result = deployer.deploy_request(f.name)
            
            # 检查是否正确处理 MX 记录的 priority
            call_args = deployer.api.create_dns_record.call_args[0][1]
            assert call_args["priority"] == 10
            
        os.unlink(f.name)
        assert result is True
    
    def test_cname_record_deployment(self, deployer):
        """测试 CNAME 记录部署"""
        request_data = {
            "domain": "ciao.su",
            "subdomain": "www",
            "record": {
                "type": "CNAME",
                "value": "example.github.io",
                "ttl": 3600,
                "proxied": True
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(request_data, f)
            f.flush()
            
            deployer.api.list_dns_records.return_value = []
            deployer.api.create_dns_record.return_value = {"id": "cname_record_id"}
            
            with patch.object(deployer, 'save_domain_record'):
                result = deployer.deploy_request(f.name)
            
            # 检查记录数据
            call_args = deployer.api.create_dns_record.call_args[0][1]
            assert call_args["type"] == "CNAME"
            assert call_args["content"] == "example.github.io"
            assert call_args["proxied"] is True
            
        os.unlink(f.name)
        assert result is True


if __name__ == "__main__":
    pytest.main([__file__])
