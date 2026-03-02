#!/usr/bin/env python3
"""
静态网站导出脚本 - v3 修复卡片排版问题
- 统一卡片高度
- 添加真实 logo
- 优化内容截断
"""

import sqlite3
import os
import json
import base64
from datetime import datetime, timedelta

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(SCRIPT_DIR, 'xiaobo_intelligent_news.db')
OUTPUT_DIR = os.path.join(SCRIPT_DIR, 'dist')
ASSETS_DIR = os.path.join(SCRIPT_DIR, '../assets')

def get_logo_base64():
    """获取 logo 的 base64 编码"""
    logo_path = os.path.join(ASSETS_DIR, 'logo-xiaobo-ai.png')
    if os.path.exists(logo_path):
        with open(logo_path, 'rb') as f:
            return base64.b64encode(f.read()).decode()
    return None

def format_date(date_str):
    """格式化日期"""
    if not date_str:
        return ""
    try:
        formats = ["%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S"]
        for fmt in formats:
            try:
                dt = datetime.strptime(str(date_str)[:19], fmt)
                return dt.strftime("%m/%d %H:%M")
            except:
                continue
        return str(date_str)[:16]
    except:
        return str(date_str)[:16]

def get_time_ago(date_str):
    """计算时间差"""
    if not date_str:
        return ""
    try:
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
            return "刚刚" if minutes <= 0 else f"{minutes}分钟前"
        elif diff < timedelta(days=1):
            hours = int(diff.total_seconds() / 3600)
            return f"{hours}小时前"
        elif diff < timedelta(days=7):
            return f"{diff.days}天前"
        else:
            return f"{diff.days//7}周前"
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
        articles = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return articles
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
    """生成首页 HTML - v3 修复版"""
    
    # 获取 logo
    logo_base64 = get_logo_base64()
    logo_data_uri = f"data:image/png;base64,{logo_base64}" if logo_base64 else ""
    
    # 主分类
    main_cats = list(categories.keys())[:7]
    
    # 分类按钮
    category_buttons = ""
    category_buttons += f'<button class="cat-btn active" onclick="filterCategory(\'all\')">全部</button>'
    for cat in main_cats:
        category_buttons += f'<button class="cat-btn" onclick="filterCategory(\'{cat}\')">{cat}</button>'
    
    # 文章卡片 - 严格统一高度
    articles_html = ""
    for art in articles[:50]:
        title = art['title'] or "无标题"
        category = art['category'] or ""
        sub_category = art['sub_category'] or ""
        author = art['author'] or category
        date = format_date(art['publish_date'])
        summary = art['summary'] or ""
        image = art['image_url'] or ""
        link = art['link'] or "#"
        
        time_ago = get_time_ago(art.get('publish_date'))
        
        # 时效性徽章
        time_badge = ""
        if "分钟" in time_ago or "小时" in time_ago:
            time_badge = '<span class="badge hot">🔥</span>'
        elif "天" in time_ago and int(time_ago.replace("天前","")) <= 2:
            time_badge = '<span class="badge new">🆕</span>'
        
        # 图片处理
        if image:
            img_html = f'<div class="card-img" style="background-image: url({image})"></div>'
        else:
            colors = ["linear-gradient(135deg, #667eea 0%, #764ba2 100%)", 
                     "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)",
                     "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)",
                     "linear-gradient(135deg, #fa709a 0%, #fee140 100%)"]
            color_idx = hash(category) % len(colors)
            img_html = f'<div class="card-img" style="background: {colors[color_idx]}"></div>'
        
        # 严格截断标题（最多 2 行）
        if len(title) > 45:
            title = title[:43] + "..."
        
        # 严格截断摘要（最多 2 行，如果有的话）
        summary_html = ""
        if summary:
            if len(summary) > 70:
                summary = summary[:68] + "..."
            summary_html = f'<p class="card-summary">{summary}</p>'
        
        display_category = sub_category or category
        if len(display_category) > 12:
            display_category = display_category[:10] + "..."
        
        articles_html += f"""
        <article class="card" data-category="{category}" onclick="window.open('{link}', '_blank')">
            {img_html}
            <div class="card-body">
                <div class="card-meta">
                    <span class="cat-tag">{display_category}</span>
                    {time_badge}
                    <span class="time">{time_ago}</span>
                </div>
                <h3 class="card-title">{title}</h3>
                {summary_html}
                <div class="card-footer">
                    <span class="author">{author}</span>
                    <span class="date">{date}</span>
                </div>
            </div>
        </article>
        """

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>晓波智能资讯站 | AI 科技金融前沿</title>
    <meta name="description" content="每日更新 AI 科技、股票投资、金融资讯">
    <meta name="keywords" content="AI，人工智能，科技，股票，投资，金融">
    <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🤖</text></svg>">
    <!-- Google AdSense -->
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-6726601289992127" crossorigin="anonymous"></script>
    <style>
        :root {{
            --primary: #667eea;
            --primary-dark: #5a67d8;
            --accent: #f093fb;
            --bg: #f7fafc;
            --card-bg: #ffffff;
            --text: #2d3748;
            --text-light: #718096;
            --border: #e2e8f0;
        }}
        
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
            background: var(--bg);
            color: var(--text);
            line-height: 1.6;
            -webkit-font-smoothing: antialiased;
        }}
        
        /* Header */
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px 20px;
            text-align: center;
            box-shadow: 0 4px 20px rgba(102, 126, 234, 0.3);
        }}
        
        .logo-container {{
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 15px;
            margin-bottom: 10px;
        }}
        
        .logo {{
            width: 60px;
            height: 60px;
            border-radius: 16px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            overflow: hidden;
        }}
        
        .logo img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
        }}
        
        .site-title {{
            font-size: 1.8rem;
            font-weight: 700;
            letter-spacing: -0.5px;
        }}
        
        .site-subtitle {{
            opacity: 0.9;
            font-size: 0.95rem;
        }}
        
        .stats {{
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-top: 15px;
            flex-wrap: wrap;
        }}
        
        .stat-item {{
            background: rgba(255,255,255,0.15);
            padding: 6px 16px;
            border-radius: 20px;
            font-size: 0.85rem;
            backdrop-filter: blur(10px);
        }}
        
        /* Container */
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        /* Category Filter */
        .category-filter {{
            background: var(--card-bg);
            padding: 15px 20px;
            border-radius: 12px;
            margin-bottom: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            align-items: center;
        }}
        
        .category-filter h2 {{
            font-size: 0.9rem;
            color: var(--text-light);
            margin-right: 10px;
            font-weight: 500;
        }}
        
        .cat-btn {{
            background: var(--bg);
            border: 1px solid var(--border);
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 0.85rem;
            cursor: pointer;
            transition: all 0.2s;
            color: var(--text);
        }}
        
        .cat-btn:hover {{
            background: var(--primary);
            color: white;
            border-color: var(--primary);
        }}
        
        .cat-btn.active {{
            background: var(--primary);
            color: white;
            border-color: var(--primary);
        }}
        
        /* Ad Banner */
        .ad-banner {{
            background: var(--card-bg);
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 20px;
            text-align: center;
            min-height: 100px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }}
        
        /* Articles Grid */
        .articles {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
        }}
        
        .card {{
            background: var(--card-bg);
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            cursor: pointer;
            transition: all 0.3s;
            display: flex;
            flex-direction: column;
            height: 380px; /* 固定高度 */
        }}
        
        .card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 8px 24px rgba(0,0,0,0.12);
        }}
        
        .card-img {{
            width: 100%;
            height: 160px;
            background-size: cover;
            background-position: center;
            background-color: #f0f0f0;
            flex-shrink: 0;
        }}
        
        .card-body {{
            padding: 16px;
            flex: 1;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }}
        
        .card-meta {{
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 10px;
            flex-wrap: wrap;
            flex-shrink: 0;
        }}
        
        .cat-tag {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 3px 10px;
            border-radius: 6px;
            font-size: 0.75rem;
            font-weight: 500;
            white-space: nowrap;
        }}
        
        .badge {{
            padding: 2px 6px;
            border-radius: 6px;
            font-size: 0.7rem;
            flex-shrink: 0;
        }}
        
        .badge.hot {{
            background: #fed7d7;
            color: #c53030;
        }}
        
        .badge.new {{
            background: #c6f6d5;
            color: #276749;
        }}
        
        .time {{
            color: var(--text-light);
            font-size: 0.75rem;
            margin-left: auto;
            white-space: nowrap;
        }}
        
        .card-title {{
            font-size: 0.95rem;
            font-weight: 600;
            line-height: 1.4;
            margin-bottom: 8px;
            color: var(--text);
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
            flex-shrink: 0;
            min-height: 2.8em;
        }}
        
        .card-summary {{
            color: var(--text-light);
            font-size: 0.85rem;
            line-height: 1.5;
            margin-bottom: 12px;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
            flex: 1;
        }}
        
        .card-footer {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-top: 12px;
            border-top: 1px solid var(--border);
            font-size: 0.75rem;
            color: var(--text-light);
            flex-shrink: 0;
        }}
        
        .author {{
            font-weight: 500;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            max-width: 60%;
        }}
        
        .date {{
            white-space: nowrap;
        }}
        
        /* Footer */
        .footer {{
            text-align: center;
            padding: 40px 20px;
            color: var(--text-light);
            font-size: 0.85rem;
            border-top: 1px solid var(--border);
            margin-top: 40px;
        }}
        
        /* Responsive */
        @media (max-width: 768px) {{
            .site-title {{ font-size: 1.4rem; }}
            .logo {{ width: 50px; height: 50px; }}
            .articles {{ grid-template-columns: 1fr; }}
            .category-filter {{ justify-content: center; }}
            .card {{ height: 360px; }}
        }}
    </style>
