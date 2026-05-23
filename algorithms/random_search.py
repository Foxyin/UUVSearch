"""
UUVSearch - 随机搜索算法（基线）

不依赖任何环境信息或地图，每步均匀随机选择动作。作为所有智能搜索算法的
下界基线：任何有意义的搜索策略应当显著优于纯随机。

支持网格环境（8 方向）和连续环境（5 航向变化），通过 num_actions 配置。

用法:
  python scripts/run_experiment.py --env continuous --algo random --episodes 50
  python scripts/run_algo.py --algo random --episodes 30
"""
import numpy as np
from .base_algo import BaseAlgorithm


class RandomSearch(BaseAlgorithm):
    """均匀随机动作选择 — 搜索效率的下界基线"""

    def __init__(self, config: dict):
        super().__init__(config)
        self.num_actions = config.get("num_actions", 8)

    def select_action(self, obs) -> int:
        return np.random.randint(0, self.num_actions)