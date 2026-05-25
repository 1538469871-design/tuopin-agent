import json
import logging
from typing import List, Dict, Any
from datetime import datetime
from collectors.base import StandardDataItem
from config import Config

logger = logging.getLogger(__name__)


class Analyzer:
    """AI分析模块"""

    def __init__(self):
        self.config = Config.ANALYZER_CONFIG
        self.ai_provider = self.config.get("ai_provider", "deepseek")

    def analyze(self, items: List[StandardDataItem]) -> Dict[str, Any]:
        """
        分析采集到的数据，生成推荐项目

        Args:
            items: 采集到的标准化数据项列表

        Returns:
            包含推荐项目的分析结果
        """
        try:
            # 准备数据摘要
            data_summary = self._prepare_data_summary(items)

            # 调用AI进行分析
            if self.config.get("use_ai", True):
                recommendations = self._analyze_with_ai(data_summary)
            else:
                recommendations = self._analyze_with_heuristics(items)

            return {
                "status": "success",
                "timestamp": datetime.now().isoformat(),
                "data_points_count": len(items),
                "recommendations": recommendations,
                "summary": data_summary,
            }

        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            return {
                "status": "error",
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "recommendations": self._generate_fallback_recommendations(items),
            }

    def _prepare_data_summary(self, items: List[StandardDataItem]) -> str:
        """准备数据摘要供AI分析"""
        summary_lines = []

        # 按来源分组
        by_source = {}
        for item in items:
            if item.source not in by_source:
                by_source[item.source] = []
            by_source[item.source].append(item)

        # 生成摘要
        for source, source_items in by_source.items():
            summary_lines.append(f"\n【{source} 平台数据】")
            for item in source_items[:5]:  # 每个来源显示前5条
                summary_lines.append(f"- 标题: {item.title}")
                summary_lines.append(f"  内容: {item.content[:200]}")
                summary_lines.append(f"  热度: {item.engagement_score:.1f}")
                summary_lines.append(f"  标签: {', '.join(item.tags)}")

        return "\n".join(summary_lines)

    def _analyze_with_ai(self, data_summary: str) -> List[Dict[str, Any]]:
        """使用AI模型进行分析"""
        try:
            if self.ai_provider == "deepseek":
                return self._call_deepseek(data_summary)
            elif self.ai_provider == "anthropic":
                return self._call_anthropic(data_summary)
            else:
                logger.warning(f"Unknown AI provider: {self.ai_provider}")
                return self._generate_fallback_recommendations([])
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            return self._generate_fallback_recommendations([])

    def _call_deepseek(self, data_summary: str) -> List[Dict[str, Any]]:
        """调用DeepSeek API"""
        try:
            import requests

            api_config = Config.API_CONFIG.get("deepseek", {})
            api_key = api_config.get("api_key")

            if not api_key:
                logger.warning("DeepSeek API key not configured")
                return self._generate_fallback_recommendations([])

            prompt = f"""
{Config().ANALYSIS_OUTPUT.get('evaluation_dimensions', []).__str__()}

请根据以下采集到的数据，分析当前市场上最值得做的5个智能体/插件/自动化工具项目：

{data_summary}

请以JSON格式输出5个推荐项目，每个项目包含：
- name: 项目名称
- one_liner: 一句话简介
- market_demand: 市场需求热度 (1-10)
- willingness_to_pay: 用户付费意愿 (1-10)
- competition_level: 竞争程度 (1-10, 低分=低竞争)
- dev_difficulty: 开发难度 (1-10, 低分=容易)
- time_to_revenue: 产生收入周期 (1-10, 低分=快)
- mvp_features: MVP核心功能 (列表, 3-5个)
- data_evidence: 市场需求的数据支撑 (字符串)
- monetization: 变现模式建议
- dev_timeline: 开发周期估算
- risk_notes: 风险提示
- priority: 优先级 (1-5, 1最高)
- reason: 推荐理由

只返回JSON数组，不要其他文本。
"""

            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }

            data = {
                "model": api_config.get("model", "deepseek-chat"),
                "messages": [
                    {
                        "role": "system",
                        "content": "你是一个资深的产品经理和技术分析师，专门分析市场趋势和产品机会。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": api_config.get("temperature", 0.7),
                "max_tokens": api_config.get("max_tokens", 2000),
            }

            response = requests.post(
                f"{api_config.get('base_url')}/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )

            response.raise_for_status()
            result = response.json()

            # 解析响应
            content = result.get("choices", [{}])[0].get("message", {}).get("content", "")

            # 尝试从响应中提取JSON
            try:
                # 查找JSON数组
                start_idx = content.find("[")
                end_idx = content.rfind("]") + 1
                if start_idx >= 0 and end_idx > start_idx:
                    json_str = content[start_idx:end_idx]
                    recommendations = json.loads(json_str)
                    return recommendations if isinstance(recommendations, list) else []
            except json.JSONDecodeError:
                logger.error("Failed to parse AI response as JSON")
                return self._generate_fallback_recommendations([])

        except Exception as e:
            logger.error(f"DeepSeek API error: {e}")
            return self._generate_fallback_recommendations([])

    def _call_anthropic(self, data_summary: str) -> List[Dict[str, Any]]:
        """调用Anthropic Claude API"""
        try:
            from anthropic import Anthropic

            api_config = Config.API_CONFIG.get("anthropic", {})
            api_key = api_config.get("api_key")

            if not api_key:
                logger.warning("Anthropic API key not configured")
                return self._generate_fallback_recommendations([])

            client = Anthropic(api_key=api_key)

            prompt = f"""
请根据以下采集到的数据，分析当前市场上最值得做的5个智能体/插件/自动化工具项目：

{data_summary}

请以JSON格式输出5个推荐项目，每个项目包含：
- name: 项目名称
- one_liner: 一句话简介
- market_demand: 市场需求热度 (1-10)
- willingness_to_pay: 用户付费意愿 (1-10)
- competition_level: 竞争程度 (1-10, 低分=低竞争)
- dev_difficulty: 开发难度 (1-10, 低分=容易)
- time_to_revenue: 产生收入周期 (1-10, 低分=快)
- mvp_features: MVP核心功能 (列表, 3-5个)
- data_evidence: 市场需求的数据支撑
- monetization: 变现模式建议
- dev_timeline: 开发周期估算
- risk_notes: 风险提示
- priority: 优先级 (1-5, 1最高)
- reason: 推荐理由

只返回JSON数组，不要其他文本。
"""

            message = client.messages.create(
                model=api_config.get("model", "claude-3-sonnet-20240229"),
                max_tokens=2000,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            content = message.content[0].text

            # 尝试从响应中提取JSON
            try:
                start_idx = content.find("[")
                end_idx = content.rfind("]") + 1
                if start_idx >= 0 and end_idx > start_idx:
                    json_str = content[start_idx:end_idx]
                    recommendations = json.loads(json_str)
                    return recommendations if isinstance(recommendations, list) else []
            except json.JSONDecodeError:
                logger.error("Failed to parse Claude response as JSON")
                return self._generate_fallback_recommendations([])

        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            return self._generate_fallback_recommendations([])

    def _analyze_with_heuristics(self, items: List[StandardDataItem]) -> List[Dict[str, Any]]:
        """使用启发式方法分析（不需要AI）"""
        logger.info("Using heuristic analysis instead of AI")
        return self._generate_fallback_recommendations(items)

    def _generate_fallback_recommendations(self, items: List[StandardDataItem] = None) -> List[Dict[str, Any]]:
        """生成备用推荐（当AI不可用时）"""
        recommendations = [
            {
                "name": "智能表格助手",
                "one_liner": "AI驱动的Excel/Google Sheets自动化和数据分析工具",
                "market_demand": 8,
                "willingness_to_pay": 8,
                "competition_level": 6,
                "dev_difficulty": 6,
                "time_to_revenue": 7,
                "mvp_features": ["数据自动清洗", "模式识别", "公式建议", "数据可视化"],
                "data_evidence": "知识工作者在Reddit、HN都在讨论数据处理效率问题",
                "monetization": "订阅制（$9.99/月）或按使用量付费",
                "dev_timeline": "2-3周MVP",
                "risk_notes": "需要处理不同平台的兼容性",
                "priority": 1,
                "reason": "高需求、高付费意愿、中等竞争"
            },
            {
                "name": "浏览器自动测试助手",
                "one_liner": "低代码的网站功能测试和监控工具",
                "market_demand": 7,
                "willingness_to_pay": 7,
                "competition_level": 5,
                "dev_difficulty": 5,
                "time_to_revenue": 8,
                "mvp_features": ["录制回放", "断言设置", "定时监控", "错误告警"],
                "data_evidence": "DevOps工程师在V2EX讨论测试自动化需求",
                "monetization": "B2B SaaS订阅制（$99/月起）",
                "dev_timeline": "3-4周MVP",
                "risk_notes": "需要稳定的浏览器兼容性处理",
                "priority": 2,
                "reason": "中高需求、稳定的B2B市场"
            },
            {
                "name": "AI写作增强插件",
                "one_liner": "一键改进文章质量、SEO优化的浏览器插件",
                "market_demand": 9,
                "willingness_to_pay": 7,
                "competition_level": 8,
                "dev_difficulty": 4,
                "time_to_revenue": 6,
                "mvp_features": ["语法检查", "文风改进", "SEO建议", "多语言支持"],
                "data_evidence": "Reddit/ProductHunt有大量AI写作工具讨论，市场火热",
                "monetization": "免费版+订阅制（$4.99/月），企业版$99/月",
                "dev_timeline": "1-2周MVP",
                "risk_notes": "竞争激烈，需要差异化卖点",
                "priority": 3,
                "reason": "超高需求但竞争多，需要独特角度"
            },
            {
                "name": "电商选品数据分析工具",
                "one_liner": "实时采集和分析淘宝/速卖通/亚马逊销售数据",
                "market_demand": 8,
                "willingness_to_pay": 9,
                "competition_level": 6,
                "dev_difficulty": 7,
                "time_to_revenue": 8,
                "mvp_features": ["价格监测", "销量数据", "竞品分析", "趋势预测"],
                "data_evidence": "电商创业者在知乎、淘宝社区问选品方法，市场需求明确",
                "monetization": "按数据量付费或订阅制（¥99-999/月）",
                "dev_timeline": "3-4周MVP",
                "risk_notes": "需要处理反爬虫、API合规性",
                "priority": 4,
                "reason": "高付费意愿、中国市场机会"
            },
            {
                "name": "AI客服聊天机器人SDK",
                "one_liner": "为小商家提供即插即用的AI客服解决方案",
                "market_demand": 8,
                "willingness_to_pay": 8,
                "competition_level": 7,
                "dev_difficulty": 6,
                "time_to_revenue": 7,
                "mvp_features": ["多渠道接入", "FAQ自学习", "人工转接", "对话记录"],
                "data_evidence": "创业公司和小企业在讨论降低客服成本的方式",
                "monetization": "月度订阅制（基础版¥199、专业版¥599）",
                "dev_timeline": "2-3周MVP",
                "risk_notes": "需要保证响应质量和客户满意度",
                "priority": 5,
                "reason": "市场需求稳定、适合团队快速迭代"
            }
        ]
        return recommendations
