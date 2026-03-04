"""
Vercel Serverless API - 获取新闻列表 (Supabase REST API 版本)

环境变量:
- SUPABASE_URL: Supabase 项目 URL
- SUPABASE_KEY: Supabase Service Role Key
"""

import os
import json
import urllib.request
import urllib.error
import urllib.parse
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # 解析 URL 和查询参数
            parsed = urlparse(self.path)
            params = parse_qs(parsed.query)
            
            page = int(params.get('page', ['1'])[0])
            limit = int(params.get('limit', ['20'])[0])
            category = params.get('category', [None])[0]
            
            # 获取 Supabase 配置
            supabase_url = os.environ.get('SUPABASE_URL')
            supabase_key = os.environ.get('SUPABASE_KEY')
            
            if not supabase_url or not supabase_key:
                raise Exception("Missing SUPABASE_URL or SUPABASE_KEY")
            
            # 构建 Supabase REST API 请求
            offset = (page - 1) * limit
            
            # 构建查询条件 - 使用正确的 Supabase REST API 格式
            if category and category != '全部':
                api_url = f"{supabase_url}/rest/v1/articles?select=*&category=eq.{urllib.parse.quote(category)}&order=publish_date.desc&limit={limit}&offset={offset}"
            else:
                api_url = f"{supabase_url}/rest/v1/articles?select=*&order=publish_date.desc&limit={limit}&offset={offset}"
            
            print(f"Requesting: {api_url[:80]}...")
            
            # 创建请求
            req = urllib.request.Request(
                api_url,
                headers={
                    'apikey': supabase_key,
                    'Authorization': f'Bearer {supabase_key}',
                    'Content-Type': 'application/json',
                    'Prefer': 'count=exact'
                }
            )
            
            # 发送请求
            with urllib.request.urlopen(req, timeout=10) as response:
                articles = json.loads(response.read().decode('utf-8'))
                
                # 获取总数（从 Content-Range header）
                content_range = response.headers.get('Content-Range', '')
                total = int(content_range.split('/')[-1]) if '/' in content_range else len(articles)
            
            # 获取总数（从 Content-Range header 或单独查询）
            # 简单处理：如果没有 header，就返回当前数量
            if total == 0 and len(articles) > 0:
                total = len(articles)  # 临时处理
            
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
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, apikey, Authorization')
        self.end_headers()
