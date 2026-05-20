"""
UUVSearch - 算法抽象基类
"""
from abc import ABC, abstractmethod


class BaseAlgorithm(ABC):
    """所有搜索算法必须实现的接口"""

    def __init__(self, config: dict):
        self.config = config

    @abstractmethod
    def select_action(self, obs: dict) -> int:
        """
        根据观测选择动作

        Args:
            obs: 环境返回的观测字典，至少包含 'auv_pos' (row, col)

        Returns:
            action: int, 0~7 之间的动作编号
        """
        pass

    def reset(self):
        """每回合开始时调用，有状态算法可重写"""
        pass