#!/usr/bin/env python3
"""
修复版 Supabase 同步 - 包含 image_url 和正确的日期格式
"""
import sqlite3
import os
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv('/Users/albert/documents/茉莉空间/xiaobo_intelligent_news_site/.env')

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
LOCAL_DB = '/Users/albert/documents/茉莉空间/xiaobo-news-v2/news.db'

def format_date(date_str):
    """格式化日期为 ISO 格式"""
    if not date_str:
        return datetime.now().isoformat()
    
    # 尝试多种格式
    formats = [
        '%a, %d %b %Y %H:%M:%S %Z',
        '%a, %d %b %Y %H:%M:%S %z',
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%d',
    ]
    
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.isoformat()
        except:
            continue
    
    # 如果都失败，返回原始值
    return date_str

def sync_to_supabase():
    """同步到 Supabase"""
    print("📊 同步本地数据库到 Supabase (修复版)")
    print("="*60)
    
    # 连接本地数据库
    conn = sqlite3.connect(LOCAL_DB)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # 获取本地文章（包含 image_url）
    cursor.execute('''
        SELECT id, title, link, summary, category, author, publish_date, image_url, created_at
        FROM articles
        WHERE image_url IS NOT NULL AND image_url != ''
        ORDER BY publish_date DESC
        LIMIT 200
    ''')
    local_articles = [dict(row) for row in cursor.fetchall()]
    
    print(f"\n📄 本地有图片的文章：{len(local_articles)} 篇")
    
    # Supabase API
    url = f"{SUPABASE_URL}/rest/v1/articles"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates"
    }
    
    success = 0
    error = 0
    
    print("\n📤 开始同步...")
    for i, article in enumerate(local_articles, 1):
        # 准备数据（包含 image_url）
        data = {
            "title": article.get('title', ''),
            "link": article.get('link', ''),
            "summary": article.get('summary', ''),
            "category": article.get('category', ''),
            "author": article.get('author', ''),
            "publish_date": format_date(article.get('publish_date')),
            "image_url": article.get('image_url', '')
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=10)
        
        if response.status_code in [200, 201, 409]:
            success += 1
            if success <= 5:
                print(f"   ✅ {article['title'][:40]}...")
        else:
            error += 1
            if error <= 3:
                print(f"   ❌ 错误：{response.text[:100]}")
        
        if i % 20 == 0:
            print(f"   已同步 {i}/{len(local_articles)} 篇...")
    
    conn.close()
    
    print("\n" + "="*60)
    print(f"✅ 同步完成")
    print(f"   成功：{success} 篇")
    print(f"   失败：{error} 篇")

if __name__ == "__main__":
    sync_to_supabase()
