# Supabase 配置说明

## 1. 创建 Supabase 项目

1. 访问 https://supabase.com
2. 点击 "Start your project"
3. 填写项目信息：
   - Name: `xiaobo-news`
   - Database Password: (生成强密码并保存)
   - Region: 选择最近的节点 (推荐 Asia East)

## 2. 获取 API 密钥

项目创建后，在 Settings → API 获取：
- **Project URL**: `https://xxxxx.supabase.co`
- **Anon Public Key**: `eyJhbG...` (用于前端)
- **Service Role Key**: `eyJhbG...` (用于后端，保密！)

## 3. 配置环境变量

### 本地开发 (.env)
```bash
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJhbG... (Service Role Key)
```

### Vercel 部署
在项目设置中添加相同的环境变量。

## 4. 数据库迁移

运行迁移脚本：
```bash
python3 tools/migrate_to_supabase.py
```

## 5. 费用预估

**Free 计划** (起步阶段):
- ✅ 500MB 数据库 (足够 10 万篇文章)
- ✅ 50K 月活用户
- ✅ 2GB 存储
- ✅ 50 万 Edge 函数调用
- ⚠️ 7 天不活跃会暂停

**Pro 计划** ($25/月):
- 8GB 数据库
- 100K 月活用户
- 100GB 存储
- 每日备份
- 邮件支持

## 6. 下一步

1. 创建 Supabase 项目
2. 将密钥添加到 .env 文件
3. 运行数据迁移
4. 测试 API
5. 部署到 Vercel
