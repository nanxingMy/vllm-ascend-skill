#!/usr/bin/env python3
"""
学习所有已合入的 PR

功能：
1. 获取所有已合入的 PR
2. 分析每个 PR 的解决方案
3. 查找对应的 Issue
4. 提取经验和最佳实践
5. 保存到 vllm-ascend-skill 仓库
"""

import os
import re
import json
import requests
from datetime import datetime
from pathlib import Path
from collections import defaultdict

# 配置
GITHUB_TOKEN_PATH = Path("C:/Users/HuaWei/AppData/Local/Temp/github_token.txt")
SKILL_DIR = Path("C:/Users/HuaWei/vllm-ascend-skill/skill/references")
LEARN_DIR = SKILL_DIR / "learned-from-prs"
GIT_USER = "nanxingMy"
GIT_EMAIL = "1014662416@qq.com"

# 确保学习目录存在
LEARN_DIR.mkdir(parents=True, exist_ok=True)

class PRLearner:
    """PR 学习器"""
    
    def __init__(self, token):
        self.token = token
        self.headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        self.learned_prs = []
        self.stats = {
            'total_prs': 0,
            'learned_prs': 0,
            'categories': defaultdict(int)
        }
    
    def get_merged_prs(self, page=1, per_page=100):
        """获取已合入的 PR"""
        response = requests.get(
            'https://api.github.com/repos/vllm-project/vllm-ascend/pulls',
            headers=self.headers,
            params={
                'state': 'closed',
                'sort': 'updated',
                'direction': 'desc',
                'page': page,
                'per_page': per_page
            }
        )
        
        if response.status_code == 200:
            prs = response.json()
            # 过滤已合入的 PR
            merged_prs = [pr for pr in prs if pr.get('merged_at')]
            return merged_prs
        return []
    
    def extract_issue_number(self, pr):
        """从 PR 中提取 Issue 编号"""
        # 从 PR body 中查找 Issue 编号
        body = pr.get('body', '') or ''
        
        # 查找 "Fixes #123" 或 "Closes #123" 或 "#123"
        patterns = [
            r'[Ff]ixes\s+#(\d+)',
            r'[Cc]loses\s+#(\d+)',
            r'[Rr]esolves\s+#(\d+)',
            r'#(\d+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, body)
            if match:
                return int(match.group(1))
        
        # 从标题中查找
        title = pr.get('title', '')
        match = re.search(r'#(\d+)', title)
        if match:
            return int(match.group(1))
        
        return None
    
    def get_issue_info(self, issue_number):
        """获取 Issue 信息"""
        response = requests.get(
            f'https://api.github.com/repos/vllm-project/vllm-ascend/issues/{issue_number}',
            headers=self.headers
        )
        
        if response.status_code == 200:
            return response.json()
        return None
    
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
    
    def categorize_pr(self, pr_title, files):
        """对 PR 分类"""
        title_lower = pr_title.lower()
        
        categories = []
        
        # 按标题关键词分类
        if any(kw in title_lower for kw in ['fix', 'bug', 'error', 'issue']):
            categories.append('Bug Fix')
        
        if any(kw in title_lower for kw in ['feature', 'add', 'support', 'implement']):
            categories.append('Feature')
        
        if any(kw in title_lower for kw in ['doc', 'readme', 'comment']):
            categories.append('Documentation')
        
        if any(kw in title_lower for kw in ['test', 'ut', 'e2e']):
            categories.append('Test')
        
        if any(kw in title_lower for kw in ['refactor', 'clean', 'improve']):
            categories.append('Refactor')
        
        if any(kw in title_lower for kw in ['perf', 'optimize', 'speed']):
            categories.append('Performance')
        
        # 按修改文件分类
        file_paths = [f.get('filename', '') for f in files]
        
        if any('ops' in path for path in file_paths):
            categories.append('Operator')
        
        if any('worker' in path for path in file_paths):
            categories.append('Worker')
        
        if any('platform' in path for path in file_paths):
            categories.append('Platform')
        
        if any('attention' in path for path in file_paths):
            categories.append('Attention')
        
        return categories if categories else ['Other']
    
    def analyze_solution(self, pr_number):
        """分析 PR 的解决方案"""
        files = self.get_pr_files(pr_number)
        commits = self.get_pr_commits(pr_number)
        
        solution = {
            'files': [],
            'approaches': [],
            'key_patterns': [],
            'additions': 0,
            'deletions': 0
        }
        
        # 分析修改的文件
        for file in files:
            solution['files'].append({
                'path': file['filename'],
                'additions': file['additions'],
                'deletions': file['deletions'],
                'change_type': file['status']
            })
            
            solution['additions'] += file['additions']
            solution['deletions'] += file['deletions']
            
            # 提取关键模式
            if file.get('patch'):
                patch = file['patch']
                
                patterns = {
                    '添加检查': r'^\+.*if\s+.*:',
                    '添加异常处理': r'^\+.*raise\s+.*:',
                    '添加函数': r'^\+.*def\s+\w+.*:',
                    '添加类': r'^\+.*class\s+\w+.*:',
                    '修改返回值': r'^\+.*return\s+.*:',
                    '添加导入': r'^\+.*import\s+.*',
                    '添加断言': r'^\+.*assert\s+.*:',
                    '添加日志': r'^\+.*logger\.\w+\(.*:',
                }
                
                for pattern_name, pattern in patterns.items():
                    matches = re.findall(pattern, patch, re.MULTILINE)
                    if matches:
                        solution['key_patterns'].append({
                            'pattern': pattern_name,
                            'file': file['filename'],
                            'count': len(matches)
                        })
        
        # 分析 commit messages
        for commit in commits:
            message = commit['commit']['message']
            solution['approaches'].append(message.split('\n')[0])
        
        return solution
    
    def learn_from_pr(self, pr):
        """从单个 PR 学习"""
        pr_number = pr['number']
        pr_title = pr['title']
        pr_user = pr['user']['login']
        merged_at = pr['merged_at']
        
        print(f"\n学习 PR #{pr_number}: {pr_title}")
        print(f"  作者: {pr_user}")
        print(f"  合入时间: {merged_at}")
        
        # 1. 提取 Issue 编号
        issue_number = self.extract_issue_number(pr)
        
        issue_info = None
        if issue_number:
            print(f"  对应 Issue: #{issue_number}")
            issue_info = self.get_issue_info(issue_number)
        
        # 2. 分析解决方案
        print(f"  分析解决方案...")
        solution = self.analyze_solution(pr_number)
        
        print(f"    修改文件: {len(solution['files'])} 个")
        print(f"    添加代码: +{solution['additions']} 行")
        print(f"    删除代码: -{solution['deletions']} 行")
        
        # 3. 分类
        categories = self.categorize_pr(pr_title, solution['files'])
        print(f"  分类: {', '.join(categories)}")
        
        # 4. 保存学习结果
        learned = {
            'pr_number': pr_number,
            'pr_title': pr_title,
            'pr_user': pr_user,
            'pr_url': pr['html_url'],
            'merged_at': merged_at,
            'issue_number': issue_number,
            'issue_title': issue_info['title'] if issue_info else None,
            'issue_labels': [label['name'] for label in issue_info.get('labels', [])] if issue_info else [],
            'categories': categories,
            'solution': solution,
            'learned_at': datetime.now().isoformat()
        }
        
        self.learned_prs.append(learned)
        
        # 更新统计
        for category in categories:
            self.stats['categories'][category] += 1
        
        return learned
    
    def learn_all_merged_prs(self, max_prs=None):
        """学习所有已合入的 PR"""
        print(f"\n{'='*70}")
        print(f"开始学习所有已合入的 PR")
        print(f"{'='*70}\n")
        
        # 读取已学习的 PR
        learned_pr_numbers = set()
        data_file = LEARN_DIR / f"prs-data-{datetime.now().strftime('%Y-%m-%d')}.json"
        if data_file.exists():
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for pr in data.get('prs', []):
                    learned_pr_numbers.add(pr['pr_number'])
            print(f"已学习 {len(learned_pr_numbers)} 个 PR，将跳过\n")
        
        page = 1
        total_learned = 0
        skipped = 0
        
        while True:
            print(f"获取第 {page} 页 PR...")
            prs = self.get_merged_prs(page=page)
            
            if not prs:
                print("没有更多 PR")
                break
            
            for pr in prs:
                if max_prs and total_learned >= max_prs:
                    print(f"\n已达到最大学习数量: {max_prs}")
                    break
                
                # 跳过已学习的 PR
                if pr['number'] in learned_pr_numbers:
                    skipped += 1
                    continue
                
                try:
                    self.learn_from_pr(pr)
                    total_learned += 1
                    self.stats['learned_prs'] += 1
                except Exception as e:
                    print(f"  ❌ 学习失败: {e}")
            
            if max_prs and total_learned >= max_prs:
                break
            
            page += 1
        
        self.stats['total_prs'] = total_learned
        
        print(f"\n{'='*70}")
        print(f"学习完成！")
        print(f"共学习 {total_learned} 个新 PR")
        print(f"跳过 {skipped} 个已学习的 PR")
        print(f"{'='*70}\n")
    
    def generate_summary_doc(self):
        """生成学习总结文档"""
        if not self.learned_prs:
            print("没有学习内容")
            return
        
        # 按分类组织
        by_category = defaultdict(list)
        for pr in self.learned_prs:
            for category in pr['categories']:
                by_category[category].append(pr)
        
        # 生成文档
        doc_content = f"""# 从已合入 PR 学习总结

> 学习时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📊 学习统计

- **总学习 PR 数**: {self.stats['total_prs']}
- **学习成功**: {self.stats['learned_prs']}

### 按分类统计

| 分类 | 数量 |
|------|------|
"""
        
        for category, count in sorted(self.stats['categories'].items(), key=lambda x: x[1], reverse=True):
            doc_content += f"| {category} | {count} |\n"
        
        doc_content += "\n---\n\n"
        
        # 按分类展示
        for category in sorted(by_category.keys()):
            prs = by_category[category]
            
            doc_content += f"""## {category}

共 {len(prs)} 个 PR

"""
            
            for pr in prs[:20]:  # 每个分类最多显示 20 个
                doc_content += f"""### PR #{pr['pr_number']}: {pr['pr_title']}

**作者**: {pr['pr_user']}

**合入时间**: {pr['merged_at']}

"""
                
                if pr['issue_number']:
                    doc_content += f"**对应 Issue**: #{pr['issue_number']}"
                    if pr['issue_title']:
                        doc_content += f" - {pr['issue_title']}"
                    doc_content += "\n\n"
                
                if pr['solution']['files']:
                    doc_content += "**修改的文件**:\n"
                    for file in pr['solution']['files'][:5]:
                        doc_content += f"- `{file['path']}`: +{file['additions']} -{file['deletions']}\n"
                    doc_content += "\n"
                
                if pr['solution']['key_patterns']:
                    doc_content += "**关键模式**:\n"
                    for pattern in pr['solution']['key_patterns'][:5]:
                        doc_content += f"- {pattern['pattern']} ({pattern['count']} 次)\n"
                    doc_content += "\n"
                
                doc_content += f"**链接**: {pr['pr_url']}\n\n---\n\n"
        
        # 保存文档
        doc_file = LEARN_DIR / f"summary-{datetime.now().strftime('%Y-%m-%d')}.md"
        doc_file.write_text(doc_content, encoding='utf-8')
        
        print(f"✅ 总结文档已保存: {doc_file}")
    
    def save_raw_data(self):
        """保存原始数据"""
        data_file = LEARN_DIR / f"prs-data-{datetime.now().strftime('%Y-%m-%d')}.json"
        
        # 读取已有数据
        existing_prs = []
        if data_file.exists():
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                existing_prs = data.get('prs', [])
        
        # 合并新的 PR
        all_prs = existing_prs + self.learned_prs
        
        # 去重
        seen = set()
        unique_prs = []
        for pr in all_prs:
            if pr['pr_number'] not in seen:
                seen.add(pr['pr_number'])
                unique_prs.append(pr)
        
        # 更新统计
        self.stats['total_prs'] = len(unique_prs)
        
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump({
                'stats': self.stats,
                'prs': unique_prs
            }, f, indent=2, ensure_ascii=False)
        
        print(f"✅ 原始数据已保存: {data_file}")
        print(f"   总计 {len(unique_prs)} 个 PR")
    
    def git_commit_and_push(self):
        """提交并推送"""
        import subprocess
        
        os.chdir(SKILL_DIR.parent.parent)
        
        subprocess.run(['git', 'config', 'user.name', GIT_USER], check=True)
        subprocess.run(['git', 'config', 'user.email', GIT_EMAIL], check=True)
        subprocess.run(['git', 'add', 'skill/references/learned-from-prs/'], check=True)
        
        commit_msg = f"[Learn] Learn from all merged PRs - {datetime.now().strftime('%Y-%m-%d')}"
        subprocess.run(['git', 'commit', '-m', commit_msg], check=True)
        subprocess.run(['git', 'push', 'origin', 'main'], check=True)

def main():
    """主函数"""
    print(f"\n{'='*70}")
    print(f"学习所有已合入的 PR")
    print(f"{'='*70}\n")
    
    # 读取 token
    with open(GITHUB_TOKEN_PATH, 'r') as f:
        token = f.read().strip()
    
    # 创建学习器
    learner = PRLearner(token)
    
    # 学习所有已合入的 PR (分批学习，每次 50 个)
    # 第一次学习 1-50
    # 第二次学习 51-100
    # 以此类推
    learner.learn_all_merged_prs(max_prs=50)
    
    # 生成总结文档
    learner.generate_summary_doc()
    
    # 保存原始数据
    learner.save_raw_data()
    
    # 提交推送
    if learner.learned_prs:
        print("\n提交并推送...")
        learner.git_commit_and_push()
    
    print(f"\n{'='*70}")
    print("全部完成！")
    print(f"{'='*70}\n")

if __name__ == "__main__":
    main()
