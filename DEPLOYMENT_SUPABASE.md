# 晓波智能资讯站 - Supabase 部署指南

## 📋 部署步骤

### 1. 创建 Supabase 项目

1. 访问 https://supabase.com
2. 登录/注册账号
3. 点击 "New Project"
4. 填写项目信息：
   - **Name**: `xiaobo-news`
   - **Database Password**: (生成强密码，保存到密码管理器)
   - **Region**: Asia East (Tokyo) - 推荐
5. 等待项目创建完成（约 2-5 分钟）

### 2. 配置数据库

1. 进入项目 → SQL Editor
2. 复制 `supabase_migration.sql` 内容
3. 粘贴并运行
4. 确认表和索引创建成功

### 3. 获取 API 密钥

1. Settings → API
2. 复制以下信息：
   - **Project URL**: `https://xxxxx.supabase.co`
   - **Anon Public Key**: `eyJhbG...` (前端使用)
   - **Service Role Key**: `eyJhbG...` (后端使用，保密！)

### 4. 本地配置

```bash
# 复制环境变量示例
cp .env.example .env

# 编辑 .env 文件，填入 Supabase 配置
nano .env
```

### 5. 数据迁移

```bash
# 安装依赖
pip3 install -r requirements.txt

# 运行迁移脚本
python3 tools/migrate_to_supabase.py
```

### 6. Vercel 配置

#### 6.1 环境变量

在 Vercel 项目设置中添加：
```
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJhbG... (Service Role Key)
```

#### 6.2 更新 API 路由

修改 `vercel.json` 配置 API 路由指向 Supabase 版本：

```json
{
  "functions": {
    "api/*.py": {
      "runtime": "vercel-python@3.2.0"
    }
  },
  "routes": [
    { "src": "/api/news", "dest": "/api/news_supabase.py" },
    { "src": "/api/categories", "dest": "/api/categories_supabase.py" }
  ]
}
```

### 7. 测试 API

```bash
# 本地测试
curl "http://localhost:3000/api/news?page=1&limit=10"

# 线上测试
curl "https://xiaobo-news-v2.vercel.app/api/news?page=1&limit=10"
```

### 8. 部署到 Vercel

```bash
# 提交更改
git add .
git commit -m "feat: 集成 Supabase 数据库"
git push origin main

# Vercel 会自动部署
```

---

## 💰 费用说明

### Free 计划 (起步阶段)
- ✅ 500MB 数据库
- ✅ 50K 月活用户
- ✅ 2GB 存储
- ✅ 50 万 Edge 函数调用/月
- ⚠️ 7 天不活跃会暂停

### Pro 计划 ($25/月)
- 8GB 数据库
- 100K 月活用户
- 100GB 存储
- 每日备份
- 邮件支持

---

## 🔧 故障排查

### 问题 1: API 返回 500 错误
**原因**: 环境变量未配置
**解决**: 检查 Vercel 环境变量设置

### 问题 2: 数据迁移失败
**原因**: 数据库表未创建
**解决**: 先运行 supabase_migration.sql

### 问题 3: 跨域错误
**原因**: CORS 配置问题
**解决**: 检查 API 响应头中的 Access-Control-Allow-Origin

---

## 📊 监控与维护

### Supabase 控制台
- Dashboard: 查看使用量
- Logs: 查看 API 日志
- Database: 管理数据

### Vercel 控制台
- Deployments: 查看部署状态
- Functions: 查看函数日志
- Analytics: 查看访问量

---

## 🚀 下一步优化

1. **添加缓存** - 使用 Vercel Edge Config
2. **实现增量更新** - 定时同步新文章
3. **添加搜索功能** - 使用 Supabase 全文搜索
4. **性能监控** - 集成 Sentry

---

*文档版本：v2.0*
*更新时间：2026-03-02*
