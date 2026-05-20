"""
UUVSearch - AUV 一阶运动学模型
恒定巡航速度，动作控制航向变化量。
"""
import numpy as np


class AUVMotionModel:
    def __init__(self, config: dict):
        self.v = config["cruise_speed"]  # m/s
        self.dt = config["time_step"]  # s
        self.max_dpsi = np.deg2rad(config.get("max_heading_change", 90))  # 弧度

    def step(self, state, action_dpsi_deg):
        """
        更新AUV状态

        Args:
            state: [x, y, psi]  位置（米）和航向（弧度）
            action_dpsi_deg: 航向变化量（度）

        Returns:
            new_state: [x, y, psi] 新状态
        """
        x, y, psi = state
        dpsi = np.deg2rad(action_dpsi_deg)
        dpsi = np.clip(dpsi, -self.max_dpsi, self.max_dpsi)

        # 以当前航向计算位移（航向变化发生在步末）
        dx = self.v * np.cos(psi) * self.dt
        dy = self.v * np.sin(psi) * self.dt

        psi_new = psi + dpsi
        psi_new = (psi_new + np.pi) % (2 * np.pi) - np.pi
        return np.array([x + dx, y + dy, psi_new])