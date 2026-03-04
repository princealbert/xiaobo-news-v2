"""
Vercel Serverless API - 获取新闻列表 (Supabase 版本)

环境变量:
- SUPABASE_URL: Supabase 项目 URL
- SUPABASE_KEY: Supabase Service Role Key
"""

import os
import psycopg2
import json
from datetime import datetime

def get_db_connection():
    """获取数据库连接（使用 psycopg2 直连）"""
    # 优先使用 DATABASE_URL，否则从 SUPABASE_URL 构建
    database_url = os.environ.get('DATABASE_URL')
    
    if not database_url:
        supabase_url = os.environ.get('SUPABASE_URL', '')
        supabase_key = os.environ.get('SUPABASE_KEY', '')
        
        # 从 SUPABASE_URL 提取项目 ID
        if 'supabase.co' in supabase_url:
            project_id = supabase_url.replace('https://', '').replace('.supabase.co', '')
            database_url = f'postgresql://postgres:{supabase_key}@db.{project_id}.supabase.co:5432/postgres'
        else:
            raise Exception("Missing DATABASE_URL or SUPABASE_URL")
    
    return psycopg2.connect(database_url)

def handler(event, context):
    """Vercel Serverless Function handler"""
    try:
        # 解析查询参数
        query_params = event.get('queryStringParameters', {}) or {}
        page = int(query_params.get('page', '1'))
        limit = int(query_params.get('limit', '20'))
        category = query_params.get('category', None)
        
        # 计算偏移量
        offset = (page - 1) * limit
        
        # 连接数据库
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 构建查询
        base_query = "SELECT * FROM articles WHERE 1=1"
        count_query = "SELECT COUNT(*) FROM articles WHERE 1=1"
        params = []
        
        if category and category != '全部':
            base_query += " AND category = %s"
            count_query += " AND category = %s"
            params.append(category)
        
        # 获取总数
        cursor.execute(count_query, params)
        total = cursor.fetchone()[0]
        
        # 获取文章
        base_query += " ORDER BY publish_date DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        cursor.execute(base_query, params)
        
        rows = cursor.fetchall()
        columns = ['id', 'title', 'link', 'summary', 'content', 'category', 'sub_category', 
                   'author', 'publish_date', 'image_url', 'view_count', 'tags', 'ai_tags', 'level2']
        
        articles = []
        for row in rows:
            article = dict(zip(columns, row))
            # 转换日期格式
            if article.get('publish_date'):
                article['publish_date'] = article['publish_date'].isoformat() if hasattr(article['publish_date'], 'isoformat') else str(article['publish_date'])
            articles.append(article)
        
        cursor.close()
        conn.close()
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'data': articles,
                'total': total,
                'page': page,
                'limit': limit
            }, ensure_ascii=False)
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }
