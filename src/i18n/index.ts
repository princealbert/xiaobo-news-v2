export { zh } from './zh';
export { en } from './en';

// 分类翻译映射（中文 → 英文）
export const CATEGORY_MAP: Record<string, string> = {
  'AI': 'AI',
  'AI 前沿': 'AI',
  '科技': 'Tech',
  '科技产业': 'Tech',
  '金融': 'Finance',
  '金融科技': 'FinTech',
  '财经': 'Business',
  '国际财经': 'Business',
  '量化交易': 'Trading',
  '天津': 'Tianjin',
  '天津滨海': 'Tianjin Binhai',
  '天津创业': 'Tianjin Startups',
  '天津产业': 'Tianjin Industry',
  '天津科技': 'Tianjin Tech',
  '天津政策': 'Tianjin Policy',
};

export function translateCategory(category: string, toEn = false): string {
  if (!toEn) return category;
  for (const [zh, en] of Object.entries(CATEGORY_MAP)) {
    if (category.includes(zh)) return en;
  }
  return category;
}
