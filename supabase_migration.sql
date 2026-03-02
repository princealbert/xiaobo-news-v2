-- Supabase 数据库迁移脚本
-- 在 Supabase SQL Editor 中运行此脚本

-- 创建 articles 表
CREATE TABLE IF NOT EXISTS articles (
    id BIGSERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    link TEXT UNIQUE,
    summary TEXT,
    content TEXT,
    category TEXT,
    sub_category TEXT,
    author TEXT,
    publish_date TIMESTAMPTZ,
    image_url TEXT,
    view_count INTEGER DEFAULT 0,
    tags TEXT,
    ai_tags TEXT,
    level2 TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 创建索引优化查询
CREATE INDEX IF NOT EXISTS idx_articles_category ON articles(category);
CREATE INDEX IF NOT EXISTS idx_articles_sub_category ON articles(sub_category);
CREATE INDEX IF NOT EXISTS idx_articles_publish_date ON articles(publish_date DESC);
CREATE INDEX IF NOT EXISTS idx_articles_category_date ON articles(category, publish_date DESC);

-- 创建分类视图
CREATE OR REPLACE VIEW category_stats AS
SELECT 
    category,
    sub_category,
    COUNT(*) as count
FROM articles
WHERE category IS NOT NULL
GROUP BY category, sub_category
ORDER BY count DESC;

-- 启用 Row Level Security (可选，根据需求)
ALTER TABLE articles ENABLE ROW LEVEL SECURITY;

-- 创建公开读取策略
CREATE POLICY "Public articles are viewable by everyone" 
ON articles FOR SELECT 
USING (true);

-- 创建插入策略 (仅服务角色)
CREATE POLICY "Service role can insert articles" 
ON articles FOR INSERT 
WITH CHECK (true);

-- 创建更新策略 (仅服务角色)
CREATE POLICY "Service role can update articles" 
ON articles FOR UPDATE 
USING (true);

-- 创建删除策略 (仅服务角色)
CREATE POLICY "Service role can delete articles" 
ON articles FOR DELETE 
USING (true);

-- 输出表结构信息
SELECT 
    'articles' as table_name,
    COUNT(*) as row_count,
    pg_size_pretty(pg_total_relation_size('articles')) as table_size
FROM articles;
