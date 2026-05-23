"""
UUVSearch - 三层信息图
覆盖图 (Coverage) | 不确定图 (Uncertainty) | 目标概率图 (Probability)
"""
import numpy as np


class InfoMap:
    def __init__(self, map_obj, config: dict, sonar=None):
        self.map = map_obj
        self.cfg = config
        self.sonar = sonar  # 声呐模型，用于距离相关贝叶斯更新

        rows, cols = map_obj.grid.shape
        self.shape = (rows, cols)

        self.coverage = np.zeros(self.shape, dtype=np.float32)
        self.kappa_max = config.get("kappa_max", 1.0)
        self.uncertainty = np.full(self.shape, self.kappa_max, dtype=np.float32)

        mask = map_obj.get_mask()
        self.probability = np.zeros(self.shape, dtype=np.float32)
        self.probability[mask] = 1.0 / np.sum(mask)

        self.growth_factor = config.get("growth_factor", 50)
        self.uncertainty_decay = config.get("uncertainty_decay", 1.0)
        self._update_counter = 0

    def update(self, fov_cells, target_detected: bool, auv_pos=None):
        """
        Args:
            fov_cells: FOV 格子列表
            target_detected: 本次是否探测到目标
            auv_pos: (row, col) AUV 位置，用于距离相关贝叶斯（可选）
        """
        self._update_counter += 1

        # 1. 覆盖图
        for (r, c) in fov_cells:
            if 0 <= r < self.shape[0] and 0 <= c < self.shape[1]:
                if self.map.is_free(r, c):
                    self.coverage[r, c] = 1.0
                    self.map.mark_visited(r, c)

        # 2. 不确定图
        for (r, c) in fov_cells:
            if 0 <= r < self.shape[0] and 0 <= c < self.shape[1]:
                if self.map.is_free(r, c):
                    self.uncertainty[r, c] = 0.0
        self.uncertainty = np.minimum(self.kappa_max, self.uncertainty / self.uncertainty_decay)

        # 3. 目标概率更新
        if self.sonar is not None and auv_pos is not None:
            self._bayesian_update(fov_cells, target_detected, auv_pos)
        else:
            self._heuristic_update(fov_cells, target_detected)

    def _bayesian_update(self, fov_cells, target_detected, auv_pos):
        """距离相关的真贝叶斯更新"""
        r0, c0 = auv_pos
        for (r, c) in fov_cells:
            if 0 <= r < self.shape[0] and 0 <= c < self.shape[1]:
                if not self.map.is_free(r, c):
                    continue
                d = np.sqrt((r - r0) ** 2 + (c - c0) ** 2)
                p_detect = self.sonar.get_detection_probability(d)
                if target_detected:
                    self.probability[r, c] *= p_detect
                else:
                    self.probability[r, c] *= (1.0 - p_detect)
        total = np.sum(self.probability)
        if total > 1e-12:
            self.probability /= total
        else:
            mask = self.map.get_mask()
            self.probability[mask] = 1.0 / np.sum(mask)

    def _heuristic_update(self, fov_cells, target_detected):
        """旧版简化启发式（声呐不可用时的回退）"""
        factor = 2.0 if target_detected else 0.5
        for (r, c) in fov_cells:
            if 0 <= r < self.shape[0] and 0 <= c < self.shape[1]:
                self.probability[r, c] *= factor
        total = np.sum(self.probability)
        if total > 1e-12:
            self.probability /= total
        else:
            mask = self.map.get_mask()
            self.probability[mask] = 1.0 / np.sum(mask)

    def get_stats(self) -> dict:
        """返回当前信息图的统计信息，用于调试"""
        return {
            "coverage_ratio": float(np.mean(self.coverage)),
            "mean_uncertainty": float(np.mean(self.uncertainty)),
            "max_probability": float(np.max(self.probability)),
            "prob_hotspot": np.unravel_index(np.argmax(self.probability), self.shape)
        }