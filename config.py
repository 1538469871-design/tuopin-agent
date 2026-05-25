import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    """全局配置类"""

    # 项目名称
    PROJECT_NAME = "拓品智能体分析系统"
    PROJECT_VERSION = "1.0.0"

    # 时间范围设置
    DAYS_BACK = 7  # 采集过去7天的数据

    # 输出配置
    REPORTS_DIR = os.path.join(os.path.dirname(__file__), "reports")
    REPORTS_DIR_ABS = os.path.abspath(REPORTS_DIR)

    # 搜索关键词配置
    SEARCH_KEYWORDS = {
        "ai": [
            "AI Agent", "智能体", "LLM应用", "AI插件", "ChatGPT插件",
            "大语言模型", "自动化AI", "智能工作流", "AI助手", "RAG应用"
        ],
        "browser": [
            "浏览器插件", "Chrome扩展", "浏览器自动化", "浏览器插件开发",
            "网页自动填充", "网页爬虫", "网页助手", "浏览器工具"
        ],
        "automation": [
            "自动化工具", "任务自动化", "流程自动化", "RPA", "自动化脚本",
            "工作流自动化", "数据自动化", "自动化测试"
        ],
        "productivity": [
            "生产力工具", "团队协作", "任务管理", "日程管理", "笔记应用",
            "知识管理", "效率提升", "工作助手"
        ],
        "commerce": [
            "电商工具", "选品", "商品分析", "价格监测", "商品推荐",
            "电商自动化", "店铺管理", "销售工具"
        ]
    }

    # 采集器配置
    COLLECTORS_CONFIG = {
        "github": {
            "enabled": True,
            "timeout": 30,
            "max_results": 50,
        },
        "reddit": {
            "enabled": True,
            "timeout": 30,
            "max_results": 30,
        },
        "hackernews": {
            "enabled": True,
            "timeout": 30,
            "max_results": 30,
        },
        "v2ex": {
            "enabled": True,
            "timeout": 30,
            "max_results": 30,
        },
        "producthunt": {
            "enabled": True,
            "timeout": 30,
            "max_results": 20,
        },
    }

    # API配置
    API_CONFIG = {
        "deepseek": {
            "api_key": os.getenv("DEEPSEEK_API_KEY", ""),
            "base_url": "https://api.deepseek.com",
            "model": "deepseek-chat",
            "temperature": 0.7,
            "max_tokens": 2000,
        },
        "github": {
            "token": os.getenv("GITHUB_TOKEN", ""),
            "api_url": "https://api.github.com",
        },
        "anthropic": {
            "api_key": os.getenv("ANTHROPIC_API_KEY", ""),
            "model": "claude-3-sonnet-20240229",
        }
    }

    # 分析配置
    ANALYZER_CONFIG = {
        "use_ai": True,  # 是否使用AI分析
        "ai_provider": "deepseek",  # deepseek 或 anthropic
        "fallback_to_local": False,  # 如果API失败是否使用本地分析
    }

    # 通知配置
    NOTIFICATION_CONFIG = {
        "email": {
            "enabled": False,
            "smtp_server": os.getenv("SMTP_SERVER", ""),
            "smtp_port": int(os.getenv("SMTP_PORT", "587")),
            "sender": os.getenv("SENDER_EMAIL", ""),
            "password": os.getenv("EMAIL_PASSWORD", ""),
            "recipients": os.getenv("EMAIL_RECIPIENTS", "").split(","),
        },
        "telegram": {
            "enabled": False,
            "bot_token": os.getenv("TELEGRAM_BOT_TOKEN", ""),
            "chat_id": os.getenv("TELEGRAM_CHAT_ID", ""),
        },
        "dingtalk": {
            "enabled": False,
            "webhook": os.getenv("DINGTALK_WEBHOOK", ""),
        },
    }

    # 分析输出配置
    ANALYSIS_OUTPUT = {
        "num_recommendations": 5,  # 推荐项目数
        "min_keywords": 2,  # 最少包含的关键词数
        "evaluation_dimensions": [
            "market_demand",  # 市场需求热度（1-10）
            "willingness_to_pay",  # 用户付费意愿（1-10）
            "competition_level",  # 竞争激烈程度（1-10，低分=低竞争）
            "dev_difficulty",  # 开发难度（1-10，低分=容易）
            "time_to_revenue",  # 产生收入周期（1-10，低分=快）
        ]
    }

    # 日志配置
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # 系统配置
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    TIMEOUT_SECONDS = 30
    MAX_RETRIES = 3


def get_time_range():
    """获取时间范围"""
    end_time = datetime.now()
    start_time = end_time - timedelta(days=Config.DAYS_BACK)
    return start_time, end_time


def get_data_collection_prompt():
    """获取数据采集提示词"""
    return """
你是一个资深的产品经理和技术分析师。根据以下从多个平台采集的最新讨论和交易数据，
请分析并给出当前最值得做的5个智能体/浏览器插件/自动化工具项目。

分析维度包括：
1. 市场需求热度（1-10分）：搜索热度、讨论量、问题数量
2. 用户付费意愿（1-10分）：社区中是否有人愿意付费，是否提到价格痛点
3. 竞争程度（1-10分）：10=竞争激烈，1=几乎无竞争
4. 开发难度（1-10分）：1=特别简单，10=非常复杂
5. 产生收入周期（1-10分）：1=可立即变现，10=需要很久才能变现

对于每个推荐项目，请输出：
- 项目名称（简洁有力）
- 一句话简介
- 市场需求的数据支撑（具体引用采集到的讨论/数据）
- 核心MVP功能（3-5个最小功能）
- 各维度评分及理由
- 建议变现模式
- 开发周期估算（如：1-2周MVP）
- 风险提示

请直接给出JSON格式的结构化输出，包含5个项目。
"""
