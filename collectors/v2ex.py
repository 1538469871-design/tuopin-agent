import requests
import logging
from datetime import datetime
from typing import List
from bs4 import BeautifulSoup
from .base import BaseCollector, StandardDataItem, CollectorError

logger = logging.getLogger(__name__)


class V2EXCollector(BaseCollector):
    """V2EX热门话题采集器"""

    def __init__(self):
        super().__init__("v2ex", timeout=30)
        self.api_url = "https://www.v2ex.com/api/v2"
        self.headers = {
            "User-Agent": "TuoPinAnalyzer/1.0"
        }

    def collect(self, keywords: List[str] = None) -> List[StandardDataItem]:
        """采集V2EX热门话题"""
        items = []
        try:
            # V2EX提供的节点: tech, ai, startup等
            nodes = ["tech", "ai", "startup", "create", "ask"]
            for node in nodes:
                items.extend(self._fetch_node_topics(node))
        except Exception as e:
            logger.error(f"V2EX collection failed: {e}")
            raise CollectorError(f"V2EX collection error: {e}")

        return self._validate_data(items)

    def _fetch_node_topics(self, node: str) -> List[StandardDataItem]:
        """获取节点热门话题"""
        items = []
        try:
            # 使用V2EX的API获取热门话题
            url = f"{self.api_url}/topics/hot"
            params = {"node_id": self._get_node_id(node)}

            response = requests.get(url, headers=self.headers, params=params, timeout=self.timeout)
            response.raise_for_status()

            topics = response.json()

            for topic in topics[:20]:  # 获取前20个
                item = StandardDataItem(
                    title=f"[V2EX] {topic['title'][:100]}",
                    content=topic.get('content', '')[:500],
                    url=f"https://www.v2ex.com/t/{topic['id']}",
                    source="V2EX",
                    timestamp=datetime.fromtimestamp(topic.get('created', 0)),
                    engagement_score=self._calculate_engagement_score(
                        replies=topic.get('replies', 0),
                        clicks=topic.get('clicks', 0),
                    ),
                    author=topic.get('member', {}).get('username', 'unknown'),
                    tags=["discussion", "v2ex", node.lower()]
                )
                items.append(item)

        except Exception as e:
            logger.debug(f"Error fetching V2EX node '{node}': {e}")

        return items

    def _get_node_id(self, node_name: str) -> int:
        """获取节点ID"""
        node_mapping = {
            "tech": 1,
            "ai": 392,
            "startup": 13,
            "create": 15,
            "ask": 2,
        }
        return node_mapping.get(node_name, 1)

    def _calculate_engagement_score(self, **metrics) -> float:
        """计算V2EX话题参与度评分"""
        score = 0.0
        if "replies" in metrics:
            score += min(metrics["replies"] / 20 * 50, 50)
        if "clicks" in metrics:
            score += min(metrics["clicks"] / 100 * 50, 50)
        return min(score, 100.0)
