#!/usr/bin/env python3
"""
静态网站导出脚本 - v4 修复只显示 2 张卡片问题
"""

import sqlite3
import os
import base64
from datetime import datetime, timedelta

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(SCRIPT_DIR, 'xiaobo_intelligent_news.db')
OUTPUT_DIR = os.path.join(SCRIPT_DIR, 'dist')
ASSETS_DIR = os.path.join(SCRIPT_DIR, '../assets')

def get_logo_base64():
    logo_path = os.path.join(ASSETS_DIR, 'logo-xiaobo-ai.png')
    if os.path.exists(logo_path):
        with open(logo_path, 'rb') as f:
            return base64.b64encode(f.read()).decode()
    return None

def format_date(date_str):
    if not date_str:
        return ""
    try:
        return datetime.strptime(str(date_str)[:19], "%Y-%m-%d %H:%M:%S").strftime("%m/%d %H:%M")
    except:
        return str(date_str)[:16]

def get_time_ago(date_str):
    if not date_str:
        return ""
    try:
        dt = datetime.strptime(str(date_str)[:19], "%Y-%m-%d %H:%M:%S")
        diff = datetime.now() - dt
        if diff < timedelta(hours=1):
            return "刚刚"
        elif diff < timedelta(days=1):
            return f"{int(diff.total_seconds() / 3600)}小时前"
        elif diff < timedelta(days=7):
            return f"{diff.days}天前"
        else:
            return f"{diff.days//7}周前"
    except:
        return ""

def get_articles(limit=30):
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM articles ORDER BY publish_date DESC LIMIT ?", (limit,))
        articles = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return articles
    except Exception as e:
        print(f"Error: {e}")
        return []

