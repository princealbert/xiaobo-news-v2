#!/usr/bin/env python3
"""
RSS 聚合器 v6.0 - 统一版本
整合所有功能：中文源 + 英文源 + 爬虫源 + 图片抓取 + 关键字管理 + 文章评分

功能清单：
1. RSS 源管理（中文/英文/自定义）
2. 网页爬虫（Playwright 支持）
3. 图片自动抓取和下载
4. 关键字过滤和匹配
5. 文章 AI 评分和精选
6. 数据库去重存储
7. 双语支持

使用方式：
    python3 tools/rss_aggregator.py              # 默认扫描
    python3 tools/rss_aggregator.py --fast       # 快速模式（仅 RSS）
    python3 tools/rss_aggregator.py --full       # 完整模式（RSS+ 爬虫 + 图片）
    python3 tools/rss_aggregator.py --keywords   # 仅关键字匹配检查
"""

import json
import sqlite3
import requests
import feedparser
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
import re
import os
from dotenv import load_dotenv
import time

load_dotenv()

# ==================== 配置 ====================
WORKSPACE = Path("/Users/albert/documents/茉莉空间")
DB_PATH = WORKSPACE / "xiaobo-news-v2" / "news.db"
RSS_CONFIG = WORKSPACE / "rss_sources_config.json"
KEYWORDS_CONFIG = WORKSPACE / "config" / "keywords.json"
ASSETS_DIR = WORKSPACE / "assets" / "news_images"
ASSETS_DIR.mkdir(parents=True, exist_ok=True)

# 评分配置
AI_SCORE_THRESHOLD = 70  # 精选阈值
KEYWORD_MATCH_WEIGHT = 30  # 关键字匹配权重
CONTENT_QUALITY_WEIGHT = 40  # 内容质量权重
SOURCE_AUTHORITY_WEIGHT = 30  # 源权威性权重

# 主题相关性：核心 AI/科技关键词（命中任一 → 加分；全不命中 → 封顶惩罚）
TOPIC_CORE_KEYWORDS = [
    "AI", "人工智能", "大模型", "LLM", "GPT", "Claude", "Gemini", "DeepSeek",
    "Agent", "智能体", "具身智能", "机器人", "自动驾驶", "自动化",
    "芯片", "半导体", "算力", "GPU", "英伟达", "华为",
    "量化", "量化投资", "量化交易",
    "融资", "创投", "IPO", "独角兽",
    "OpenAI", "Anthropic", "字节跳动", "百度", "阿里", "腾讯", "科大讯飞",
    "神经网络", "机器学习", "深度学习", "多模态",
    "Cursor", "Copilot", "编程", "开源",
]

# 主题无关：命中这些词直接扣分
TOPIC_IRRELEVANT_KEYWORDS = [
    "明星", "八卦", "娱乐", "综艺", "电视剧", "电影明星", "网红", "博主",
    "美食", "旅游攻略", "护肤", "美妆", "时尚", "穿搭",
    "彩票", "足球", "篮球", "体育",
    "去世", "逝世", "病逝", "葬礼",  # 人物讣告（非科技）
]

