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
    markdown.append("# 🤖 域名配置验证结果\n")
    
    # 统计信息
    total_files = len(results)
    error_files = sum(1 for errors in results.values() if errors)
    success_files = total_files - error_files
    
    if error_files == 0:
        markdown.append("## ✅ 验证通过")
        markdown.append(f"所有 {total_files} 个文件验证通过，没有发现问题。\n")
    else:
        markdown.append("## ❌ 验证失败")
        markdown.append(f"共 {total_files} 个文件，其中 {error_files} 个文件有问题，{success_files} 个文件正常。\n")
    
    # 详细结果
    for file_path, errors in results.items():
        if errors:
            markdown.append(f"### ❌ `{file_path}`")
            markdown.append("")
            for i, error in enumerate(errors, 1):
                # 将多行错误信息格式化
                if '\n' in error:
                    lines = error.split('\n')
                    markdown.append(f"**错误 {i}:** {lines[0]}")
                    for line in lines[1:]:
                        if line.strip():
                            markdown.append(f"  - {line.strip()}")
                else:
                    markdown.append(f"**错误 {i}:** {error}")
            markdown.append("")
        else:
            markdown.append(f"### ✅ `{file_path}`")
            markdown.append("")
            markdown.append("验证通过，没有发现问题。")
            markdown.append("")
    
    # 添加帮助提示
    if error_files > 0:
        markdown.append("---")
        markdown.append("## 💡 常见问题解决方法")
        markdown.append("")
        markdown.append("### JSON 格式错误")
        markdown.append("- **缺少逗号**: 确保 JSON 对象中的字段用逗号分隔")
        markdown.append("- **缺少冒号**: 确保键值对用冒号分隔")
        markdown.append("- **引号不匹配**: 确保所有字符串用双引号包围")
        markdown.append("- **多余逗号**: 删除最后一个字段后的多余逗号")
        markdown.append("")
        markdown.append("### 推荐工具")
        markdown.append("- 使用 [JSONLint](https://jsonlint.com/) 验证 JSON 格式")
        markdown.append("- 使用支持 JSON 语法高亮的编辑器（如 VS Code）")
        markdown.append("")
        markdown.append("如需帮助，请查看 [用户指南](https://github.com/bestzwei/LibreDomains/blob/main/docs/user-guide.md)")
    
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
        import traceback
        error_msg = f"验证过程中发生错误: {str(e)}"
        # 添加详细的错误追踪信息
        traceback_info = traceback.format_exc()
        print(f"详细错误信息:\n{traceback_info}", file=sys.stderr)
        return False, f"## ❌ 验证失败\n\n{error_msg}\n\n详细错误信息请查看 Actions 日志。"


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
