#!/usr/bin/env python3
"""
每天学习当天合入的 PR

功能：
1. 获取今天合入的 PR
2. 分析每个 PR 的解决方案
3. 提取经验和最佳实践
4. 累积到已有知识库
"""

import os
import re
import json
import requests
from datetime import datetime, timedelta
from pathlib import Path

# 配置
GITHUB_TOKEN_PATH = Path("C:/Users/HuaWei/AppData/Local/Temp/github_token.txt")
SKILL_DIR = Path("C:/Users/HuaWei/vllm-ascend-skill/skill/references")
LEARN_DIR = SKILL_DIR / "learned-from-prs"
GIT_USER = "nanxingMy"
GIT_EMAIL = "1014662416@qq.com"

# 确保学习目录存在
LEARN_DIR.mkdir(parents=True, exist_ok=True)

class DailyPRLearner:
    """每日 PR 学习器"""
    
    def __init__(self, token):
        self.token = token
        self.headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        self.today_prs = []
    
    def get_today_merged_prs(self):
        """获取今天合入的 PR"""
        # 获取今天的时间范围
        today = datetime.now().date()
        since = datetime.combine(today, datetime.min.time()).isoformat() + 'Z'
        
        print(f"查询时间范围: {since} 至今")
        
        response = requests.get(
            'https://api.github.com/repos/vllm-project/vllm-ascend/pulls',
            headers=self.headers,
            params={
                'state': 'closed',
                'sort': 'updated',
                'direction': 'desc',
                'per_page': 100
            }
        )
        
        if response.status_code == 200:
            prs = response.json()
            
            # 过滤今天合入的 PR
            today_prs = []
            for pr in prs:
                merged_at = pr.get('merged_at')
                if merged_at:
                    merged_date = datetime.fromisoformat(merged_at.replace('Z', '+00:00'))
                    if merged_date.date() == today:
                        today_prs.append(pr)
            
            return today_prs
        return []
    
    def get_pr_files(self, pr_number):
        """获取 PR 修改的文件"""
        response = requests.get(
            f'https://api.github.com/repos/vllm-project/vllm-ascend/pulls/{pr_number}/files',
            headers=self.headers
        )
        
        if response.status_code == 200:
            return response.json()
        return []
    
    def analyze_pr(self, pr):
        """分析 PR"""
        pr_number = pr['number']
        pr_title = pr['title']
        pr_user = pr['user']['login']
        merged_at = pr['merged_at']
        
        print(f"\n学习 PR #{pr_number}: {pr_title}")
        print(f"  作者: {pr_user}")
        
        # 获取修改的文件
        files = self.get_pr_files(pr_number)
        
        print(f"  修改文件: {len(files)} 个")
        
        # 提取关键信息
        additions = sum(f.get('additions', 0) for f in files)
        deletions = sum(f.get('deletions', 0) for f in files)
        
        print(f"  添加: +{additions} 行")
        print(f"  删除: -{deletions} 行")
        
        # 保存学习结果
        learned = {
            'pr_number': pr_number,
            'pr_title': pr_title,
            'pr_user': pr_user,
            'pr_url': pr['html_url'],
            'merged_at': merged_at,
            'files': [
                {
                    'path': f.get('filename', ''),
                    'additions': f.get('additions', 0),
                    'deletions': f.get('deletions', 0)
                }
                for f in files
            ],
            'additions': additions,
            'deletions': deletions,
            'learned_at': datetime.now().isoformat()
        }
        
        self.today_prs.append(learned)
        
        return learned
    
    def learn_today_prs(self):
        """学习今天合入的 PR"""
        print(f"\n{'='*70}")
        print(f"学习今天合入的 PR - {datetime.now().strftime('%Y-%m-%d')}")
        print(f"{'='*70}\n")
        
        # 获取今天合入的 PR
        today_prs = self.get_today_merged_prs()
        
        if not today_prs:
            print("今天没有合入的 PR")
            return
        
        print(f"找到 {len(today_prs)} 个今天合入的 PR\n")
        
        # 学习每个 PR
        for pr in today_prs:
            try:
                self.analyze_pr(pr)
            except Exception as e:
                print(f"  ❌ 学习失败: {e}")
        
        print(f"\n{'='*70}")
        print(f"学习完成！共学习 {len(self.today_prs)} 个 PR")
        print(f"{'='*70}\n")
    
    def append_to_knowledge(self):
        """追加到知识库"""
        if not self.today_prs:
            print("没有新的学习内容")
            return
        
        # 读取现有数据
        data_file = LEARN_DIR / f"prs-data-{datetime.now().strftime('%Y-%m-%d')}.json"
        
        existing_prs = []
        if data_file.exists():
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                existing_prs = data.get('prs', [])
        
        # 追加新的 PR
        all_prs = existing_prs + self.today_prs
        
        # 去重
        seen = set()
        unique_prs = []
        for pr in all_prs:
            if pr['pr_number'] not in seen:
                seen.add(pr['pr_number'])
                unique_prs.append(pr)
        
        # 保存
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump({
                'date': datetime.now().strftime('%Y-%m-%d'),
                'total_prs': len(unique_prs),
                'prs': unique_prs
            }, f, indent=2, ensure_ascii=False)
        
        print(f"✅ 已追加到知识库: {data_file}")
    
    def git_commit_and_push(self):
        """提交并推送"""
        import subprocess
        
        os.chdir(SKILL_DIR.parent.parent)
        
        subprocess.run(['git', 'config', 'user.name', GIT_USER], check=True)
        subprocess.run(['git', 'config', 'user.email', GIT_EMAIL], check=True)
        subprocess.run(['git', 'add', 'skill/references/learned-from-prs/'], check=True)
        
        commit_msg = f"[Learn] Daily PR learning - {datetime.now().strftime('%Y-%m-%d')}"
        subprocess.run(['git', 'commit', '-m', commit_msg], check=True)
        subprocess.run(['git', 'push', 'origin', 'main'], check=True)

def main():
    """主函数"""
    print(f"\n{'='*70}")
    print(f"每天学习当天合入的 PR")
    print(f"{'='*70}\n")
    
    # 读取 token
    with open(GITHUB_TOKEN_PATH, 'r') as f:
        token = f.read().strip()
    
    # 创建学习器
    learner = DailyPRLearner(token)
    
    # 学习今天合入的 PR
    learner.learn_today_prs()
    
    # 追加到知识库
    learner.append_to_knowledge()
    
    # 提交推送
    if learner.today_prs:
        print("\n提交并推送...")
        learner.git_commit_and_push()
    
    print(f"\n{'='*70}")
    print("完成！")
    print(f"{'='*70}\n")

if __name__ == "__main__":
    main()
