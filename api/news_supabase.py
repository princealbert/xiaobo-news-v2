"""
Vercel Serverless API - 获取新闻列表 (Supabase 版本)

环境变量:
- SUPABASE_URL: Supabase 项目 URL
- SUPABASE_KEY: Supabase Service Role Key
"""

import os
from supabase import create_client, Client
import json

def get_supabase_client():
    """获取 Supabase 客户端"""
    supabase_url = os.environ.get('SUPABASE_URL')
    supabase_key = os.environ.get('SUPABASE_KEY')
    
    if not supabase_url or not supabase_key:
        raise Exception("Missing SUPABASE_URL or SUPABASE_KEY environment variables")
    
    return create_client(supabase_url, supabase_key)

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
        
        # 连接 Supabase
        supabase = get_supabase_client()
        
        # 构建查询
        query = supabase.table('articles').select('*', count='exact')
        
        if category and category != '全部':
            query = query.eq('category', category)
        
        # 执行查询
        query = query.order('publish_date', desc=True).range(offset, offset + limit - 1)
        response = query.execute()
        
        # 格式化结果
        articles = []
        for row in response.data:
            article = {
                'id': row.get('id'),
                'title': row.get('title', ''),
                'link': row.get('link', ''),
                'summary': row.get('summary', ''),
                'category': row.get('category', ''),
                'sub_category': row.get('sub_category', ''),
                'author': row.get('author', ''),
                'publish_date': row.get('publish_date', ''),
                'image_url': row.get('image_url', ''),
                'view_count': row.get('view_count', 0),
                'tags': row.get('tags', ''),
                'ai_tags': row.get('ai_tags', ''),
                'level2': row.get('level2', '')
            }
            articles.append(article)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'data': articles,
                'total': response.count,
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
