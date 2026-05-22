#!/usr/bin/env python3
"""
Daily learning script - learns PRs merged today

Usage:
    python learn_daily_prs.py

This script is meant to be run daily via cron job.
"""

import os
import json
import requests
from datetime import datetime, timedelta
from pathlib import Path

# Configuration
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
REPO_OWNER = 'vllm-project'
REPO_NAME = 'vllm-ascend'
OUTPUT_DIR = Path('skill/references/learned-from-prs')

def get_github_token():
    """Get GitHub token"""
    if GITHUB_TOKEN:
        return GITHUB_TOKEN
    
    token_file = Path('C:/Users/HuaWei/AppData/Local/Temp/github_token.txt')
    if token_file.exists():
        return token_file.read_text().strip()
    
    raise ValueError("GitHub token not found")

def get_todays_merged_prs():
    """Get PRs merged today"""
    token = get_github_token()
    
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    # Get PRs merged in last 24 hours
    since = (datetime.now() - timedelta(days=1)).isoformat()
    
    response = requests.get(
        f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/pulls',
        headers=headers,
        params={
            'state': 'closed',
            'sort': 'updated',
            'direction': 'desc',
            'per_page': 100
        },
        timeout=30
    )
    
    if response.status_code != 200:
        return []
    
    prs = response.json()
    
    # Filter to today's merged PRs
    today = datetime.now().date()
    todays_prs = []
    
    for pr in prs:
        if not pr.get('merged_at'):
            continue
        
        merged_date = datetime.fromisoformat(pr['merged_at'].replace('Z', '+00:00'))
        if merged_date.date() == today:
            todays_prs.append(pr)
    
    return todays_prs

def main():
    """Learn from today's merged PRs"""
    print(f"\n{'='*70}")
    print(f"每日学习 - {datetime.now().strftime('%Y-%m-%d')}")
    print(f"{'='*70}\n")
    
    prs = get_todays_merged_prs()
    
    if not prs:
        print("今天没有新合入的 PR")
        return
    
    print(f"找到 {len(prs)} 个今天合入的 PR")
    
    # Import main learning function
    from learn_all_prs import learn_from_pr, save_results
    
    prs_learned = []
    for pr in prs:
        try:
            learned = learn_from_pr(pr)
            prs_learned.append(learned)
        except Exception as e:
            print(f"学习 PR #{pr['number']} 失败: {e}")
    
    if prs_learned:
        # Read existing total
        date_str = datetime.now().strftime('%Y-%m-%d')
        data_file = OUTPUT_DIR / f"prs-data-{date_str}.json"
        
        total_prs = len(prs_learned)
        if data_file.exists():
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                total_prs = data.get('total_prs', 0) + len(prs_learned)
        
        save_results(prs_learned, total_prs)
        print(f"\n✅ 学习完成！新增 {len(prs_learned)} 个 PR")

if __name__ == '__main__':
    main()
