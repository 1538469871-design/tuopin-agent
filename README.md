# 🚀 拓品智能体分析系统

一个完全自动化的每日市场分析系统，能自动采集多平台数据并使用AI分析，输出**最值得做的5个智能体/插件项目推荐**。

## ✨ 核心特性

- ✅ **完全自动化**: 每日定时自动运行，无需手动干预
- ✅ **多平台数据采集**: GitHub、Reddit、HackerNews、V2EX、ProductHunt
- ✅ **AI智能分析**: 使用DeepSeek/Claude进行深度市场分析
- ✅ **结构化输出**: Markdown格式的精美报告，包含详细的评分和建议
- ✅ **低成本运行**: 使用免费API和廉价AI模型（DeepSeek $0.0001/1K tokens）
- ✅ **灵活部署**: 支持本地运行、GitHub Actions、Docker等多种方式
- ✅ **多渠道通知**: 支持邮件、Telegram、钉钉通知

## 📊 分析维度

每个推荐项目包含5个关键评分：

| 维度 | 说明 | 评分范围 |
|------|------|--------|
| **市场需求热度** | 搜索热度、讨论量、用户关注度 | 1-10分，越高越好 |
| **用户付费意愿** | 社区中是否有人愿意付费 | 1-10分，越高越好 |
| **竞争程度** | 市场竞争激烈程度 | 1-10分，1=低竞争，10=高竞争 |
| **开发难度** | 技术实现的复杂度 | 1-10分，1=简单，10=复杂 |
| **变现周期** | 从开发到产生收入的时间 | 1-10分，1=快速，10=缓慢 |

## 🎯 推荐项目示例

根据系统分析，近期最值得做的项目方向包括：

1. **智能表格助手** - AI驱动的Excel/Google Sheets自动化工具
2. **浏览器自动测试助手** - 低代码的网站功能测试工具
3. **AI写作增强插件** - 一键改进文章质量的浏览器插件
4. **电商选品数据分析工具** - 实时采集和分析电商销售数据
5. **AI客服聊天机器人SDK** - 为小商家提供即插即用的客服解决方案

## 🚀 快速开始

### 方案A: 本地运行（推荐用于测试）

#### 1. 克隆项目
```bash
git clone https://github.com/yourusername/tuopin-analyzer.git
cd tuopin-analyzer
```

#### 2. 创建虚拟环境
```bash
# macOS/Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

#### 3. 安装依赖
```bash
pip install -r requirements.txt
```

#### 4. 配置环境变量
```bash
# 复制示例配置
cp .env.example .env

# 编辑 .env，填入你的 API Key
# 最少需要配置 DeepSeek API Key (或 Anthropic API Key)
nano .env  # 或使用你喜欢的编辑器
```

#### 5. 第一次运行（测试模式）
```bash
# 使用模拟数据测试（不需要网络）
python scheduler.py --mock

