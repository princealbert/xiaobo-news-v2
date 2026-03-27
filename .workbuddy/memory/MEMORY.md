# MEMORY.md — 晓波资讯站长期记忆

## 项目概况

- **项目路径**：`/Users/albert/Documents/茉莉空间/xiaobo-news-v2`
- **项目名**：晓波资讯（xiaoboAI / 晓波智能）
- **技术栈**：Astro 6 + React 19 + Tailwind CSS 4 + Supabase + Vercel
- **部署**：GitHub Actions → Vercel 静态部署（output: 'static'）
- **数据库**：Supabase（articles 表，1015+ 篇）
- **站点 URL**：https://xiaobo-news.com

## 关键配置

- Supabase URL：`https://vmrzypjvjhivzlwjsdug.supabase.co`（anon key 已在代码中，建议迁移到环境变量）
- siteConfig 位于 `src/config/site.ts`，品牌名"晓波智能"，双层 IP：晓波智能/xiaoboAI + 花眼道士
- AdSense publisher ID：`ca-pub-6726601289992127`（当前 enable: false）

## 2026-03-25 已完成的优化

### P0 修复
- data-category 语法错误已修复，分类过滤功能恢复正常
- 英文版 lang="en" 已修正
- 英文版广告位/按钮/日期/console 等中文残留全部替换

### 数据接入
- /blog 和 /en/blog 已接入 Supabase 真实数据（20篇/页 + 加载更多）

### i18n 框架
- src/i18n/zh.ts、en.ts、index.ts 已建立
- 英文主页使用 i18n 字符串，translateCategory() 统一管理分类翻译
- 双语主页均已加 hreflang 标签 + 语言切换按钮

### 视觉统一
- BaseLayout.astro 重写，蓝色渐变玻璃风，支持 lang prop 自动切换语言
- about/blog/contact 等所有次级页面自动继承统一风格

## 文件结构要点

- 主页：`src/pages/index.astro`（完整实现，含 hreflang + 语言切换）
- 英文主页：`src/pages/en/index.astro`（i18n 驱动，含 CategoryNav）
- BaseLayout：`src/layouts/BaseLayout.astro`（已升级，支持 lang prop）
- i18n：`src/i18n/zh.ts` / `src/i18n/en.ts` / `src/i18n/index.ts`
- 数据层：`src/lib/supabase.ts`
- 站点配置：`src/config/site.ts`

## 待办（下次继续）

- [ ] 评估 output:'static' → 'hybrid' 切换（实时数据 vs 构建时快照）
- [x] 文章详情页路由（src/pages/article/[id].astro）✅ 2026-03-25
- [x] 英文版文章内容翻译策略（Supabase 增加 title_en/summary_en 字段）✅ 2026-03-25（文档已创建）
- [x] @astrojs/sitemap 在 astro.config.mjs 中启用 ✅ 2026-03-25
- [x] Supabase key 迁移到环境变量 ✅ 2026-03-25

## 2026-03-25 设计优化（降低AI感）

### 已完成的视觉优化
- **去除所有emoji**：CategoryNav、标签云、文章列表等处的emoji全部替换为Lucide风格SVG图标
- **配色系统升级**：
  - 主色调从 #0077b6/#00b4d8 改为 #1e40af/#3b82f6（更沉稳的深蓝）
  - 背景渐变从亮青蓝改为深蓝系（#1e3a5f → #2563eb → #3b82f6）
  - 文字色从 #1a202c/#2d3748 改为 #0f172a/#334155（更专业的灰度）
- **玻璃拟态优化**：blur(20px) → blur(12px)，阴影更柔和自然
- **卡片样式优化**：
  - 圆角从20px降至12px，更克制
  - hover效果从translateY(-10px)改为translateY(-4px)
  - 阴影从彩色改为中性色
- **按钮优化**：去除过度渐变，使用更简洁的扁平设计
- **标签云优化**：从渐变彩色改为浅灰背景，去除阴影

### 设计原则
- 降低饱和度，提升专业感
- 减少动画幅度，更克制
- 统一使用CSS变量管理颜色
- 圆角更保守（12px为主）

## 新增待办

- [ ] 执行数据库迁移（添加 title_en/summary_en 字段）
- [ ] 运行批量翻译脚本填充英文内容
- [ ] 更新英文版详情页优先使用 title_en/summary_en
- [ ] GitHub Secrets 配置（SUPABASE_URL, SUPABASE_ANON_KEY）
- [ ] 验证部署流程（环境变量注入是否正常）
- [ ] 引入衬线字体用于标题（可选，进一步提升设计感）
