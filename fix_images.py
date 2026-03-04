#!/usr/bin/env python3
"""修复资讯站的图片显示问题"""

import re

# 读取文件
with open('simple_server.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 修复资讯流卡片图片生成逻辑
old_feed = '''    # 资讯流 HTML
    feed_list_html = ''.join([
        f'''<div class="feed-card" onclick="window.open('{a.get("link", "#")}', '_blank')">
            <div class="feed-card-img placeholder">📰</div>'''

new_feed = '''    # 资讯流 HTML
    def generate_feed_card(a):
        image_url = a.get('image_url')
        if image_url and image_url.startswith('http'):
            img_html = f'<div class="feed-card-img" style="background-image: url({image_url})"></div>'
        else:
            img_html = '<div class="feed-card-img no-image"><i class="fas fa-newspaper"></i></div>'
        return f"""<div class="feed-card" onclick="window.open('{a.get("link", "#")}', '_blank')">
            {img_html}"""

# 查找并替换
pattern = r"(\s+)# 资讯流 HTML\n\1feed_list_html = ''.join\(\[\n\1\s+f'''<div class=\"feed-card\" onclick=\"window\.open\('\{a\.get\(\"link\", \"#\"\)\}', '_blank'\)\">\n\1\s+<div class=\"feed-card-img placeholder\">📰</div>"
replacement = r"\1# 资讯流 HTML\n\1def generate_feed_card(a):\n\1    image_url = a.get('image_url')\n\1    if image_url and image_url.startswith('http'):\n\1        img_html = f'<div class=\"feed-card-img\" style=\"background-image: url({image_url})\"></div>'\n\1    else:\n\1        img_html = '<div class=\"feed-card-img no-image\"><i class=\"fas fa-newspaper\"></i></div>'\n\1    return f\"\"\"<div class=\"feed-card\" onclick=\"window.open('{a.get(\"link\", \"#\")}', '_blank')\">\n\1        {img_html}\"\"\""

content = re.sub(pattern, replacement, content, flags=re.MULTILINE)

# 保存文件
with open('simple_server.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ 图片显示逻辑已修复")
