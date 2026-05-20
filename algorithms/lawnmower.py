"""
UUVSearch - 梳形覆盖算法（改进版）
生成蛇形航路点（只含自由格子），贪心导航，卡住时随机脱困。
"""
import numpy as np
from .base_algo import BaseAlgorithm


class LawnmowerSearch(BaseAlgorithm):
    def __init__(self, config: dict):
        super().__init__(config)
        self.waypoints = []           # 全局航路点列表（仅自由格子）
        self.current_target_idx = 0
        self.stuck_counter = 0
        self.last_pos = None
        self.swath_width = 2          # 扫描行间隔（3×3探测半径=1）
        self.random_steps_left = 0    # 剩余随机脱困步数

        # 必须在config中提供 map 对象或至少 map_shape
        self.map_obj = config.get("map_obj", None)  # 可选：直接传入地图对象

    def reset(self):
        self.current_target_idx = 0
        self.stuck_counter = 0
        self.last_pos = None
        self.random_steps_left = 0
        self.waypoints = []

    def _generate_waypoints(self, map_obj):
        """生成蛇形航路点，自动跳过障碍物格子"""
        rows, cols = map_obj.grid.shape
        waypoints = []
        row = 1
        direction = 1
        while row < rows - 1:
            if direction == 1:
                col_range = range(1, cols - 1)
            else:
                col_range = range(cols - 2, 0, -1)

            for col in col_range:
                if map_obj.is_free(row, col):
                    waypoints.append((row, col))
                else:
                    # 尝试在相邻行找自由格子（最多偏移±1）
                    for dr in [-1, 1]:
                        nr = row + dr
                        if 0 < nr < rows - 1 and map_obj.is_free(nr, col):
                            waypoints.append((nr, col))
                            break
            row += self.swath_width
            direction *= -1
        self.waypoints = waypoints

    def select_action(self, obs: dict) -> int:
        # 延迟生成：需要地图对象
        if not self.waypoints:
            if self.map_obj is None:
                raise RuntimeError("LawnmowerSearch 需要 map_obj 参数")
            self._generate_waypoints(self.map_obj)
            self.current_target_idx = 0

        # 随机脱困模式（临时）
        if self.random_steps_left > 0:
            self.random_steps_left -= 1
            return np.random.randint(0, 8)

        # 无航路点可用
        if self.current_target_idx >= len(self.waypoints):
            return np.random.randint(0, 8)

        pos = obs['auv_pos']
        target = self.waypoints[self.current_target_idx]

        # 到达目标附近（距离<=1）
        if max(abs(pos[0] - target[0]), abs(pos[1] - target[1])) <= 1:
            self.current_target_idx += 1
            self.stuck_counter = 0
            self.last_pos = pos
            if self.current_target_idx >= len(self.waypoints):
                return 0
            target = self.waypoints[self.current_target_idx]

        # 卡住检测
        if self.last_pos is not None and pos == self.last_pos:
            self.stuck_counter += 1
        else:
            self.stuck_counter = 0
        self.last_pos = pos

        # 连续卡住 >= 4 步 → 启动随机脱困 3 步
        if self.stuck_counter >= 4:
            self.random_steps_left = 3
            self.stuck_counter = 0
            return np.random.randint(0, 8)

        # 贪心导航
        dr = target[0] - pos[0]
        dc = target[1] - pos[1]
        dr_sign = np.sign(dr)
        dc_sign = np.sign(dc)

        action_map = {
            (-1, 0): 0, (1, 0): 1, (0, -1): 2, (0, 1): 3,
            (-1, -1): 4, (-1, 1): 5, (1, -1): 6, (1, 1): 7
        }
        return action_map.get((dr_sign, dc_sign), 0)