import requests
import logging
from datetime import datetime
from typing import List
from .base import BaseCollector, StandardDataItem, CollectorError

logger = logging.getLogger(__name__)


class ProductHuntCollector(BaseCollector):
    """ProductHunt新产品采集器"""

    def __init__(self):
        super().__init__("producthunt", timeout=30)
        self.headers = {
            "User-Agent": "TuoPinAnalyzer/1.0"
        }

    def collect(self, keywords: List[str] = None) -> List[StandardDataItem]:
        """采集ProductHunt新产品"""
        items = []
        try:
            items.extend(self._fetch_today_products())
        except Exception as e:
            logger.error(f"ProductHunt collection failed: {e}")
            raise CollectorError(f"ProductHunt collection error: {e}")

        return self._validate_data(items)

    def _fetch_today_products(self) -> List[StandardDataItem]:
        """获取今天的热门产品"""
        items = []
        try:
            # 使用非官方API或RSS源采集数据
            # ProductHunt 官方API需要认证，这里使用RSS或爬虫方式
            url = "https://api.producthunt.com/v2/posts"

            # 如果没有API key，使用替代方案
            items.extend(self._fetch_via_scraping())

        except Exception as e:
            logger.debug(f"Error fetching ProductHunt: {e}")

        return items

    def _fetch_via_scraping(self) -> List[StandardDataItem]:
        """通过爬虫获取ProductHunt数据"""
        items = []
        try:
            # 使用GraphQL API (需要处理CORS)
            # 或者使用RSS源: https://www.producthunt.com/feed
            url = "https://www.producthunt.com/feed"

            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()

            # 使用feedparser解析RSS
            import feedparser
            feed = feedparser.parse(response.content)

            for entry in feed.entries[:20]:
                # 解析RSS条目
                title = entry.get('title', '')
                summary = entry.get('summary', '')
                link = entry.get('link', '')

                # 简单的参与度评估（基于描述长度）
                engagement_score = min(len(summary) / 10, 100)

                item = StandardDataItem(
                    title=f"[ProductHunt] {title[:100]}",
                    content=summary[:500],
                    url=link,
                    source="ProductHunt",
                    timestamp=datetime.now(),
                    engagement_score=engagement_score,
                    author="ProductHunt",
                    tags=["product", "producthunt", "new"]
                )
                items.append(item)

        except Exception as e:
            logger.debug(f"ProductHunt scraping error: {e}")

        return items

    def _calculate_engagement_score(self, **metrics) -> float:
        """计算ProductHunt产品参与度评分"""
        score = 0.0
        if "upvotes" in metrics:
            score += min(metrics["upvotes"] / 100 * 50, 50)
        if "comments" in metrics:
            score += min(metrics["comments"] / 20 * 50, 50)
        return min(score, 100.0)
