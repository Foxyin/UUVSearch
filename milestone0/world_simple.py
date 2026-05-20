import numpy as np

class World:
    """
    20x20 栅格世界
    0 = 自由
    1 = 障碍物
    2 = 目标
    3 = 已访问（探测过）
    """
    def __init__(self, size=20):
        self.size = size
        self.grid = np.zeros((size, size), dtype=np.int8)
        self._place_obstacles()
        self._place_target()

    def _place_obstacles(self):
        # 随机放一些障碍物（约10%的格子）
        np.random.seed(42)
        for _ in range(int(self.size * self.size * 0.1)):
            x, y = np.random.randint(0, self.size, 2)
            self.grid[x, y] = 1

    def _place_target(self):
        # 在自由格子上随机放目标
        free_cells = np.argwhere(self.grid == 0)
        if len(free_cells) == 0:
            raise ValueError("没有自由格子放置目标")
        idx = np.random.randint(0, len(free_cells))
        self.target_pos = tuple(free_cells[idx])
        self.grid[self.target_pos] = 2

    def is_free(self, x, y):
        if 0 <= x < self.size and 0 <= y < self.size:
            return self.grid[x, y] != 1
        return False

    def mark_visited(self, x, y):
        # 如果是自由格子或目标格子，标记为已访问
        if 0 <= x < self.size and 0 <= y < self.size:
            if self.grid[x, y] == 0:
                self.grid[x, y] = 3
            # 目标格子不覆盖，保持为2