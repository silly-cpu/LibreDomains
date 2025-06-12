#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证脚本测试
"""

import pytest
import json
import tempfile
import os
from unittest.mock import patch, MagicMock
import sys

# 添加脚本目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from validate_request import RequestValidator


class TestRequestValidator:
    """请求验证器测试"""
    
    @pytest.fixture
    def validator(self):
        """创建验证器实例"""
        with patch.object(RequestValidator, 'load_config'), \
             patch.object(RequestValidator, 'load_schema'):
            validator = RequestValidator()
            
            # 模拟配置
            validator.domains_config = {
                "domains": {
                    "ciao.su": {
                        "enabled": True,
                        "cloudflare_zone_id": "test_zone_id",
                        "allowed_record_types": ["A", "AAAA", "CNAME", "MX", "TXT", "SRV"]
                    },
                    "ciallo.de": {
                        "enabled": False,
                        "cloudflare_zone_id": "test_zone_id_2"
                    }
                },
                "settings": {
                    "require_github_verification": True,
                    "min_account_age_days": 30,
                    "max_subdomains_per_user": 3,
                    "blocked_subdomains": ["www", "mail", "admin"],
                    "blocked_users": ["blocked_user"]
                }
            }
            
            # 模拟 schema
            validator.schema = {
                "type": "object",
                "required": ["domain", "subdomain", "owner", "record", "description"],
                "properties": {
                    "domain": {"type": "string"},
                    "subdomain": {"type": "string"},
                    "owner": {
                        "type": "object",
                        "required": ["username", "email"],
                        "properties": {
                            "username": {"type": "string"},
                            "email": {"type": "string", "format": "email"}
                        }
                    },
                    "record": {
                        "type": "object",
                        "required": ["type", "value"],
                        "properties": {
                            "type": {"type": "string"},
                            "value": {"type": "string"}
                        }
                    },
                    "description": {"type": "string"}
                }
            }
            
            return validator
    
    def test_valid_request(self, validator):
        """测试有效请求"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({
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
            }, f)
            f.flush()
            
            with patch.object(validator, 'validate_github_user', return_value=[]), \
                 patch.object(validator, 'count_user_subdomains', return_value=0), \
                 patch('os.path.exists', return_value=False):
                
                result = validator.validate_request(f.name)
                
        os.unlink(f.name)
        assert result["valid"] is True
        assert len(result["errors"]) == 0
    
    def test_invalid_domain(self, validator):
        """测试无效域名"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({
                "domain": "invalid.com",
                "subdomain": "test",
                "owner": {
                    "username": "testuser",
                    "email": "test@example.com"
                },
                "record": {
                    "type": "A",
                    "value": "192.168.1.1"
                },
                "description": "测试"
            }, f)
            f.flush()
            
            result = validator.validate_request(f.name)
                
        os.unlink(f.name)
        assert result["valid"] is False
        assert any("不存在于配置中" in error for error in result["errors"])
    
    def test_disabled_domain(self, validator):
        """测试已禁用域名"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({
                "domain": "ciallo.de",
                "subdomain": "test",
                "owner": {
                    "username": "testuser",
                    "email": "test@example.com"
                },
                "record": {
                    "type": "A",
                    "value": "192.168.1.1"
                },
                "description": "测试"
            }, f)
            f.flush()
            
            result = validator.validate_request(f.name)
                
        os.unlink(f.name)
        assert result["valid"] is False
        assert any("不接受申请" in error for error in result["errors"])
    
    def test_blocked_subdomain(self, validator):
        """测试被禁用的子域名"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({
                "domain": "ciao.su",
                "subdomain": "www",
                "owner": {
                    "username": "testuser",
                    "email": "test@example.com"
                },
                "record": {
                    "type": "A",
                    "value": "192.168.1.1"
                },
                "description": "测试"
            }, f)
            f.flush()
            
            with patch('os.path.exists', return_value=False):
                result = validator.validate_request(f.name)
                
        os.unlink(f.name)
        assert result["valid"] is False
        assert any("被禁用" in error for error in result["errors"])
    
    def test_invalid_ipv4(self, validator):
        """测试无效的 IPv4 地址"""
        assert not validator.is_valid_ipv4("999.999.999.999")
        assert not validator.is_valid_ipv4("192.168.1")
        assert not validator.is_valid_ipv4("not_an_ip")
        assert validator.is_valid_ipv4("192.168.1.1")
        assert validator.is_valid_ipv4("203.0.113.100")
    
    def test_invalid_ipv6(self, validator):
        """测试无效的 IPv6 地址"""
        assert not validator.is_valid_ipv6("invalid_ipv6")
        assert not validator.is_valid_ipv6("2001:db8::gggg")
        assert validator.is_valid_ipv6("2001:db8::1")
        assert validator.is_valid_ipv6("::1")
    
    def test_record_format_validation(self, validator):
        """测试记录格式验证"""
        # A 记录
        errors = validator.validate_record_format({
            "type": "A",
            "value": "192.168.1.1"
        })
        assert len(errors) == 0
        
        errors = validator.validate_record_format({
            "type": "A",
            "value": "invalid_ip"
        })
        assert len(errors) > 0
        
        # CNAME 记录
        errors = validator.validate_record_format({
            "type": "CNAME",
            "value": "example.com"
        })
        assert len(errors) == 0
        
        # MX 记录缺少 priority
        errors = validator.validate_record_format({
            "type": "MX",
            "value": "mail.example.com"
        })
        assert any("缺少 priority" in error for error in errors)


class TestDNSRecordValidation:
    """DNS 记录验证测试"""
    
    def test_srv_record_validation(self):
        """测试 SRV 记录验证"""
        validator = RequestValidator.__new__(RequestValidator)
        
        # 有效的 SRV 记录
        assert validator.is_valid_srv_record("10 20 80 target.example.com")
        assert validator.is_valid_srv_record("0 0 443 ssl.example.com")
        
        # 无效的 SRV 记录
        assert not validator.is_valid_srv_record("invalid")
        assert not validator.is_valid_srv_record("10 20 80")  # 缺少目标
        assert not validator.is_valid_srv_record("10 20 invalid_port target.com")
    
    def test_domain_validation(self):
        """测试域名验证"""
        validator = RequestValidator.__new__(RequestValidator)
        
        # 有效域名
        assert validator.is_valid_domain("example.com")
        assert validator.is_valid_domain("sub.example.com")
        assert validator.is_valid_domain("test-domain.co.uk")
        
        # 无效域名
        assert not validator.is_valid_domain("invalid_domain")
        assert not validator.is_valid_domain("-example.com")
        assert not validator.is_valid_domain("example-.com")
        assert not validator.is_valid_domain("a" * 300)  # 太长


if __name__ == "__main__":
    pytest.main([__file__])
