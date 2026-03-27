# GitHub Secrets 设置指南

## 需要配置的 Secrets

在 GitHub 仓库设置中添加以下 Secrets：

| Secret Name | 值 | 来源 |
|-------------|-----|------|
| `SUPABASE_URL` | `https://vmrzypjvjhivzlwjsdug.supabase.co` | Supabase 项目设置 |
| `SUPABASE_ANON_KEY` | `eyJhbGciOiJIUzI1NiIs...` | Supabase 项目设置 → API → anon/public |
| `VERCEL_TOKEN` | Vercel Token | Vercel 设置 → Tokens |
| `VERCEL_ORG_ID` | Vercel Org ID | Vercel 项目设置 |
| `VERCEL_PROJECT_ID` | Vercel Project ID | Vercel 项目设置 |

## 设置步骤

1. 打开 GitHub 仓库 → Settings → Secrets and variables → Actions
2. 点击 "New repository secret"
3. 逐个添加上述 secrets

## 本地开发

复制 `.env.example` 为 `.env` 并填入真实值：

```bash
cp .env.example .env
# 编辑 .env 填入你的 SUPABASE_ANON_KEY
```

⚠️ **注意**: `.env` 文件已被 `.gitignore` 排除，不会被提交到 Git。
