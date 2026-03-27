// Schema.org 结构化数据生成器 - 让 Google 和 AI 理解内容

export interface ArticleSchema {
  id: string
  title: string
  content: string
  summary: string
  category: string
  author: string
  publish_date: string
  image_url?: string
  link?: string
}

export function generateArticleSchema(article: ArticleSchema) {
  return {
    "@context": "https://schema.org",
    "@type": "NewsArticle",
    "headline": article.title,
    "datePublished": article.publish_date,
    "dateModified": new Date().toISOString(),
    "author": {
      "@type": "Organization",
      "name": "晓波智能资讯站",
      "url": "https://xiaobo-news-v2.vercel.app"
    },
    "publisher": {
      "@type": "Organization",
      "name": "晓波智能资讯站",
      "logo": {
        "@type": "ImageObject",
        "url": "https://xiaobo-news-v2.vercel.app/logo.png"
      }
    },
    "articleSection": article.category,
    "wordCount": article.content?.length || 0,
    "inLanguage": "zh-CN",
    "description": article.summary,
    "keywords": [article.category, "AI", "科技新闻", "人工智能"],
    "mainEntityOfPage": {
      "@type": "WebPage",
      "@id": article.link || `https://xiaobo-news-v2.vercel.app/blog/${article.id}`
    },
    ...(article.image_url && {
      "image": {
        "@type": "ImageObject",
        "url": article.image_url
      }
    })
  }
}

export function generateWebsiteSchema() {
  return {
    "@context": "https://schema.org",
    "@type": "WebSite",
    "name": "晓波智能资讯站",
    "alternateName": "XiaoboAI News",
    "url": "https://xiaobo-news-v2.vercel.app",
    "description": "AI 前沿、科技产业、金融科技深度资讯",
    "inLanguage": "zh-CN",
    "publisher": {
      "@type": "Organization",
      "name": "晓波智能资讯站",
      "logo": {
        "@type": "ImageObject",
        "url": "https://xiaobo-news-v2.vercel.app/logo.png"
      }
    },
    "potentialAction": {
      "@type": "SearchAction",
      "target": "https://xiaobo-news-v2.vercel.app/search?q={search_term_string}",
      "query-input": "required name=search_term_string"
    }
  }
}

export function generateBlogPostingSchema(article: ArticleSchema) {
  return {
    "@context": "https://schema.org",
    "@type": "BlogPosting",
    "headline": article.title,
    "datePublished": article.publish_date,
    "dateModified": new Date().toISOString(),
    "author": {
      "@type": "Person",
      "name": article.author || "Molly AI"
    },
    "publisher": {
      "@type": "Organization",
      "name": "晓波智能资讯站",
      "logo": {
        "@type": "ImageObject",
        "url": "https://xiaobo-news-v2.vercel.app/logo.png"
      }
    },
    "description": article.summary,
    "articleBody": article.content,
    "wordCount": article.content?.length || 0,
    "inLanguage": "zh-CN",
    "keywords": [article.category, "AI", "科技"],
    ...(article.image_url && {
      "image": article.image_url
    })
  }
}
