"""
Vercel Serverless API - 获取新闻列表
"""

import sqlite3
import json
import os
from datetime import datetime

DB_PATH = os.environ.get('DB_PATH', '/Users/albert/documents/茉莉空间/xiaobo_intelligent_news_site/xiaobo_intelligent_news.db')

def get_articles_from_db(limit=50, page=1, category=None, offset=0):
    """从数据库获取文章"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 基础查询
        query = "SELECT * FROM articles WHERE 1=1"
        params = []
        
        if category and category != '全部':
            query += " AND category = ?"
            params.append(category)
        
        # 获取总数
        count_query = query.replace("SELECT *", "SELECT COUNT(*)")
        cursor.execute(count_query, params)
        total = cursor.fetchone()[0]
        
        # 分页
        query += " ORDER BY publish_date DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        articles = []
        for row in rows:
            article = dict(row)
            # 格式化日期
            if article.get('publish_date'):
                try:
                    dt = datetime.strptime(str(article['publish_date'])[:19], "%Y-%m-%d %H:%M:%S")
                    article['publish_date'] = dt.strftime("%Y-%m-%d %H:%M:%S")
                except:
                    pass
            articles.append(article)
        
        conn.close()
        return {"data": articles, "total": total, "page": page, "limit": limit}
    
    except Exception as e:
        return {"error": str(e), "data": [], "total": 0}

def handler(req):
    """Vercel Serverless Function handler"""
    from urllib.parse import urlparse, parse_qs
    
    # 解析查询参数
    query_params = req.get('query', {})
    
    page = int(query_params.get('page', ['1'])[0])
    limit = int(query_params.get('limit', ['50'])[0])
    category = query_params.get('category', [None])[0]
    
    offset = (page - 1) * limit
    
    result = get_articles_from_db(limit=limit, page=page, category=category, offset=offset)
    
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps(result, ensure_ascii=False)
    }