</head>
<body>
    <header class="header">
        <div class="logo-container">
            <div class="logo">
                {"<img src='" + logo_data_uri + "' alt='Logo'>" if logo_data_uri else "🤖"}
            </div>
            <div>
                <h1 class="site-title">晓波智能资讯站</h1>
                <p class="site-subtitle">AI 科技 | 金融投资 | 前沿趋势</p>
            </div>
        </div>
        <div class="stats">
            <span class="stat-item">📰 {len(articles)} 篇</span>
            <span class="stat-item">⏰ 实时更新</span>
            <span class="stat-item">🤖 AI 驱动</span>
        </div>
    </header>
    
    <div class="container">
        <!-- 广告位 1 -->
        <div class="ad-banner">
            <ins class="adsbygoogle"
                 style="display:block"
                 data-ad-client="ca-pub-6726601289992127"
                 data-ad-slot="1234567890"
                 data-ad-format="auto"
                 data-full-width-responsive="true"></ins>
        </div>
        
        <!-- 分类筛选 -->
        <div class="category-filter">
            <h2>筛选：</h2>
            {category_buttons}
        </div>
        
        <!-- 文章列表 -->
        <div class="articles">
            {articles_html}
        </div>
        
        <!-- 广告位 2 -->
        <div class="ad-banner" style="margin-top: 30px;">
            <ins class="adsbygoogle"
                 style="display:block"
                 data-ad-client="ca-pub-6726601289992127"
                 data-ad-slot="1234567890"
                 data-ad-format="auto"
                 data-full-width-responsive="true"></ins>
        </div>
    </div>
    
    <footer class="footer">
        <p>© 2026 晓波智能资讯站 · 每日更新 AI 科技金融前沿资讯</p>
    </footer>
    
    <script>
        function filterCategory(cat) {{
            const cards = document.querySelectorAll('.card');
            const buttons = document.querySelectorAll('.cat-btn');
            
            buttons.forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');
            
            cards.forEach(card => {{
                if (cat === 'all' || card.dataset.category === cat) {{
                    card.style.display = 'flex';
                }} else {{
                    card.style.display = 'none';
                }}
            }});
        }}
        
        // 初始化广告
        (adsbygoogle = window.adsbygoogle || []).push({{}});
    </script>
</body>
</html>"""
    
    return html

def main():
    """主函数"""
    print("📦 正在导出静态网站 v3...")
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    articles = get_articles(100)
    categories = get_categories()
    
    html = generate_index_html(articles, categories)
    
    output_path = os.path.join(OUTPUT_DIR, 'index.html')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✅ 已生成：{output_path}")
    print(f"🌐 文章数量：{len(articles)}")
    print(f"📂 分类数量：{len(categories)}")
    
    # 检查 logo
    if get_logo_base64():
        print("✅ Logo 已添加")
    else:
        print("⚠️ 未找到 logo")

if __name__ == '__main__':
    main()
