import { createClient } from '@supabase/supabase-js';

// Supabase 配置
const supabaseUrl = import.meta.env.SUPABASE_URL || 'https://your-project.supabase.co';
const supabaseKey = import.meta.env.SUPABASE_KEY || 'your-anon-key';

export const supabase = createClient(supabaseUrl, supabaseKey);

export interface Article {
  id: number;
  title: string;
  content: string;
  summary: string;
  category: string;
  tags: string[];
  author: string;
  pubDate: string;
  imageUrl?: string;
  views: number;
}

export async function getFeaturedArticles(limit: number = 6): Promise<Article[]> {
  const { data, error } = await supabase
    .from('articles')
    .select('*')
    .order('pubDate', { ascending: false })
    .limit(limit);
  
  if (error) {
    console.error('Error fetching articles:', error);
    return [];
  }
  
  return data || [];
}

export async function getArticlesByCategory(category: string, limit: number = 20): Promise<Article[]> {
  const { data, error } = await supabase
    .from('articles')
    .select('*')
    .eq('category', category)
    .order('pubDate', { ascending: false })
    .limit(limit);
  
  if (error) {
    console.error('Error fetching articles:', error);
    return [];
  }
  
  return data || [];
}

export async function searchArticles(keyword: string): Promise<Article[]> {
  const { data, error } = await supabase
    .from('articles')
    .select('*')
    .or(`title.ilike.%${keyword}%,content.ilike.%${keyword}%`)
    .order('pubDate', { ascending: false });
  
  if (error) {
    console.error('Error searching articles:', error);
    return [];
  }
  
  return data || [];
}
