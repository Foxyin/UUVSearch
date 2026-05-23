"""
UUVSearch - 网格搜索环境（Gymnasium 接口）
"""
import numpy as np
import gymnasium as gym
from gymnasium import spaces
from .info_map import InfoMap
from .sonar_model import SonarModel


class GridEnv(gym.Env):
    metadata = {"render_modes": ["human"]}

    ACTIONS = {
        0: (-1, 0),    # 上
        1: (1, 0),     # 下
        2: (0, -1),    # 左
        3: (0, 1),     # 右
        4: (-1, -1),   # 左上
        5: (-1, 1),    # 右上
        6: (1, -1),    # 左下
        7: (1, 1)      # 右下
    }

    ACTION_HEADING = {
        0: 270,  # 上
        1: 90,   # 下
        2: 180,  # 左
        3: 0,    # 右
        4: 225,  # 左上
        5: 315,  # 右上
        6: 135,  # 左下
        7: 45    # 右下
    }

    def __init__(self, map_obj, config: dict, render_mode=None):
        super().__init__()
        self.map = map_obj
        self.cfg = config
        self.render_mode = render_mode
        self.info_map = InfoMap(map_obj, config.get("info_map", {}))
        self.sonar = SonarModel(config.get("sonar", {}))
        self.max_steps = config.get("simulation", {}).get("max_steps", 500)

        self.initial_grid = self.map.grid.copy()

        self.action_space = spaces.Discrete(8)
        # Dict 观测（传统算法需要各字段）
        self.observation_space = spaces.Dict({
            "auv_pos": spaces.Tuple((spaces.Discrete(map_obj.size), spaces.Discrete(map_obj.size))),
            "target_found": spaces.Discrete(2),
            "step": spaces.Discrete(self.max_steps + 1),
            "coverage": spaces.Box(0, 1, shape=()),
            "max_prob": spaces.Box(0, 1, shape=()),
            "hotspot": spaces.Tuple((spaces.Discrete(map_obj.size), spaces.Discrete(map_obj.size))),
        })

        self.np_random = np.random.RandomState()

        self.auv_pos = None
        self.target_pos = None
        self.step_count = 0
        self.found = False
        self.last_action = 3

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)

        self.map.grid = self.initial_grid.copy()
        self.info_map = InfoMap(self.map, self.cfg.get("info_map", {}))

        free_cells = self.map.get_free_cells()
        if not free_cells:
            raise RuntimeError("地图无自由格子")
        target_idx = self.np_random.choice(len(free_cells))
        self.target_pos = free_cells[target_idx]
        self.map.set_target(*self.target_pos)

        while True:
            start_idx = self.np_random.choice(len(free_cells))
            start_pos = free_cells[start_idx]
            if start_pos != self.target_pos:
                break
        self.auv_pos = start_pos

        self.step_count = 0
        self.found = False
        self.last_action = 3

        return self._get_obs(), {}

    def _get_obs(self):
        r, c = self.auv_pos
        stats = self.info_map.get_stats()
        return {
            "auv_pos": (r, c),
            "target_found": int(self.found),
            "step": self.step_count,
            "coverage": stats["coverage_ratio"],
            "max_prob": stats["max_probability"],
            "hotspot": stats["prob_hotspot"]
        }

    def step(self, action: int):
        if self.found:
            return self._get_obs(), 0.0, True, False, {"msg": "already found"}

        self.last_action = action

        dr, dc = self.ACTIONS[action]
        new_r = self.auv_pos[0] + dr
        new_c = self.auv_pos[1] + dc
        can_move = self.map.is_free(new_r, new_c)
        # 对角线移动时检查侧邻格，防止穿过障碍物角落
        if can_move and abs(dr) == 1 and abs(dc) == 1:
            if (not self.map.is_free(self.auv_pos[0], new_c) or
                    not self.map.is_free(new_r, self.auv_pos[1])):
                can_move = False
        if can_move:
            self.auv_pos = (new_r, new_c)

        heading = self.ACTION_HEADING.get(action, 0)
        fov_cells = self.sonar.get_fov_cells(self.auv_pos, heading, self.map.grid)
        target_detected = self.target_pos in fov_cells

        prev_coverage = self.info_map.coverage.copy()
        self.info_map.update(fov_cells, target_detected)

        if target_detected:
            self.found = True
            reward = 100.0
        else:
            new_coverage = 0
            for (r, c) in fov_cells:
                if (0 <= r < self.map.size and 0 <= c < self.map.size
                        and prev_coverage[r, c] == 0
                        and self.info_map.coverage[r, c] == 1):
                    new_coverage += 1
            reward = new_coverage * 1.0

        self.step_count += 1
        terminated = self.found
        truncated = self.step_count >= self.max_steps
        return self._get_obs(), reward, terminated, truncated, {"detected": target_detected}

    def render(self):
        pass
