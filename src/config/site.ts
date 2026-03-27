export const siteConfig = {
  name: "晓波智能资讯站",
  description: "AI 前沿、科技产业、金融科技深度资讯",
  url: "https://xiaobo-news.com",
  ogImage: "/og.png",
  links: {
    twitter: "https://twitter.com/xiaobonews",
    github: "https://github.com/xiaobo/xiaobo-news",
  },
  keywords: [
    "AI 资讯",
    "人工智能",
    "科技新闻",
    "金融科技",
    "大模型",
    "机器学习",
    "深度学习"
  ],
  author: "晓波",
  adsense: {
    publisher: "ca-pub-6726601289992127", // 替换为你的 AdSense Publisher ID
    enable: false // AdSense 审批通过后改为 true
  }
};

export type SiteConfig = typeof siteConfig;
