#!/usr/bin/env python3
"""
晓波智能资讯站 - 静态服务器 + API 支持 + Markdown渲染 + 移动端首页
"""

import http.server
import socketserver
import sqlite3
import json
import os
import markdown
from datetime import datetime, timedelta

PORT = 9000
DIRECTORY = "/Users/albert/documents/茉莉空间/xiaobo_intelligent_news_site"
DB_PATH = "/Users/albert/documents/茉莉空间/xiaobo_intelligent_news_site/xiaobo_intelligent_news.db"


def format_date(date_str):
    """格式化日期显示"""
    if not date_str:
        return ""
    from datetime import datetime
    try:
        # 尝试多种日期格式
        formats = [
            "%Y-%m-%d %H:%M:%S.%f",
            "%Y-%m-%d %H:%M:%S",
            "%a, %d %b %Y %H:%M:%S %Z",
            "%a, %d %b %Y %H:%M:%S %z",
            "%d %b %Y %H:%M:%S %z",
        ]
        for fmt in formats:
            try:
                dt = datetime.strptime(str(date_str).replace(" +0000", " +0000").replace(" GMT", " +0000"), fmt.replace(" %Z", " %z"))
                return dt.strftime("%Y年%m月%d日 %H:%M")
            except:
                continue
        return str(date_str)[:16]
    except:
        return str(date_str)[:16]


def is_mobile_user_agent(self):
    """检测是否为移动端用户"""
    user_agent = self.headers.get('User-Agent', '').lower()
    mobile_keywords = ['iphone', 'ipad', 'android', 'mobile', 'wap', 'smarttv', 'hbbtv', 'appletv', 'ipod']
    return any(keyword in user_agent for keyword in mobile_keywords)


