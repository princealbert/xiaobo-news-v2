#!/usr/bin/env python3
"""
QA 自动测试脚本 - 检测页面问题
"""

import requests
import re
from bs4 import BeautifulSoup

URL = "https://xiaobointelligentnewssiteastro.vercel.app"

def test_page():
    print("🔍 开始 QA 自动测试...\n")
    
    # 获取页面
    response = requests.get(URL)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    issues = []
    
    # 1. 检查轮播图
    carousel_slides = soup.select('.carousel-slide')
    if len(carousel_slides) < 3:
        issues.append(f"⚠️ 轮播图文章不足 3 篇（当前：{len(carousel_slides)}）")
    else:
        print(f"✅ 轮播图：{len(carousel_slides)} 篇")
    
    # 2. 检查文章卡片
    articles = soup.select('.article-card')
    print(f"✅ 文章卡片：{len(articles)} 篇")
    
    # 3. 检查日期格式
    dates = soup.select('.article-date')
    date_issues = []
    for date in dates:
        text = date.get_text(strip=True)
        if '1 月 1 日' in text or '最新发布' in text:
            date_issues.append(text)
    
    if date_issues:
        issues.append(f"⚠️ 日期显示异常：{', '.join(date_issues[:3])}")
    else:
        print(f"✅ 日期显示：正常")
    
    # 4. 检查图片
    images = soup.select('.article-image img')
    bg_images = [s for s in soup.select('.article-image') if 'background-image' in str(s)]
    
    if len(images) == 0 and len(bg_images) == 0:
        issues.append("⚠️ 所有文章都无图片")
    else:
        print(f"✅ 文章图片：{len(images)} 张真实图片，{len(bg_images)} 张背景图")
    
    # 5. 检查分类
    categories = soup.select('.category-item')
    if len(categories) < 4:
        issues.append(f"⚠️ 分类不足 4 个（当前：{len(categories)}）")
    else:
        print(f"✅ 分类浏览：{len(categories)} 个")
    
    # 6. 检查链接
    links = soup.select('a.article-card')
    valid_links = [l for l in links if l.get('href') and l.get('href') != '#']
    
    if len(valid_links) < len(links):
        issues.append(f"⚠️ {len(links) - len(valid_links)} 篇文章链接无效")
    else:
        print(f"✅ 文章链接：{len(valid_links)} 个有效")
    
    # 总结
    print("\n" + "="*50)
    if issues:
        print("❌ 发现问题：")
        for issue in issues:
            print(f"  {issue}")
    else:
        print("✅ 所有测试通过！")
    print("="*50)
    
    return len(issues) == 0

if __name__ == "__main__":
    test_page()
