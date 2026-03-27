# AdSense 配置和审核修复指南

## ✅ 已完成的修复 (2026-03-22)

### 1. 广告展示位置修复
- ✅ 从 `BaseLayout.astro` 移除全局 AdSense
- ✅ 只在 `BlogPost.astro`（文章页）加载广告
- ✅ 移除首页广告代码
- ✅ 确保 404 页面无广告

### 2. 必要页面创建
- ✅ `/about` - 关于我们
- ✅ `/contact` - 联系我们  
- ✅ `/privacy` - 隐私政策

---

## 🔧 下一步操作

### 第 1 步：配置 AdSense ID

编辑 `src/config/site.ts`：

```typescript
adsense: {
  publisher: "ca-pub-你的真实 ID", // 替换为你的 Publisher ID
  slot: "你的广告位 ID",          // 替换为你的广告位 ID
  enable: false // 先保持 false，审核通过后再改 true
}
```

### 第 2 步：部署代码

```bash
cd /Users/albert/documents/茉莉空间/xiaobo-news-v2
git add .
git commit -m "fix: AdSense 审核修复，添加必要页面"
git push origin main
```

### 第 3 步：验证部署

访问以下页面确认正常：
- https://xiaobo-news-v2.vercel.app/about
- https://xiaobo-news-v2.vercel.app/contact
- https://xiaobo-news-v2.vercel.app/privacy

### 第 4 步：添加原创内容

**重要**: AdSense 审核要求至少 15-20 篇高质量原创文章

建议：
- 每篇 800+ 字
- 添加"晓波点评"或人工润色
- 添加图表、数据可视化
- 确保内容独特有价值

### 第 5 步：重新提交审核

1. 登录 [AdSense 控制台](https://adsense.google.com)
2. 进入"网站"标签
3. 点击"请求审核"
4. 等待 2-3 天

---

## 📋 审核通过检查清单

### 技术要求
- [x] 广告只在文章页展示
- [x] 网站可公开访问
- [x] 有清晰的导航结构
- [ ] 页面加载速度快（待优化）

### 内容要求
- [ ] 15-20 篇原创文章
- [ ] 每篇 800+ 字
- [ ] 内容有独特价值
- [ ] 无版权问题

### 必要页面
- [x] 关于我们 (/about)
- [x] 联系我们 (/contact)
- [x] 隐私政策 (/privacy)
- [ ] 服务条款 (/terms) - 可选

### 用户体验
- [ ] 移动端友好
- [ ] 无过多广告
- [ ] 内容易于阅读

---

## ⚠️ 重要提醒

1. **审核期间不要频繁修改网站结构**
2. **确保所有文章都是原创或有独特价值**
3. **不要使用自动生成的低质量内容**
4. **广告位不要过多（每页 1-2 个即可）**

---

## 📞 审核被拒怎么办？

如果再次被拒：

1. **仔细阅读拒审理由**
   - AdSense 会说明具体问题

2. **对照检查清单逐项修复**
   - 重点关注"低价值内容"问题

3. **提升内容质量**
   - 增加原创分析
   - 添加人工观点
   - 优化排版和可读性

4. **等待 1-2 周后重新提交**
   - 给审核团队时间看到改进

---

## 🔗 相关资源

- [AdSense 计划政策](https://support.google.com/adsense/answer/48182)
- [低价值内容详解](https://support.google.com/adsense/answer/12176698)
- [网站最佳实践](https://support.google.com/adsense/answer/12170829)

---

*最后更新：2026-03-22*
