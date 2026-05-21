"""
UUVSearch - 正方形地图（支持连续坐标）
"""
import numpy as np
from .base_map import BaseMap


class SquareMap(BaseMap):
    """规则正方形区域，内部有随机障碍物"""

    def __init__(self, config: dict):
        super().__init__(config)

        # 优先使用物理尺寸，否则使用网格尺寸
        if "length" in config and "resolution" in config:
            self.length = config["length"]          # 地图边长（米）
            self.resolution = config["resolution"]  # 米/格
            self.size = int(self.length / self.resolution)
        else:
            self.size = config["grid_size"]
            self.resolution = config.get("resolution", 30.0)  # 默认30m/格
            self.length = self.size * self.resolution

        self.obstacle_ratio = config.get("obstacle_ratio", 0.1)

        # 初始化网格
        self.grid = np.zeros((self.size, self.size), dtype=np.int8)
        self._place_obstacles()

    def _place_obstacles(self):
        rng = np.random.RandomState(42)
        for _ in range(int(self.size * self.size * self.obstacle_ratio)):
            r, c = rng.randint(1, self.size-1, 2)
            if self.grid[r, c] == 0:
                self.grid[r, c] = 1

    def get_mask(self) -> np.ndarray:
        return self.grid != 1