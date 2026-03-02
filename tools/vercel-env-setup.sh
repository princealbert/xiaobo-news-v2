#!/bin/bash
# Vercel 环境变量配置脚本

echo "======================================"
echo "🚀 Vercel 环境变量配置工具"
echo "======================================"
echo ""

# 检查是否登录
echo "🔍 检查登录状态..."
if ! vercel whoami &>/dev/null; then
    echo "❌ 未登录 Vercel"
    echo ""
    echo "请登录 Vercel："
    echo "1. 访问：https://vercel.com/login"
    echo "2. 登录后，在设置中获取 Token"
    echo "3. 运行：vercel login"
    echo ""
    exit 1
fi

USER=$(vercel whoami)
echo "✅ 已登录：$USER"
echo ""

# 配置环境变量
echo "📝 配置环境变量..."
echo ""

# 1. SUPABASE_URL
echo "添加 SUPABASE_URL..."
vercel env add SUPABASE_URL https://vmrzypjvjhivzlwjsdug.supabase.co --environment production --yes

# 2. SUPABASE_KEY
echo "添加 SUPABASE_KEY..."
vercel env add SUPABASE_KEY "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZtcnp5cGp2amhpdnpsd2pzZHVnIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjQyMTYxMiwiZXhwIjoyMDg3OTk3NjEyfQ.kxU_Mes7ZepaKdIdry9OCV9l-auxHO_gHeqaK9eB6gE" --environment production --yes

# 3. DATABASE_URL
echo "添加 DATABASE_URL..."
vercel env add DATABASE_URL "postgresql://postgres:xiaobonewsdata@db.vmrzypjvjhivzlwjsdug.supabase.co:5432/postgres" --environment production --yes

echo ""
echo "======================================"
echo "✅ 环境变量配置完成！"
echo "======================================"
echo ""
echo "下一步："
echo "1. 运行 vercel --prod 重新部署"
echo "2. 或推送代码到 GitHub 触发自动部署"
echo ""
