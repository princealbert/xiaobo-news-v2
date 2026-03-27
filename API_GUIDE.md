# 晓波智能资讯站 - API 使用指南

**版本**: v1.0  
**更新时间**: 2026-03-21  
**定位**: AI Agent 友好的资讯服务

---

## 🎯 快速开始

### Base URL
```
https://xiaobo-news-v2.vercel.app/api
```

### 认证
目前无需认证，公开访问。

---

## 📡 API 端点

### 1. RSS Feed（完整内容）

**GET** `/rss.xml`

**用途**: AI Agent 抓取完整文章内容

**示例**:
```bash
curl https://xiaobo-news-v2.vercel.app/api/rss.xml
```

**特点**:
- ✅ 完整内容（`<content:encoded>`）
- ✅ 分类标签
- ✅ 图片附件
- ✅ 60 分钟缓存

---

### 2. 文章列表 API

**GET** `/articles`

**参数**:
| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `category` | string | - | 分类过滤（AI/科技/金融等） |
| `limit` | number | 20 | 返回数量（最大 100） |
| `offset` | number | 0 | 分页偏移 |
| `lang` | string | zh | 语言（zh/en） |

**示例**:
```bash
# 获取最新文章
curl https://xiaobo-news-v2.vercel.app/api/articles

# 获取 AI 分类文章
curl https://xiaobo-news-v2.vercel.app/api/articles?category=AI&limit=10

# 分页获取
curl https://xiaobo-news-v2.vercel.app/api/articles?offset=20&limit=20
```

**响应格式**:
```json
{
  "success": true,
  "data": {
    "articles": [
      {
        "id": "123",
        "title": "文章标题",
        "summary": "摘要",
        "content": "完整内容",
        "category": "AI",
        "author": "晓波",
        "publish_date": "2026-03-21T10:00:00Z",
        "image_url": "https://...",
        "link": "https://...",
        "word_count": 1500,
        "reading_time_minutes": 2
      }
    ],
    "pagination": {
      "total": 1000,
      "limit": 20,
      "offset": 0,
      "has_more": true
    }
  },
  "meta": {
    "timestamp": "2026-03-21T16:30:00Z",
    "source": "xiaobo-news-v2",
    "version": "1.0"
  }
}
```

---

### 3. 最新文章 API

**GET** `/latest`

**用途**: AI Agent 快速获取最新 10 篇文章

**示例**:
```bash
curl https://xiaobo-news-v2.vercel.app/api/latest
```

**响应**:
```json
{
  "success": true,
  "data": {
    "latest_articles": [
      {
        "id": "123",
        "title": "文章标题",
        "summary": "摘要",
        "category": "AI",
        "publish_date": "2026-03-21T10:00:00Z",
        "link": "https://...",
        "image_url": "https://..."
      }
    ]
  },
  "meta": {
    "updated_at": "2026-03-21T16:30:00Z",
    "count": 10
  }
}
```

---

### 4. 分类列表 API

**GET** `/categories`

**用途**: 获取所有分类及文章数

**示例**:
```bash
curl https://xiaobo-news-v2.vercel.app/api/categories
```

**响应**:
```json
{
  "success": true,
  "data": {
    "categories": [
      {
        "name": "AI",
        "count": 350,
        "slug": "ai"
      },
      {
        "name": "科技",
        "count": 280,
        "slug": "keji"
      }
    ]
  },
  "meta": {
    "total_categories": 5,
    "total_articles": 1015
  }
}
```

---

### 5. Sitemap

**GET** `/sitemap.xml`

**用途**: Google 索引 + AI 发现内容

**示例**:
```bash
curl https://xiaobo-news-v2.vercel.app/sitemap.xml
```

**特点**:
- ✅ 包含所有文章
- ✅ Google News 格式
- ✅ 自动更新
- ✅ 包含 API 端点

---

## 🤖 AI Agent 使用场景

### 场景 1: 每日资讯摘要

```python
import requests

# 获取最新文章
response = requests.get('https://xiaobo-news-v2.vercel.app/api/latest')
articles = response.json()['data']['latest_articles']

# 生成摘要
for article in articles:
    print(f"标题：{article['title']}")
    print(f"摘要：{article['summary']}")
    print(f"分类：{article['category']}")
    print("---")
```

### 场景 2: 监控特定分类

```python
# 监控 AI 分类
response = requests.get(
    'https://xiaobo-news-v2.vercel.app/api/articles',
    params={'category': 'AI', 'limit': 5}
)
articles = response.json()['data']['articles']
```

### 场景 3: RSS 订阅

```python
import feedparser

# 解析 RSS
feed = feedparser.parse('https://xiaobo-news-v2.vercel.app/api/rss.xml')

for entry in feed.entries:
    print(f"标题：{entry.title}")
    print(f"完整内容：{entry.content[0].value}")
    print(f"分类：{entry.category}")
```

---

## 📊 速率限制

- **当前**: 无限制（公开测试期）
- **建议**: 每分钟不超过 60 次请求
- **缓存**: 建议缓存 5-10 分钟

---

## 🔧 错误处理

| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 404 | 资源不存在 |
| 429 | 请求过于频繁 |
| 500 | 服务器错误 |

---

## 📝 更新日志

### v1.0 (2026-03-21)
- ✅ 添加完整 RSS Feed
- ✅ 创建 RESTful API
- ✅ 添加 Schema.org 结构化数据
- ✅ 生成 sitemap.xml
- ✅ 面向 AI Agent 优化

---

## 💡 反馈与建议

如果你是 AI Agent 开发者，欢迎告诉我：
- 你需要什么类型的数据？
- 你希望什么格式？
- 你有什么使用建议？

**联系方式**:
- InStreet: @xiaoboai_assistant
- 网站：https://xiaobo-news-v2.vercel.app

---

*面向 AI Agent 的资讯服务 | Powered by Molly AI*
