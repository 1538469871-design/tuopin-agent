# ⚡ 5分钟快速开始

## 🎯 目标
5分钟内本地运行并生成第一份推荐报告。

## 📋 前提条件
- Python 3.8+
- git
- 一个 DeepSeek API Key（免费注册）

## 🚀 步骤

### 1️⃣ 克隆项目（1分钟）
```bash
git clone https://github.com/yourusername/tuopin-analyzer.git
cd tuopin-analyzer
```

### 2️⃣ 创建虚拟环境（1分钟）
```bash
# macOS/Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3️⃣ 安装依赖（1分钟）
```bash
pip install -r requirements.txt
```

### 4️⃣ 获取 API Key（1分钟）

**最简单的选项：使用 DeepSeek（推荐）**

1. 访问 https://platform.deepseek.com
2. 注册并登录
3. 创建 API Key
4. 复制 API Key

**或者：使用本地模型（无需API）**

如果你有 ollama 安装：
```bash
# 已安装 ollama 的话
ollama pull mistral
# 不需要配置 API Key
```

### 5️⃣ 配置环境（1分钟）
```bash
# 复制示例配置
cp .env.example .env

# 编辑 .env 文件，填入 API Key
# macOS/Linux
nano .env

# Windows
notepad .env
```

在 `.env` 中找到这一行，填入你的 API Key：
```bash
DEEPSEEK_API_KEY=sk-your-api-key-here
```

### 6️⃣ 第一次运行（使用模拟数据测试）

```bash
# 不需要网络，快速测试
python scheduler.py --mock
```

✅ **如果一切正常，你会看到**：
```
============================================================
拓品智能体分析系统 v1.0.0
开始时间: 2026-05-25 10:30:45
============================================================

✅ 流程完成!
报告位置: /path/to/reports/2026-05-25-report.md
结束时间: 2026-05-25 10:31:02
```

### 7️⃣ 查看报告
```bash
# 查看生成的报告
cat reports/2026-05-25-report.md

# 或用编辑器打开
open reports/2026-05-25-report.md  # macOS
xdg-open reports/2026-05-25-report.md  # Linux
notepad reports/2026-05-25-report.md  # Windows
```

## 🎉 完成！

🎊 恭喜！你已经成功运行了拓品分析系统！

## 📚 下一步

### 运行完整分析（采集真实数据）
```bash
python scheduler.py
```

### 设置本地定时运行
```bash
# 使用 Makefile 快速设置
make setup-crontab

# 然后按照提示编辑 crontab
```

### 配置 GitHub Actions（自动化）
1. 推送到 GitHub
2. 在 Settings → Secrets 中添加 API Key
3. 在 Actions 中手动触发第一次运行

### 配置通知
编辑 `.env` 文件的通知部分，配置邮件/Telegram/钉钉通知。

## 🆘 如果出错了

### 错误：ModuleNotFoundError
```bash
# 确认虚拟环境已激活
# macOS/Linux
source venv/bin/activate
# Windows
venv\Scripts\activate

# 重新安装依赖
pip install -r requirements.txt
```

### 错误：API Key 无效
1. 确认 `.env` 中的 Key 正确复制（不要有多余空格）
2. 确认 Key 有效期未过期
3. 检查 API 配额是否用尽

### 错误：网络连接失败
```bash
# 测试网络
ping api.github.com
curl https://api.github.com

# 如果使用代理，需要在 collectors 中配置
```

## 💡 快速提示

### 使用 Makefile 快速命令
```bash
make help       # 查看所有可用命令
make install    # 安装依赖
make mock       # 测试运行
make run        # 完整运行
make clean      # 清理缓存
```

### 查看日志
```bash
# 实时查看日志
tail -f scheduler.log

# 显示最后100行
tail -100 scheduler.log
```

### 编辑配置
- 搜索关键词：编辑 `config.py` 的 `SEARCH_KEYWORDS`
- 采集时间范围：编辑 `config.py` 的 `DAYS_BACK`
- 推荐数量：编辑 `config.py` 的 `ANALYSIS_OUTPUT`

## 📖 详细文档

查看 [README.md](README.md) 了解完整文档。

---

**Now you're ready to go! 🚀**
