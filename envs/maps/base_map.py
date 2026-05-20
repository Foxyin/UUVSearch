"""
UUVSearch - 地图抽象基类
"""
from abc import ABC, abstractmethod
import numpy as np


class BaseMap(ABC):
    """所有地图必须实现的接口"""

    def __init__(self, config: dict):
        self.config = config
        # 子类需在此初始化 self.grid (np.ndarray, dtype=int8)
        # 0=自由, 1=障碍物, 2=目标（由环境在reset时设置）

    @abstractmethod
    def get_mask(self) -> np.ndarray:
        """
        返回可搜索区域的布尔掩码 (True=可搜索)
        """
        pass

    def is_free(self, row: int, col: int) -> bool:
        """检查 (row, col) 是否为自由格子（非障碍物且未出界）"""
        rows, cols = self.grid.shape
        if 0 <= row < rows and 0 <= col < cols:
            return self.grid[row, col] != 1
        return False

    def mark_visited(self, row: int, col: int):
        """标记已访问（若为自由格子）"""
        if self.is_free(row, col) and self.grid[row, col] == 0:
            self.grid[row, col] = 3

    def set_target(self, row: int, col: int):
        """放置目标"""
        self.grid[row, col] = 2

    def get_target_pos(self) -> tuple:
        """返回目标位置 (row, col)，若无目标返回None"""
        target_idx = np.argwhere(self.grid == 2)
        if len(target_idx) > 0:
            return tuple(target_idx[0])
        return None

    def get_free_cells(self) -> list:
        """返回所有自由格子的坐标列表"""
        return [tuple(coord) for coord in np.argwhere(self.grid == 0)]