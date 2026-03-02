#!/usr/bin/env python3
"""
AI摘要生成脚本 - 使用通义千问生成文章摘要
"""

import sqlite3
import os
import json
import requests
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(SCRIPT_DIR, 'xiaobo_intelligent_news.db')
API_KEY = os.environ.get('DASHSCOPE_API_KEY', 'sk-2acd33338b594d5d88bb1cc5da2bcc34')

def get_articles_without_summary(limit=10):
    """获取没有摘要的文章"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, title, content, link, category, sub_category, author, publish_date
            FROM articles 
            WHERE (summary IS NULL OR summary = '' OR summary = title)
            AND content IS NOT NULL 
            AND length(content) > 50
            ORDER BY publish_date DESC 
            LIMIT ?
        """, (limit,))
        articles = cursor.fetchall()
        conn.close()
        return articles
    except Exception as e:
        print(f"Error: {e}")
        return []

def generate_summary(title, content):
    """调用通义千问生成摘要"""
    if not content or len(content) < 50:
        return ""
    
    # 截取内容（前2000字）
    content = content[:2000]
    
    prompt = f"""请为以下文章生成一个简洁的中文摘要（50-100字），概括文章核心内容：

标题：{title}

内容：
{content}

摘要："""

    url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "qwen-turbo",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 200
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        result = response.json()
        
        if 'choices' in result and len(result['choices']) > 0:
            summary = result['choices'][0]['message']['content'].strip()
            # 清理摘要
            summary = summary.replace("摘要：", "").strip()
            return summary
        else:
            print(f"API返回异常: {result}")
            return ""
    except Exception as e:
        print(f"生成摘要失败: {e}")
        return ""

def update_summary(article_id, summary):
    """更新文章摘要"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("UPDATE articles SET summary = ? WHERE id = ?", (summary, article_id))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"更新失败: {e}")
        return False

def generate_ai_summaries(limit=10):
    """为没有摘要的文章生成AI摘要"""
    print("🤖 正在生成AI摘要...")
    
    articles = get_articles_without_summary(limit)
    
    if not articles:
        print("✅ 所有文章已有摘要")
        return
    
    print(f"📰 找到 {len(articles)} 篇需要生成摘要的文章")
    
    success_count = 0
    for i, art in enumerate(articles):
        article_id, title, content, link, category, sub_category, author, publish_date = art
        
        print(f"[{i+1}/{len(articles)}] 处理: {title[:30]}...")
        
        summary = generate_summary(title, content)
        
        if summary:
            if update_summary(article_id, summary):
                print(f"  ✅ 摘要生成成功")
                success_count += 1
            else:
                print(f"  ❌ 摘要更新失败")
        else:
            print(f"  ⚠️ 跳过（内容太短或API失败）")
    
    print(f"\n🎉 完成！成功生成 {success_count} 篇摘要")

if __name__ == '__main__':
    import sys
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    generate_ai_summaries(limit)
