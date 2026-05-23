"""
UUVSearch - 算法抽象基类

所有传统搜索算法（Random、Lawnmower、GreedyProb）继承此类。
RL 算法（DQN、SAC）有自己的接口，不继承此类。
"""
from abc import ABC, abstractmethod


class BaseAlgorithm(ABC):
    """传统搜索算法接口"""

    def __init__(self, config: dict):
        self.config = config

    @abstractmethod
    def select_action(self, obs) -> int:
        """
        根据观测选择动作。

        网格环境: obs 为 dict，含 auv_pos、hotspot 等字段
        连续环境: obs 为 1D numpy array（patch + 归一化状态）

        Returns: 动作编号（网格 0-7，连续 0-4）
        """
        pass

    def reset(self):
        """每回合开始时调用，有状态算法可重写"""
        pass