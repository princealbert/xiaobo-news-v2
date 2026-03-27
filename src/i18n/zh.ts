// 中文翻译字符串
export const zh = {
  lang: 'zh-CN',
  locale: 'zh-CN' as const,

  nav: {
    home: '首页',
    news: '资讯',
    about: '关于',
  },

  home: {
    featuredLabel: '精选推荐',
    readMore: '阅读全文',
    loadMore: '加载更多',
    loading: '加载中...',
    sidebarCategories: '分类标签',
    sidebarAds: '广告合作',
    sidebarStats: '站点统计',
    sidebarRecommended: '🎯 推荐阅读',
    adSlot1Title: '广告位招租',
    adSlot1Sub: '精准流量 · 高转化',
    adSlot2Sub: '审核中...',
    statsArticles: '文章总数',
    statsCategories: '分类',
    statsRss: 'RSS 源',
    statsUptime: '正常运行',
    updating: '更新中...',
  },

  footer: {
    aboutUs: '关于我们',
    contact: '联系我们',
    privacy: '隐私政策',
    terms: '服务条款',
    advertise: '广告合作',
    poweredBy: '茉莉空间',
  },

  date: {
    today: '今天',
    yesterday: '昨天',
    daysAgo: (n: number) => `${n}天前`,
    latest: '最新发布',
  },
} as const;

export type ZhI18n = typeof zh;
