"""
Vercel Serverless API - 获取分类列表 (Supabase 版本)
"""

import os
import psycopg2
import json

def get_db_connection():
    """获取数据库连接"""
    database_url = os.environ.get('DATABASE_URL')
    
    if not database_url:
        supabase_url = os.environ.get('SUPABASE_URL', '')
        supabase_key = os.environ.get('SUPABASE_KEY', '')
        
        if 'supabase.co' in supabase_url:
            project_id = supabase_url.replace('https://', '').replace('.supabase.co', '')
            database_url = f'postgresql://postgres:{supabase_key}@db.{project_id}.supabase.co:5432/postgres'
        else:
            raise Exception("Missing DATABASE_URL or SUPABASE_URL")
    
    return psycopg2.connect(database_url)

def handler(event, context):
    """Vercel Serverless Function handler"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 获取分类统计
        cursor.execute('''
            SELECT category, sub_category, COUNT(*) as count 
            FROM articles 
            WHERE category IS NOT NULL 
            GROUP BY category, sub_category 
            ORDER BY count DESC
        ''')
        
        rows = cursor.fetchall()
        categories = []
        for row in rows:
            categories.append({
                'name': row[0],
                'sub_category': row[1] or '',
                'count': row[2]
            })
        
        cursor.close()
        conn.close()
        
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
