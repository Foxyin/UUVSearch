import numpy as np


class SimpleAUV:
    """
    最简 AUV：只能上下左右移动，没有传感器模型，
    只要走到目标格子上就算"发现"。
    """

    def __init__(self, world, start_pos=(0, 0)):
        self.world = world
        self.x, self.y = start_pos
        self.world.mark_visited(self.x, self.y)
        self.path = [start_pos]  # 记录轨迹

        # 动作定义：0=上, 1=下, 2=左, 3=右
        self.action_map = {
            0: (-1, 0),
            1: (1, 0),
            2: (0, -1),
            3: (0, 1)
        }

    def move(self, action):
        """
        执行动作，返回 (observation, reward, done, info)
        """
        dx, dy = self.action_map[action]
        nx, ny = self.x + dx, self.y + dy

        # 碰撞检测（边界或障碍物）
        if not self.world.is_free(nx, ny):
            reward = -1.0  # 碰撞惩罚
            done = False
            info = {"collision": True, "pos": (self.x, self.y)}
        else:
            # 移动成功
            self.x, self.y = nx, ny
            self.world.mark_visited(self.x, self.y)
            self.path.append((self.x, self.y))

            reward = -0.1  # 每步时间惩罚（鼓励尽快找到）
            done = False
            info = {"collision": False, "pos": (self.x, self.y)}

            # 检查是否发现目标
            if self.world.check_target(self.x, self.y):
                reward = 100.0  # 大额成功奖励
                done = True
                info["found"] = True

        obs = self._get_observation()
        return obs, reward, done, info

    def _get_observation(self):
        """
        最简观测：AUV 周围 3×3 区域的内容（拍平成列表）。
        越界或障碍物 = 1，自由/已访问 = 0。
        """
        obs = []
        for i in range(-1, 2):
            for j in range(-1, 2):
                nx, ny = self.x + i, self.y + j
                if self.world.is_free(nx, ny):
                    obs.append(0)
                else:
                    obs.append(1)
        return obs

    def get_pos(self):
        return (self.x, self.y)