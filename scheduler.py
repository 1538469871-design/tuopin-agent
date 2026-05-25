#!/usr/bin/env python3
import sys
import logging
import argparse
from datetime import datetime

from collectors.github import GitHubCollector
from collectors.reddit import RedditCollector
from collectors.hackernews import HackerNewsCollector
from collectors.v2ex import V2EXCollector
from collectors.producthunt import ProductHuntCollector
from collectors.base import StandardDataItem, CollectorError
from analyzer import Analyzer
from reporter import Reporter
from config import Config

# 配置日志
logging.basicConfig(
    level=Config.LOG_LEVEL,
    format=Config.LOG_FORMAT
)
logger = logging.getLogger(__name__)


class Scheduler:
    """调度器：协调所有步骤"""

    def __init__(self):
        self.collectors = []
        self.analyzer = Analyzer()
        self.reporter = Reporter()
        self._initialize_collectors()

    def _initialize_collectors(self):
        """初始化数据采集器"""
        collectors_config = Config.COLLECTORS_CONFIG

        if collectors_config.get("github", {}).get("enabled"):
            self.collectors.append(GitHubCollector())

        if collectors_config.get("reddit", {}).get("enabled"):
            self.collectors.append(RedditCollector())

        if collectors_config.get("hackernews", {}).get("enabled"):
            self.collectors.append(HackerNewsCollector())

        if collectors_config.get("v2ex", {}).get("enabled"):
            self.collectors.append(V2EXCollector())

        if collectors_config.get("producthunt", {}).get("enabled"):
            self.collectors.append(ProductHuntCollector())

        logger.info(f"Initialized {len(self.collectors)} collectors")

    def collect_data(self) -> list:
        """采集所有平台数据"""
        logger.info("=" * 60)
        logger.info("🚀 开始数据采集...")
        logger.info("=" * 60)

        all_items = []

        for collector in self.collectors:
            try:
                logger.info(f"采集 {collector.name} 数据...")
                items = collector.collect(keywords=self._get_keywords())
                all_items.extend(items)
                logger.info(f"✅ {collector.name}: 采集 {len(items)} 条数据")
            except CollectorError as e:
                logger.error(f"❌ {collector.name} 采集失败: {e}")
            except Exception as e:
                logger.error(f"❌ {collector.name} 异常: {e}")

        logger.info(f"📊 共采集 {len(all_items)} 条数据")
        return all_items

    def _get_keywords(self) -> list:
        """获取搜索关键词"""
        keywords = []
        for category_keywords in Config.SEARCH_KEYWORDS.values():
            keywords.extend(category_keywords)
        return keywords

    def analyze_data(self, items: list) -> dict:
        """分析数据"""
        logger.info("=" * 60)
        logger.info("🤖 开始AI分析...")
        logger.info("=" * 60)

        result = self.analyzer.analyze(items)

        if result.get("status") == "success":
            logger.info(f"✅ 分析完成，生成 {len(result.get('recommendations', []))} 个推荐")
        else:
            logger.error(f"❌ 分析失败: {result.get('error', 'Unknown error')}")

        return result

    def generate_report(self, analysis_result: dict) -> str:
        """生成报告"""
        logger.info("=" * 60)
        logger.info("📝 生成报告...")
        logger.info("=" * 60)

        try:
            report_path = self.reporter.generate_report(analysis_result)
            logger.info(f"✅ 报告已生成: {report_path}")

            # 发送通知
            try:
                recommendations = analysis_result.get("recommendations", [])
                self.reporter.send_notification(report_path, recommendations)
            except Exception as e:
                logger.warning(f"通知发送失败: {e}")

            return report_path

        except Exception as e:
            logger.error(f"❌ 报告生成失败: {e}")
            raise

    def run(self, debug: bool = False):
        """运行完整流程"""
        try:
            logger.info(f"\n{'=' * 60}")
            logger.info(f"拓品智能体分析系统 v{Config.PROJECT_VERSION}")
            logger.info(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info(f"{'=' * 60}\n")

            # 步骤1: 采集数据
            items = self.collect_data()

            if not items:
                logger.warning("没有采集到数据，尝试使用备用数据...")
                items = self._generate_mock_data()

            # 步骤2: 分析数据
            analysis_result = self.analyze_data(items)

            # 步骤3: 生成报告
            report_path = self.generate_report(analysis_result)

            # 输出总结
            logger.info(f"\n{'=' * 60}")
            logger.info("✅ 流程完成!")
            logger.info(f"报告位置: {report_path}")
            logger.info(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info(f"{'=' * 60}\n")

            return report_path

        except Exception as e:
            logger.error(f"\n❌ 执行失败: {e}")
            if debug:
                raise
            return None

    def _generate_mock_data(self) -> list:
        """生成模拟数据（用于测试）"""
        logger.info("生成模拟数据用于测试...")
        mock_items = [
            StandardDataItem(
                title="[示例] AI Agent框架新进展",
                content="最新的AI Agent框架支持多模态输入和实时流处理",
                url="https://example.com/1",
                source="Example",
                timestamp=datetime.now(),
                engagement_score=85.0,
                tags=["ai", "trending"]
            ),
            StandardDataItem(
                title="[示例] 浏览器插件市场调查",
                content="研究发现用户对自动化插件的需求正在增长",
                url="https://example.com/2",
                source="Example",
                timestamp=datetime.now(),
                engagement_score=75.0,
                tags=["plugin", "market"]
            ),
        ]
        return mock_items


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="拓品智能体分析系统 - 每日自动市场分析和项目推荐"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="调试模式（显示详细错误信息）"
    )
    parser.add_argument(
        "--mock",
        action="store_true",
        help="使用模拟数据测试（跳过真实采集）"
    )

    args = parser.parse_args()

    scheduler = Scheduler()

    # 测试模式
    if args.mock:
        logger.info("📝 使用模拟数据测试模式...")
        items = scheduler._generate_mock_data()
        analysis_result = scheduler.analyze_data(items)
        report_path = scheduler.generate_report(analysis_result)
        logger.info(f"✅ 测试完成: {report_path}")
        return

    # 正常模式
    scheduler.run(debug=args.debug)


if __name__ == "__main__":
    main()
