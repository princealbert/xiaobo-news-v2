# 晓波智能资讯站 - Astro 迁移部署指南

**版本**: v2.0 (Astro)  
**创建时间**: 2026-03-16

---

## 🎯 迁移目标

1. **技术栈升级**: 静态 HTML → Astro 现代化框架
2. **SEO 优化**: 完善 Meta 标签、sitemap、结构化数据
3. **性能提升**: Lighthouse 95+，首屏加载 < 1.5 秒
4. **广告变现**: Google AdSense 集成
5. **数据分析**: Google Analytics 4 集成

---

## 📋 部署步骤

### 1. 本地开发

```bash
cd xiaobo_intelligent_news_site_astro
npm install
npm run dev
```

访问 http://localhost:4321 预览

### 2. 内容迁移

```bash
# 从旧站迁移 1500+ 文章
python tools/migrate_content.py
```

### 3. 构建生产版本

```bash
npm run build
```

输出目录：`dist/`

### 4. Vercel 部署

```bash
# 安装 Vercel CLI
npm i -g vercel

# 部署
cd xiaobo_intelligent_news_site_astro
vercel --prod
```

### 5. 配置自定义域名

1. Vercel 控制台 → Settings → Domains
2. 添加域名：`xiaobo-news.com`
3. 配置 DNS CNAME 记录

### 6. AdSense 配置

1. 获取 Publisher ID (审批邮件)
2. 修改 `src/config/site.ts`:
   ```ts
   adsense: {
     publisher: "ca-pub-你的 ID",
     enable: true
   }
   ```
3. 重新部署

### 7. Google Analytics 配置

1. 创建 GA4 属性
2. 获取 Measurement ID (G-XXXXXXXXXX)
3. 添加到 `src/layouts/BaseLayout.astro`

---

## 📊 性能优化清单

- [ ] 图片优化 (WebP 格式，懒加载)
- [ ] 字体优化 (预加载，系统字体优先)
- [ ] CSS 压缩
- [ ] JS 按需加载
- [ ] CDN 配置
- [ ] 缓存策略

---

## 🔍 SEO 优化清单

- [ ] 每篇文章 unique title/description
- [ ] sitemap.xml 生成
- [ ] robots.txt 配置
- [ ] 结构化数据 (Schema.org)
- [ ] Open Graph 标签
- [ ] Twitter Card 标签

---

## 💰 广告变现清单

- [ ] AdSense 审批通过
- [ ] 首页顶部广告位
- [ ] 文章底部广告位
- [ ] 侧边栏广告位
- [ ] 广告性能追踪

---

## 📈 数据分析清单

- [ ] GA4 基础追踪
- [ ] 页面浏览事件
- [ ] 点击事件追踪
- [ ] 广告收入追踪
- [ ] 自定义报表

---

## 🚀 下一步

1. **内容迁移**: 迁移 1500+ 历史文章
2. **SEO 优化**: 关键词研究，优化标题描述
3. **性能测试**: Lighthouse 跑分 95+
4. **广告上线**: AdSense 审批通过后立即部署
5. **数据监控**: 每日检查流量和收入数据

---

*创建时间：2026-03-16*  
*负责人：资讯站开发 Agent + 晓波*
