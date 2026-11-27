"""
UUVSearch - 全局贝叶斯贪心搜索（经典 search-theory 基线）

维护自己的目标概率图（不读取环境的 info_map，不使用特权地图）：
  - 初始先验均匀（可选 config["prior"] 传入非均匀先验）
  - 每步用与声呐模型一致的 P(detect|d) 对 FOV 内格子做贝叶斯更新
  - 障碍物只来自观测到的 11x11 obstacle patch，未知格按自由处理
  - 决策：选后验概率最高的格子作为目标，概率并列时取最近；朝目标选最接近的航向
  - 卡住 4 步则把当前目标概率降权并随机游走 5 步

这是"信息驱动"的经典基线：只看一步后验，没有长时程规划。
"""
import numpy as np
from .base_algo import BaseAlgorithm
from .nav import AStarNavigator
from envs.sonar_model import SonarModel


class BayesMyopicSearch(BaseAlgorithm):
    def __init__(self, config: dict):
        super().__init__(config)
        self.action_angles = np.array(config.get("action_angles", [-90, -45, 0, 45, 90]))
        self.num_actions = len(self.action_angles)
        self.resolution = config.get("resolution", 30.0)
        self.map_length = config.get("map_length", 420.0)
        self.sonar = SonarModel(config.get("sonar", {"type": "circle", "max_range": 3,
                                                     "attenuation": 0.3}))
        self.shape = tuple(config.get("grid_shape", (14, 14)))
        self.patch_radius = int(config.get("obs_patch_radius", 5))
        self.prior = config.get("prior", None)

        self.belief = None
        self.known_obstacle = None
        self.free = np.ones(self.shape, dtype=bool)
        self.nav = AStarNavigator(self.free, self.action_angles, lookahead=2)
        self.stuck_counter = 0
        self.last_pos = None
        self.random_steps_left = 0

    # ------------------------------------------------------------------ reset
    def reset(self):
        self.stuck_counter = 0
        self.last_pos = None
        self.random_steps_left = 0
        self.known_obstacle = np.zeros(self.shape, dtype=bool)
        self.free[:] = True
        self.nav.reset()
        if self.prior is not None:
            self.belief = np.asarray(self.prior, dtype=np.float64).copy()
        else:
            self.belief = np.ones(self.shape, dtype=np.float64)
        self.belief /= self.belief.sum()

    # ------------------------------------------------------------------ utils
    def _get_pos_heading(self, obs):
        """返回连续格坐标 (row_f, col_f) 与航向；取格时再 int()。"""
        x_norm, y_norm = float(obs[-4]), float(obs[-3])
        rf = y_norm * self.map_length / self.resolution
        cf = x_norm * self.map_length / self.resolution
        psi = np.arctan2(float(obs[-2]), float(obs[-1]))
        return (rf, cf), psi

    def _update_known_obstacle(self, obs, pos):
        """从观测的第 4 个 patch 累积已知障碍物"""
        n = self.patch_radius
        side = 2 * n + 1
        start = 3 * side * side
        patch = obs[start:start + side * side].reshape(side, side)
        r0, c0 = pos
        rows, cols = self.shape
        for dr in range(-n, n + 1):
            for dc in range(-n, n + 1):
                if patch[dr + n, dc + n] > 0.5:
                    r, c = r0 + dr, c0 + dc
                    if 0 <= r < rows and 0 <= c < cols:
                        self.known_obstacle[r, c] = True
        # 在线建图：未知格按可通行处理，已知障碍封闭
        self.free[:] = ~self.known_obstacle

    def _bayes_update(self, pos, psi):
        grid = self.known_obstacle.astype(np.int8)
        heading_deg = np.rad2deg(psi) % 360
        fov = self.sonar.get_fov_cells(pos, heading_deg, grid)
        r0, c0 = pos
        for (r, c) in fov:
            d = np.hypot(r - r0, c - c0)
            p_detect = self.sonar.get_detection_probability(d)
            self.belief[r, c] *= (1.0 - p_detect)
        self.belief[self.known_obstacle] = 0.0
        total = self.belief.sum()
        if total > 1e-12:
            self.belief /= total

    def _pick_target(self, pos):
        p = np.where(self.known_obstacle, 0.0, self.belief)
        max_p = p.max()
        if max_p <= 0:
            return None
        cand = np.argwhere(p >= 0.995 * max_p)
        r0, c0 = pos
        d2 = (cand[:, 0] - r0) ** 2 + (cand[:, 1] - c0) ** 2
        best = cand[int(np.argmin(d2))]
        return (int(best[0]), int(best[1]))

    # ------------------------------------------------------------------ policy
    def select_action(self, obs) -> int:
        pos, psi = self._get_pos_heading(obs)
        cell = (int(pos[0]), int(pos[1]))
        self._update_known_obstacle(obs, cell)
        self._bayes_update(cell, psi)

        if self.random_steps_left > 0:
            self.random_steps_left -= 1
            return int(np.random.randint(0, self.num_actions))

        if self.last_pos is not None and cell == self.last_pos:
            self.stuck_counter += 1
        else:
            self.stuck_counter = 0
        self.last_pos = cell
        if self.stuck_counter >= 4:
            target = self._pick_target(cell)
            if target is not None:
                self.belief[target] *= 0.01
            self.stuck_counter = 0
            self.random_steps_left = 5
            return int(np.random.randint(0, self.num_actions))

        target = self._pick_target(cell)
        if target is None or target == cell:
            return int(np.random.randint(0, self.num_actions))

        a = self.nav.goto(pos, psi, target)
        if a is None:
            return int(np.random.randint(0, self.num_actions))
        return a
