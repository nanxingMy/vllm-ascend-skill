#!/usr/bin/env python3
"""
自动学习其他用户的 Issue 解决方式

功能：
1. 查看自己修改的 Issue
2. 检查 PR 是否合入
3. 如果未合入，检查 issue 评论
4. 查找其他用户的 PR
5. 学习已合入的修改方式
6. 提取经验和最佳实践
"""

import os
import re
import json
import requests
from datetime import datetime
from pathlib import Path

# 配置
GITHUB_TOKEN_PATH = Path("C:/Users/HuaWei/AppData/Local/Temp/github_token.txt")
SKILL_DIR = Path("C:/Users/HuaWei/vllm-ascend-skill/skill/references")
LEARN_DIR = SKILL_DIR / "learned-from-others"
GIT_USER = "nanxingMy"
GIT_EMAIL = "1014662416@qq.com"

# 确保学习目录存在
LEARN_DIR.mkdir(parents=True, exist_ok=True)

# 我创建的 PR 列表
MY_PRS = [
    {"number": 9199, "issue": 9167, "title": "vllm_version_is 版本后缀"},
    {"number": 9383, "issue": 9291, "title": "MiniMax-M2.7 文档"},
    {"number": 9381, "issue": 9358, "title": "DeepSeek-V3.2 参数"},
    {"number": 9416, "issue": 8975, "title": "BalanceScheduler 死锁"},
    {"number": 9216, "issue": 4112, "title": "NPUWorker shutdown"},
]

