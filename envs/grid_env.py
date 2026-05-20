"""
UUVSearch - 网格搜索环境（里程碑3：集成声纳模型 + 修复地图重置）
"""
import numpy as np
from .info_map import InfoMap
from .sonar_model import SonarModel


class GridEnv:
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

    def __init__(self, map_obj, config: dict):
        self.map = map_obj
        self.cfg = config
        self.info_map = InfoMap(map_obj, config.get("info_map", {}))
        self.sonar = SonarModel(config.get("sonar", {}))
        self.max_steps = config.get("simulation", {}).get("max_steps", 500)

        # 保存初始网格状态（仅障碍物布局），用于 reset 恢复
        self.initial_grid = self.map.grid.copy()

        self.np_random = np.random.RandomState()

        self.auv_pos = None
        self.target_pos = None
        self.step_count = 0
        self.found = False
        self.last_action = 3

    def reset(self):
        # 恢复地图到初始状态（清除标记的已访问和目标）
        self.map.grid = self.initial_grid.copy()

        # 重置信息图
        self.info_map = InfoMap(self.map, self.cfg.get("info_map", {}))

        # 随机放置目标
        free_cells = self.map.get_free_cells()
        if not free_cells:
            raise RuntimeError("地图无自由格子")
        target_idx = self.np_random.choice(len(free_cells))
        self.target_pos = free_cells[target_idx]
        self.map.set_target(*self.target_pos)

        # 随机放置AUV（不与目标重合）
        while True:
            start_idx = self.np_random.choice(len(free_cells))
            start_pos = free_cells[start_idx]
            if start_pos != self.target_pos:
                break
        self.auv_pos = start_pos

        self.step_count = 0
        self.found = False
        self.last_action = 3

        return self._get_obs()

    def _get_obs(self):
        r, c = self.auv_pos
        stats = self.info_map.get_stats()
        return {
            "auv_pos": (r, c),
            "target_found": self.found,
            "step": self.step_count,
            "coverage": stats["coverage_ratio"],
            "max_prob": stats["max_probability"],
            "hotspot": stats["prob_hotspot"]
        }

    def step(self, action: int):
        if self.found:
            return self._get_obs(), 0.0, True, {"msg": "already found"}

        self.last_action = action

        dr, dc = self.ACTIONS[action]
        new_r = self.auv_pos[0] + dr
        new_c = self.auv_pos[1] + dc
        if self.map.is_free(new_r, new_c):
            self.auv_pos = (new_r, new_c)

        heading = self.ACTION_HEADING.get(action, 0)
        fov_cells = self.sonar.get_fov_cells(self.auv_pos, heading, self.map.grid)
        target_detected = self.target_pos in fov_cells

        # 记录更新前的覆盖图，用于计算新增覆盖
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
        done = self.found or (self.step_count >= self.max_steps)
        return self._get_obs(), reward, done, {"detected": target_detected}