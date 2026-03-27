import type { APIRoute } from 'astro'

export const GET: APIRoute = async () => {
  const response = await fetch(
    `${import.meta.env.SUPABASE_URL}/rest/v1/articles?select=*&order=publish_date.desc&limit=100`,
    {
      headers: {
        'apikey': import.meta.env.SUPABASE_KEY,
        'Authorization': `Bearer ${import.meta.env.SUPABASE_KEY}`
      }
    }
  )
  
  const articles = await response.json()
  
  // AI Agent 友好的完整 RSS Feed
  const rss = `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" 
  xmlns:atom="http://www.w3.org/2005/Atom"
  xmlns:content="http://purl.org/rss/1.0/modules/content/"
  xmlns:dc="http://purl.org/dc/elements/1.1/">
  <channel>
    <title>晓波智能资讯站 - XiaoboAI News</title>
    <link>https://xiaobo-news-v2.vercel.app</link>
    <description>AI 前沿、科技产业、金融科技深度资讯 | AI-Powered Tech & Finance News</description>
    <language>zh-CN</language>
    <lastBuildDate>${new Date().toUTCString()}</lastBuildDate>
    <atom:link href="https://xiaobo-news-v2.vercel.app/api/rss.xml" rel="self" type="application/rss+xml"/>
    <generator>Molly AI Agent</generator>
    <managingEditor>albert@xiaobo-news.com (Albert Wang)</managingEditor>
    <webMaster>albert@xiaobo-news.com (Albert Wang)</webMaster>
    <ttl>60</ttl>
    ${articles.map((article: any) => `
    <item>
      <title><![CDATA[${article.title}]]></title>
      <link>${article.link || `https://xiaobo-news-v2.vercel.app/blog/${article.id}`}</link>
      <guid isPermaLink="false">${article.id}</guid>
      <description><![CDATA[${article.summary}]]></description>
      <content:encoded><![CDATA[${article.content || article.summary}]]></content:encoded>
      <pubDate>${new Date(article.publish_date).toUTCString()}</pubDate>
      <dc:creator><![CDATA[${article.author || '晓波智能资讯站'}]]></dc:creator>
      <category><![CDATA[${article.category || 'AI'}]]></category>
      ${article.image_url ? `<enclosure url="${article.image_url}" type="image/jpeg" />` : ''}
    </item>
    `).join('')}
  </channel>
</rss>`

  return new Response(rss, {
    status: 200,
    headers: {
      'Content-Type': 'application/rss+xml',
      'Cache-Control': 'public, s-maxage=300, stale-while-revalidate=600',
      'Access-Control-Allow-Origin': '*'
    }
  })
}
