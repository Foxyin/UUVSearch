"""
UUVSearch - 不规则多边形地图
支持自定义多边形边界和内部圆形障碍物。
"""
import numpy as np
from .base_map import BaseMap

class IrregularMap(BaseMap):
    def __init__(self, config: dict):
        super().__init__(config)
        self.length = config["length"]
        self.resolution = config["resolution"]
        self.size = int(self.length / self.resolution)

        # 边界多边形顶点（网格坐标），例如一个八边形
        self.polygon = config.get("polygon", None)
        # 内部障碍物：列表，每项 (row, col, radius_grid)
        self.obstacles = config.get("obstacles", [])

        self.grid = np.zeros((self.size, self.size), dtype=np.int8)
        self._apply_polygon_boundary()
        self._apply_obstacles()

    def _apply_polygon_boundary(self):
        """将多边形外部的网格标记为障碍物"""
        if self.polygon is None:
            return
        try:
            from shapely.geometry import Point, Polygon
        except ImportError:
            print("警告：未安装 shapely，多边形边界将被忽略。安装：pip install shapely")
            return

        poly = Polygon(self.polygon)
        for r in range(self.size):
            for c in range(self.size):
                # 使用网格中心坐标判断
                if not poly.contains(Point(r, c)):
                    self.grid[r, c] = 1

    def _apply_obstacles(self):
        """绘制内部圆形障碍物"""
        for r, c, radius in self.obstacles:
            for dr in range(-radius, radius + 1):
                for dc in range(-radius, radius + 1):
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < self.size and 0 <= nc < self.size:
                        if dr ** 2 + dc ** 2 <= radius ** 2:
                            self.grid[nr, nc] = 1

    def get_mask(self) -> np.ndarray:
        return self.grid != 1