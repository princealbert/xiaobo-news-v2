import type { APIRoute } from 'astro'

// 分类列表 API - AI Agent 了解内容结构
export const GET: APIRoute = async () => {
  const response = await fetch(
    `${import.meta.env.SUPABASE_URL}/rest/v1/articles?select=category&order=publish_date.desc`,
    {
      headers: {
        'apikey': import.meta.env.SUPABASE_KEY,
        'Authorization': `Bearer ${import.meta.env.SUPABASE_KEY}`
      }
    }
  )
  
  const articles = await response.json()
  
  // 统计每个分类的文章数
  const categoryCount: Record<string, number> = {}
  articles.forEach((article: any) => {
    const cat = article.category || '其他'
    categoryCount[cat] = (categoryCount[cat] || 0) + 1
  })

  const apiResponse = {
    success: true,
    data: {
      categories: Object.entries(categoryCount).map(([name, count]) => ({
        name,
        count,
        slug: name.toLowerCase().replace(/\s+/g, '-')
      })).sort((a, b) => b.count - a.count)
    },
    meta: {
      total_categories: Object.keys(categoryCount).length,
      total_articles: articles.length
    }
  }

  return new Response(JSON.stringify(apiResponse, null, 2), {
    status: 200,
    headers: {
      'Content-Type': 'application/json; charset=utf-8',
      'Cache-Control': 'public, s-maxage=3600',
      'Access-Control-Allow-Origin': '*'
    }
  })
}