# ==================== 工具函数 ====================
def parse_date(date_value) -> Optional[datetime]:
    """解析日期，支持多种格式"""
    if not date_value:
        return datetime.now()
    
    # 如果是 datetime 对象
    if isinstance(date_value, datetime):
        return date_value
    
    # 如果是 time.struct_time (feedparser 返回)
    if isinstance(date_value, time.struct_time):
        try:
            return datetime(*date_value[:6])
        except:
            return datetime.now()
    
    # 如果是字符串
    if isinstance(date_value, str):
        try:
            return datetime.fromisoformat(date_value.replace('Z', '+00:00'))
        except:
            pass
        
        # 尝试其他常见格式
        for fmt in ['%a, %d %b %Y %H:%M:%S %Z', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d']:
            try:
                return datetime.strptime(date_value, fmt)
            except:
                continue
    
    return datetime.now()

# ==================== 数据库管理 ====================
class DatabaseManager:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
    
    def connect(self):
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
    
    def init_db(self):
        """初始化数据库表结构"""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                link TEXT UNIQUE,
                summary TEXT,
                content TEXT,
                category TEXT,
                author TEXT,
                publish_date TIMESTAMP,
                image_path TEXT,
                image_url TEXT,
                ai_summary TEXT,
                ai_score INTEGER DEFAULT 0,
                is_featured BOOLEAN DEFAULT FALSE,
                source_origin TEXT,
                language TEXT DEFAULT 'zh',
                en_title TEXT,
                en_summary TEXT,
                keywords_matched TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP,
                is_read INTEGER DEFAULT 0
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS keywords (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                keyword TEXT UNIQUE,
                category TEXT,
                weight INTEGER DEFAULT 10,
                enabled BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS rss_sources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                url TEXT UNIQUE,
                category TEXT,
                language TEXT DEFAULT 'zh',
                enabled BOOLEAN DEFAULT TRUE,
                last_fetch TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.conn.commit()
    
    def article_exists(self, link: str) -> bool:
        self.cursor.execute('SELECT 1 FROM articles WHERE link = ?', (link,))
        return self.cursor.fetchone() is not None
    
    def save_article(self, article: Dict) -> int:
        """保存文章，返回文章 ID"""
        try:
            # 确保日期格式正确
            publish_date = article.get('publish_date')
            if isinstance(publish_date, datetime):
                publish_date = publish_date.isoformat()
            elif isinstance(publish_date, time.struct_time):
                publish_date = datetime(*publish_date[:6]).isoformat()
            
            self.cursor.execute('''
                INSERT OR REPLACE INTO articles 
                (title, link, summary, content, category, author, publish_date, 
                 image_path, image_url, ai_summary, ai_score, is_featured, 
                 source_origin, language, keywords_matched, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                article.get('title'),
                article.get('link'),
                article.get('summary'),
                article.get('content'),
                article.get('category'),
                article.get('author'),
                publish_date,
                article.get('image_path'),
                article.get('image_url'),
                article.get('ai_summary'),
                article.get('ai_score', 0),
                article.get('is_featured', False),
                article.get('source_origin'),
                article.get('language', 'zh'),
                article.get('keywords_matched'),
                datetime.now().isoformat()
            ))
            self.conn.commit()
            return self.cursor.lastrowid
        except Exception as e:
            print(f"   ❌ 保存失败：{e}")
            return -1
    
    def get_unprocessed_articles(self, limit: int = 50) -> List[Dict]:
        """获取未处理的文章"""
        self.cursor.execute('''
            SELECT * FROM articles 
            WHERE ai_summary IS NULL OR ai_summary = ''
            ORDER BY created_at DESC
            LIMIT ?
        ''', (limit,))
        
        columns = [desc[0] for desc in self.cursor.description]
        return [dict(zip(columns, row)) for row in self.cursor.fetchall()]
    
    def update_article_summary(self, article_id: int, ai_summary: str, ai_score: int):
        """更新文章 AI 摘要和评分"""
        is_featured = ai_score >= AI_SCORE_THRESHOLD
        self.cursor.execute('''
            UPDATE articles 
            SET ai_summary = ?, ai_score = ?, is_featured = ?, updated_at = ?
            WHERE id = ?
        ''', (ai_summary, ai_score, is_featured, datetime.now().isoformat(), article_id))
        self.conn.commit()
    
    def close(self):
        if self.conn:
            self.conn.close()

# ==================== 关键字管理 ====================
class KeywordManager:
    def __init__(self, config_path: Path):
        self.config_path = config_path
        self.keywords = []
        self.load_keywords()
    
    def load_keywords(self):
        """加载关键字配置"""
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                self.keywords = config.get('keywords', [])
        else:
            # 默认关键字
            self.keywords = [
                {"keyword": "AI 智能体", "category": "AI", "weight": 30, "enabled": True},
                {"keyword": "大模型", "category": "AI", "weight": 25, "enabled": True},
                {"keyword": "自动驾驶", "category": "AI", "weight": 20, "enabled": True},
                {"keyword": "机器人", "category": "AI", "weight": 20, "enabled": True},
                {"keyword": "OpenClaw", "category": "工具", "weight": 25, "enabled": True},
                {"keyword": "自动化", "category": "工具", "weight": 15, "enabled": True},
                {"keyword": "创业", "category": "商业", "weight": 15, "enabled": True},
                {"keyword": "融资", "category": "商业", "weight": 20, "enabled": True},
            ]
            self.save_keywords()
    
    def save_keywords(self):
        """保存关键字配置"""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump({"keywords": self.keywords}, f, ensure_ascii=False, indent=2)
    
    def match_keywords(self, text: str) -> tuple:
        """匹配关键字，返回 (匹配列表，总分)"""
        if not text:
            return [], 0
        
        matched = []
        total_weight = 0
        
        for kw in self.keywords:
            if kw.get('enabled', True) and kw['keyword'] in text:
                matched.append(kw['keyword'])
                total_weight += kw.get('weight', 10)
        
        return matched, total_weight
    
    def add_keyword(self, keyword: str, category: str = "通用", weight: int = 10):
        """添加关键字"""
        if not any(k['keyword'] == keyword for k in self.keywords):
            self.keywords.append({
                "keyword": keyword,
                "category": category,
                "weight": weight,
                "enabled": True
            })
            self.save_keywords()
            print(f"   ✅ 添加关键字：{keyword}")
    
    def remove_keyword(self, keyword: str):
        """移除关键字"""
        self.keywords = [k for k in self.keywords if k['keyword'] != keyword]
        self.save_keywords()
        print(f"   ✅ 移除关键字：{keyword}")
    
    def list_keywords(self):
        """列出所有关键字"""
        print("\n📑 关键字列表:")
        for kw in sorted(self.keywords, key=lambda x: x.get('weight', 0), reverse=True):
            status = "✅" if kw.get('enabled', True) else "⏸️"
            print(f"   {status} {kw['keyword']:20} [{kw.get('category', '通用')}] 权重：{kw.get('weight', 10)}")

# ==================== RSS 源管理 ====================
class RSSSourceManager:
    def __init__(self, config_path: Path):
        self.config_path = config_path
        self.sources = []
        self.load_sources()
    
    def load_sources(self):
        """加载 RSS 源配置"""
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                # 合并中文源和英文源
                for key in ['chinese_sources', 'english_sources', 'custom_sources']:
                    if key in config:
                        for source in config[key].get('sources', []):
                            if source.get('enabled', True):
                                source['language'] = 'zh' if key == 'chinese_sources' else 'en'
                                self.sources.append(source)
    
    def get_sources(self, language: str = None) -> List[Dict]:
        """获取 RSS 源列表"""
        if language:
            return [s for s in self.sources if s.get('language') == language]
        return self.sources
    
    def add_source(self, name: str, url: str, category: str = "通用", language: str = "zh"):
        """添加 RSS 源"""
        if not any(s['url'] == url for s in self.sources):
            self.sources.append({
                "name": name,
                "url": url,
                "category": category,
                "language": language,
                "enabled": True
            })
            print(f"   ✅ 添加 RSS 源：{name}")
    
    def remove_source(self, url: str):
        """移除 RSS 源"""
        self.sources = [s for s in self.sources if s['url'] != url]
        print(f"   ✅ 移除 RSS 源：{url}")

# ==================== 图片抓取 ====================
class ImageFetcher:
    @staticmethod
    def extract_from_html(html_content: str) -> Optional[str]:
        """从 HTML 中提取第一张图片"""
        if not html_content:
            return None
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 尝试多个选择器
        selectors = [
            'img',
            'meta[property="og:image"]',
            'meta[name="twitter:image"]',
            '.article-image img',
            '.post-thumbnail img',
        ]
        
        for selector in selectors:
            elements = soup.select(selector)
            for elem in elements:
                if selector.startswith('meta'):
                    img_url = elem.get('content')
                else:
                    img_url = elem.get('src')
                
                if img_url:
                    return img_url
        
        return None
    
    @staticmethod
    def download_image(image_url: str, article_id: int) -> Optional[str]:
        """下载图片到本地"""
        try:
            if not image_url:
                return None
            
            # 规范化 URL
            if image_url.startswith('//'):
                image_url = 'https:' + image_url
            
            # 下载图片
            response = requests.get(image_url, timeout=10, stream=True)
            response.raise_for_status()
            
            # 生成文件名
            ext = Path(image_url.split('?')[0]).suffix or '.jpg'
            filename = f"article_{article_id}{ext}"
            filepath = ASSETS_DIR / filename
            
            # 保存图片
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            return str(filepath)
        
        except Exception as e:
            print(f"   ⚠️ 图片下载失败：{e}")
            return None

# ==================== 文章评分 ====================
class ArticleScorer:
    def __init__(self, keyword_manager: KeywordManager, source_manager: RSSSourceManager = None):
        self.keyword_manager = keyword_manager
        self.source_manager = source_manager
        # 从 source_manager 构建权威性映射
        self._authority_map = self._build_authority_map() if source_manager else {}
    
    def _build_authority_map(self) -> dict:
        """从 RSS 源配置构建权威性映射"""
        authority_map = {}
        for source in self.source_manager.get_sources():
            authority_map[source['name']] = source.get('authority', 15)
        return authority_map
    
    def calculate_score(self, article: Dict) -> int:
        """计算文章综合评分 (0-100)
        
        评分维度（v2.0，加入主题相关性）：
          A. 主题相关性：+20（命中核心词）/ -10（命中无关词）/ 封顶限制
          B. 关键字匹配：0-30 分（按关键词权重归一化）
          C. 内容质量：0-40 分（字段完整度）
          D. 源权威性：0-30 分（RSS 源配置 authority）
        """
        title    = article.get('title', '')
        summary  = article.get('summary', '') or ''
        content  = article.get('content', '') or ''
        
        # 36 氪「9点1氪」等聚合日报标题包含多条新闻用 ｜ 分隔，
        # 只取第一段评分，避免虚假命中
        title_for_score = title.split('｜')[0].split('|')[0].strip()[:80]
        text_all = f"{title_for_score} {summary[:300]} {content[:500]}"
        
        # ── A. 主题相关性 ──────────────────────────────────────────
        topic_bonus = 0
        
        # 命中无关词：直接硬性封顶 40 分（内容质量再好也没用）
        has_irrelevant = any(kw in text_all for kw in TOPIC_IRRELEVANT_KEYWORDS)
        
        # 命中核心 AI/科技词数量
        core_hits = sum(1 for kw in TOPIC_CORE_KEYWORDS if kw in text_all)
        
        if has_irrelevant and core_hits == 0:
            # 纯八卦/娱乐，直接限制分数上限为 40
            cap_score = 40
        else:
            cap_score = 100
        
        if core_hits >= 3:
            topic_bonus = 20   # 强相关
        elif core_hits >= 1:
            topic_bonus = 10   # 弱相关
        else:
            topic_bonus = -5   # 无相关词，轻微扣分
        
        # ── B. 关键字匹配 (0-30 分) ──────────────────────────────
        matched, keyword_score = self.keyword_manager.match_keywords(text_all)
        article['keywords_matched'] = ','.join(matched) if matched else None
        kw_part = min(30, (keyword_score / 100) * 30)
        
        # ── C. 内容质量 (0-40 分) ────────────────────────────────
        content_quality = self._assess_content_quality(article)
        quality_part = content_quality * 0.4
        
        # ── D. 源权威性 (0-30 分) ────────────────────────────────
        source_score = self._get_source_authority(article.get('source_origin', ''))
        
        # ── 合计 ─────────────────────────────────────────────────
        score = topic_bonus + kw_part + quality_part + source_score
        return int(min(cap_score, max(0, score)))
    
    def _assess_content_quality(self, article: Dict) -> int:
        """评估内容质量 (0-100)"""
        quality = 0
        
        # 有摘要
        if article.get('summary'):
            quality += 20
        
        # 有内容
        content = article.get('content', '')
        if content:
            quality += 20
            # 内容长度适中
            if 200 < len(content) < 3000:
                quality += 20
        
        # 有图片
        if article.get('image_url'):
            quality += 20
        
        # 有作者
        if article.get('author'):
            quality += 10
        
        # 发布时间较新
        if article.get('publish_date'):
            try:
                pub_date = parse_date(article['publish_date'])
                if (datetime.now() - pub_date).days <= 3:
                    quality += 10
            except:
                pass
        
        return quality
    
    def _get_source_authority(self, source: str) -> int:
        """评估源权威性 (0-30)，从配置文件读取"""
        # 先尝试从配置文件读取
        if self._authority_map and source in self._authority_map:
            return self._authority_map[source]
        # 兜底：如果配置文件没有，使用默认值
        return 15

# ==================== RSS 抓取 ====================
class RSSFetcher:
    @staticmethod
    def fetch_feed(url: str) -> Optional[feedparser.FeedParserDict]:
        """获取 RSS 源"""
        try:
            response = requests.get(url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            })
            response.raise_for_status()
            return feedparser.parse(response.content)
        except Exception as e:
            print(f"   ❌ 获取 RSS 失败 {url}: {e}")
            return None
    
    @staticmethod
    def parse_entries(feed: feedparser.FeedParserDict, source_info: Dict) -> List[Dict]:
        """解析 RSS 条目"""
        articles = []
        
        for entry in feed.entries[:20]:  # 每个源最多 20 篇
            # 解析日期
            publish_date = entry.get('published_parsed') or entry.get('updated_parsed')
            publish_date = parse_date(publish_date)
            
            article = {
                'title': entry.get('title', ''),
                'link': entry.get('link', ''),
                'summary': entry.get('summary', entry.get('description', '')),
                'content': '',
                'category': source_info.get('category', '通用'),
                'author': entry.get('author', ''),
                'publish_date': publish_date,
                'image_url': None,
                'source_origin': source_info.get('name', ''),
                'language': source_info.get('language', 'zh'),
            }
            
            # 提取图片
            image_fields = ['media_content', 'media_thumbnail', 'image', 'enclosures']
            for field in image_fields:
                if field in entry:
                    value = entry[field]
                    if isinstance(value, list) and len(value) > 0:
                        article['image_url'] = value[0].get('url')
                        break
                    elif isinstance(value, str):
                        article['image_url'] = value
                        break
            
            # 如果 RSS 中没有图片，尝试从 summary 中提取
            if not article['image_url'] and article['summary']:
                article['image_url'] = ImageFetcher.extract_from_html(article['summary'])
            
            articles.append(article)
        
        return articles

# ==================== 主聚合器 ====================
class RSSAggregator:
    def __init__(self, mode: str = 'full'):
        self.mode = mode  # 'fast', 'full', 'keywords'
        self.db = DatabaseManager(DB_PATH)
        self.db.connect()
        self.db.init_db()
        
        self.keyword_manager = KeywordManager(KEYWORDS_CONFIG)
        self.source_manager = RSSSourceManager(RSS_CONFIG)
        self.scorer = ArticleScorer(self.keyword_manager, self.source_manager)
        
        self.stats = {
            'total_sources': 0,
            'fetched_articles': 0,
            'new_articles': 0,
            'featured_articles': 0,
            'errors': 0
        }
    
    def run(self):
        """运行聚合器"""
        print(f"\n🦞 Molly RSS 聚合器 v6.0 [{'完整模式' if self.mode == 'full' else '快速模式'}]")
        print("=" * 60)
        
        sources = self.source_manager.get_sources()
        self.stats['total_sources'] = len(sources)
        
        print(f"📡 RSS 源数量：{len(sources)}")
        print(f"📑 关键字数量：{len(self.keyword_manager.keywords)}")
        print(f"💾 数据库：{DB_PATH}")
        print("=" * 60)
        
        # 遍历所有 RSS 源
        for source in sources:
            print(f"\n📰 抓取：{source['name']} ({source['url']})")
            
            # 处理 Crawler 类型源（如 GitHub Trending）
            if source.get('type') == 'crawler':
                articles = self._fetch_crawler(source)
                if not articles:
                    self.stats['errors'] += 1
                    continue
                self.stats['fetched_articles'] += len(articles)
                for article in articles:
                    self._process_article(article)
                continue
            
            feed = RSSFetcher.fetch_feed(source['url'])
            if not feed:
                self.stats['errors'] += 1
                continue
            
            articles = RSSFetcher.parse_entries(feed, source)
            self.stats['fetched_articles'] += len(articles)
            
            # 处理每篇文章
            for article in articles:
                self._process_article(article)
        
        # 输出统计
        self._print_stats()
        
        self.db.close()
    
    def _fetch_crawler(self, source: Dict) -> List[Dict]:
        """处理爬虫类型的数据源"""
        url = source.get('url', '')
        
        # GitHub Trending
        if 'github.com/trending' in url:
            try:
                # 动态导入避免循环依赖
                import sys
                sys.path.insert(0, str(WORKSPACE / 'tools'))
                from github_trending import fetch_trending
                
                # 从 URL 提取语言参数
                language = ''
                if 'l=python' in url:
                    language = 'Python'
                elif 'l=javascript' in url:
                    language = 'JavaScript'
                elif 'l=typescript' in url:
                    language = 'TypeScript'
                elif 'l=go' in url:
                    language = 'Go'
                elif 'l=rust' in url:
                    language = 'Rust'
                
                projects = fetch_trending(language=language if language else '')
                
                # 转换为统一格式
                articles = []
                for p in projects:
                    articles.append({
                        'title': p['title'],
                        'link': p['url'],
                        'summary': p['description'],
                        'content': p['description'],
                        'author': '',
                        'source': source['name'],
                        'category': source.get('category', '开源'),
                        'language': 'en',
                        'image_url': '',
                        'published_at': p['published_at'],
                        'tags': p.get('tags', []),
                        'stars_today': p.get('stars_today', 0),
                    })
                
                print(f"   ✅ GitHub Trending: {len(articles)} 个项目")
                return articles
                
            except Exception as e:
                print(f"   ❌ GitHub Trending 抓取失败: {e}")
                return []
        
        print(f"   ⚠️ 未知爬虫类型: {url}")
        return []
    
    def _process_article(self, article: Dict):
        """处理单篇文章"""
        # 检查是否已存在
        if self.db.article_exists(article['link']):
            return
        
        # 计算评分
        article['ai_score'] = self.scorer.calculate_score(article)
        article['is_featured'] = article['ai_score'] >= AI_SCORE_THRESHOLD
        
        if article['is_featured']:
            self.stats['featured_articles'] += 1
        
        # 下载图片（完整模式）
        if self.mode == 'full' and article.get('image_url'):
            article['image_path'] = ImageFetcher.download_image(
                article['image_url'],
                hash(article['link']) % 100000
            )
        
        # 保存到数据库
        article_id = self.db.save_article(article)
        if article_id > 0:
            self.stats['new_articles'] += 1
            print(f"   ✅ 新增：{article['title'][:50]}... (评分：{article['ai_score']})")
    
    def _print_stats(self):
        """输出统计信息"""
        print("\n" + "=" * 60)
        print("📊 聚合统计:")
        print(f"   RSS 源数量：{self.stats['total_sources']}")
        print(f"   获取文章：{self.stats['fetched_articles']}")
        print(f"   新增文章：{self.stats['new_articles']}")
        print(f"   精选文章：{self.stats['featured_articles']}")
        print(f"   错误次数：{self.stats['errors']}")
        print("=" * 60)

# ==================== CLI 入口 ====================
if __name__ == '__main__':
    import sys
    
    mode = 'full'
    if '--fast' in sys.argv:
        mode = 'fast'
    elif '--keywords' in sys.argv:
        mode = 'keywords'
    
    aggregator = RSSAggregator(mode=mode)
    aggregator.run()
