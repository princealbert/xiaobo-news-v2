import { createClient } from '@supabase/supabase-js';

const supabaseUrl = import.meta.env.SUPABASE_URL;
const supabaseAnonKey = import.meta.env.SUPABASE_ANON_KEY;

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error('Missing Supabase environment variables: SUPABASE_URL and SUPABASE_ANON_KEY must be set');
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey);

export interface Article {
  id: number;
  title: string;
  content: string;
  summary: string;
  category: string;
  author: string;
  publish_date: string;
  image_url?: string;
  link?: string;
}

export async function getFeaturedArticles(limit: number = 6): Promise<Article[]> {
  const { data: articlesWithImages, error: error1 } = await supabase
    .from('articles')
    .select('*')
    .not('image_url', 'is', null)
    .not('publish_date', 'is', null)
    .order('publish_date', { ascending: false })
    .limit(limit);
  
  if (error1) {
    console.error('Error fetching articles with images:', error1);
    return [];
  }
  
  if (articlesWithImages && articlesWithImages.length < limit) {
    const remaining = limit - articlesWithImages.length;
    const { data: otherArticles, error: error2 } = await supabase
      .from('articles')
      .select('*')
      .not('publish_date', 'is', null)
      .order('publish_date', { ascending: false })
      .limit(remaining);
    
    if (error2) {
      console.error('Error fetching other articles:', error2);
      return articlesWithImages || [];
    }
    
    return [...(articlesWithImages || []), ...(otherArticles || [])];
  }
  
  return articlesWithImages || [];
}

export async function getArticles(limit: number = 20, offset: number = 0): Promise<Article[]> {
  const { data, error } = await supabase
    .from('articles')
    .select('*')
    .not('publish_date', 'is', null)
    .order('publish_date', { ascending: false })
    .range(offset, offset + limit - 1);
  
  if (error) {
    console.error('Error fetching articles:', error);
    return [];
  }
  
  return data || [];
}

export async function getArticleById(id: number): Promise<Article | null> {
  const { data, error } = await supabase
    .from('articles')
    .select('*')
    .eq('id', id)
    .single();
  
  if (error) {
    console.error('Error fetching article:', error);
    return null;
  }
  
  return data;
}

export async function getAllArticleIds(): Promise<number[]> {
  const { data, error } = await supabase
    .from('articles')
    .select('id');
  
  if (error) {
    console.error('Error fetching article ids:', error);
    return [];
  }
  
  return (data || []).map(a => a.id);
}
