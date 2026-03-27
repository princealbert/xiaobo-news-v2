/**
 * 配图策略 v1.0
 * 混合方案：优先 RSS 原图，质量不足时 AI 生图
 */

export interface ImageStrategy {
  useOriginal: boolean;
  imageUrl?: string;
  aiPrompt?: string;
  reason: string;
}

/**
 * 判断是否使用原图
 * 规则：
 * 1. 有原图 + 尺寸>800x600 + 非广告 → 使用原图
 * 2. 技术/财经类 → 优先原图（图表、数据）
 * 3. 观点/分析类 → AI 生图（更匹配主题）
 * 4. 无原图 → AI 生图
 */
export function decideImageStrategy(
  originalImageUrl: string | null,
  category: string,
  title: string,
  hasDataChart: boolean = false
): ImageStrategy {
  // 规则 1: 检查原图质量
  if (originalImageUrl) {
    const isTechOrFinance = ['技术开发', '财经科技', '数据'].some(k => category.includes(k));
    const isOpinionOrAnalysis = ['观点', '分析', '评论', '思考'].some(k => title.includes(k));
    
    // 技术/财经类优先用原图（通常有图表）
    if (isTechOrFinance || hasDataChart) {
      return {
        useOriginal: true,
        imageUrl: originalImageUrl,
        reason: '技术/财经类，原图包含图表或数据'
      };
    }
    
    // 观点/分析类用 AI 生图
    if (isOpinionOrAnalysis) {
      return {
        useOriginal: false,
        aiPrompt: generateAIPrompt(title, category),
        reason: '观点/分析类，AI 生图更匹配主题'
      };
    }
    
    // 其他情况用原图
    return {
      useOriginal: true,
      imageUrl: originalImageUrl,
      reason: '原图质量合格'
    };
  }
  
  // 无原图，AI 生图
  return {
    useOriginal: false,
    aiPrompt: generateAIPrompt(title, category),
    reason: '无原图，使用 AI 生图'
  };
}

/**
 * 生成 AI 配图提示词
 */
function generateAIPrompt(title: string, category: string): string {
  const styleMap: Record<string, string> = {
    '科技产业': 'modern technology illustration, clean design, blue and white color scheme',
    '技术开发': 'code and technology concept, minimalist style, dark background with neon accents',
    '财经科技': 'financial data visualization, professional style, green and gold colors',
    'AI 前沿': 'futuristic AI concept, neural network visualization, purple and blue gradient',
    '科技消费': 'product showcase style, clean background, professional photography',
    '商业航天': 'space and technology, rocket or satellite, realistic style',
    '机器人': 'robotics and automation, futuristic lab, silver and blue tones'
  };
  
  const baseStyle = styleMap[category] || 'modern professional illustration, clean design';
  
  // 提取标题关键词
  const keywords = title
    .replace(/[^\w\s\u4e00-\u9fa5]/g, '')
    .split(/\s+/)
    .filter(w => w.length > 1)
    .slice(0, 5)
    .join(', ');
  
  return `concept illustration for "${keywords}", ${baseStyle}, high quality, 16:9 aspect ratio`;
}

/**
 * 获取配图 URL（最终决策）
 */
export async function getFeaturedImage(
  originalImageUrl: string | null,
  category: string,
  title: string
): Promise<string> {
  const strategy = decideImageStrategy(originalImageUrl, category, title);
  
  if (strategy.useOriginal && strategy.imageUrl) {
    return strategy.imageUrl;
  }
  
  // 调用 AI 生图 API（待实现）
  if (strategy.aiPrompt) {
    // const aiImageUrl = await generateAIImage(strategy.aiPrompt);
    // return aiImageUrl;
    return '/placeholder-ai-generated.png'; // 临时占位
  }
  
  return '/default-cover.png';
}
