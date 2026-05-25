import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Any
from config import Config

logger = logging.getLogger(__name__)


class Reporter:
    """报告生成模块"""

    def __init__(self):
        self.reports_dir = Config.REPORTS_DIR_ABS
        self._ensure_reports_dir()

    def _ensure_reports_dir(self):
        """确保报告目录存在"""
        os.makedirs(self.reports_dir, exist_ok=True)

    def generate_report(self, analysis_result: Dict[str, Any]) -> str:
        """
        生成Markdown报告

        Args:
            analysis_result: 分析结果字典

        Returns:
            报告文件路径
        """
        try:
            # 生成报告文件名
            today = datetime.now().strftime("%Y-%m-%d")
            report_filename = f"{today}-report.md"
            report_path = os.path.join(self.reports_dir, report_filename)

            # 构建Markdown内容
            markdown_content = self._build_markdown(analysis_result, today)

            # 写入文件
            with open(report_path, "w", encoding="utf-8") as f:
                f.write(markdown_content)

            logger.info(f"Report generated: {report_path}")
            return report_path

        except Exception as e:
            logger.error(f"Report generation failed: {e}")
            raise

    def _build_markdown(self, analysis_result: Dict[str, Any], date: str) -> str:
        """构建Markdown内容"""
        lines = []

        # 标题和元数据
        lines.append(f"# 拓品智能体/插件项目推荐 - {date}\n")
        lines.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        lines.append(f"**数据采样范围**: 过去7天\n")

        if analysis_result.get("status") == "error":
            lines.append(f"\n❌ **分析状态**: 出错\n")
            lines.append(f"**错误信息**: {analysis_result.get('error', 'Unknown error')}\n")
            return "\n".join(lines)

        # 数据统计
        lines.append(f"\n## 📊 数据统计\n")
        lines.append(f"- **采集数据点**: {analysis_result.get('data_points_count', 0)} 个\n")
        lines.append(f"- **分析维度**: 市场需求热度、付费意愿、竞争程度、开发难度、变现周期\n")

        # 推荐项目
        recommendations = analysis_result.get("recommendations", [])
        if recommendations:
            lines.append(f"\n## 🎯 5大推荐项目\n")
            lines.append(self._build_recommendations_table(recommendations))
            lines.append("\n## 📋 详细分析\n")
            lines.extend(self._build_detailed_analysis(recommendations))
        else:
            lines.append("\n❌ 没有推荐项目\n")

        # 数据摘要
        if analysis_result.get("summary"):
            lines.append("\n## 📈 数据摘要\n")
            lines.append("### 采集数据来源分析\n")
            lines.append(analysis_result.get("summary", ""))

        # 使用说明
        lines.append("\n---\n")
        lines.append("\n## 📌 使用说明\n")
        lines.append("- 本报告每日自动生成\n")
        lines.append("- 数据来源: GitHub、Reddit、HackerNews、V2EX、ProductHunt\n")
        lines.append("- 推荐优先级: 1 = 最高优先级，5 = 最低优先级\n")
        lines.append("- 评分范围: 1-10分，越高越好（竞争程度除外）\n")

        return "\n".join(lines)

    def _build_recommendations_table(self, recommendations: List[Dict[str, Any]]) -> str:
        """构建推荐项目表格"""
        lines = []

        # 表头
        lines.append("| 优先级 | 项目名称 | 一句话简介 | 市场需求 | 付费意愿 | 竞争 | 难度 | 变现周期 |")
        lines.append("|--------|--------|----------|--------|--------|------|------|--------|")

        # 数据行
        for rec in recommendations:
            priority = rec.get("priority", "-")
            name = rec.get("name", "-")[:20]
            one_liner = rec.get("one_liner", "-")[:30]
            market_demand = rec.get("market_demand", "-")
            willingness = rec.get("willingness_to_pay", "-")
            competition = rec.get("competition_level", "-")
            difficulty = rec.get("dev_difficulty", "-")
            revenue_time = rec.get("time_to_revenue", "-")

            # 添加评分颜色提示
            demand_indicator = self._get_score_indicator(market_demand)
            willingness_indicator = self._get_score_indicator(willingness)

            line = f"| {priority} | **{name}** | {one_liner} | {demand_indicator} {market_demand}/10 | {willingness_indicator} {willingness}/10 | {competition}/10 | {difficulty}/10 | {revenue_time}/10 |"
            lines.append(line)

        return "\n".join(lines)

    def _build_detailed_analysis(self, recommendations: List[Dict[str, Any]]) -> List[str]:
        """构建详细分析内容"""
        lines = []

        for i, rec in enumerate(recommendations, 1):
            lines.append(f"\n### {i}. {rec.get('name', 'Unknown')} (优先级: {rec.get('priority', '-')})\n")

            # 基本信息
            lines.append(f"**简介**: {rec.get('one_liner', '-')}\n")
            lines.append(f"**推荐理由**: {rec.get('reason', '-')}\n")

            # 评分分析
            lines.append("\n**评分分析**:\n")
            lines.append(f"- 市场需求热度: {rec.get('market_demand', '-')}/10 {self._get_bar(rec.get('market_demand', 0))}")
            lines.append(f"- 用户付费意愿: {rec.get('willingness_to_pay', '-')}/10 {self._get_bar(rec.get('willingness_to_pay', 0))}")
            lines.append(f"- 竞争程度: {rec.get('competition_level', '-')}/10 {self._get_bar(rec.get('competition_level', 0))}")
            lines.append(f"- 开发难度: {rec.get('dev_difficulty', '-')}/10 {self._get_bar(rec.get('dev_difficulty', 0))}")
            lines.append(f"- 变现周期: {rec.get('time_to_revenue', '-')}/10 {self._get_bar(rec.get('time_to_revenue', 0))}")

            # MVP功能
            mvp_features = rec.get("mvp_features", [])
            if mvp_features:
                lines.append(f"\n**MVP核心功能**:\n")
                for feature in mvp_features:
                    lines.append(f"- {feature}")

            # 市场数据支撑
            lines.append(f"\n**市场需求数据支撑**: {rec.get('data_evidence', '-')}\n")

            # 变现模式
            lines.append(f"**变现模式**: {rec.get('monetization', '-')}\n")

            # 开发周期
            lines.append(f"**开发周期**: {rec.get('dev_timeline', '-')}\n")

            # 风险提示
            lines.append(f"**风险提示**: ⚠️ {rec.get('risk_notes', '-')}\n")

        return lines

    def _get_score_indicator(self, score: int) -> str:
        """获取评分指示器"""
        if score >= 8:
            return "🔴"
        elif score >= 6:
            return "🟠"
        elif score >= 4:
            return "🟡"
        else:
            return "🟢"

    def _get_bar(self, score: int) -> str:
        """获取评分条"""
        max_bar = 10
        filled = int(score / 10 * max_bar)
        empty = max_bar - filled
        return "█" * filled + "░" * empty

    def send_notification(self, report_path: str, recommendations: List[Dict[str, Any]]):
        """发送通知（邮件、Telegram等）"""
        try:
            config = Config.NOTIFICATION_CONFIG

            # 生成摘要
            summary = self._generate_summary(recommendations)

            # 邮件通知
            if config.get("email", {}).get("enabled"):
                self._send_email(summary, report_path)

            # Telegram通知
            if config.get("telegram", {}).get("enabled"):
                self._send_telegram(summary)

            # 钉钉通知
            if config.get("dingtalk", {}).get("enabled"):
                self._send_dingtalk(summary)

        except Exception as e:
            logger.error(f"Notification sending failed: {e}")

    def _generate_summary(self, recommendations: List[Dict[str, Any]]) -> str:
        """生成摘要"""
        lines = ["📊 今日5大推荐项目:", ""]

        for i, rec in enumerate(recommendations, 1):
            priority = rec.get("priority", "-")
            name = rec.get("name", "-")
            one_liner = rec.get("one_liner", "-")
            lines.append(f"{i}. [{priority}] {name} - {one_liner}")

        lines.append("")
        lines.append("详细报告请查看项目目录的 reports/ 文件夹")

        return "\n".join(lines)

    def _send_email(self, summary: str, report_path: str):
        """发送邮件"""
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart

            config = Config.NOTIFICATION_CONFIG.get("email", {})
            sender = config.get("sender")
            password = config.get("password")
            recipients = config.get("recipients", [])
            smtp_server = config.get("smtp_server")
            smtp_port = config.get("smtp_port")

            if not all([sender, password, recipients]):
                logger.warning("Email configuration incomplete")
                return

            msg = MIMEMultipart()
            msg["From"] = sender
            msg["To"] = ",".join(recipients)
            msg["Subject"] = f"拓品日报 - {datetime.now().strftime('%Y-%m-%d')}"

            msg.attach(MIMEText(summary, "plain", "utf-8"))

            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(sender, password)
                server.send_message(msg)

            logger.info("Email notification sent")

        except Exception as e:
            logger.error(f"Email sending failed: {e}")

    def _send_telegram(self, summary: str):
        """发送Telegram消息"""
        try:
            import requests

            config = Config.NOTIFICATION_CONFIG.get("telegram", {})
            bot_token = config.get("bot_token")
            chat_id = config.get("chat_id")

            if not all([bot_token, chat_id]):
                logger.warning("Telegram configuration incomplete")
                return

            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            data = {
                "chat_id": chat_id,
                "text": summary,
                "parse_mode": "Markdown",
            }

            response = requests.post(url, data=data, timeout=10)
            response.raise_for_status()

            logger.info("Telegram notification sent")

        except Exception as e:
            logger.error(f"Telegram sending failed: {e}")

    def _send_dingtalk(self, summary: str):
        """发送钉钉消息"""
        try:
            import requests
            import hmac
            import hashlib
            import base64
            import time

            config = Config.NOTIFICATION_CONFIG.get("dingtalk", {})
            webhook = config.get("webhook")

            if not webhook:
                logger.warning("Dingtalk configuration incomplete")
                return

            # 钉钉消息格式
            data = {
                "msgtype": "text",
                "text": {
                    "content": summary
                }
            }

            response = requests.post(webhook, json=data, timeout=10)
            response.raise_for_status()

            logger.info("Dingtalk notification sent")

        except Exception as e:
            logger.error(f"Dingtalk sending failed: {e}")
