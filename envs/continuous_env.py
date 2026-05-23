"""
UUVSearch - 连续运动学搜索环境（奖励调优版）
"""
import numpy as np
import gymnasium as gym
from gymnasium import spaces
from .info_map import InfoMap
from .sonar_model import SonarModel
from .auv_model import AUVMotionModel


class ContinuousSearchEnv(gym.Env):
    metadata = {"render_modes": ["human", "rgb_array"]}

    ACTION_ANGLES = np.array([-90, -45, 0, 45, 90])

    def __init__(self, map_obj, config: dict, render_mode=None):
        super().__init__()
        self.map = map_obj
        self.cfg = config
        self.render_mode = render_mode

        auv_cfg = config["auv"]
        self.auv_model = AUVMotionModel(auv_cfg)
        self.sonar = SonarModel(config["sonar"])

        info_cfg = config["info_map"].copy()
        info_cfg["resolution"] = map_obj.resolution
        self.info_map = InfoMap(map_obj, info_cfg)

        self.action_space = spaces.Discrete(len(self.ACTION_ANGLES))
        self.action_angles = self.ACTION_ANGLES

        patch_radius = config.get("obs_patch_radius", 5)
        patch_size = 2 * patch_radius + 1
        # 4 个 patch: coverage + uncertainty + probability + obstacle
        obs_dim = 4 * patch_size * patch_size + 3
        kappa_max = info_cfg.get("kappa_max", 1.0)
        self.observation_space = spaces.Box(low=0, high=max(1.0, kappa_max),
                                            shape=(obs_dim,), dtype=np.float32)
        self.patch_radius = patch_radius

        self.max_steps = config["simulation"]["max_steps"]
        self.reward_weights = config["rewards"]

        self.auv_state = None
        self.target_pos_grid = None
        self.step_count = 0
        self.found = False
        self.initial_grid = self.map.grid.copy()

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)

        self.map.grid = self.initial_grid.copy()
        self.info_map = InfoMap(self.map, self.cfg["info_map"])

        free_cells = self.map.get_free_cells()
        target_idx = self.np_random.choice(len(free_cells))
        self.target_pos_grid = free_cells[target_idx]
        self.map.set_target(*self.target_pos_grid)

        while True:
            start_idx = self.np_random.choice(len(free_cells))
            start_pos_grid = free_cells[start_idx]
            if start_pos_grid != self.target_pos_grid:
                break
        init_x = (start_pos_grid[1] + 0.5) * self.map.resolution
        init_y = (start_pos_grid[0] + 0.5) * self.map.resolution
        init_psi = self.np_random.uniform(-np.pi, np.pi)
        self.auv_state = np.array([init_x, init_y, init_psi])

        self.step_count = 0
        self.found = False

        obs = self._get_observation()
        info = {}
        return obs, info

    def step(self, action):
        if self.found:
            return self._get_observation(), 0.0, True, False, {"msg": "already found"}

        dpsi = self.ACTION_ANGLES[action]
        old_state = self.auv_state.copy()
        self.auv_state = self.auv_model.step(self.auv_state, dpsi)
        x, y, psi = self.auv_state

        terminated = False
        collision = False
        grid_r = int(y / self.map.resolution)
        grid_c = int(x / self.map.resolution)

        if not (0 <= grid_r < self.map.size and 0 <= grid_c < self.map.size):
            collision = True
        elif self.map.grid[grid_r, grid_c] == 1:
            collision = True

        if collision:
            self.auv_state = old_state
            # 随机旋转 90-180° 打破碰撞死循环
            perturb = self.np_random.uniform(np.pi / 2, np.pi)
            perturb *= self.np_random.choice([-1, 1])
            self.auv_state[2] = (self.auv_state[2] + perturb + np.pi) % (2 * np.pi) - np.pi
            reward = self.reward_weights.get("collision_penalty", -2.0)
            self.step_count += 1
            obs = self._get_observation()
            return obs, reward, terminated, self.step_count >= self.max_steps, {"collision": True}

        # psi 与声呐 heading 在 grid 坐标系下天然对齐（y 轴向下）
        heading_deg = np.rad2deg(psi) % 360
        fov_cells = self.sonar.get_fov_cells((grid_r, grid_c), heading_deg, self.map.grid)

        target_detected = self.target_pos_grid in fov_cells

        # 记录更新前的覆盖图
        prev_coverage = self.info_map.coverage.copy()
        self.info_map.update(fov_cells, target_detected)

        if target_detected:
            self.found = True
            reward = self.reward_weights["find_target"]
        else:
            # 区分首次覆盖和重复访问（仅统计 FOV 内格子）
            new_count = 0
            revisit_count = 0
            seen = set()
            for (r, c) in fov_cells:
                if 0 <= r < self.map.size and 0 <= c < self.map.size:
                    if (r, c) in seen:
                        continue
                    seen.add((r, c))
                    if self.map.is_free(r, c):
                        if prev_coverage[r, c] == 0 and self.info_map.coverage[r, c] == 1:
                            new_count += 1
                        elif prev_coverage[r, c] == 1:
                            revisit_count += 1

            reward = (self.reward_weights.get("coverage_gain", 1.0) * new_count +
                      self.reward_weights.get("revisit_gain", 0.1) * revisit_count +
                      self.reward_weights.get("step_penalty", -0.05))

        self.step_count += 1
        terminated = self.found
        truncated = self.step_count >= self.max_steps

        obs = self._get_observation()
        info = {"detected": target_detected}
        return obs, reward, terminated, truncated, info

    def _get_observation(self):
        x, y, psi = self.auv_state

        center_r = int(y / self.map.resolution)
        center_c = int(x / self.map.resolution)

        def extract_patch(matrix, r, c, radius):
            patch = np.zeros((2*radius+1, 2*radius+1), dtype=np.float32)
            rows, cols = matrix.shape
            for dr in range(-radius, radius+1):
                for dc in range(-radius, radius+1):
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < rows and 0 <= nc < cols:
                        patch[dr+radius, dc+radius] = matrix[nr, nc]
            return patch

        cov_patch = extract_patch(self.info_map.coverage, center_r, center_c, self.patch_radius)
        unc_patch = extract_patch(self.info_map.uncertainty, center_r, center_c, self.patch_radius)
        prob_patch = extract_patch(self.info_map.probability, center_r, center_c, self.patch_radius)
        # 障碍物通道：agent 直接看到附近的地形
        obs_patch = (extract_patch(self.map.grid, center_r, center_c, self.patch_radius) == 1).astype(np.float32)

        x_norm = x / self.map.length
        y_norm = y / self.map.length
        psi_norm = (psi + np.pi) / (2 * np.pi)

        obs = np.concatenate([
            cov_patch.flatten(),
            unc_patch.flatten(),
            prob_patch.flatten(),
            obs_patch.flatten(),
            [x_norm, y_norm, psi_norm]
        ]).astype(np.float32)
        return obs

    def render(self):
        pass