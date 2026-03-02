"""
Vercel Serverless API - 获取分类列表
"""

import sqlite3
import json
import os

DB_PATH = os.environ.get('DB_PATH', '/Users/albert/documents/茉莉空间/xiaobo_intelligent_news_site/xiaobo_intelligent_news.db')

def get_categories_from_db():
    """从数据库获取分类统计"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 按一级分类统计
        cursor.execute("""
            SELECT category, COUNT(*) as count 
            FROM articles 
            WHERE category IS NOT NULL AND category != ''
            GROUP BY category 
            ORDER BY count DESC
        """)
        
        categories = []
        for row in cursor.fetchall():
            categories.append({
                "name": row[0],
                "count": row[1]
            })
        
        conn.close()
        return {"data": categories}
    
    except Exception as e:
        return {"error": str(e), "data": []}

def handler(req):
    """Vercel Serverless Function handler"""
    result = get_categories_from_db()
    
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps(result, ensure_ascii=False)
    }