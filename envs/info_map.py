"""
UUVSearch - 三层信息图
覆盖图 (Coverage) | 不确定图 (Uncertainty) | 目标概率图 (Probability)
"""
import numpy as np


class InfoMap:
    def __init__(self, map_obj, config: dict):
        self.map = map_obj
        self.cfg = config

        rows, cols = map_obj.grid.shape
        self.shape = (rows, cols)

        # 覆盖图：0=未覆盖，1=已覆盖
        self.coverage = np.zeros(self.shape, dtype=np.float32)

        # 不确定图：初始为最大值
        self.kappa_max = config.get("kappa_max", 1.0)
        self.uncertainty = np.full(self.shape, self.kappa_max, dtype=np.float32)

        # 目标概率图：初始均匀分布（只分布在自由格子上）
        mask = map_obj.get_mask()
        self.probability = np.zeros(self.shape, dtype=np.float32)
        self.probability[mask] = 1.0 / np.sum(mask)

        self.growth_factor = config.get("growth_factor", 50)
        self._update_counter = 0

    def update(self, fov_cells, target_detected: bool):
        """
        根据声纳探测结果更新三张图

        Args:
            fov_cells: list of (row, col) 当前探测到的网格坐标
            target_detected: bool 本次探测是否发现目标
        """
        self._update_counter += 1

        # 1. 更新覆盖图：FOV内所有自由格子标记为已覆盖
        for (r, c) in fov_cells:
            if 0 <= r < self.shape[0] and 0 <= c < self.shape[1]:
                if self.map.is_free(r, c):  # 障碍物不标记
                    self.coverage[r, c] = 1.0
                    self.uncertainty[r, c] = 0.0
                    self.map.mark_visited(r, c)  # 同步更新地图的已访问标记

        # 2. 更新不确定图（简化版：仅被探测过的归零，其他保持不变）
        #    论文中有随时间增长逻辑，这里暂时不做增长，保持简单。

        # 3. 贝叶斯更新目标概率（极度简化）
        #    如果探测到目标：FOV内格子概率倍增，FOV外略降
        #    如果未探测到：FOV内格子概率减半，FOV外略增
        if target_detected:
            # 探测到目标：FOV内概率大幅提高
            for (r, c) in fov_cells:
                if 0 <= r < self.shape[0] and 0 <= c < self.shape[1]:
                    self.probability[r, c] *= 2.0
            # 全局重新归一化
            total = np.sum(self.probability)
            if total > 0:
                self.probability /= total
        else:
            # 未探测到目标：FOV内概率降低
            for (r, c) in fov_cells:
                if 0 <= r < self.shape[0] and 0 <= c < self.shape[1]:
                    self.probability[r, c] *= 0.5
            # 重新归一化（注意不能把概率全置零）
            total = np.sum(self.probability)
            if total > 1e-12:
                self.probability /= total
            else:
                # 如果概率全部接近0，重置为均匀分布（安全措施）
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