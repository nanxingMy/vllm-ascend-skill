#!/usr/bin/env python3
"""
Learn from all merged PRs in a repository

Usage:
    python learn_all_prs.py

Features:
    - Learns from merged PRs in batches of 50
    - Skips already-learned PRs
    - Categorizes PRs (Bug Fix, Feature, Performance, etc.)
    - Extracts patterns and techniques
    - Saves to JSON and Markdown
    - Commits and pushes to repository
"""

import os
import re
import json
import requests
import subprocess
import time
from datetime import datetime
from pathlib import Path

# Configuration
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
REPO_OWNER = 'vllm-project'
REPO_NAME = 'vllm-ascend'
OUTPUT_DIR = Path('skill/references/learned-from-prs')
MAX_PRS_PER_RUN = 50  # Learn 50 PRs per batch

def get_github_token():
    """Get GitHub token from environment or file"""
    if GITHUB_TOKEN:
        return GITHUB_TOKEN
    
    # Try reading from file
    token_file = Path('C:/Users/HuaWei/AppData/Local/Temp/github_token.txt')
    if token_file.exists():
        return token_file.read_text().strip()
    
    raise ValueError("GitHub token not found")

def get_merged_prs(page=1, per_page=100):
    """Get merged PRs from GitHub API with retry"""
    token = get_github_token()
    
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    max_retries = 5
    for retry in range(max_retries):
        try:
            response = requests.get(
                f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/pulls',
                headers=headers,
                params={
                    'state': 'closed',
                    'sort': 'updated',
                    'direction': 'desc',
                    'page': page,
                    'per_page': per_page
                },
                timeout=30
            )
            
            if response.status_code == 200:
                prs = response.json()
                # Filter merged PRs
                merged_prs = [pr for pr in prs if pr.get('merged_at')]
                return merged_prs
            return []
        except Exception as e:
            if retry < max_retries - 1:
                print(f"  ⚠️ 网络错误，等待 10s 后重试... ({retry + 1}/{max_retries})")
                time.sleep(10)
            else:
                print(f"  ❌ 网络错误，已达到最大重试次数: {e}")
                return []

def categorize_pr(pr_title, files):
    """Categorize PR based on title and files"""
    title_lower = pr_title.lower()
    
    categories = []
    
    # Bug Fix
    if any(kw in title_lower for kw in ['fix', 'bugfix', 'bug', 'error', 'issue', 'resolve', 'patch']):
        categories.append('Bug Fix')
    
    # Feature
    if any(kw in title_lower for kw in ['feat', 'feature', 'add', 'support', 'implement', 'enable']):
        categories.append('Feature')
    
    # Performance
    if any(kw in title_lower for kw in ['perf', 'performance', 'optimize', 'speed', 'memory']):
        categories.append('Performance')
    
    # Refactor
    if any(kw in title_lower for kw in ['refactor', 'restructure', 'clean', 'simplify']):
        categories.append('Refactor')
    
    # Documentation
    if any(kw in title_lower for kw in ['doc', 'docs', 'document', 'readme', 'comment']):
        categories.append('Documentation')
    
    # Test
    if any(kw in title_lower for kw in ['test', 'tests', 'ut', 'e2e', 'nightly']):
        categories.append('Test')
    
    # Other
    if any(kw in title_lower for kw in ['ci', 'lint', 'build', 'deps', 'dependabot']):
        categories.append('Other')
    
    if not categories:
        categories.append('Other')
    
    return categories

def extract_issue_number(pr):
    """Extract issue number from PR"""
    body = pr.get('body', '') or ''
    
    # Look for "Fixes #123" or "Closes #123" patterns
    match = re.search(r'(?:fixes|closes|resolves)\s+#(\d+)', body, re.IGNORECASE)
    if match:
        return int(match.group(1))
    
    return None

def learn_from_pr(pr):
    """Learn from a single PR"""
    print(f"\n学习 PR #{pr['number']}: {pr['title']}")
    print(f"  作者: {pr['user']['login']}")
    print(f"  合入时间: {pr['merged_at']}")
    
    # Extract issue
    issue_number = extract_issue_number(pr)
    if issue_number:
        print(f"  对应 Issue: #{issue_number}")
    
    # Get files changed
    token = get_github_token()
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    files_response = requests.get(
        f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/pulls/{pr['number']}/files",
        headers=headers,
        timeout=30
    )
    
    files = files_response.json() if files_response.status_code == 200 else []
    
    # Calculate stats
    lines_added = sum(f.get('additions', 0) for f in files)
    lines_deleted = sum(f.get('deletions', 0) for f in files)
    
    print(f"  分析解决方案...")
    print(f"    修改文件: {len(files)} 个")
    print(f"    添加代码: +{lines_added} 行")
    print(f"    删除代码: -{lines_deleted} 行")
    
    # Categorize
    categories = categorize_pr(pr['title'], files)
    print(f"  分类: {', '.join(categories)}")
    
    return {
        'pr_number': pr['number'],
        'title': pr['title'],
        'author': pr['user']['login'],
        'merged_at': pr['merged_at'],
        'issue_number': issue_number,
        'files_modified': len(files),
        'lines_added': lines_added,
        'lines_deleted': lines_deleted,
        'categories': categories,
        'url': pr['html_url']
    }