def generate_mobile_index_html(articles, categories):
    """生成移动端首页HTML - 参考36kr移动端设计"""
    # 分类列表
    category_map = {
        'all': '全部',
        'AI科技': 'AI前沿',
        '科技产业': '科技产业',
        '智能金融速递': '金融',
        '优质RSS源': '创投',
        '今日重大事件': '要闻'
    }
    
    # 分类标签HTML
    category_tabs = ''.join([
        f'<div class="category-item {"active" if cat == "all" else ""}" data-category="{cat}">{name}</div>'
        for cat, name in category_map.items()
    ])
    
    # 热点文章（取前5篇）
    hot_articles = articles[:5]
    hot_list_html = ''.join([
        f'''<div class="hot-item" onclick="window.open('{a.get("link", "#")}', '_blank')">
            <div class="hot-rank top3">{i+1}</div>
            <div class="hot-content">
                <div class="hot-title">{a.get('title', '')}</div>
                <div class="hot-meta">
                    <span>{a.get('author', '未知')}</span>
                    <span>•</span>
                    <span>{a.get('publish_date', '')}</span>
                </div>
            </div>
        </div>''' for i, a in enumerate(hot_articles)
    ])
    
    # 资讯流HTML
    feed_list_html = ''.join([
        f'''<div class="feed-card" onclick="window.open('{a.get("link", "#")}', '_blank')">
            <div class="feed-card-img no-image"><i class="fas fa-newspaper"></i></div>
            <div class="feed-card-content">
                <div class="feed-card-title">{a.get('title', '')}</div>
                <div class="feed-card-meta">
                    <span class="feed-card-tag">{a.get('category', '')}</span>
                    <span>{a.get('author', '未知')}</span>
                    <span>{a.get('publish_date', '')}</span>
                </div>
            </div>
        </div>''' for a in articles
    ])
    
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>晓波智能资讯站 | AI科技金融前沿</title>
    <meta name="description" content="每日更新 AI 科技、股票投资、金融资讯">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {{
            --primary: #1890FF;
            --primary-dark: #096dd9;
            --primary-light: #40a9ff;
            --accent: #1890FF;
            --bg: #F5F5F5;
            --card-bg: #FFFFFF;
            --text: #1F1F1F;
            --text-secondary: #8C8C8C;
            --text-tertiary: #BFBFBF;
            --border: #E8E8E8;
            --divider: #F0F0F0;
            --radius: 12px;
            --radius-sm: 8px;
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; -webkit-tap-highlight-color: transparent; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', 'SF Pro Text', 'Microsoft YaHei', sans-serif; background: var(--bg); color: var(--text); line-height: 1.5; padding-bottom: 70px; }}
        
        /* 顶部搜索栏 */
        .header {{ position: sticky; top: 0; z-index: 100; background: linear-gradient(135deg, #1890FF 0%, #096dd9 100%); padding: 12px 16px; padding-top: max(12px, env(safe-area-inset-top)); }}
        .header-content {{ display: flex; align-items: center; gap: 12px; }}
        .logo {{ width: 40px; height: 40px; border-radius: 10px; overflow: hidden; flex-shrink: 0; background: #fff; }}
        .logo img {{ width: 100%; height: 100%; object-fit: contain; }}
        .search-bar {{ flex: 1; background: rgba(255,255,255,0.95); border-radius: 20px; padding: 10px 16px; display: flex; align-items: center; gap: 8px; color: var(--text-secondary); font-size: 14px; }}
        
        /* 分类导航 */
        .category-nav {{ background: var(--card-bg); position: sticky; top: 60px; z-index: 99; border-bottom: 1px solid var(--divider); }}
        .category-scroll {{ display: flex; overflow-x: auto; padding: 0 12px; -webkit-overflow-scrolling: touch; scrollbar-width: none; }}
        .category-scroll::-webkit-scrollbar {{ display: none; }}
        .category-item {{ flex-shrink: 0; padding: 12px 16px; font-size: 14px; color: var(--text-secondary); cursor: pointer; position: relative; white-space: nowrap; }}
        .category-item.active {{ color: var(--primary); font-weight: 600; }}
        .category-item.active::after {{ content: ''; position: absolute; bottom: 0; left: 50%; transform: translateX(-50%); width: 20px; height: 3px; background: var(--primary); border-radius: 2px; }}
        
        /* 轮播图 */
        .banner {{ margin: 12px; border-radius: var(--radius); overflow: hidden; position: relative; height: 180px; }}
        .banner-slide {{ position: absolute; inset: 0; background-size: cover; background-position: center; opacity: 0; transition: opacity 0.5s; }}
        .banner-slide.active {{ opacity: 1; }}
        .banner-content {{ position: absolute; bottom: 0; left: 0; right: 0; padding: 40px 16px 16px; background: linear-gradient(transparent, rgba(0,0,0,0.7)); color: #fff; }}
        .banner-title {{ font-size: 18px; font-weight: 600; line-height: 1.4; }}
        .banner-dots {{ position: absolute; bottom: 12px; right: 12px; display: flex; gap: 6px; }}
        .banner-dot {{ width: 6px; height: 6px; border-radius: 3px; background: rgba(255,255,255,0.5); }}
        .banner-dot.active {{ width: 16px; background: #fff; }}
        
        /* 区块 */
        .section {{ background: var(--card-bg); margin-bottom: 12px; }}
        .section-header {{ display: flex; align-items: center; justify-content: space-between; padding: 16px; border-bottom: 1px solid var(--divider); }}
        .section-title {{ display: flex; align-items: center; gap: 8px; font-size: 16px; font-weight: 600; }}
        .section-title i {{ color: var(--primary); }}
        
        /* 热点 */
        .hot-list {{ padding: 12px 16px; }}
        .hot-item {{ display: flex; align-items: flex-start; padding: 12px 0; border-bottom: 1px solid var(--divider); cursor: pointer; }}
        .hot-item:active {{ background: #fafafa; }}
        .hot-item:last-child {{ border-bottom: none; }}
        .hot-rank {{ width: 24px; height: 24px; border-radius: 6px; display: flex; align-items: center; justify-content: center; font-size: 13px; font-weight: 700; margin-right: 12px; flex-shrink: 0; background: linear-gradient(135deg, #FF4D4F, #FF7A45); color: #fff; }}
        .hot-rank.other {{ background: var(--divider); color: var(--text-tertiary); }}
        .hot-content {{ flex: 1; min-width: 0; }}
        .hot-title {{ font-size: 15px; font-weight: 500; line-height: 1.4; }}
        .hot-meta {{ display: flex; align-items: center; gap: 8px; margin-top: 6px; font-size: 12px; color: var(--text-tertiary); }}
        
        /* 资讯流 */
        .feed-card {{ display: flex; padding: 16px; background: var(--card-bg); border-bottom: 1px solid var(--divider); gap: 12px; cursor: pointer; }}
        .feed-card:active {{ background: #fafafa; }}
        .feed-card-img {{ width: 100px; height: 75px; border-radius: var(--radius-sm); background-size: cover; background-position: center; flex-shrink: 0; display: flex; align-items: center; justify-content: center; color: #fff; font-size: 24px; }}
        .feed-card-img.no-image {{ background: linear-gradient(135deg, #1890FF, #096dd9); }}
        .feed-card-img.no-image i {{ opacity: 0.8; }}
        .feed-card-content {{ flex: 1; min-width: 0; display: flex; flex-direction: column; justify-content: space-between; }}
        .feed-card-title {{ font-size: 15px; font-weight: 500; line-height: 1.4; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }}
        .feed-card-meta {{ display: flex; align-items: center; gap: 8px; font-size: 12px; color: var(--text-tertiary); margin-top: 8px; }}
        .feed-card-tag {{ color: var(--primary); font-weight: 500; }}
        
        /* 底部Tab */
        .tab-bar {{ position: fixed; bottom: 0; left: 0; right: 0; background: var(--card-bg); border-top: 1px solid var(--divider); display: flex; padding: 8px 0; padding-bottom: max(8px, env(safe-area-inset-bottom)); z-index: 100; }}
        .tab-item {{ flex: 1; display: flex; flex-direction: column; align-items: center; gap: 4px; color: var(--text-tertiary); font-size: 10px; cursor: pointer; }}
        .tab-item i {{ font-size: 20px; }}
        .tab-item.active {{ color: var(--primary); }}
        
        .load-more {{ padding: 20px; text-align: center; color: var(--text-tertiary); font-size: 13px; }}
        
        @media (min-width: 768px) {{ .container {{ max-width: 600px; margin: 0 auto; }} }}
    </style>
</head>
<body>
    <header class="header">
        <div class="header-content">
            <div class="logo"><img src="/public/logo.png" alt="晓波智能"></div>
            <div class="search-bar"><i class="fas fa-search"></i><span>搜索资讯、股票...</span></div>
        </div>
    </header>
    
    <nav class="category-nav">
        <div class="category-scroll" id="categoryList">
            {category_tabs}
        </div>
    </nav>
    
    <div class="container">
        <div class="banner">
            <div class="banner-slide active" style="background: linear-gradient(135deg, #1890FF, #096dd9);">
                <div class="banner-content"><div class="banner-title">AI浪潮来袭：2026科技新趋势</div></div>
            </div>
            <div class="banner-slide" style="background: linear-gradient(135deg, #40a9ff, #1890FF);">
                <div class="banner-content"><div class="banner-title">深度解读：Claude为何登顶App Store</div></div>
            </div>
            <div class="banner-slide" style="background: linear-gradient(135deg, #096dd9, #0050b3);">
                <div class="banner-content"><div class="banner-title">港股开户指南：低佣金交易攻略</div></div>
            </div>
            <div class="banner-dots">
                <div class="banner-dot active"></div>
                <div class="banner-dot"></div>
                <div class="banner-dot"></div>
            </div>
        </div>
        
        <section class="section">
            <div class="section-header">
                <div class="section-title"><i class="fas fa-fire"></i>热点推荐</div>
            </div>
            <div class="hot-list" id="hotList">{hot_list_html}</div>
        </section>
        
        <section class="section">
            <div class="section-header">
                <div class="section-title"><i class="fas fa-newspaper"></i>最新资讯</div>
            </div>
            <div class="feed-list" id="feedList">{feed_list_html}</div>
        </section>
        
        <div class="load-more">上拉加载更多</div>
    </div>
    
    <nav class="tab-bar">
        <div class="tab-item active"><i class="fas fa-home"></i><span>首页</span></div>
        <div class="tab-item"><i class="fas fa-chart-line"></i><span>行情</span></div>
        <div class="tab-item"><i class="fas fa-bolt"></i><span>快讯</span></div>
        <div class="tab-item"><i class="fas fa-user"></i><span>我的</span></div>
    </nav>
    
    <script>
        // 轮播图
        let currentSlide = 0;
        const slides = document.querySelectorAll('.banner-slide');
        const dots = document.querySelectorAll('.banner-dot');
        setInterval(() => {{
            slides[currentSlide].classList.remove('active');
            dots[currentSlide].classList.remove('active');
            currentSlide = (currentSlide + 1) % slides.length;
            slides[currentSlide].classList.add('active');
            dots[currentSlide].classList.add('active');
        }}, 4000);
        
        // 分类切换
        document.getElementById('categoryList').addEventListener('click', (e) => {{
            if (e.target.classList.contains('category-item')) {{
                document.querySelectorAll('.category-item').forEach(item => item.classList.remove('active'));
                e.target.classList.add('active');
                // TODO: 实现分类过滤
            }}
        }});
    </script>
</body>
</html>'''
    return html


def generate_article_html(article):
    """生成文章详情页HTML - 带Markdown解析和配图"""
    title = article[1] or "无标题"
    content = article[2] or ""
    category = article[4] or ""
    author = article[5] or ""
    publish_date = format_date(article[6])
    cover_image = article[7] or ""
    
    # 解析Markdown
    md = markdown.Markdown(extensions=['fenced_code', 'tables', 'toc'])
    content_html = md.convert(content)
    
    # 封面图
    cover_html = ""
    if cover_image:
        cover_html = '<img src="' + cover_image + '" class="w-full h-64 md:h-96 object-cover" />'
    
    html = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>''' + title + ''' - 晓波智能资讯站</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    colors: { primary: '#6366f1', primaryDark: '#4f46e5' }
                }
            }
        }
    </script>
    <style>
        .gradient-bg { background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #a855f7 100%); }
        .prose h1 { font-size: 2rem; font-weight: bold; margin: 1.5rem 0 1rem; color: #1f2937; }
        .prose h2 { font-size: 1.5rem; font-weight: bold; margin: 1.25rem 0 0.75rem; color: #374151; border-left: 4px solid #6366f1; padding-left: 1rem; }
        .prose h3 { font-size: 1.25rem; font-weight: 600; margin: 1rem 0 0.5rem; color: #4b5563; }
        .prose p { margin: 0.75rem 0; line-height: 1.8; color: #4b5563; }
        .prose a { color: #6366f1; text-decoration: underline; }
        .prose ul, .prose ol { margin: 0.75rem 0; padding-left: 1.5rem; }
        .prose li { margin: 0.25rem 0; line-height: 1.6; }
        .prose blockquote { border-left: 4px solid #6366f1; padding-left: 1rem; margin: 1rem 0; background: #f3f4f6; padding: 1rem; }
        .prose code { background: #f3f4f6; padding: 0.2rem 0.4rem; border-radius: 0.25rem; font-family: monospace; font-size: 0.9em; }
        .prose pre { background: #1f2937; color: #e5e7eb; padding: 1rem; border-radius: 0.5rem; overflow-x: auto; margin: 1rem 0; }
        .prose pre code { background: none; padding: 0; }
        .prose img { max-width: 100%; height: auto; border-radius: 0.5rem; margin: 1rem 0; }
        .prose table { width: 100%; border-collapse: collapse; margin: 1rem 0; }
        .prose th, .prose td { border: 1px solid #e5e7eb; padding: 0.5rem 1rem; text-align: left; }
        .prose th { background: #f3f4f6; font-weight: 600; }
        .prose hr { border: none; border-top: 2px solid #e5e7eb; margin: 2rem 0; }
        .prose img[src*="covers"] { width: 100%; max-height: 400px; object-fit: cover; margin: 1.5rem 0; }
        .prose img[src*="illustrations"] { display: block; margin: 2rem auto; max-width: 80%; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }
    </style>
</head>
<body class="bg-gray-50 min-h-screen">
    <header class="gradient-bg shadow-lg">
        <div class="container mx-auto px-4 py-4">
            <div class="flex items-center justify-between">
                <a href="/" class="flex items-center space-x-3">
                    <div class="w-10 h-10 bg-white/20 rounded-xl flex items-center justify-center">
                        <i class="fas fa-robot text-white text-xl"></i>
                    </div>
                    <h1 class="text-white text-xl font-bold">晓波智能资讯站</h1>
                </a>
                <a href="/" class="text-white/90 hover:text-white flex items-center gap-2">
                    <i class="fas fa-arrow-left"></i> 返回首页
                </a>
            </div>
        </div>
    </header>
    
    <main class="container mx-auto px-4 py-8 max-w-4xl">
        <article class="bg-white rounded-xl shadow-lg overflow-hidden">
            ''' + cover_html + '''
            <div class="p-8">
                <div class="flex items-center gap-4 mb-4 flex-wrap">
                    <span class="px-3 py-1 text-sm font-medium text-primary bg-primary/10 rounded-full">''' + category + '''</span>
                    <span class="text-gray-500 text-sm"><i class="far fa-clock mr-1"></i>''' + publish_date + '''</span>
                    <span class="text-gray-500 text-sm"><i class="far fa-user mr-1"></i>''' + author + '''</span>
                </div>
                <h1 class="text-3xl font-bold text-gray-800 mb-6">''' + title + '''</h1>
                <div class="prose max-w-none">
                    ''' + content_html + '''
                </div>
            </div>
        </article>
    </main>
    
    <footer class="bg-gray-800 text-gray-400 py-6 mt-12">
        <div class="container mx-auto px-4 text-center">
            <p>© 2026 晓波智能资讯站 - AI 驱动的科技资讯平台</p>
        </div>
    </footer>
</body>
</html>'''
    return html


class APIHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)
    
    def do_GET(self):
        if self.path.startswith('/articles/'):
            self.handle_article()
        elif self.path.startswith('/api'):
            self.handle_api()
        elif self.path == '/' or self.path == '/index.html':
            # 检测移动端并返回相应首页
            if is_mobile_user_agent(self):
                self.handle_mobile_index()
            else:
                super().do_GET()
        else:
            super().do_GET()
    
    def handle_article(self):
        slug = self.path.split('/')[-1]
        
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute('SELECT id, title, content, summary, category, author, publish_date, image_url FROM articles WHERE link=?', 
                          ('/articles/' + slug,))
            article = cursor.fetchone()
            conn.close()
            
            if not article:
                self.send_error(404, 'Article not found')
                return
            
            html = generate_article_html(article)
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(html.encode('utf-8'))
            
        except Exception as e:
            print("文章渲染错误: " + str(e), flush=True)
            self.send_error(500, str(e))
    
    def handle_mobile_index(self):
        """生成移动端首页"""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, title, link, summary, category, author, publish_date, image_url 
                FROM articles 
                ORDER BY publish_date DESC 
                LIMIT 30
            ''')
            rows = cursor.fetchall()
            conn.close()
            
            # 格式化文章数据
            articles = []
            for r in rows:
                author = r[5] or "未知来源"
                articles.append({
                    'id': r[0],
                    'title': r[1] or "无标题",
                    'link': r[2] or "#",
                    'summary': r[3] or "",
                    'category': r[4] or "",
                    'author': author if author else "未知来源",
                    'publish_date': format_date(r[6]),
                    'image_url': r[7]
                })
            
            # 获取分类
            categories = list(set([a['category'] for a in articles if a['category']]))
            
            html = generate_mobile_index_html(articles, categories)
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(html.encode('utf-8'))
            
        except Exception as e:
            print("移动端首页错误: " + str(e), flush=True)
            self.send_error(500, str(e))
    
    def handle_api(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        path = self.path.split('?')[0]
        
        if path == '/api/news':
            self.api_news()
        elif path == '/api/categories':
            self.api_categories()
        elif path == '/api/popular':
            self.api_popular()
        else:
            self.send_json({"error": "Unknown API: " + path})
    
    def api_news(self):
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            import urllib.parse
            params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            page = int(params.get('page', [1])[0])
            limit = int(params.get('limit', [12])[0])
            category = params.get('category', [None])[0]
            
            query = 'SELECT id, title, link, summary, category, author, publish_date, image_url, level2, ai_tags FROM articles'
            params_list = []
            
            if category and category != 'all':
                query += ' WHERE category = ?'
                params_list.append(category)
            
            query += ' ORDER BY publish_date DESC LIMIT ? OFFSET ?'
            params_list.extend([limit, (page - 1) * limit])
            
            cursor.execute(query, params_list)
            rows = cursor.fetchall()
            
            count_query = 'SELECT COUNT(*) FROM articles'
            if category and category != 'all':
                count_query += ' WHERE category = ?'
                cursor.execute(count_query, [category] if category != 'all' else [])
            else:
                cursor.execute(count_query)
            
            total = cursor.fetchone()[0]
            conn.close()
            
            def format_row(r):
                author = r[5] or ""
                if not author and r[4]:
                    author = r[4]  # 使用分类作为来源
                
                # 如果link为空，用标题生成搜索链接
                link = r[2] if r[2] else f"https://www.baidu.com/s?wd={r[1]}"
                
                return {
                    "id": r[0], "title": r[1], "link": link, "summary": r[3],
                    "category": r[4], "author": author if author else "未知来源",
                    "publish_date": format_date(r[6]), "image_url": r[7],
                    "level2": r[8] or "",  # 二级分类
                    "tags": r[9] or ""     # AI标签
                }
            
            articles = [format_row(r) for r in rows]
            
            self.send_json({"success": True, "data": articles, "pagination": {"page": page, "limit": limit, "total": total}})
        except Exception as e:
            self.send_json({"success": False, "error": str(e)})
    
    def api_categories(self):
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute('SELECT category, COUNT(*) as count FROM articles GROUP BY category ORDER BY count DESC')
            rows = cursor.fetchall()
            conn.close()
            self.send_json({"success": True, "data": [{"name": r[0], "count": r[1]} for r in rows]})
        except Exception as e:
            self.send_json({"success": False, "error": str(e)})
    
    def api_popular(self):
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute('SELECT id, title, link, summary, category, author, publish_date, image_url, level2, ai_tags FROM articles ORDER BY view_count DESC LIMIT 5')
            rows = cursor.fetchall()
            conn.close()
            
            def format_row(r):
                author = r[5] or ""
                if not author and r[4]:
                    author = r[4]
                return {
                    "id": r[0], "title": r[1], "link": r[2], "summary": r[3],
                    "category": r[4], "author": author if author else "未知来源",
                    "publish_date": format_date(r[6]), "image_url": r[7],
                    "level2": r[8] or "", "tags": r[9] or ""
                }
            
            self.send_json({"success": True, "data": [format_row(r) for r in rows]})
        except Exception as e:
            self.send_json({"success": False, "error": str(e)})
    
    def send_json(self, data):
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
    
    def log_message(self, format, *args):
        pass


class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True
    allow_reuse_port = True

    def server_bind(self):
        import socket
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        except:
            pass
        socketserver.TCPServer.server_bind(self)


def start_server():
    with ReusableTCPServer(("", PORT), APIHandler) as httpd:
        print("晓波智能资讯站运行在 http://localhost:" + str(PORT))
        print("✅ Markdown渲染 | 文章详情页 | API支持", flush=True)
        httpd.serve_forever()


if __name__ == "__main__":
    start_server()
