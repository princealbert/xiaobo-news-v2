#!/usr/bin/env python3
"""从旧站 SQLite 数据库迁移文章到新站"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
import re
from email.utils import parsedate_to_datetime

OLD_DB = Path(__file__).parent.parent.parent / "xiaobo_intelligent_news_site/news.db"
OUTPUT_FILE = Path(__file__).parent.parent / "src/data/articles.json"

def migrate():
    if not OLD_DB.exists():
        print(f"❌ 旧数据库不存在：{OLD_DB}")
        return False
    
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(OLD_DB)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, title, content, category, author, publish_date, image_url, summary
        FROM articles 
        ORDER BY publish_date DESC 
        LIMIT 50
    """)
    
    articles = cursor.fetchall()
    print(f"✅ 找到 {len(articles)} 篇文章")
    
    migrated = []
    for i, article in enumerate(articles):
        try:
            migrated_article = convert_article(article, i)
            migrated.append(migrated_article)
            if i < 10:
                print(f"  ✓ {i + 1}. {article['title'][:50]}...")
        except Exception as e:
            print(f"  ⚠️  跳过文章 {i + 1}: {e}")
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump({
            "migrated_at": datetime.now().isoformat(),
            "total": len(migrated),
            "articles": migrated
        }, f, ensure_ascii=False, indent=2)
    
    conn.close()
    print(f"✅ 迁移完成！输出：{OUTPUT_FILE}")
    print(f"✅ 总计：{len(migrated)} 篇文章")
    return True

def convert_article(article, index):
    # 解析日期
    pub_date = parse_date(article['publish_date']) if article['publish_date'] else datetime.now()
    slug = generate_slug(article['title'])
    
    return {
        "id": article['id'],
        "title": article['title'],
        "content": article['content'],
        "summary": article['summary'] or article['title'][:200] + '...',
        "category": article['category'] or '未分类',
        "tags": [],
        "author": article['author'] or '晓波',
        "pubDate": pub_date.isoformat(),
        "slug": f"/article/{slug}",
        "imageUrl": article['image_url'],
        "views": 0
    }

def parse_date(date_str):
    """解析多种日期格式"""
    try:
        # 尝试 RFC 822 格式
        return parsedate_to_datetime(date_str)
    except:
        try:
            # 尝试 ISO 格式
            return datetime.fromisoformat(date_str)
        except:
            # 默认返回当前时间
            return datetime.now()

def generate_slug(title):
    slug = title.lower()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug[:80]

if __name__ == "__main__":
    migrate()
