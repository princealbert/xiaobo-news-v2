"""
Vercel Serverless API - 获取新闻列表 (Supabase 版本)

环境变量:
- SUPABASE_URL: Supabase 项目 URL
- SUPABASE_KEY: Supabase Service Role Key
- DATABASE_URL: PostgreSQL 直连 URL
"""

import os
import psycopg2
import json
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from datetime import datetime

def get_db_connection():
    """获取数据库连接（使用 Supabase 连接池）"""
    supabase_url = os.environ.get('SUPABASE_URL', '')
    supabase_key = os.environ.get('SUPABASE_KEY', '')
    
    if not supabase_url or not supabase_key:
        raise Exception("Missing SUPABASE_URL or SUPABASE_KEY")
    
    # 从 SUPABASE_URL 提取项目 ID
    if 'supabase.co' in supabase_url:
        project_id = supabase_url.replace('https://', '').replace('.supabase.co', '')
        # 使用 Supabase 连接池 (pgbouncer) - 端口 6543
        database_url = f'postgresql://postgres.{project_id}:{supabase_key}@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres?sslmode=require'
    else:
        raise Exception("Invalid SUPABASE_URL")
    
    print(f"Connecting to Supabase pooler...")
    return psycopg2.connect(database_url)

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # 记录请求信息
            print(f"Request path: {self.path}")
            print(f"Environment variables: DATABASE_URL={os.environ.get('DATABASE_URL', 'NOT SET')[:20]}...")
            
            # 解析 URL 和查询参数
            parsed = urlparse(self.path)
            params = parse_qs(parsed.query)
            
            page = int(params.get('page', ['1'])[0])
            limit = int(params.get('limit', ['20'])[0])
            category = params.get('category', [None])[0]
            
            print(f"Query params: page={page}, limit={limit}, category={category}")
            
            # 计算偏移量
            offset = (page - 1) * limit
            
            # 连接数据库
            print("Connecting to database...")
            conn = get_db_connection()
            cursor = conn.cursor()
            print("Database connected successfully")
            
            # 构建查询
            base_query = "SELECT * FROM articles WHERE 1=1"
            count_query = "SELECT COUNT(*) FROM articles WHERE 1=1"
            query_params = []
            
            if category and category != '全部':
                base_query += " AND category = %s"
                count_query += " AND category = %s"
                query_params.append(category)
            
            # 获取总数
            cursor.execute(count_query, query_params)
            total = cursor.fetchone()[0]
            
            # 获取文章
            base_query += " ORDER BY publish_date DESC LIMIT %s OFFSET %s"
            query_params.extend([limit, offset])
            cursor.execute(base_query, query_params)
            
            rows = cursor.fetchall()
            columns = ['id', 'title', 'link', 'summary', 'content', 'category', 'sub_category', 
                       'author', 'publish_date', 'image_url', 'view_count', 'tags', 'ai_tags', 'level2']
            
            articles = []
            for row in rows:
                article = dict(zip(columns, row))
                if article.get('publish_date'):
                    article['publish_date'] = article['publish_date'].isoformat() if hasattr(article['publish_date'], 'isoformat') else str(article['publish_date'])
                articles.append(article)
            
            cursor.close()
            conn.close()
            
            # 返回响应
            response_data = {
                'data': articles,
                'total': total,
                'page': page,
                'limit': limit
            }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response_data, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Error: {error_details}")
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            error_response = {
                'error': str(e),
                'details': error_details
            }
            self.wfile.write(json.dumps(error_response, ensure_ascii=False).encode('utf-8'))
    
    def do_OPTIONS(self):
        """处理 CORS preflight 请求"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
