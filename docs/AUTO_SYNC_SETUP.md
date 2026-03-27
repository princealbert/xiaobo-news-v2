# 自动同步与增量更新配置指南

**创建时间**: 2026-03-17  
**版本**: v1.0

---

## 📋 功能概述

### 自动同步 (Automated Sync)
- **作用**: 定时从 RSS 源抓取新文章并同步到 Supabase
- **频率**: 每 6 小时 (北京时间 08:00, 14:00, 20:00, 02:00)
- **执行位置**: GitHub Actions

### 增量更新 (Incremental Update)
- **作用**: 自动更新页面内容，无需手动部署
- **频率**: 
  - ISR: 每小时重新验证
  - 客户端：每 5 分钟后台刷新
- **执行位置**: Vercel CDN + 浏览器

---

## 🔧 配置步骤

### 1. GitHub Actions 自动同步

#### 1.1 配置 Secrets

在 GitHub 仓库中设置以下 Secrets：

```
Settings → Secrets and variables → Actions → New repository secret
```

| Secret Name | Value |
|-------------|-------|
| `SUPABASE_URL` | `https://vmrzypjvjhivzlwjsdug.supabase.co` |
| `SUPABASE_KEY` | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` |
| `VERCEL_DEPLOY_HOOK` | (可选) Vercel Deploy Hook URL |

#### 1.2 获取 Vercel Deploy Hook (可选)

如果希望自动同步后触发 Vercel 重新部署：

1. 打开 Vercel Dashboard
2. 进入项目 Settings → Git
3. 复制 Deploy Hook URL
4. 添加到 GitHub Secrets

#### 1.3 测试工作流

```bash
# 手动触发工作流
GitHub → Actions → Auto Sync Articles → Run workflow
```

---

### 2. Vercel ISR 配置

#### 2.1 修改 Astro 配置

已配置 `astro.config.mjs`:

```javascript
export default defineConfig({
  output: 'hybrid',  // 混合模式
  // ...
})
```

#### 2.2 页面 ISR 配置

已在 `src/pages/index.astro` 添加:

```typescript
export const revalidate = 3600;  // 每小时重新验证
```

#### 2.3 部署到 Vercel

```bash
cd xiaobo_intelligent_news_site_astro
vercel --prod
```

---

### 3. 客户端自动刷新

已在首页添加 JavaScript 自动刷新逻辑：

```javascript
// 每 5 分钟刷新一次
setInterval(fetchLatestArticles, 5 * 60 * 1000);

// 页面可见时刷新
document.addEventListener('visibilitychange', () => {
  if (!document.hidden) fetchLatestArticles();
});
```

---

## 📊 工作流程

```
┌─────────────────────────────────────────────────────────────┐
│              完整自动化流程                                  │
└─────────────────────────────────────────────────────────────┘

1. GitHub Actions (每 6 小时)
   └─→ RSS 抓取 → SQLite → Supabase
   └─→ (可选) 触发 Vercel Deploy Hook

2. Vercel ISR (每小时)
   └─→ 自动重新验证页面
   └─→ 重新生成静态 HTML

3. 客户端 JavaScript (每 5 分钟)
   └─→ 后台获取最新数据
   └─→ 动态更新页面内容

┌─────────────────────────────────────────────────────────────┐
│              数据新鲜度保证                                  │
└─────────────────────────────────────────────────────────────┘

- 数据库：最多延迟 6 小时
- 静态页面：最多延迟 1 小时
- 用户看到：最多延迟 5 分钟
```

---

## 🔍 监控与调试

### 检查 GitHub Actions 执行

```
GitHub → Actions → Auto Sync Articles
```

查看执行日志，确认：
- ✅ RSS 抓取成功
- ✅ Supabase 同步成功
- ✅ (可选) Vercel 部署成功

### 检查 Vercel ISR

```
Vercel Dashboard → Analytics → Function Invocations
```

查看 ISR 重新验证次数和响应时间。

### 客户端调试

打开浏览器控制台，查看日志：
```
🔄 自动刷新已启动 (每 5 分钟)
✅ 文章已自动更新
📄 更新 X 篇文章
```

---

## ⚠️ 注意事项

### 1. GitHub Actions 限制

- **免费额度**: 每月 2000 分钟
- **当前配置**: 每天 4 次 × 约 5 分钟 = 每天 20 分钟
- **月度消耗**: 约 600 分钟 (在免费额度内)

### 2. Supabase 限制

- **免费计划**: 500MB 数据库，50,000 次 API 请求/月
- **当前消耗**: 
  - 自动同步：每天 4 次写入
  - 客户端刷新：每个用户每 5 分钟 1 次读取

### 3. Vercel 限制

- **免费计划**: 100GB 带宽/月， ISR 需要 Pro 计划
- **替代方案**: 如果 ISR 不可用，依赖客户端刷新即可

---

## 🎯 优化建议

### 1. 调整同步频率

如果 RSS 源更新不频繁，可以减少同步次数：

```yaml
# .github/workflows/auto-sync.yml
schedule:
  - cron: '0 2,14 * * *'  # 改为每天 2 次
```

### 2. 智能刷新

只在有新文章时刷新：

```javascript
async function fetchLatestArticles() {
  const response = await fetch(...);
  const articles = await response.json();
  
  // 检查是否有新文章
  const latestId = articles[0]?.id;
  const currentId = window.latestArticleId;
  
  if (latestId !== currentId) {
    updateArticlesGrid(articles);
    window.latestArticleId = latestId;
  }
}
```

### 3. 添加通知

当检测到新文章时，显示通知：

```javascript
if (newArticles.length > 0) {
  showToast(`📰 新增 ${newArticles.length} 篇文章`);
}
```

---

## 📝 故障排查

### 问题 1: GitHub Actions 失败

**症状**: 工作流显示红色 ❌

**解决**:
1. 检查 Secrets 配置是否正确
2. 查看具体错误日志
3. 确认 RSS 源可访问

### 问题 2: Supabase 同步失败

**症状**: 日志显示 API 错误

**解决**:
1. 检查 SUPABASE_KEY 是否过期
2. 确认 articles 表结构正确
3. 检查 RLS 权限配置

### 问题 3: 客户端刷新不工作

**症状**: 控制台没有日志输出

**解决**:
1. 检查浏览器控制台是否有 JavaScript 错误
2. 确认 Supabase URL 和 Key 正确
3. 检查网络请求是否被 CORS 阻止

---

## 📚 相关文件

| 文件 | 说明 |
|------|------|
| `.github/workflows/auto-sync.yml` | GitHub Actions 工作流 |
| `astro.config.mjs` | Astro 配置 (ISR) |
| `src/pages/index.astro` | 首页 (含客户端刷新) |
| `tools/rss_aggregator.py` | RSS 抓取脚本 |
| `tools/sync_to_supabase.py` | Supabase 同步脚本 |

---

*配置完成后，系统将自动运行，无需人工干预。*
