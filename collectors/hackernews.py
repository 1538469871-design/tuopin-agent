import requests
import logging
from datetime import datetime
from typing import List
from .base import BaseCollector, StandardDataItem, CollectorError

logger = logging.getLogger(__name__)


class HackerNewsCollector(BaseCollector):
    """HackerNews趋势采集器"""

    def __init__(self):
        super().__init__("hackernews", timeout=30)
        self.api_url = "https://hacker-news.firebaseio.com/v0"

    def collect(self, keywords: List[str] = None) -> List[StandardDataItem]:
        """采集HackerNews热门故事"""
        items = []
        try:
            items.extend(self._fetch_top_stories())
        except Exception as e:
            logger.error(f"HackerNews collection failed: {e}")
            raise CollectorError(f"HackerNews collection error: {e}")

        return self._validate_data(items)

    def _fetch_top_stories(self) -> List[StandardDataItem]:
        """获取热门故事"""
        items = []
        try:
            # 获取top stories ID列表
            url = f"{self.api_url}/topstories.json"
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()

            story_ids = response.json()[:30]  # 获取前30个

            for story_id in story_ids:
                try:
                    item_data = self._fetch_story(story_id)
                    if item_data:
                        items.append(item_data)
                except Exception as e:
                    logger.debug(f"Failed to fetch story {story_id}: {e}")

        except requests.Timeout:
            logger.warning("HackerNews request timeout")
        except Exception as e:
            logger.error(f"Error fetching HackerNews stories: {e}")

        return items

    def _fetch_story(self, story_id: int) -> StandardDataItem:
        """获取单个故事详情"""
        try:
            url = f"{self.api_url}/item/{story_id}.json"
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()

            story = response.json()

            # 只保留有效的故事
            if not story.get("title") or not story.get("url"):
                return None

            item = StandardDataItem(
                title=f"[HN] {story.get('title', '')[:100]}",
                content=story.get("title", "")[:500],
                url=story.get("url", f"https://news.ycombinator.com/item?id={story_id}"),
                source="HackerNews",
                timestamp=datetime.fromtimestamp(story.get("time", 0)),
                engagement_score=self._calculate_engagement_score(
                    points=story.get("score", 0),
                    comments=story.get("descendants", 0),
                ),
                author=story.get("by", "unknown"),
                tags=["trending", "hackernews", "tech"]
            )
            return item

        except Exception as e:
            logger.debug(f"Error fetching story {story_id}: {e}")
            return None

    def _calculate_engagement_score(self, **metrics) -> float:
        """计算HackerNews故事参与度评分"""
        score = 0.0
        if "points" in metrics:
            score += min(metrics["points"] / 100 * 50, 50)
        if "comments" in metrics:
            score += min(metrics["comments"] / 50 * 50, 50)
        return min(score, 100.0)