# 查看生成的报告
ls reports/
cat reports/*.md
```

#### 6. 完整运行（采集真实数据）
```bash
python scheduler.py
```

#### 7. 本地定时运行

**macOS/Linux（使用 crontab）**:
```bash
# 编辑 crontab
crontab -e

# 添加以下行（每天早上8点运行）
0 8 * * * cd /path/to/tuopin-analyzer && /path/to/venv/bin/python scheduler.py >> scheduler.log 2>&1
```

**Windows（使用任务计划程序）**:
1. 打开"任务计划程序"
2. 创建基本任务
3. 触发器设置为每天8:00 AM
4. 操作：启动程序 → 选择 `python.exe`
5. 参数：`C:\path\to\scheduler.py`

### 方案B: GitHub Actions（推荐用于自动化）

#### 1. 推送到 GitHub

```bash
git add .
git commit -m "Initial commit: tuopin-analyzer"
git push origin main
```

#### 2. 配置 Secrets

在 GitHub 仓库设置中添加：

**Settings → Secrets and variables → Actions → New repository secret**

需要配置的 Secrets：

```
DEEPSEEK_API_KEY      # DeepSeek API 密钥（https://platform.deepseek.com）
ANTHROPIC_API_KEY     # Claude API 密钥（可选，https://console.anthropic.com）
GITHUB_TOKEN          # GitHub Token（可选，用于提升 API 限制）
```

#### 3. 启用 Workflow

1. 进入 GitHub 仓库的 **Actions** 标签
2. 找到 **"每日拓品分析"** workflow
3. 点击 **"Enable workflow"**

#### 4. 首次手动触发测试

在 Actions 标签中，选择 **"每日拓品分析"** → **"Run workflow"** → **"Run workflow"**

#### 5. 查看运行结果

- Workflow 每天 UTC 0点（北京时间 08:00）自动运行
- 生成的报告会自动提交到仓库的 `reports/` 目录
- 报告也会保存为 Artifact（可下载30天）

## 🔧 配置说明

### DeepSeek API 配置（推荐）

1. 前往 https://platform.deepseek.com
2. 注册并登录
3. 创建 API Key
4. 复制 API Key 到 `.env` 的 `DEEPSEEK_API_KEY`

**优点**:
- 价格极低：$0.0001/1K tokens（比ChatGPT便宜100倍）
- 国内可用，无需代理
- 性能不错，支持中文
- 一次完整分析成本 < $0.001

### Anthropic Claude API 配置（备选）

1. 前往 https://console.anthropic.com
2. 创建 API Key
3. 复制到 `.env` 的 `ANTHROPIC_API_KEY`

### 可选通知配置

#### 邮件通知

```bash
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your-email@gmail.com
EMAIL_PASSWORD=your-app-password  # 不是密码，是App Password
EMAIL_RECIPIENTS=recipient@example.com
```

使用 Gmail 需要：
1. 开启 2-Step Verification
2. 生成 App Password: https://myaccount.google.com/apppasswords
3. 将 App Password 填入 `EMAIL_PASSWORD`

#### Telegram 通知

1. 在 Telegram 搜索 `@BotFather`
2. 创建 Bot，获得 `bot_token`
3. 创建私人 Channel 或 Group
4. 将 Bot 添加到 Channel/Group
5. 发送消息 `/start`
6. 访问 `https://api.telegram.org/bot{bot_token}/getUpdates` 获得 `chat_id`
7. 配置到 `.env` 中

## 📁 项目结构

```
tuopin-analyzer/
├── config.py                     # 全局配置
├── scheduler.py                  # 主入口程序
├── analyzer.py                   # AI分析模块
├── reporter.py                   # 报告生成模块
├── collectors/                   # 数据采集模块
│   ├── __init__.py
│   ├── base.py                  # 基类
│   ├── github.py                # GitHub采集器
│   ├── reddit.py                # Reddit采集器
│   ├── hackernews.py            # HackerNews采集器
│   ├── v2ex.py                  # V2EX采集器
│   ├── producthunt.py           # ProductHunt采集器
│   └── zhihu.py                 # 知乎采集器（可选）
├── reports/                      # 生成的报告目录
├── .github/
│   └── workflows/
│       └── daily.yml            # GitHub Actions 工作流
├── requirements.txt             # Python依赖
├── .env.example                 # 环境变量示例
├── .env                         # 环境变量（不提交）
├── .gitignore
└── README.md
```

## 📝 报告示例

生成的报告位置：`reports/2026-05-25-report.md`

### 报告包含内容

1. **标题和元数据**: 生成时间、数据采样范围
2. **数据统计**: 采集数据点数、分析维度
3. **推荐项目表格**: 5个项目的快速概览
4. **详细分析**: 每个项目的详细评分、MVP功能、市场支撑、变现建议等
5. **数据摘要**: 各平台采集数据的概览

### 报告示例片段

```markdown
# 拓品智能体/插件项目推荐 - 2026-05-25

**生成时间**: 2026-05-25 08:15:32
**数据采样范围**: 过去7天

## 📊 数据统计

- **采集数据点**: 250 个
- **分析维度**: 市场需求热度、付费意愿、竞争程度、开发难度、变现周期

## 🎯 5大推荐项目

| 优先级 | 项目名称 | 一句话简介 | 市场需求 | 付费意愿 | 竞争 | 难度 | 变现周期 |
|--------|--------|----------|--------|--------|------|------|--------|
| 1 | **智能表格助手** | AI驱动的Excel/Google Sheets自动化工具 | 🔴 8/10 | 🔴 8/10 | 6/10 | 6/10 | 7/10 |
```

## 🐛 故障排查

### 问题1: 采集数据为空

**原因**: 网络问题或平台限流

**解决**:
```bash
# 使用 --mock 测试是否是数据采集问题
python scheduler.py --mock

# 检查网络连接
ping github.com
curl https://api.github.com
```

### 问题2: AI 分析失败

**原因**: API Key 配置错误或API不可用

**检查**:
1. 确认 `.env` 中的 API Key 正确
2. 检查 API 配额是否用尽
3. 查看日志中的具体错误信息

```bash
# 调试模式运行，查看详细错误
DEBUG=true LOG_LEVEL=DEBUG python scheduler.py --debug
```

### 问题3: 报告没有生成

**原因**: 目录权限或磁盘空间问题

**检查**:
```bash
# 确保 reports 目录存在且可写
ls -la reports/
chmod 755 reports/

# 检查磁盘空间
df -h
```

### 问题4: GitHub Actions 失败

**检查**:
1. 进入 GitHub 仓库 **Actions** 标签
2. 查看最近的 workflow run
3. 点击失败的 run 查看具体日志
4. 常见原因：Secrets 未配置、依赖安装失败

## 💡 使用技巧

### 自定义搜索关键词

编辑 `config.py` 中的 `SEARCH_KEYWORDS` 字典：

```python
SEARCH_KEYWORDS = {
    "ai": ["AI Agent", "LLM应用", ...],
    "browser": ["浏览器插件", ...],
    "automation": ["自动化工具", ...],
    # 添加自己的关键词组
    "saas": ["SaaS应用", "订阅制服务", ...],
}
```

### 调整分析时间范围

编辑 `config.py` 中的 `DAYS_BACK`：

```python
DAYS_BACK = 7  # 改为 30 采集过去30天的数据
```

### 本地运行加速

使用国内镜像源安装依赖：

```bash
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
```

## 📊 数据流

```
┌─────────────────┐
│   定时触发      │
│  (GitHub Actions│
│   或 crontab)   │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│    数据采集 (Collectors)                │
│  ┌──────────────────────────────────┐  │
│  │ GitHub │ Reddit │ HN │ V2EX │ PH│  │
│  └──────────────────────────────────┘  │
│         ▼ (StandardDataItem)            │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│    数据分析 (Analyzer)              │
│  ▼ (调用 DeepSeek/Claude API)       │
│  提取5个项目推荐                   │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│    报告生成 (Reporter)              │
│  ▼ (Markdown格式)                   │
│  保存到 reports/ 目录               │
│  可选: 发送通知                    │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│    输出结果                         │
│  reports/YYYY-MM-DD-report.md      │
│  (Git commit / Artifact / Notification)│
└─────────────────────────────────────┘
```

## 🎓 学习资源

- [Python requests 库](https://requests.readthedocs.io/)
- [DeepSeek API 文档](https://platform.deepseek.com/docs)
- [Anthropic Claude API](https://docs.anthropic.com/)
- [GitHub Actions](https://docs.github.com/en/actions)
- [Markdown 语法](https://www.markdownguide.org/)

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issues 和 Pull Requests！

## 📧 联系方式

有问题或建议？欢迎提交 GitHub Issue。

---

**Made with ❤️ for Product Makers**

**最后更新**: 2026-05-25
