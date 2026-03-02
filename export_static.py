#!/usr/bin/env python3
"""
静态网站导出脚本 - 将资讯站导出为纯静态HTML
增强版：支持跳转原文、时效性显示
"""

import sqlite3
import os
import json
from datetime import datetime, timedelta

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(SCRIPT_DIR, 'xiaobo_intelligent_news.db')
OUTPUT_DIR = os.path.join(SCRIPT_DIR, 'dist')

def format_date(date_str):
    """格式化日期"""
    if not date_str:
        return ""
    try:
        from datetime import datetime
        formats = ["%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S"]
        for fmt in formats:
            try:
                dt = datetime.strptime(str(date_str)[:19], fmt)
                return dt.strftime("%Y年%m月%d日 %H:%M")
            except:
                continue
        return str(date_str)[:16]
    except:
        return str(date_str)[:16]

def get_time_ago(date_str):
    """计算时间差，显示为X小时前/X天前"""
    if not date_str:
        return ""
    try:
        from datetime import datetime
        formats = ["%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S"]
        dt = None
        for fmt in formats:
            try:
                dt = datetime.strptime(str(date_str)[:19], fmt)
                break
            except:
                continue
        
        if dt is None:
            return ""
        
        now = datetime.now()
        diff = now - dt
        
        if diff < timedelta(hours=1):
            minutes = int(diff.total_seconds() / 60)
            if minutes <= 0:
                return "刚刚"
            return f"{minutes}分钟前"
        elif diff < timedelta(days=1):
            hours = int(diff.total_seconds() / 3600)
            return f"{hours}小时前"
        elif diff < timedelta(days=7):
            days = diff.days
            return f"{days}天前"
        else:
            return f"{int(days/7)}周前"
    except:
        return ""

def get_articles(limit=100):
    """获取文章列表"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, title, content, link, category, sub_category, author, publish_date, summary, image_url
            FROM articles 
            ORDER BY publish_date DESC 
            LIMIT ?
        """, (limit,))
        articles = cursor.fetchall()
        conn.close()
        return [dict(row) for row in articles]
    except Exception as e:
        print(f"Error: {e}")
        return []

def get_categories():
    """获取分类统计"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT category, sub_category, COUNT(*) as count 
            FROM articles 
            GROUP BY category, sub_category
            ORDER BY count DESC
        """)
        categories = cursor.fetchall()
        conn.close()
        
        # 按主分类汇总
        cat_dict = {}
        for cat, sub_cat, count in categories:
            if cat not in cat_dict:
                cat_dict[cat] = {'total': 0, 'subcategories': {}}
            cat_dict[cat]['total'] += count
            if sub_cat:
                cat_dict[cat]['subcategories'][sub_cat] = count
        return cat_dict
    except:
        return {}

