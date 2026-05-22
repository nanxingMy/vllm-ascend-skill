#!/usr/bin/env python3
"""
每天凌晨自动更新 memory 到 vllm-ascend-skill 仓库

功能：
1. 读取当前的 memory 文件
2. 提取有价值的经验教训和知识点
3. 更新到 vllm-ascend-skill 仓库
4. 推送到 GitHub
"""

import os
import re
from datetime import datetime
from pathlib import Path

# 配置
MEMORY_DIR = Path("C:/Users/HuaWei/AppData/Local/hermes/memory")
SKILL_DIR = Path("C:/Users/HuaWei/vllm-ascend-skill/skill/references")
GIT_USER = "nanxingMy"
GIT_EMAIL = "1014662416@qq.com"

def read_memory():
    """读取 memory 文件"""
    memory_content = {}
    
    # 读取 memory.md
    memory_file = MEMORY_DIR / "memory.md"
    if memory_file.exists():
        with open(memory_file, 'r', encoding='utf-8') as f:
            memory_content['memory'] = f.read()
    
    # 读取 user.md
    user_file = MEMORY_DIR / "user.md"
    if user_file.exists():
        with open(user_file, 'r', encoding='utf-8') as f:
            memory_content['user'] = f.read()
    
    return memory_content

def extract_lessons_learned(memory_content):
    """提取经验教训"""
    lessons = []
    
    # 从 memory 中提取
    if 'memory' in memory_content:
        content = memory_content['memory']
        
        # 查找经验教训相关的条目
        patterns = [
            r'关键学习：(.*?)§',
            r'经验：(.*?)§',
            r'教训：(.*?)§',
            r'注意：(.*?)§',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.DOTALL)
            lessons.extend(matches)
    
    return lessons

def extract_development_guide(memory_content):
    """提取开发指南"""
    guides = []
    
    # 从 memory 中提取
    if 'memory' in memory_content:
        content = memory_content['memory']
        
        # 查找开发指南相关的条目
        patterns = [
            r'规则：(.*?)§',
            r'最佳实践：(.*?)§',
            r'建议：(.*?)§',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.DOTALL)
            guides.extend(matches)
    
    return guides

def update_lessons_learned(lessons):
    """更新 lessons-learned.md"""
    lessons_file = SKILL_DIR / "lessons-learned.md"
    
    # 读取现有内容
    if lessons_file.exists():
        with open(lessons_file, 'r', encoding='utf-8') as f:
            content = f.read()
    else:
        content = "# 经验教训\n\n"
    
    # 添加新的经验教训
    if lessons:
        content += f"\n## {datetime.now().strftime('%Y-%m-%d')}\n\n"
        for i, lesson in enumerate(lessons, 1):
            content += f"{i}. {lesson.strip()}\n"
        
        # 写入文件
        with open(lessons_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True
    return False

def update_development_guide(guides):
    """更新 development-guide.md"""
    guide_file = SKILL_DIR / "development-guide.md"
    
    # 读取现有内容
    if guide_file.exists():
        with open(guide_file, 'r', encoding='utf-8') as f:
            content = f.read()
    else:
        content = "# 开发指南\n\n"
    
    # 添加新的指南
    if guides:
        content += f"\n## {datetime.now().strftime('%Y-%m-%d')}\n\n"
        for i, guide in enumerate(guides, 1):
            content += f"{i}. {guide.strip()}\n"
        
        # 写入文件
        with open(guide_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True
    return False

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
    commit_message = f"[Auto] Update memory - {datetime.now().strftime('%Y-%m-%d')}"
    subprocess.run(['git', 'commit', '-m', commit_message], check=True)
    
    # 推送
    subprocess.run(['git', 'push', 'origin', 'main'], check=True)

def main():
    """主函数"""
    print(f"开始更新 memory - {datetime.now()}")
    
    # 读取 memory
    memory_content = read_memory()
    print(f"读取 memory 完成")
    
    # 提取经验教训
    lessons = extract_lessons_learned(memory_content)
    print(f"提取经验教训: {len(lessons)} 条")
    
    # 提取开发指南
    guides = extract_development_guide(memory_content)
    print(f"提取开发指南: {len(guides)} 条")
    
    # 更新文件
    updated = False
    if lessons:
        updated |= update_lessons_learned(lessons)
        print("更新 lessons-learned.md")
    
    if guides:
        updated |= update_development_guide(guides)
        print("更新 development-guide.md")
    
    # 提交并推送
    if updated:
        git_commit_and_push()
        print("提交并推送完成")
    else:
        print("没有需要更新的内容")
    
    print("更新完成")

if __name__ == "__main__":
    main()
