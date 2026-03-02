"""
Vercel Serverless API - 获取分类列表 (Supabase 版本)
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
        # 连接 Supabase
        supabase = get_supabase_client()
        
        # 调用数据库视图获取分类统计
        response = supabase.rpc('category_stats').execute()
        
        # 格式化结果
        categories = []
        if response.data:
            for row in response.data:
                categories.append({
                    'name': row.get('category', ''),
                    'sub_category': row.get('sub_category', ''),
                    'count': row.get('count', 0)
                })
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'data': categories
            }, ensure_ascii=False)
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }
