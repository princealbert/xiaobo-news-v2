# 英文版文章翻译策略

## 方案对比

| 方案 | 优点 | 缺点 | 推荐度 |
|------|------|------|--------|
| A. 数据库增加字段 | 性能好，SEO友好 | 需要存储空间 | ⭐⭐⭐ |
| B. 实时翻译 API | 无需存储 | 慢，贵，API依赖 | ⭐ |
| C. 构建时翻译 | 平衡 | 构建时间长 | ⭐⭐ |

## 推荐方案 A：数据库增加字段

### 1. Supabase 迁移

```sql
-- 添加英文字段
ALTER TABLE articles ADD COLUMN IF NOT EXISTS title_en TEXT;
ALTER TABLE articles ADD COLUMN IF NOT EXISTS summary_en TEXT;

-- 创建索引加速查询
CREATE INDEX IF NOT EXISTS idx_articles_title_en ON articles(title_en);
```

### 2. 批量翻译脚本

创建 `scripts/translate_articles.py`：

```python
import os
from supabase import create_client
import openai

supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_ANON_KEY')
)
openai.api_key = os.getenv('OPENAI_API_KEY')

def translate_text(text: str) -> str:
    if not text or len(text) < 10:
        return text
    
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Translate the following Chinese text to English. Keep it concise and natural."},
            {"role": "user", "content": text[:1000]}  # Limit length
        ]
    )
    return response.choices[0].message.content

# 批量处理
articles = supabase.table('articles').select('id,title,summary').is_('title_en', None).limit(100).execute()

for article in articles.data:
    title_en = translate_text(article['title'])
    summary_en = translate_text(article['summary'])
    
    supabase.table('articles').update({
        'title_en': title_en,
        'summary_en': summary_en
    }).eq('id', article['id']).execute()
    
    print(f"✓ Translated: {article['id']}")
```

### 3. 代码适配

修改 `src/lib/supabase.ts`：

```typescript
export interface Article {
  id: number;
  title: string;
  title_en?: string;      // 新增
  content: string;
  summary: string;
  summary_en?: string;    // 新增
  category: string;
  // ...
}
```

修改英文版页面，优先使用 `title_en` / `summary_en`：

```astro
<h1>{article.title_en || article.title}</h1>
<p>{article.summary_en || article.summary}</p>
```

## 快速实施步骤

1. 在 Supabase SQL Editor 执行迁移 SQL
2. 设置 OpenAI API Key 环境变量
3. 运行翻译脚本（分批处理避免超限）
4. 更新代码使用新字段
5. 部署验证

## 成本估算

- 1015 篇文章 × 平均 500 tokens ≈ 500K tokens
- GPT-4o-mini: ~$0.15 可完成全部翻译
