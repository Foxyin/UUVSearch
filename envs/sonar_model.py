"""
UUVSearch - 声纳模型
支持圆形和扇形探测区域，带射线遮挡（Bresenham直线遍历）。
"""
import numpy as np


class SonarModel:
    def __init__(self, config: dict):
        self.type = config.get("type", "circle")
        self.max_range = config.get("max_range", 5)
        self.sector_angle = config.get("sector_angle", 120)  # 度
        self.attenuation = config.get("attenuation", 0.3)  # 距离衰减系数

    def get_detection_probability(self, distance: float) -> float:
        """距离相关的检测概率 P(detect | target present at distance)"""
        if distance > self.max_range:
            return 0.0
        return max(0.0, 1.0 - self.attenuation * distance / self.max_range)

    def get_fov_cells(self, auv_pos: tuple, heading_deg: float,
                      grid: np.ndarray) -> list:
        """
        计算声纳探测覆盖的网格列表 (row, col)

        Args:
            auv_pos: (row, col) AUV 所在网格坐标
            heading_deg: AUV 当前朝向（度），0→右，90→下（网格行方向）
                         （注意：此处约定与屏幕坐标一致，可调整）
            grid: 二维障碍物网格 (0=自由, 1=障碍物)

        Returns:
            fov_cells: list of (row, col) 未被遮挡的网格
        """
        if self.type == "circle":
            return self._circle_fov(auv_pos, grid)
        elif self.type == "sector":
            return self._sector_fov(auv_pos, heading_deg, grid)
        else:
            raise ValueError(f"未知声纳类型: {self.type}")

    def _circle_fov(self, auv_pos, grid):
        """圆形探测区域"""
        rows, cols = grid.shape
        r0, c0 = auv_pos
        radius = self.max_range
        fov_cells = []
        # 遍历外接正方形
        for r in range(max(0, r0 - radius), min(rows, r0 + radius + 1)):
            for c in range(max(0, c0 - radius), min(cols, c0 + radius + 1)):
                dr = r - r0
                dc = c - c0
                if dr * dr + dc * dc <= radius * radius:
                    # 射线检测
                    if self._is_visible(r0, c0, r, c, grid):
                        fov_cells.append((r, c))
        return fov_cells

    def _sector_fov(self, auv_pos, heading_deg, grid):
        """扇形探测区域"""
        rows, cols = grid.shape
        r0, c0 = auv_pos
        radius = self.max_range
        half_angle = self.sector_angle / 2.0

        fov_cells = []
        for r in range(max(0, r0 - radius), min(rows, r0 + radius + 1)):
            for c in range(max(0, c0 - radius), min(cols, c0 + radius + 1)):
                dr = r - r0
                dc = c - c0
                dist_sq = dr * dr + dc * dc
                if dist_sq <= radius * radius and dist_sq > 0:
                    # 计算该格子相对于AUV的角度（0°朝右，顺时针为正）
                    angle = np.degrees(np.arctan2(dr, dc))  # arctan2(row, col)
                    # 归一化到 [0, 360)
                    if angle < 0:
                        angle += 360
                    # 计算相对朝向的夹角差
                    diff = abs(angle - heading_deg)
                    diff = min(diff, 360 - diff)
                    if diff <= half_angle:
                        if self._is_visible(r0, c0, r, c, grid):
                            fov_cells.append((r, c))
        # 加入自身所在格
        if self._is_visible(r0, c0, r0, c0, grid):
            fov_cells.append((r0, c0))
        return fov_cells

    def _is_visible(self, r0, c0, r1, c1, grid):
        """Bresenham直线检查。路径上无障碍物→True；中途碰到障碍物→False（障碍物格不可见）"""
        r0, c0 = int(r0), int(c0)
        r1, c1 = int(r1), int(c1)
        if r0 == r1 and c0 == c1:
            return True

        dr = abs(r1 - r0)
        dc = abs(c1 - c0)
        sr = 1 if r1 > r0 else -1
        sc = 1 if c1 > c0 else -1
        err = dr - dc

        r, c = r0, c0
        while True:
            # 检查当前格子是否为障碍物（起点除外，因为起点是AUV位置，不可能是障碍物）
            if (r != r0 or c != c0) and grid[r, c] == 1:
                return False  # 射线被阻挡，目标不可见
            if r == r1 and c == c1:
                break
            e2 = 2 * err
            if e2 > -dc:
                err -= dc
                r += sr
            if e2 < dr:
                err += dr
                c += sc
        return True