class IssueLearner:
    """Issue 学习器"""
    
    def __init__(self, token):
        self.token = token
        self.headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        self.lessons = []
    
    def get_pr_status(self, pr_number):
        """获取 PR 状态"""
        response = requests.get(
            f'https://api.github.com/repos/vllm-project/vllm-ascend/pulls/{pr_number}',
            headers=self.headers
        )
        
        if response.status_code == 200:
            pr = response.json()
            return {
                'number': pr_number,
                'state': pr['state'],
                'merged': pr.get('merged', False),
                'closed_at': pr.get('closed_at'),
                'merged_at': pr.get('merged_at'),
                'user': pr['user']['login']
            }
        return None
    
    def get_issue_comments(self, issue_number):
        """获取 Issue 评论"""
        response = requests.get(
            f'https://api.github.com/repos/vllm-project/vllm-ascend/issues/{issue_number}/comments',
            headers=self.headers
        )
        
        if response.status_code == 200:
            return response.json()
        return []
    
    def find_other_prs(self, issue_number):
        """查找其他用户的相关 PR"""
        # 搜索 issue 相关的 PR
        response = requests.get(
            f'https://api.github.com/search/issues?q=repo:vllm-project/vllm-ascend+is:pr+"{issue_number}"+in:body',
            headers=self.headers
        )
        
        other_prs = []
        if response.status_code == 200:
            items = response.json()['items']
            
            for item in items:
                if item['user']['login'] != GIT_USER:
                    other_prs.append({
                        'number': item['number'],
                        'title': item['title'],
                        'state': item['state'],
                        'user': item['user']['login'],
                        'url': item['html_url']
                    })
        
        return other_prs
    
    def get_pr_files(self, pr_number):
        """获取 PR 修改的文件"""
        response = requests.get(
            f'https://api.github.com/repos/vllm-project/vllm-ascend/pulls/{pr_number}/files',
            headers=self.headers
        )
        
        if response.status_code == 200:
            return response.json()
        return []
    
    def get_pr_commits(self, pr_number):
        """获取 PR 的 commits"""
        response = requests.get(
            f'https://api.github.com/repos/vllm-project/vllm-ascend/pulls/{pr_number}/commits',
            headers=self.headers
        )
        
        if response.status_code == 200:
            return response.json()
        return []
    
    def analyze_pr_solution(self, pr_number):
        """分析 PR 的解决方案"""
        files = self.get_pr_files(pr_number)
        commits = self.get_pr_commits(pr_number)
        
        solution = {
            'files': [],
            'approach': [],
            'key_changes': []
        }
        
        # 分析修改的文件
        for file in files:
            solution['files'].append({
                'path': file['filename'],
                'additions': file['additions'],
                'deletions': file['deletions'],
                'change_type': file['status']
            })
            
            # 提取关键修改
            if file.get('patch'):
                patch = file['patch']
                
                # 查找关键模式
                patterns = {
                    '添加检查': r'^\+.*if.*:',
                    '添加异常': r'^\+.*raise.*:',
                    '添加函数': r'^\+.*def.*:',
                    '添加类': r'^\+.*class.*:',
                    '修改逻辑': r'^\+.*return.*:',
                }
                
                for pattern_name, pattern in patterns.items():
                    if re.search(pattern, patch, re.MULTILINE):
                        solution['key_changes'].append(f"{pattern_name} in {file['filename']}")
        
        # 分析 commit messages
        for commit in commits:
            message = commit['commit']['message']
            solution['approach'].append(message.split('\n')[0])
        
        return solution
    
    def learn_from_issue(self, my_pr_info):
        """从 Issue 学习"""
        pr_number = my_pr_info['number']
        issue_number = my_pr_info['issue']
        title = my_pr_info['title']
        
        print(f"\n分析 Issue #{issue_number} - {title}")
        print(f"我的 PR: #{pr_number}")
        
        # 1. 检查我的 PR 状态
        my_pr_status = self.get_pr_status(pr_number)
        
        if not my_pr_status:
            print(f"  ❌ 无法获取 PR #{pr_number} 状态")
            return
        
        print(f"  我的 PR 状态: {my_pr_status['state']}")
        print(f"  是否合入: {my_pr_status['merged']}")
        
        # 如果已合入，不需要学习
        if my_pr_status['merged']:
            print(f"  ✅ 我的 PR 已合入，无需学习")
            return
        
        # 2. 检查 Issue 评论
        print(f"\n  检查 Issue #{issue_number} 评论...")
        comments = self.get_issue_comments(issue_number)
        
        other_solutions = []
        
        for comment in comments:
            # 查找评论中提到的 PR
            pr_mentions = re.findall(r'#(\d+)', comment['body'])
            
            for mentioned_pr in pr_mentions:
                pr_status = self.get_pr_status(int(mentioned_pr))
                
                if pr_status and pr_status['user'] != GIT_USER:
                    print(f"    发现其他用户的 PR: #{mentioned_pr} by {pr_status['user']}")
                    
                    if pr_status['merged']:
                        print(f"      ✅ 已合入！")
                        
                        # 分析解决方案
                        solution = self.analyze_pr_solution(int(mentioned_pr))
                        
                        other_solutions.append({
                            'pr_number': int(mentioned_pr),
                            'user': pr_status['user'],
                            'merged_at': pr_status['merged_at'],
                            'solution': solution
                        })
        
        # 3. 查找其他相关 PR
        print(f"\n  搜索其他相关 PR...")
        other_prs = self.find_other_prs(issue_number)
        
        for other_pr in other_prs:
            pr_status = self.get_pr_status(other_pr['number'])
            
            if pr_status and pr_status['merged']:
                print(f"    发现已合入的 PR: #{other_pr['number']} by {other_pr['user']}")
                
                # 分析解决方案
                solution = self.analyze_pr_solution(other_pr['number'])
                
                other_solutions.append({
                    'pr_number': other_pr['number'],
                    'user': other_pr['user'],
                    'merged_at': pr_status['merged_at'],
                    'solution': solution
                })
        
        # 4. 保存学习结果
        if other_solutions:
            lesson = {
                'issue_number': issue_number,
                'my_pr': pr_number,
                'title': title,
                'other_solutions': other_solutions,
                'learned_at': datetime.now().isoformat()
            }
            
            self.lessons.append(lesson)
            
            print(f"\n  📚 学习到 {len(other_solutions)} 种解决方案")
        
        return other_solutions
    
    def generate_lesson_doc(self):
        """生成学习文档"""
        if not self.lessons:
            print("\n没有需要学习的内容")
            return
        
        doc_content = f"""# 从其他用户学习 Issue 解决方式

> 学习时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 学习概览

共学习 {len(self.lessons)} 个 Issue 的解决方案。

---

"""
        
        for i, lesson in enumerate(self.lessons, 1):
            doc_content += f"""## {i}. Issue #{lesson['issue_number']}: {lesson['title']}

**我的 PR**: #{lesson['my_pr']}

**其他用户的解决方案**: {len(lesson['other_solutions'])} 个

"""
            
            for j, solution in enumerate(lesson['other_solutions'], 1):
                doc_content += f"""### 解决方案 {j}: PR #{solution['pr_number']}

**用户**: {solution['user']}

**合入时间**: {solution['merged_at']}

**修改的文件**:
"""
                
                for file in solution['solution']['files']:
                    doc_content += f"- `{file['path']}`: +{file['additions']} -{file['deletions']}\n"
                
                if solution['solution']['key_changes']:
                    doc_content += f"\n**关键修改**:\n"
                    for change in solution['solution']['key_changes'][:5]:
                        doc_content += f"- {change}\n"
                
                if solution['solution']['approach']:
                    doc_content += f"\n**实现方式**:\n"
                    for approach in solution['solution']['approach'][:3]:
                        doc_content += f"- {approach}\n"
                
                doc_content += "\n---\n\n"
            
            doc_content += "\n"
        
        # 保存文档
        doc_file = LEARN_DIR / f"lessons-{datetime.now().strftime('%Y-%m-%d')}.md"
        doc_file.write_text(doc_content, encoding='utf-8')
        
        print(f"\n✅ 学习文档已保存: {doc_file}")
    
    def git_commit_and_push(self):
        """提交并推送"""
        import subprocess
        
        os.chdir(SKILL_DIR.parent.parent)
        
        subprocess.run(['git', 'config', 'user.name', GIT_USER], check=True)
        subprocess.run(['git', 'config', 'user.email', GIT_EMAIL], check=True)
        subprocess.run(['git', 'add', 'skill/references/learned-from-others/'], check=True)
        
        commit_msg = f"[Learn] Learn from other users - {datetime.now().strftime('%Y-%m-%d')}"
        subprocess.run(['git', 'commit', '-m', commit_msg], check=True)
        subprocess.run(['git', 'push', 'origin', 'main'], check=True)

def main():
    """主函数"""
    print(f"\n{'='*70}")
    print(f"自动学习其他用户的 Issue 解决方式")
    print(f"{'='*70}\n")
    
    # 读取 token
    with open(GITHUB_TOKEN_PATH, 'r') as f:
        token = f.read().strip()
    
    # 创建学习器
    learner = IssueLearner(token)
    
    # 学习每个 Issue
    for pr_info in MY_PRS:
        learner.learn_from_issue(pr_info)
    
    # 生成学习文档
    learner.generate_lesson_doc()
    
    # 提交推送
    if learner.lessons:
        print("\n提交并推送...")
        learner.git_commit_and_push()
    
    print(f"\n{'='*70}")
    print("学习完成！")
    print(f"{'='*70}\n")

if __name__ == "__main__":
    main()
