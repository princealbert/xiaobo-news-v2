#!/usr/bin/env python3
"""
SQLite → Supabase 数据迁移脚本

使用前：
1. 在 Supabase 创建项目
2. 运行 supabase_migration.sql 创建表结构
3. 配置 .env 文件中的 SUPABASE_URL 和 SUPABASE_KEY
4. 运行此脚本：python3 tools/migrate_to_supabase.py
"""

import sqlite3
import os
from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import datetime

# 加载环境变量
load_dotenv()

# 配置
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(SCRIPT_DIR, '../xiaobo_intelligent_news.db')
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

def connect_supabase():
    """连接 Supabase"""
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise Exception("请配置 SUPABASE_URL 和 SUPABASE_KEY 环境变量")
    
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def get_sqlite_articles():
    """从 SQLite 读取文章"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM articles 
        ORDER BY publish_date DESC
    """)
    
    articles = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return articles

def migrate_articles(supabase: Client, articles: list):
    """迁移文章到 Supabase"""
    print(f"📦 开始迁移 {len(articles)} 篇文章...")
    
    # 分批插入（每批 100 条）
    batch_size = 100
    total_batches = (len(articles) + batch_size - 1) // batch_size
    
    for i in range(0, len(articles), batch_size):
        batch = articles[i:i + batch_size]
        batch_num = (i // batch_size) + 1
        
        # 转换数据格式
        articles_to_insert = []
        for article in batch:
            # 转换日期格式
            publish_date = article.get('publish_date')
            if publish_date and isinstance(publish_date, str):
                try:
                    publish_date = datetime.strptime(publish_date[:19], "%Y-%m-%d %H:%M:%S").isoformat()
                except:
                    publish_date = None
            
            articles_to_insert.append({
                'title': article.get('title', ''),
                'link': article.get('link', ''),
                'summary': article.get('summary', ''),
                'content': article.get('content', ''),
                'category': article.get('category', ''),
                'sub_category': article.get('sub_category', ''),
                'author': article.get('author', ''),
                'publish_date': publish_date,
                'image_url': article.get('image_url', ''),
                'view_count': article.get('view_count', 0),
                'tags': article.get('tags', ''),
                'ai_tags': article.get('ai_tags', ''),
                'level2': article.get('level2', '')
            })
        
        # 批量插入
        try:
            response = supabase.table('articles').insert(articles_to_insert).execute()
            print(f"  ✅ 批次 {batch_num}/{total_batches}: 插入 {len(response.data)} 篇文章")
        except Exception as e:
            print(f"  ❌ 批次 {batch_num}/{total_batches}: 错误 - {str(e)}")
    
    print(f"🎉 迁移完成！")

def verify_migration(supabase: Client):
    """验证迁移结果"""
    print("\n🔍 验证迁移结果...")
    
    try:
        # 获取总数
        response = supabase.table('articles').select('count', count='exact').execute()
        count = response.count
        print(f"  ✅ Supabase 文章总数：{count}")
        
        # 获取分类统计
        response = supabase.rpc('category_stats').execute()
        if response.data:
            print(f"  ✅ 分类统计可用")
            for cat in response.data[:5]:
                print(f"     - {cat['category']}: {cat['count']}篇")
        
    except Exception as e:
        print(f"  ⚠️ 验证失败：{str(e)}")

def main():
    print("=" * 60)
    print("🚀 SQLite → Supabase 数据迁移工具")
    print("=" * 60)
    
    # 检查 SQLite 数据库
    if not os.path.exists(DB_PATH):
        print(f"❌ 错误：找不到 SQLite 数据库 {DB_PATH}")
        return
    
    # 连接 Supabase
    try:
        supabase = connect_supabase()
        print("✅ 成功连接 Supabase")
    except Exception as e:
        print(f"❌ Supabase 连接失败：{str(e)}")
        print("请检查 .env 文件中的 SUPABASE_URL 和 SUPABASE_KEY")
        return
    
    # 读取 SQLite 数据
    try:
        articles = get_sqlite_articles()
        print(f"✅ 从 SQLite 读取 {len(articles)} 篇文章")
    except Exception as e:
        print(f"❌ 读取 SQLite 失败：{str(e)}")
        return
    
    # 确认迁移
    print(f"\n⚠️ 即将迁移 {len(articles)} 篇文章到 Supabase")
    response = input("确认迁移？(y/N): ")
    if response.lower() != 'y':
        print("❌ 迁移已取消")
        return
    
    # 执行迁移
    try:
        migrate_articles(supabase, articles)
        verify_migration(supabase)
        
        print("\n" + "=" * 60)
        print("✅ 迁移成功完成！")
        print("=" * 60)
        print("\n下一步：")
        print("1. 在 Supabase 控制台验证数据")
        print("2. 更新 API 代码使用 Supabase 客户端")
        print("3. 部署到 Vercel 并配置环境变量")
        
    except Exception as e:
        print(f"\n❌ 迁移失败：{str(e)}")

if __name__ == '__main__':
    main()
