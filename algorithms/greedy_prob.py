"""
UUVSearch - 贪心概率搜索算法（信息驱动基线）

与 Random 和 Lawnmower 不同，此算法使用信息地图（概率图）的输出来驱动搜索：
每步走向当前观测中目标概率最高的可达自由格子。

作用：验证"信息地图驱动搜索"是否比"不使用信息的搜索"更好。
- vs Random:  信息驱动 vs 纯粹随机
- vs Lawnmower: 信息驱动 vs 预知地图的全覆盖（公平性见下）

⚠️ 当前概率更新为简化启发式（×0.5/×2.0），非真贝叶斯。概率图质量直接影响此
算法的表现。升级为真贝叶斯更新后，此算法的表现会自然提升。

支持网格环境（读取 obs["hotspot"]）和连续环境（从概率 patch 提取最大值）。

用法:
  # 网格环境
  python scripts/run_algo.py --algo greedy_prob --episodes 30
  # 连续环境
  python scripts/run_experiment.py --env continuous --algo greedy_prob --episodes 50
"""
import numpy as np
from .base_algo import BaseAlgorithm


class GreedyProbSearch(BaseAlgorithm):
    def __init__(self, config: dict):
        super().__init__(config)
        self.map_obj = config.get("map_obj", None)
        self.action_angles = np.array(config.get("action_angles", [-90, -45, 0, 45, 90]))
        self.num_actions = len(self.action_angles)
        self.resolution = config.get("resolution", 30.0)
        self.map_length = config.get("map_length", 420.0)
        self.stuck_counter = 0
        self.last_pos = None
        self.random_steps_left = 0

    def reset(self):
        self.stuck_counter = 0
        self.last_pos = None
        self.random_steps_left = 0

    def _get_grid_pos(self, obs):
        if isinstance(obs, dict):
            return obs["auv_pos"]
        x_norm = float(obs[-3])
        y_norm = float(obs[-2])
        r = int(y_norm * self.map_length / self.resolution)
        c = int(x_norm * self.map_length / self.resolution)
        return (r, c)

    def select_action(self, obs) -> int:
        if isinstance(obs, dict):
            # 网格环境：走向 hotspot
            target = obs["hotspot"]
            pos = obs["auv_pos"]
            dr = target[0] - pos[0]
            dc = target[1] - pos[1]
            action_map = {
                (-1, 0): 0, (1, 0): 1, (0, -1): 2, (0, 1): 3,
                (-1, -1): 4, (-1, 1): 5, (1, -1): 6, (1, 1): 7
            }
            return action_map.get((np.sign(dr), np.sign(dc)), 3)
        else:
            # 连续环境：走向最高概率格子 + 脱困
            pos = self._get_grid_pos(obs)

            # 卡住检测 + 随机脱困
            if self.random_steps_left > 0:
                self.random_steps_left -= 1
                return np.random.randint(0, self.num_actions)
            if self.last_pos is not None and pos == self.last_pos:
                self.stuck_counter += 1
            else:
                self.stuck_counter = 0
            self.last_pos = pos
            if self.stuck_counter >= 4:
                self.random_steps_left = 5
                self.stuck_counter = 0
                return np.random.randint(0, self.num_actions)

            x_norm = float(obs[-3])
            y_norm = float(obs[-2])
            psi = float(obs[-1]) * 2 * np.pi - np.pi
            cur_x = x_norm * self.map_length
            cur_y = y_norm * self.map_length

            # 从概率 patch 找最高点
            patch_side = int(np.sqrt((len(obs) - 3) / 3))
            prob_start = 2 * patch_side * patch_side
            prob_patch = obs[prob_start:prob_start + patch_side * patch_side].reshape(patch_side, patch_side)

            # 按概率降序排序，选第一个可达的自由格子
            flat_indices = np.argsort(prob_patch.flatten())[::-1]
            r, c = pos
            for idx in flat_indices:
                dr = idx // patch_side - patch_side // 2
                dc = idx % patch_side - patch_side // 2
                target_r = r + dr
                target_c = c + dc
                if (0 <= target_r < self.map_obj.size and 0 <= target_c < self.map_obj.size
                        and self.map_obj.is_free(target_r, target_c)):
                    break  # 找到可达自由格子

            target_x = (target_c + 0.5) * self.resolution
            target_y = (target_r + 0.5) * self.resolution
            desired_psi = np.arctan2(target_y - cur_y, target_x - cur_x)
            dpsi = desired_psi - psi
            dpsi = (dpsi + np.pi) % (2 * np.pi) - np.pi
            return int(np.argmin(np.abs(self.action_angles - np.rad2deg(dpsi))))
