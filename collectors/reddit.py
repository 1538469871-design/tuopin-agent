import requests
import logging
from datetime import datetime
from typing import List
from .base import BaseCollector, StandardDataItem, CollectorError

logger = logging.getLogger(__name__)


class RedditCollector(BaseCollector):
    """Reddit热门讨论采集器"""

    def __init__(self):
        super().__init__("reddit", timeout=30)
        self.api_url = "https://www.reddit.com"
        self.headers = {
            "User-Agent": "TuoPinAnalyzer/1.0"
        }
        # Reddit子版块配置
        self.subreddits = [
            "learnprogramming",
            "webdev",
            "SideProject",
            "startups",
            "AutomationTesting",
            "ChatGPT",
        ]

    def collect(self, keywords: List[str] = None) -> List[StandardDataItem]:
        """采集Reddit热门帖子"""
        items = []
        try:
            for subreddit in self.subreddits:
                items.extend(self._fetch_subreddit(subreddit))
        except Exception as e:
            logger.error(f"Reddit collection failed: {e}")
            raise CollectorError(f"Reddit collection error: {e}")

        return self._validate_data(items)

    def _fetch_subreddit(self, subreddit: str) -> List[StandardDataItem]:
        """获取子版块热门帖子"""
        items = []
        try:
            # 获取热门帖子（top posts）
            url = f"{self.api_url}/r/{subreddit}/hot.json"
            params = {
                "limit": 25,
            }

            response = requests.get(url, headers=self.headers, params=params, timeout=self.timeout)
            response.raise_for_status()

            data = response.json()
            posts = data.get("data", {}).get("children", [])

            for post_data in posts:
                post = post_data.get("data", {})

                # 过滤自我帖子
                if post.get("is_self") and len(post.get("selftext", "")) < 50:
                    continue

                item = StandardDataItem(
                    title=f"[Reddit] r/{subreddit}: {post['title'][:100]}",
                    content=post.get("selftext", "")[:500],
                    url=post.get("url", f"https://reddit.com{post.get('permalink', '')}"),
                    source="Reddit",
                    timestamp=datetime.fromtimestamp(post.get("created_utc", 0)),
                    engagement_score=self._calculate_engagement_score(
                        upvotes=post.get("ups", 0),
                        comments=post.get("num_comments", 0),
                    ),
                    author=post.get("author", "unknown"),
                    tags=["discussion", "reddit", subreddit.lower()]
                )
                items.append(item)

        except requests.Timeout:
            logger.warning(f"Reddit request timeout for subreddit: {subreddit}")
        except Exception as e:
            logger.error(f"Error fetching subreddit '{subreddit}': {e}")

        return items

    def _calculate_engagement_score(self, **metrics) -> float:
        """计算Reddit帖子参与度评分"""
        score = 0.0
        if "upvotes" in metrics:
            score += min(metrics["upvotes"] / 100 * 50, 50)
        if "comments" in metrics:
            score += min(metrics["comments"] / 50 * 50, 50)
        return min(score, 100.0)
