"""
UUVSearch - 随机搜索算法
"""
import numpy as np
from .base_algo import BaseAlgorithm


class RandomSearch(BaseAlgorithm):
    """完全随机的动作选择，可配置动作数量"""

    def __init__(self, config: dict):
        super().__init__(config)
        self.num_actions = config.get("num_actions", 8)

    def select_action(self, obs: dict) -> int:
        return np.random.randint(0, self.num_actions)