def get_categories():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT category, sub_category, COUNT(*) as count FROM articles GROUP BY category, sub_category ORDER BY count DESC")
        categories = cursor.fetchall()
        conn.close()
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
    logo_base64 = get_logo_base64()
    logo_img = f"<img src='data:image/png;base64,{logo_base64}' alt='Logo'>" if logo_base64 else "🤖"
    
    main_cats = list(categories.keys())[:7]
    cat_buttons = '<button class="cat-btn active" data-cat="all">全部</button>'
    for cat in main_cats:
        cat_buttons += f'<button class="cat-btn" data-cat="{cat}">{cat}</button>'
    
    cards_html = ""
    for art in articles[:50]:
        title = (art['title'] or "无标题")[:45] + ("..." if len(art['title'] or "") > 45 else "")
        category = art['category'] or ""
        sub_cat = art['sub_category'] or ""
        author = (art['author'] or category)[:20]
        date = format_date(art['publish_date'])
        summary = art['summary'] or ""
        image = art['image_url'] or ""
        link = art['link'] or "#"
        time_ago = get_time_ago(art.get('publish_date'))
        
        badge = ""
        if "分钟" in time_ago or "小时" in time_ago:
            badge = '<span class="badge hot">🔥</span>'
        elif "天" in time_ago and int(time_ago.replace("天前","")) <= 2:
            badge = '<span class="badge new">🆕</span>'
        
        if image:
            img_html = f'<div class="card-img" style="background-image: url({image})"></div>'
        else:
            colors = ["#667eea", "#f093fb", "#4facfe", "#fa709a"]
            img_html = f'<div class="card-img" style="background: linear-gradient(135deg, {colors[hash(category) % len(colors)]}, #fff)"></div>'
        
        display_cat = (sub_cat or category)[:12]
        summary_html = f'<p class="card-summary">{summary[:70]}...</p>' if summary else ''
        
        cards_html += f'''
        <article class="card" data-category="{category}" onclick="window.open('{link}', '_blank')">
            {img_html}
            <div class="card-body">
                <div class="card-meta">
                    <span class="cat-tag">{display_cat}</span>
                    {badge}
                    <span class="time">{time_ago}</span>
                </div>
                <h3 class="card-title">{title}</h3>
                {summary_html}
                <div class="card-footer">
                    <span class="author">{author}</span>
                    <span class="date">{date}</span>
                </div>
            </div>
        </article>'''
    
    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>晓波智能资讯站 | AI 科技金融前沿</title>
    <meta name="description" content="每日更新 AI 科技、股票投资、金融资讯">
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-6726601289992127" crossorigin="anonymous"></script>
    <style>
        :root {{ --primary: #667eea; --bg: #f7fafc; --card-bg: #fff; --text: #2d3748; --text-light: #718096; --border: #e2e8f0; }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Microsoft YaHei', sans-serif; background: var(--bg); color: var(--text); }}
        
        .header {{ background: linear-gradient(135deg, #667eea, #764ba2); color: #fff; padding: 30px 20px; text-align: center; }}
        .logo-container {{ display: flex; align-items: center; justify-content: center; gap: 15px; margin-bottom: 10px; }}
        .logo {{ width: 60px; height: 60px; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.15); }}
        .logo img {{ width: 100%; height: 100%; object-fit: cover; }}
        .site-title {{ font-size: 1.8rem; font-weight: 700; }}
        .site-subtitle {{ opacity: 0.9; font-size: 0.95rem; }}
        .stats {{ display: flex; justify-content: center; gap: 20px; margin-top: 15px; flex-wrap: wrap; }}
        .stat-item {{ background: rgba(255,255,255,0.15); padding: 6px 16px; border-radius: 20px; font-size: 0.85rem; }}
        
        .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
        
        .category-filter {{ background: var(--card-bg); padding: 15px 20px; border-radius: 12px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); display: flex; gap: 10px; flex-wrap: wrap; align-items: center; }}
        .category-filter h2 {{ font-size: 0.9rem; color: var(--text-light); margin-right: 10px; }}
        .cat-btn {{ background: var(--bg); border: 1px solid var(--border); padding: 6px 14px; border-radius: 20px; font-size: 0.85rem; cursor: pointer; transition: all 0.2s; }}
        .cat-btn:hover, .cat-btn.active {{ background: var(--primary); color: #fff; border-color: var(--primary); }}
        
        .ad-banner {{ background: var(--card-bg); padding: 20px; border-radius: 12px; margin-bottom: 20px; text-align: center; min-height: 100px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }}
        
        .articles {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; }}
        
        .card {{ background: var(--card-bg); border-radius: 12px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.08); cursor: pointer; transition: all 0.3s; display: flex; flex-direction: column; height: 380px; }}
        .card:hover {{ transform: translateY(-4px); box-shadow: 0 8px 24px rgba(0,0,0,0.12); }}
        .card-img {{ width: 100%; height: 160px; background-size: cover; background-position: center; flex-shrink: 0; }}
        .card-body {{ padding: 16px; flex: 1; display: flex; flex-direction: column; overflow: hidden; }}
        .card-meta {{ display: flex; align-items: center; gap: 8px; margin-bottom: 10px; flex-wrap: wrap; flex-shrink: 0; }}
        .cat-tag {{ background: linear-gradient(135deg, #667eea, #764ba2); color: #fff; padding: 3px 10px; border-radius: 6px; font-size: 0.75rem; white-space: nowrap; }}
        .badge {{ padding: 2px 6px; border-radius: 6px; font-size: 0.7rem; }}
        .badge.hot {{ background: #fed7d7; color: #c53030; }}
        .badge.new {{ background: #c6f6d5; color: #276749; }}
        .time {{ color: var(--text-light); font-size: 0.75rem; margin-left: auto; white-space: nowrap; }}
        .card-title {{ font-size: 0.95rem; font-weight: 600; line-height: 1.4; margin-bottom: 8px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; flex-shrink: 0; min-height: 2.8em; }}
        .card-summary {{ color: var(--text-light); font-size: 0.85rem; line-height: 1.5; margin-bottom: 12px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; flex: 1; }}
        .card-footer {{ display: flex; justify-content: space-between; align-items: center; padding-top: 12px; border-top: 1px solid var(--border); font-size: 0.75rem; color: var(--text-light); flex-shrink: 0; }}
        .author {{ max-width: 60%; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}
        
        .footer {{ text-align: center; padding: 40px 20px; color: var(--text-light); font-size: 0.85rem; border-top: 1px solid var(--border); margin-top: 40px; }}
        
        @media (max-width: 768px) {{ .articles {{ grid-template-columns: 1fr; }} .card {{ height: 360px; }} }}
    </style>
</head>
<body>
    <header class="header">
        <div class="logo-container">
            <div class="logo">{logo_img}</div>
            <div>
                <h1 class="site-title">晓波智能资讯站</h1>
                <p class="site-subtitle">AI 科技 | 金融投资 | 前沿趋势</p>
            </div>
        </div>
        <div class="stats">
            <span class="stat-item">📰 {len(articles)} 篇</span>
            <span class="stat-item">⏰ 实时更新</span>
        </div>
    </header>
    
    <div class="container">
        <div class="ad-banner">
            <ins class="adsbygoogle" style="display:block" data-ad-client="ca-pub-6726601289992127" data-ad-slot="1234567890" data-ad-format="auto" data-full-width-responsive="true"></ins>
        </div>
        
        <div class="category-filter">
            <h2>筛选：</h2>
            {cat_buttons}
        </div>
        
        <div class="articles">
            {cards_html}
        </div>
        
        <div class="ad-banner" style="margin-top: 30px;">
            <ins class="adsbygoogle" style="display:block" data-ad-client="ca-pub-6726601289992127" data-ad-slot="1234567890" data-ad-format="auto" data-full-width-responsive="true"></ins>
        </div>
    </div>
    
    <footer class="footer">
        <p>© 2026 晓波智能资讯站</p>
    </footer>
    
    <script>
        document.querySelectorAll('.cat-btn').forEach(btn => {{
            btn.addEventListener('click', function() {{
                const cat = this.dataset.cat;
                document.querySelectorAll('.cat-btn').forEach(b => b.classList.remove('active'));
                this.classList.add('active');
                document.querySelectorAll('.card').forEach(card => {{
                    card.style.display = (cat === 'all' || card.dataset.category === cat) ? 'flex' : 'none';
                }});
            }});
        }});
        (adsbygoogle = window.adsbygoogle || []).push({{}});
    </script>
</body>
</html>'''

def main():
    print("📦 导出静态网站 v4...")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    articles = get_articles(100)
    categories = get_categories()
    html = generate_index_html(articles, categories)
    output_path = os.path.join(OUTPUT_DIR, 'index.html')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"✅ 已生成：{output_path}")
    print(f"🌐 文章：{len(articles)}篇")

if __name__ == '__main__':
    main()
