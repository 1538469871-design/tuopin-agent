import logging
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List, Optional
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


@dataclass
class StandardDataItem:
    """标准化数据项"""
    title: str
    content: str
    url: str
    source: str
    timestamp: datetime
    engagement_score: float = 0.0
    author: Optional[str] = None
    tags: List[str] = None

    def to_dict(self):
        """转换为字典"""
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        return data

    def __post_init__(self):
        if self.tags is None:
            self.tags = []


class BaseCollector(ABC):
    """数据采集器基类"""

    def __init__(self, name: str, timeout: int = 30):
        self.name = name
        self.timeout = timeout
        self.logger = logging.getLogger(f"collector.{name}")

    @abstractmethod
    def collect(self, keywords: List[str] = None) -> List[StandardDataItem]:
        """
        采集数据（必须实现）

        Args:
            keywords: 搜索关键词列表

        Returns:
            标准化数据项列表
        """
        pass

    def _validate_data(self, items: List[StandardDataItem]) -> List[StandardDataItem]:
        """数据验证"""
        valid_items = []
        for item in items:
            if not item.title or not item.url:
                self.logger.warning(f"Invalid data item: {item}")
                continue
            valid_items.append(item)
        return valid_items

    def _calculate_engagement_score(self, **metrics) -> float:
        """计算参与度评分（0-100）"""
        score = 0.0
        weights = {
            "views": 0.2,
            "likes": 0.3,
            "comments": 0.3,
            "shares": 0.2,
        }
        for key, weight in weights.items():
            if key in metrics:
                score += (metrics[key] or 0) * weight
        return min(score, 100.0)


class CollectorError(Exception):
    """采集器异常"""
    pass


class CollectorTimeout(CollectorError):
    """采集超时异常"""
    pass


class CollectorAuthError(CollectorError):
    """采集认证异常"""
    pass
