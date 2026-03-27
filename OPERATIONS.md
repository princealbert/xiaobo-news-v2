# 资讯站运维手册

## 一、自动化脚本

### 1. 内容采集脚本

| 脚本 | 功能 | 频率 |
|------|------|------|
| `tools/tianjin_news_crawler.py` | 天津新闻（北方网+天津日报+津云） | 每天 2 次 |
| `tools/bilibili_crawler.py` | B站科技区 | 每 4 小时 |
| `tools/rss_aggregator.py` | RSS 聚合 | 每 2 小时 |
| `tools/jinyun_crawler.py` | 津云 API | 每天 2 次 |

### 2. 部署脚本

| 脚本 | 功能 |
|------|------|
| `npm run build` | 构建网站 |
| `vercel --prod` | 部署到 Vercel |

### 3. 一键运维

```bash
# 完整运维流程
cd /Users/albert/documents/茉莉空间

# 1. 采集内容
python3 tools/tianjin_news_crawler.py   # 天津新闻
python3 tools/bilibili_crawler.py tech  # B站科技
python3 tools/rss_aggregator.py --fast # RSS聚合

# 2. 构建部署
cd xiaobo-news-v2
npm run build && vercel --prod
```

## 二、定时任务 (Crontab)

```bash
# 内容采集
0 */2 * * * /bin/bash /Users/albert/documents/茉莉空间/tools/run_rss_and_deploy.sh
0 9,18 * * * cd /Users/albert/documents/茉莉空间 && python3 tools/tianjin_news_crawler.py >> logs/tianjin_crawler.log 2>&1
0 */4 * * * cd /Users/albert/documents/茉莉空间 && python3 tools/bilibili_crawler.py >> logs/bilibili_crawler.log 2>&1

# 其他
0 3 * * * cd /Users/albert/documents/茉莉空间 && ./molly_env/bin/python3 agents/evolver_v2.py >> logs/evolver.log 2>&1
```

## 三、数据统计

```bash
# 查看数据库文章数
sqlite3 xiaobo-news-v2/news.db "SELECT COUNT(*) FROM articles;"

# 查看各来源文章数
sqlite3 xiaobo-news-v2/news.db "SELECT source_origin, COUNT(*) FROM articles GROUP BY source_origin;"
```

## 四、Docker 服务

```bash
# RSSHub
docker start rsshub   # 启动
docker stop rsshub    # 停止
docker logs rsshub    # 查看日志

# 访问: http://localhost:1200
```

## 五、GitHub Actions

### 工作流文件
- `.github/workflows/ci-cd.yml` - CI/CD 流水线
- `.github/workflows/auto-sync.yml` - 自动同步

### 手动触发
```bash
cd xiaobo-news-v2
gh workflow run ci-cd
```

## 六、数据库

- 路径: `xiaobo-news-v2/news.db`
- 表: `articles`
- 主要字段: title, link, summary, category, author, publish_date, source_origin

## 七、日志

- RSS 聚合: `logs/rss_aggregator.log`
- 天津爬虫: `logs/tianjin_crawler.log`
- B站爬虫: `logs/bilibili_crawler.log`
- Vercel 部署: Vercel Dashboard
