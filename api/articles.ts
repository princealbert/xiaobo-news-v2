import type { APIRoute } from 'astro'

// AI Agent 友好的 RESTful API
export const GET: APIRoute = async ({ url }) => {
  const searchParams = url.searchParams
  const category = searchParams.get('category')
  const limit = parseInt(searchParams.get('limit') || '20')
  const offset = parseInt(searchParams.get('offset') || '0')
  const lang = searchParams.get('lang') || 'zh'

  // 构建查询
  let queryUrl = `${import.meta.env.SUPABASE_URL}/rest/v1/articles?select=*&order=publish_date.desc&limit=${limit}&offset=${offset}`
  
  if (category) {
    queryUrl = `${import.meta.env.SUPABASE_URL}/rest/v1/articles?select=*&category=eq.${category}&order=publish_date.desc&limit=${limit}&offset=${offset}`
  }

  const response = await fetch(queryUrl, {
    headers: {
      'apikey': import.meta.env.SUPABASE_KEY,
      'Authorization': `Bearer ${import.meta.env.SUPABASE_KEY}`,
      'Prefer': 'count=exact'
    }
  })
  
  const articles = await response.json()
  const totalCount = response.headers.get('Content-Range')?.split('/')[1] || articles.length

  // API 响应格式（AI Agent 友好）
  const apiResponse = {
    success: true,
    data: {
      articles: articles.map((article: any) => ({
        id: article.id,
        title: article.title,
        summary: article.summary,
        content: article.content,
        category: article.category,
        author: article.author,
        publish_date: article.publish_date,
        image_url: article.image_url,
        link: article.link,
        source: article.source_origin,
        lang: article.lang || 'zh',
        // AI Agent 专用字段
        word_count: article.content?.length || 0,
        reading_time_minutes: Math.ceil((article.content?.length || 0) / 1000)
      })),
      pagination: {
        total: parseInt(totalCount),
        limit,
        offset,
        has_more: offset + articles.length < parseInt(totalCount)
      }
    },
    meta: {
      timestamp: new Date().toISOString(),
      source: 'xiaobo-news-v2',
      version: '1.0'
    }
  }

  return new Response(JSON.stringify(apiResponse, null, 2), {
    status: 200,
    headers: {
      'Content-Type': 'application/json; charset=utf-8',
      'Cache-Control': 'public, s-maxage=300, stale-while-revalidate=600',
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type'
    }
  })
}

// 支持 OPTIONS 预检请求
export const OPTIONS: APIRoute = () => {
  return new Response(null, {
    status: 204,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type'
    }
  })
}
