---
// 自动生成 sitemap.xml - 让 Google 和 AI 更容易索引
import type { APIRoute } from 'astro'

export const GET: APIRoute = async () => {
  // 获取所有文章
  const response = await fetch(
    `${import.meta.env.SUPABASE_URL}/rest/v1/articles?select=id,publish_date,category&order=publish_date.desc`,
    {
      headers: {
        'apikey': import.meta.env.SUPABASE_KEY,
        'Authorization': `Bearer ${import.meta.env.SUPABASE_KEY}`
      }
    }
  )
  
  const articles = await response.json()
  const baseUrl = 'https://xiaobo-news-v2.vercel.app'

  const sitemap = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:news="http://www.google.com/schemas/sitemap-news/0.9">
  <!-- 首页 -->
  <url>
    <loc>${baseUrl}</loc>
    <lastmod>${new Date().toISOString()}</lastmod>
    <changefreq>hourly</changefreq>
    <priority>1.0</priority>
  </url>
  
  <!-- 分类页面 -->
  <url>
    <loc>${baseUrl}/blog</loc>
    <lastmod>${new Date().toISOString()}</lastmod>
    <changefreq>daily</changefreq>
    <priority>0.9</priority>
  </url>
  
  <!-- API 端点（AI Agent 友好） -->
  <url>
    <loc>${baseUrl}/api/rss.xml</loc>
    <lastmod>${new Date().toISOString()}</lastmod>
    <changefreq>hourly</changefreq>
    <priority>0.8</priority>
  </url>
  <url>
    <loc>${baseUrl}/api/articles</loc>
    <lastmod>${new Date().toISOString()}</lastmod>
    <changefreq>hourly</changefreq>
    <priority>0.8</priority>
  </url>
  <url>
    <loc>${baseUrl}/api/latest</loc>
    <lastmod>${new Date().toISOString()}</lastmod>
    <changefreq>hourly</changefreq>
    <priority>0.7</priority>
  </url>
  
  <!-- 文章页面 -->
  ${articles.map((article: any) => `
  <url>
    <loc>${baseUrl}/blog/${article.id}</loc>
    <lastmod>${new Date(article.publish_date).toISOString()}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.6</priority>
    <news:news>
      <news:publication>
        <news:name>晓波智能资讯站</news:name>
        <news:language>zh-CN</news:language>
      </news:publication>
      <news:publication_date>${new Date(article.publish_date).toISOString().split('T')[0]}</news:publication_date>
      <news:title>${article.title}</news:title>
    </news:news>
  </url>
  `).join('')}
</urlset>`

  return new Response(sitemap, {
    status: 200,
    headers: {
      'Content-Type': 'application/xml',
      'Cache-Control': 'public, s-maxage=3600'
    }
  })
}
---