def generate_index_html(articles, categories):
    """生成首页HTML - 增强版"""
    
    # 分类列表HTML
    category_html = ""
    for cat, data in categories.items():
        sub_cats = data.get('subcategories', {})
        sub_html = ""
        for sub, cnt in sub_cats.items():
            sub_html += f'<span class="tag" onclick="filterBySubCategory(\'{sub}\')">{sub}({cnt})</span>'
        
        category_html += f"""
        <div class="category-section">
            <h3>{cat} ({data['total']})</h3>
            <div class="sub-tags">{sub_html}</div>
        </div>
        """
    
    # 文章列表HTML - 点击直接跳转原链接 + 显示时效性
    articles_html = ""
    for art in articles[:50]:  # 首页显示50篇
        title = art['title'] or "无标题"
        category = art['category'] or ""
        sub_category = art['sub_category'] or ""
        author = art['author'] or category
        date = format_date(art['publish_date'])
        summary = art['summary'] or ""
        image = art['image_url'] or ""
        link = art['link'] or "#"
        
        # 时效性显示
        time_ago = get_time_ago(art.get('publish_date'))
        
        # 标记时效（颜色区分）
        time_badge = ""
        if "分钟" in time_ago or "小时" in time_ago:
            time_badge = '<span class="time-badge hot">🔥 最新</span>'
        elif "天" in time_ago and int(time_ago.replace("天前","").replace("周前","")) <= 2:
            time_badge = '<span class="time-badge new">🆕 更新</span>'
        
        img_html = f'<img src="{image}" alt="" loading="lazy">' if image else ''
        
        articles_html += f"""
        <article class="card" onclick="window.open('{link}', '_blank')">
            {img_html}
            <div class="card-content">
                <span class="category">{sub_category or category}</span>
                {time_badge}
                <h3>{title}</h3>
                <p class="summary">{summary[:100]}...</p>
                <span class="meta">{author} · {date} · {time_ago}</span>
            </div>
        </article>
        """

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>晓波智能资讯站 - AI科技金融前沿</title>
    <meta name="description" content="每日更新AI科技、股票投资、金融资讯">
    <meta name="keywords" content="AI,人工智能,科技,股票,投资,金融">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; color: #333; line-height: 1.6; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
        header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px 20px; text-align: center; border-radius: 0 0 20px 20px; margin-bottom: 30px; }}
        header h1 {{ font-size: 2.5rem; margin-bottom: 10px; }}
        header p {{ opacity: 0.9; }}
        .stats {{ display: flex; justify-content: center; gap: 20px; margin-top: 15px; }}
        .stats span {{ background: rgba(255,255,255,0.2); padding: 5px 15px; border-radius: 20px; font-size: 0.9rem; }}
        .categories {{ background: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .category-section {{ margin-bottom: 15px; }}
        .category-section h3 {{ color: #667eea; margin-bottom: 10px; font-size: 1.1rem; }}
        .sub-tags {{ display: flex; flex-wrap: wrap; gap: 8px; }}
        .tag {{ background: #f0f0f0; padding: 5px 12px; border-radius: 15px; font-size: 0.85rem; cursor: pointer; transition: all 0.2s; }}
        .tag:hover {{ background: #667eea; color: white; }}
        .articles {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; }}
        .card {{ background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.1); cursor: pointer; transition: transform 0.2s; }}
        .card:hover {{ transform: translateY(-5px); box-shadow: 0 5px 20px rgba(0,0,0,0.15); }}
        .card img {{ width: 100%; height: 180px; object-fit: cover; }}
        .card-content {{ padding: 15px; }}
        .card .category {{ background: #667eea; color: white; padding: 3px 10px; border-radius: 10px; font-size: 0.75rem; display: inline-block; margin-bottom: 8px; }}
        .time-badge {{ margin-left: 8px; padding: 2px 8px; border-radius: 10px; font-size: 0.7rem; }}
        .time-badge.hot {{ background: #ff4757; color: white; }}
        .time-badge.new {{ background: #2ed573; color: white; }}
        .card h3 {{ font-size: 1.1rem; margin-bottom: 8px; line-height: 1.4; }}
        .card .summary {{ color: #666; font-size: 0.9rem; margin-bottom: 10px; }}
        .card .meta {{ color: #999; font-size: 0.8rem; }}
        .search-box {{ margin-bottom: 20px; }}
        .search-box input {{ width: 100%; padding: 15px; border: none; border-radius: 10px; font-size: 1rem; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .refresh-btn {{ display: inline-block; background: white; color: #667eea; padding: 8px 20px; border-radius: 20px; margin-top: 10px; font-size: 0.9rem; }}
    </style>
</head>
<body>
    <header>
        <div class="container">
            <h1>🤖 晓波智能资讯站</h1>
            <p>AI科技 | 金融投资 | 前沿趋势</p>
            <div class="stats">
                <span>📰 {len(articles)} 篇</span>
                <span>⏰ 实时更新</span>
            </div>
        </div>
    </header>
    
    <div class="container">
        <div class="search-box">
            <input type="text" placeholder="搜索文章..." onkeyup="searchArticles(this.value)">
        </div>
        
        <div class="categories">
            <h2 style="margin-bottom:15px;">📂 文章分类</h2>
            {category_html}
        </div>
        
        <div class="articles" id="articles">
            {articles_html}
        </div>
    </div>
    
    <script>
        function searchArticles(keyword) {{
            const cards = document.querySelectorAll('.card');
            keyword = keyword.toLowerCase();
            cards.forEach(card => {{
                const text = card.innerText.toLowerCase();
                card.style.display = text.includes(keyword) ? 'block' : 'none';
            }});
        }}
    </script>
</body>
</html>"""
    return html

def export_static_site():
    """导出静态网站"""
    print("📦 正在导出静态网站...")
    
    # 创建输出目录
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    
    # 获取数据
    articles = get_articles(100)
    categories = get_categories()
    
    print(f"📰 获取到 {len(articles)} 篇文章")
    
    # 生成首页
    index_html = generate_index_html(articles, categories)
    
    # 写入文件
    index_path = os.path.join(OUTPUT_DIR, 'index.html')
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(index_html)
    
    print(f"✅ 已生成: {index_path}")
    print(f"🌐 文章数量: {len(articles)}")
    print(f"📂 分类数量: {len(categories)}")

if __name__ == '__main__':
    export_static_site()
