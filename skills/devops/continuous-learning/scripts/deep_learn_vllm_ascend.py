#!/usr/bin/env python3
"""
每天凌晨自动深入学习 vllm-ascend 项目

功能：
1. 分析项目结构和架构
2. 学习关键模块和类
3. 提取最佳实践和设计模式
4. 更新到 vllm-ascend-skill 仓库
"""

import os
import re
import json
from datetime import datetime
from pathlib import Path

# 配置
VLLM_ASCEND_DIR = Path("C:/Users/HuaWei/vllm-ascend")
SKILL_DIR = Path("C:/Users/HuaWei/vllm-ascend-skill/skill/references")
GIT_USER = "nanxingMy"
GIT_EMAIL = "1014662416@qq.com"

def analyze_project_structure():
    """分析项目结构"""
    structure = {
        "directories": {},
        "key_files": [],
        "modules": []
    }
    
    # 关键目录
    key_dirs = [
        "vllm_ascend",
        "vllm_ascend/worker",
        "vllm_ascend/platform",
        "vllm_ascend/attention",
        "vllm_ascend/ops",
        "vllm_ascend/distributed",
        "tests",
        "docs"
    ]
    
    for dir_name in key_dirs:
        dir_path = VLLM_ASCEND_DIR / dir_name
        if dir_path.exists():
            files = list(dir_path.glob("*.py"))
            structure["directories"][dir_name] = {
                "file_count": len(files),
                "files": [f.name for f in files[:10]]  # 前10个文件
            }
    
    # 关键文件
    key_files = [
        "vllm_ascend/platform.py",
        "vllm_ascend/worker/worker.py",
        "vllm_ascend/ascend_config.py",
        "vllm_ascend/utils.py"
    ]
    
    for file_name in key_files:
        file_path = VLLM_ASCEND_DIR / file_name
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            structure["key_files"].append({
                "path": file_name,
                "lines": len(content.split('\n')),
                "classes": len(re.findall(r'^class \w+', content, re.MULTILINE)),
                "functions": len(re.findall(r'^def \w+', content, re.MULTILINE))
            })
    
    return structure

def extract_key_classes():
    """提取关键类"""
    classes = []
    
    key_files = [
        "vllm_ascend/platform.py",
        "vllm_ascend/worker/worker.py"
    ]
    
    for file_name in key_files:
        file_path = VLLM_ASCEND_DIR / file_name
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 提取类定义
            class_matches = re.findall(r'^class (\w+)(?:\(([^)]+)\))?:', content, re.MULTILINE)
            
            for class_name, base_class in class_matches:
                classes.append({
                    "name": class_name,
                    "file": file_name,
                    "base": base_class if base_class else "object"
                })
    
    return classes

def extract_design_patterns():
    """提取设计模式"""
    patterns = []
    
    # 检查常见设计模式
    pattern_checks = [
        ("Singleton", r'class \w+:[\s\S]*?_instance\s*=\s*None'),
        ("Factory", r'def create_\w+'),
        ("Strategy", r'class \w+Strategy'),
        ("Adapter", r'class \w+Adapter'),
    ]
    
    for file_path in VLLM_ASCEND_DIR.glob("vllm_ascend/**/*.py"):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            for pattern_name, pattern_regex in pattern_checks:
                if re.search(pattern_regex, content):
                    patterns.append({
                        "pattern": pattern_name,
                        "file": str(file_path.relative_to(VLLM_ASCEND_DIR))
                    })
        except:
            pass
    
    return patterns[:20]  # 限制数量

def update_architecture_doc(structure, classes, patterns):
    """更新架构文档"""
    arch_file = SKILL_DIR / "architecture.md"
    
    content = f"""# vLLM-Ascend 架构详解

> 自动生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 项目结构

### 关键目录

"""
    
    for dir_name, info in structure["directories"].items():
        content += f"\n#### {dir_name}\n\n"
        content += f"- 文件数: {info['file_count']}\n"
        content += f"- 主要文件: {', '.join(info['files'][:5])}\n"
    
    content += "\n## 关键文件\n\n"
    
    for file_info in structure["key_files"]:
        content += f"### {file_info['path']}\n\n"
        content += f"- 行数: {file_info['lines']}\n"
        content += f"- 类数: {file_info['classes']}\n"
        content += f"- 函数数: {file_info['functions']}\n\n"
    
    content += "\n## 关键类\n\n"
    
    for cls in classes:
        content += f"- **{cls['name']}** ({cls['file']})\n"
        content += f"  - 基类: {cls['base']}\n\n"
    
    content += "\n## 设计模式\n\n"
    
    for pattern in patterns:
        content += f"- {pattern['pattern']} ({pattern['file']})\n"
    
    # 写入文件
    with open(arch_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True

def update_inheritance_doc(classes):
    """更新继承关系文档"""
    inherit_file = SKILL_DIR / "inheritance.md"
    
    content = f"""# vLLM-Ascend 继承关系

> 自动生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 类继承图

"""
    
    # 按基类分组
    by_base = {}
    for cls in classes:
        base = cls['base']
        if base not in by_base:
            by_base[base] = []
        by_base[base].append(cls['name'])
    
    for base, children in by_base.items():
        content += f"\n### 继承自 {base}\n\n"
        for child in children:
            content += f"- {child}\n"
    
    # 写入文件
    with open(inherit_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True

def git_commit_and_push():
    """提交并推送到 GitHub"""
    import subprocess
    
    # 切换到仓库目录
    os.chdir(SKILL_DIR.parent.parent)
    
    # 配置 Git
    subprocess.run(['git', 'config', 'user.name', GIT_USER], check=True)
    subprocess.run(['git', 'config', 'user.email', GIT_EMAIL], check=True)
    
    # 添加修改
    subprocess.run(['git', 'add', 'skill/references/'], check=True)
    
    # 提交
    commit_message = f"[Auto] Deep learn vllm-ascend - {datetime.now().strftime('%Y-%m-%d')}"
    subprocess.run(['git', 'commit', '-m', commit_message], check=True)
    
    # 推送
    subprocess.run(['git', 'push', 'origin', 'main'], check=True)

def main():
    """主函数"""
    print(f"开始深入学习 vllm-ascend - {datetime.now()}")
    
    # 分析项目结构
    print("1. 分析项目结构...")
    structure = analyze_project_structure()
    print(f"   找到 {len(structure['directories'])} 个关键目录")
    
    # 提取关键类
    print("2. 提取关键类...")
    classes = extract_key_classes()
    print(f"   找到 {len(classes)} 个关键类")
    
    # 提取设计模式
    print("3. 提取设计模式...")
    patterns = extract_design_patterns()
    print(f"   找到 {len(patterns)} 个设计模式")
    
    # 更新文档
    print("4. 更新架构文档...")
    update_architecture_doc(structure, classes, patterns)
    
    print("5. 更新继承关系文档...")
    update_inheritance_doc(classes)
    
    # 提交并推送
    print("6. 提交并推送...")
    git_commit_and_push()
    
    print("学习完成！")

if __name__ == "__main__":
    main()
