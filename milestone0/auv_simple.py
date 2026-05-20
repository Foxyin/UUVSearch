"""
UUVSearch - 里程碑0：简单AUV模型
===================================
功能：维护AUV的(x, y)坐标，支持4方向移动，遇到边界或障碍物回弹。

类：
    AUV：简单水下无人潜航器模型

用法：
    from auv_simple import AUV
    auv = AUV((5, 5))
    auv.step(0, world)  # 向上移动
"""
import numpy as np


class AUV:
    """简单的AUV模型，只在四个方向上移动"""

    def __init__(self, start_pos):
        """
        初始化AUV

        Args:
            start_pos: tuple (x, y)，AUV的初始坐标
        """
        self.x, self.y = start_pos
        # 动作映射：0=上, 1=下, 2=左, 3=右
        self.actions = {
            0: (-1, 0),   # 上：行减1
            1: (1, 0),    # 下：行加1
            2: (0, -1),   # 左：列减1
            3: (0, 1)     # 右：列加1
        }

    def step(self, action, world):
        """
        执行动作，如果碰到边界或障碍物则原地不动

        Args:
            action: int，0-3之间的动作索引
            world: World对象，用于碰撞检测

        Returns:
            tuple (new_x, new_y, moved):
                new_x: int，新位置的x坐标
                new_y: int，新位置的y坐标
                moved: bool，是否成功移动
        """
        if action not in self.actions:
            return self.x, self.y, False

        dx, dy = self.actions[action]
        new_x = self.x + dx
        new_y = self.y + dy

        if world.is_free(new_x, new_y):
            self.x, self.y = new_x, new_y
            return self.x, self.y, True
        else:
            return self.x, self.y, False

    def get_pos(self):
        """
        获取AUV当前位置

        Returns:
            tuple (x, y)
        """
        return self.x, self.y


# ============================================================
# 单元测试：验证AUV模块独立运行
# ============================================================
if __name__ == "__main__":
    from world_simple import World

    print("=== AUV 模块单元测试 ===")

    # 创建世界和AUV
    w = World(size=5)
    # 手动设置简单地图用于测试（必须是numpy数组）
    test_grid = np.array([
        [0, 0, 0, 0, 0],
        [0, 1, 0, 0, 0],
        [0, 0, 0, 1, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0]
    ], dtype=np.int8)
    w.grid = test_grid.copy()
    w.grid[4][4] = 2  # 目标放在右下角

    a = AUV((0, 0))
    print(f"初始位置: {a.get_pos()}")

    # 测试移动
    for i in range(3):
        a.step(3, w)  # 向右移动
        print(f"向右移动后: {a.get_pos()}")

    # 测试碰撞（向上会碰到障碍物）
    a = AUV((1, 0))
    _, _, moved = a.step(0, w)
    print(f"尝试向上移动（应碰到障碍物）: {a.get_pos()}, moved={moved}")

    # 测试边界（在左边界向左）
    a = AUV((0, 0))
    _, _, moved = a.step(2, w)
    print(f"尝试向左移动（应碰到边界）: {a.get_pos()}, moved={moved}")

    print("=== 测试完成 ===")