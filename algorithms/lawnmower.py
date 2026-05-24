"""
UUVSearch - 梳形覆盖算法（全覆盖基线 / 上界）

依赖完整地图（map_obj）预生成蛇形航路点，遍历所有自由格子。自带卡住检测与
随机脱困。导航方式根据环境自动切换：网格环境用 8 方向离散移动，连续环境用
航向导航。

⚠️ 此算法需要完整的 grid 信息才能生成航路点，不代表真实 UUV（无先验地图）
的能力。它作为"已知地图最优全覆盖"的上界基线，用于衡量其他算法的覆盖率差距。

用法:
  # 网格环境
  python scripts/run_algo.py --algo lawnmower --episodes 30
  # 连续环境
  python scripts/run_experiment.py --env continuous --algo lawnmower --episodes 50
"""
import numpy as np
from .base_algo import BaseAlgorithm


class LawnmowerSearch(BaseAlgorithm):
    def __init__(self, config: dict):
        super().__init__(config)
        self.waypoints = []
        self.current_target_idx = 0
        self.stuck_counter = 0
        self.last_pos = None
        self.swath_width = 2
        self.random_steps_left = 0

        self.map_obj = config.get("map_obj", None)
        # 连续环境：5 个航向变化动作 [-90, -45, 0, 45, 90] 度
        self.action_angles = np.array(config.get("action_angles", [-90, -45, 0, 45, 90]))
        self.num_actions = len(self.action_angles)
        self.resolution = config.get("resolution", 30.0)
        self.map_length = config.get("map_length", 420.0)

    def reset(self):
        self.current_target_idx = 0
        self.stuck_counter = 0
        self.last_pos = None
        self.random_steps_left = 0
        self.waypoints = []

    def _generate_waypoints(self, map_obj):
        rows, cols = map_obj.grid.shape
        waypoints = []
        row = 1
        direction = 1
        while row < rows:
            if direction == 1:
                col_range = range(1, cols - 1)
            else:
                col_range = range(cols - 2, 0, -1)

            for col in col_range:
                if map_obj.is_free(row, col):
                    waypoints.append((row, col))
                else:
                    for dr in [-1, 1]:
                        nr = row + dr
                        if 0 < nr < rows - 1 and map_obj.is_free(nr, col):
                            waypoints.append((nr, col))
                            break
            row += self.swath_width
            direction *= -1
        self.waypoints = waypoints

    def _get_grid_pos(self, obs):
        """从网格或连续观测中提取网格坐标 (row, col)"""
        if isinstance(obs, dict):
            return obs["auv_pos"]

        # 连续环境：obs 尾部为 [x_norm, y_norm, sin_psi, cos_psi]
        x_norm = float(obs[-4])
        y_norm = float(obs[-3])
        r = int(y_norm * self.map_length / self.resolution)
        c = int(x_norm * self.map_length / self.resolution)
        return (r, c)

    def _get_heading(self, obs):
        """从连续观测中提取 AUV 航向（弧度），网格环境返回 None"""
        if isinstance(obs, dict):
            return None
        sin_psi = float(obs[-2])
        cos_psi = float(obs[-1])
        return np.arctan2(sin_psi, cos_psi)

    def _is_continuous(self, obs):
        return not isinstance(obs, dict)

    def select_action(self, obs) -> int:
        if not self.waypoints:
            if self.map_obj is None:
                raise RuntimeError("LawnmowerSearch 需要 map_obj 参数")
            self._generate_waypoints(self.map_obj)
            self.current_target_idx = 0

        n_acts = self.num_actions if self._is_continuous(obs) else 8

        if self.random_steps_left > 0:
            self.random_steps_left -= 1
            return np.random.randint(0, n_acts)

        if self.current_target_idx >= len(self.waypoints):
            return np.random.randint(0, n_acts)

        pos = self._get_grid_pos(obs)
        target = self.waypoints[self.current_target_idx]

        advanced = False
        if max(abs(pos[0] - target[0]), abs(pos[1] - target[1])) <= 1:
            self.current_target_idx += 1
            self.stuck_counter = 0
            self.last_pos = pos
            advanced = True
            if self.current_target_idx >= len(self.waypoints):
                return 0
            target = self.waypoints[self.current_target_idx]

        if not advanced:
            if self.last_pos is not None and pos == self.last_pos:
                self.stuck_counter += 1
            else:
                self.stuck_counter = 0
        self.last_pos = pos

        if self.stuck_counter >= 4:
            # 跳过当前行剩余航路点，直接跳到下一扫描行
            jumped = False
            if self._is_continuous(obs) and self.current_target_idx < len(self.waypoints):
                current_row = self.waypoints[self.current_target_idx][0]
                while self.current_target_idx < len(self.waypoints):
                    self.current_target_idx += 1
                    if self.current_target_idx >= len(self.waypoints):
                        break
                    if abs(self.waypoints[self.current_target_idx][0] - current_row) >= self.swath_width:
                        jumped = True
                        break
            if not jumped:
                self.current_target_idx += 1
            self.stuck_counter = 0
            self.random_steps_left = 5
            return np.random.randint(0, n_acts)

        if isinstance(obs, dict):
            # 网格模式：8 方向离散导航
            dr = target[0] - pos[0]
            dc = target[1] - pos[1]
            action_map = {
                (-1, 0): 0, (1, 0): 1, (0, -1): 2, (0, 1): 3,
                (-1, -1): 4, (-1, 1): 5, (1, -1): 6, (1, 1): 7
            }
            return action_map.get((np.sign(dr), np.sign(dc)), 0)
        else:
            # 连续模式：计算期望航向，选最接近的航向变化动作
            psi = self._get_heading(obs)
            target_r, target_c = target
            target_x = (target_c + 0.5) * self.resolution
            target_y = (target_r + 0.5) * self.resolution

            x_norm, y_norm = float(obs[-4]), float(obs[-3])
            cur_x = x_norm * self.map_length
            cur_y = y_norm * self.map_length

            desired_psi = np.arctan2(target_y - cur_y, target_x - cur_x)
            dpsi = desired_psi - psi
            dpsi = (dpsi + np.pi) % (2 * np.pi) - np.pi
            dpsi_deg = np.rad2deg(dpsi)
            return int(np.argmin(np.abs(self.action_angles - dpsi_deg)))
