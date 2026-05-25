import requests
import logging
from datetime import datetime, timedelta
from typing import List
from urllib.parse import urljoin
from .base import BaseCollector, StandardDataItem, CollectorError

logger = logging.getLogger(__name__)


class GitHubCollector(BaseCollector):
    """GitHub趋势repo和讨论采集器"""

    def __init__(self):
        super().__init__("github", timeout=30)
        self.api_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "TuoPinAnalyzer/1.0"
        }

    def collect(self, keywords: List[str] = None) -> List[StandardDataItem]:
        """采集GitHub热门项目"""
        if keywords is None:
            keywords = ["AI agent", "browser extension", "automation"]

        items = []
        try:
            for keyword in keywords[:5]:
                items.extend(self._search_repos(keyword))
        except Exception as e:
            logger.error(f"GitHub collection failed: {e}")
            raise CollectorError(f"GitHub collection error: {e}")

        return self._validate_data(items)

    def _search_repos(self, keyword: str) -> List[StandardDataItem]:
        """搜索仓库"""
        items = []
        try:
            # 搜索过去7天新增的仓库
            since_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
            query = f"{keyword} created:>{since_date} stars:>10"

            url = f"{self.api_url}/search/repositories"
            params = {
                "q": query,
                "sort": "stars",
                "order": "desc",
                "per_page": 20,
                "page": 1
            }

            response = requests.get(url, headers=self.headers, params=params, timeout=self.timeout)
            response.raise_for_status()

            data = response.json()
            repos = data.get("items", [])

            for repo in repos:
                item = StandardDataItem(
                    title=f"[GitHub] {repo['name']} - {repo.get('description', '')[:100]}",
                    content=repo.get("description", "")[:500],
                    url=repo["html_url"],
                    source="GitHub",
                    timestamp=datetime.fromisoformat(repo["updated_at"].replace("Z", "+00:00")),
                    engagement_score=self._calculate_engagement_score(
                        stars=repo.get("stargazers_count", 0),
                        forks=repo.get("forks_count", 0),
                        issues=repo.get("open_issues_count", 0),
                    ),
                    author=repo["owner"]["login"],
                    tags=["trending", "github", keyword.lower()]
                )
                items.append(item)

        except requests.Timeout:
            logger.warning(f"GitHub request timeout for keyword: {keyword}")
        except Exception as e:
            logger.error(f"Error searching repos for '{keyword}': {e}")

        return items

    def _calculate_engagement_score(self, **metrics) -> float:
        """计算GitHub项目参与度评分"""
        score = 0.0
        if "stars" in metrics:
            score += min(metrics["stars"] / 1000 * 30, 30)
        if "forks" in metrics:
            score += min(metrics["forks"] / 100 * 30, 30)
        if "issues" in metrics:
            score += min(metrics["issues"] / 50 * 20, 20)
        return min(score, 100.0)
