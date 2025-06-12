#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GitHub PR 检查机器人

此模块提供了检查 GitHub Pull Request 的功能。
"""

import json
import os
import sys
from typing import Dict, List, Any, Optional, Tuple

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from scripts.validation.domain_validator import validate_pull_request, load_config


def format_validation_result(results: Dict[str, List[str]]) -> str:
    """
    格式化验证结果为 Markdown 格式
    
    Args:
        results: 验证结果字典 {文件路径: 错误信息列表}
    
    Returns:
        Markdown 格式的验证结果
    """
    markdown = []
    
    for file_path, errors in results.items():
        if errors:
            markdown.append(f"### ❌ {file_path}")
            markdown.append("")
            for error in errors:
                markdown.append(f"- {error}")
            markdown.append("")
        else:
            markdown.append(f"### ✅ {file_path}")
            markdown.append("")
            markdown.append("验证通过，没有发现问题。")
            markdown.append("")
    
    if not markdown:
        return "所有文件验证通过，没有发现问题。"
    
    return "\n".join(markdown)


def check_pr_files(pr_files: List[str], config: Optional[Dict[str, Any]] = None) -> Tuple[bool, str]:
    """
    检查 Pull Request 中的文件
    
    Args:
        pr_files: Pull Request 中的文件路径列表
        config: 项目配置信息 (可选)
    
    Returns:
        (是否所有文件有效, Markdown 格式的验证结果)
    """
    # 过滤出实际存在的文件
    existing_files = [f for f in pr_files if os.path.exists(f)]
    missing_files = [f for f in pr_files if not os.path.exists(f)]
    
    # 如果有文件不存在，添加到错误信息中
    if missing_files:
        print(f"警告: 以下文件不存在: {', '.join(missing_files)}", file=sys.stderr)
    
    # 如果没有文件需要验证
    if not existing_files:
        return False, "没有找到需要验证的文件。"
    
    try:
        # 验证文件
        all_valid, results = validate_pull_request(existing_files, config)
        
        # 格式化结果
        markdown = format_validation_result(results)
        
        return all_valid, markdown
    except Exception as e:
        error_msg = f"验证过程中发生错误: {str(e)}"
        print(error_msg, file=sys.stderr)
        return False, f"## ❌ 验证失败\n\n{error_msg}"


def main():
    """命令行入口点"""
    import argparse
    
    parser = argparse.ArgumentParser(description='GitHub PR 检查工具')
    parser.add_argument('--config', help='配置文件路径')
    parser.add_argument('--files', nargs='+', required=True, help='要检查的文件路径')
    parser.add_argument('--output', help='输出文件路径')
    
    args = parser.parse_args()
    
    try:
        # 加载项目配置
        config = load_config(args.config) if args.config else None
        
        # 检查文件
        all_valid, markdown = check_pr_files(args.files, config)
        
        # 输出结果
        if args.output:
            os.makedirs(os.path.dirname(args.output), exist_ok=True)
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(markdown)
        else:
            print(markdown)
        
        return 0 if all_valid else 1
    except Exception as e:
        error_msg = f"程序执行失败: {str(e)}"
        print(error_msg, file=sys.stderr)
        if args.output:
            try:
                os.makedirs(os.path.dirname(args.output), exist_ok=True)
                with open(args.output, 'w', encoding='utf-8') as f:
                    f.write(f"## ❌ 执行失败\n\n{error_msg}")
            except:
                pass
        return 1


if __name__ == "__main__":
    sys.exit(main())
