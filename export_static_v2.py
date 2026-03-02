#!/usr/bin/env python3
"""
静态网站导出脚本 - 专业UI/UX redesign版
目标：提升用户体验 → 增加停留时间 → 提高广告收入
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
    """计算时间差，显示为 X 小时前/X 天前"""
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
    """生成首页 HTML - 专业 redesign 版"""
    
    # 主分类（用于筛选）
    main_cats = list(categories.keys())[:7]  # 只显示前 7 个主分类
    
    # 分类按钮 HTML（简化版）
    category_buttons = ""
    category_buttons += f'<button class="cat-btn active" onclick="filterCategory(\'all\')">全部</button>'
    for cat in main_cats:
        category_buttons += f'<button class="cat-btn" onclick="filterCategory(\'{cat}\')">{cat}</button>'
    
    # 文章卡片 HTML - 统一高度，优化显示
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
        img_html = ""
        if image:
            img_html = f'<div class="card-img" style="background-image: url({image})"></div>'
        else:
            # 默认图片（渐变色）
            colors = ["linear-gradient(135deg, #667eea 0%, #764ba2 100%)", 
                     "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)",
                     "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)"]
            color_idx = hash(category) % len(colors)
            img_html = f'<div class="card-img" style="background: {colors[color_idx]}"></div>'
        
        # 截断过长的标题
        if len(title) > 50:
            title = title[:48] + "..."
        
        # 截断摘要（最多 2 行）
        if summary and len(summary) > 80:
            summary = summary[:78] + "..."
        
        display_category = sub_category or category
        
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
                {f'<p class="card-summary">{summary}</p>' if summary else ''}
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
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', sans-serif;
            background: var(--bg);
            color: var(--text);
            line-height: 1.6;
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
            width: 50px;
            height: 50px;
            background: white;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 28px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
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
        
        /* Category Filter - 简化版 */
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
            grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
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
            height: 100%;
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
        }}
        
        .card-body {{
            padding: 16px;
            flex: 1;
            display: flex;
            flex-direction: column;
        }}
        
        .card-meta {{
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 10px;
            flex-wrap: wrap;
        }}
        
        .cat-tag {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 3px 10px;
            border-radius: 6px;
            font-size: 0.75rem;
            font-weight: 500;
        }}
        
        .badge {{
            padding: 2px 6px;
            border-radius: 6px;
            font-size: 0.7rem;
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
        }}
        
        .card-title {{
            font-size: 1rem;
            font-weight: 600;
            line-height: 1.5;
            margin-bottom: 8px;
            color: var(--text);
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }}
        
        .card-summary {{
            color: var(--text-light);
            font-size: 0.85rem;
            line-height: 1.6;
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
        }}
        
        .author {{
            font-weight: 500;
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
            .articles {{ grid-template-columns: 1fr; }}
            .category-filter {{ justify-content: center; }}
        }}
    </style>
</head>
<body>
    <header class="header">
        <div class="logo-container">
            <div class="logo">🤖</div>
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
    print("📦 正在导出静态网站...")
    
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

if __name__ == '__main__':
    main()