def save_results(prs_learned, total_prs):
    """Save learning results"""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    date_str = datetime.now().strftime('%Y-%m-%d')
    
    # Save raw data
    data_file = OUTPUT_DIR / f"prs-data-{date_str}.json"
    
    # Read existing data
    existing_data = {'date': date_str, 'total_prs': 0, 'prs': []}
    if data_file.exists():
        with open(data_file, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
    
    # Append new PRs
    existing_data['prs'].extend(prs_learned)
    existing_data['total_prs'] = total_prs
    
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(existing_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ 原始数据已保存: {data_file}")
    print(f"   总计 {total_prs} 个 PR")
    
    # Save summary
    summary_file = OUTPUT_DIR / f"summary-{date_str}.md"
    
    # Calculate stats
    stats = {
        'Bug Fix': 0,
        'Feature': 0,
        'Performance': 0,
        'Refactor': 0,
        'Documentation': 0,
        'Test': 0,
        'Other': 0
    }
    
    for pr in existing_data['prs']:
        for cat in pr['categories']:
            if cat in stats:
                stats[cat] += 1
    
    summary = f"""# PR Learning Summary - {date_str}

## Statistics

- Total PRs learned: {total_prs}

### By Category

"""
    for cat, count in stats.items():
        summary += f"- {cat}: {count}\n"
    
    summary += f"""

## Latest PRs

"""
    for pr in prs_learned[:10]:  # Show last 10
        summary += f"- #{pr['pr_number']}: {pr['title']}\n"
    
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write(summary)
    
    print(f"✅ 总结文档已保存: {summary_file}")

def git_commit_and_push():
    """Commit and push results with infinite retry"""
    subprocess.run(['git', 'add', '.'], check=True)
    subprocess.run(['git', 'commit', '-m', f'[Learn] Learn from all merged PRs - {datetime.now().strftime("%Y-%m-%d")}'], check=True)
    
    # Push with infinite retry
    retry_count = 0
    while True:
        try:
            subprocess.run(['git', 'push', 'origin', 'main'], check=True)
            return True
        except Exception as e:
            retry_count += 1
            if retry_count <= 5:
                wait_time = 10
            else:
                wait_time = 60  # After 5 retries, wait 1 minute
            print(f"  ⚠️ 推送失败，等待 {wait_time}s 后重试... (重试 #{retry_count})")
            time.sleep(wait_time)

def main():
    """Main learning loop"""
    print(f"\n{'='*70}")
    print(f"学习所有已合入的 PR")
    print(f"{'='*70}\n")
    
    # Read already learned PRs
    learned_pr_numbers = set()
    date_str = datetime.now().strftime('%Y-%m-%d')
    data_file = OUTPUT_DIR / f"prs-data-{date_str}.json"
    
    if data_file.exists():
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for pr in data.get('prs', []):
                learned_pr_numbers.add(pr['pr_number'])
        print(f"已学习 {len(learned_pr_numbers)} 个 PR，将跳过\n")
    
    page = 1
    total_learned = 0
    prs_learned = []
    
    while True:
        print(f"获取第 {page} 页 PR...")
        prs = get_merged_prs(page=page)
        
        if not prs:
            print("没有更多 PR")
            break
        
        for pr in prs:
            if total_learned >= MAX_PRS_PER_RUN:
                print(f"\n已达到最大学习数量: {MAX_PRS_PER_RUN}")
                break
            
            # Skip already learned
            if pr['number'] in learned_pr_numbers:
                continue
            
            try:
                learned = learn_from_pr(pr)
                prs_learned.append(learned)
                total_learned += 1
            except Exception as e:
                print(f"  ❌ 学习失败: {e}")
        
        if total_learned >= MAX_PRS_PER_RUN:
            break
        
        page += 1
        time.sleep(1)  # Rate limiting
    
    if prs_learned:
        total_prs = len(learned_pr_numbers) + total_learned
        save_results(prs_learned, total_prs)
        
        print(f"\n提交并推送...")
        try:
            git_commit_and_push()
            print(f"\n{'='*70}")
            print(f"全部完成！")
            print(f"{'='*70}")
        except Exception as e:
            print(f"推送失败: {e}")
    else:
        print("\n没有新的 PR 需要学习")

if __name__ == '__main__':
    main()
