import type { APIRoute } from 'astro'

// 最新文章 API - AI Agent 快速获取最新内容
export const GET: APIRoute = async () => {
  const response = await fetch(
    `${import.meta.env.SUPABASE_URL}/rest/v1/articles?select=*&order=publish_date.desc&limit=10`,
    {
      headers: {
        'apikey': import.meta.env.SUPABASE_KEY,
        'Authorization': `Bearer ${import.meta.env.SUPABASE_KEY}`
      }
    }
  )
  
  const articles = await response.json()

  const apiResponse = {
    success: true,
    data: {
      latest_articles: articles.map((article: any) => ({
        id: article.id,
        title: article.title,
        summary: article.summary,
        category: article.category,
        publish_date: article.publish_date,
        link: article.link,
        image_url: article.image_url
      }))
    },
    meta: {
      updated_at: new Date().toISOString(),
      count: articles.length
    }
  }

  return new Response(JSON.stringify(apiResponse, null, 2), {
    status: 200,
    headers: {
      'Content-Type': 'application/json; charset=utf-8',
      'Cache-Control': 'public, s-maxage=60',
      'Access-Control-Allow-Origin': '*'
    }
  })
}
