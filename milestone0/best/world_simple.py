import numpy as np
from collections import deque


class GridWorld:
    """
    最简网格世界：20×20，包含障碍物和目标。
    格子状态：0=自由, 1=障碍物, 2=目标, 3=已访问, 4=AUV当前位置（仅显示用）
    """
    FREE = 0
    OBSTACLE = 1
    TARGET = 2
    VISITED = 3
    AUV = 4

    def __init__(self, size=20, obstacle_ratio=0.10):
        self.size = size
        self.grid = np.zeros((size, size), dtype=int)

        # 放置障碍物（避开起点 (0,0)）
        self._place_obstacles(obstacle_ratio)

        # 放置目标（确保可达）
        self._place_target()

        # 记录哪些格子被访问过
        self.visited = np.zeros((size, size), dtype=bool)

    def _place_obstacles(self, ratio):
        """随机放置障碍物，避开起点"""
        num_obstacles = int(self.size * self.size * ratio)
        # 所有可用坐标（排除起点）
        coords = [(i, j) for i in range(self.size) for j in range(self.size) if (i, j) != (0, 0)]
        chosen = np.random.choice(len(coords), size=num_obstacles, replace=False)
        for idx in chosen:
            x, y = coords[idx]
            self.grid[x, y] = self.OBSTACLE

    def _place_target(self):
        """随机放置目标，并确保从起点可达"""
        max_try = 100
        for _ in range(max_try):
            x, y = np.random.randint(0, self.size, size=2)
            if self.grid[x, y] == self.FREE and (x, y) != (0, 0):
                self.grid[x, y] = self.TARGET
                self.target_pos = (x, y)
                if self._is_reachable():
                    return
                else:
                    # 不可达则清除，重试
                    self.grid[x, y] = self.FREE
        # 兜底：如果一直不可达，清空地图中央区域放目标
        self.grid[15, 15] = self.TARGET
        self.target_pos = (15, 15)

    def _is_reachable(self):
        """从起点 (0,0) BFS 检查目标是否可达"""
        q = deque([(0, 0)])
        seen = {(0, 0)}
        while q:
            x, y = q.popleft()
            if (x, y) == self.target_pos:
                return True
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = x + dx, y + dy
                if (0 <= nx < self.size and 0 <= ny < self.size and
                        (nx, ny) not in seen and self.grid[nx, ny] != self.OBSTACLE):
                    seen.add((nx, ny))
                    q.append((nx, ny))
        return False

    def is_free(self, x, y):
        """判断坐标是否在边界内且不是障碍物"""
        return 0 <= x < self.size and 0 <= y < self.size and self.grid[x, y] != self.OBSTACLE

    def check_target(self, x, y):
        """检查是否到达目标"""
        return (x, y) == self.target_pos

    def mark_visited(self, x, y):
        """标记AUV访问过的格子"""
        if 0 <= x < self.size and 0 <= y < self.size:
            self.visited[x, y] = True

    def get_render_grid(self, auv_pos):
        """
        生成用于 matplotlib 显示的网格副本。
        优先级：目标 > AUV > 已访问 > 自由 > 障碍物
        """
        render = self.grid.copy()

        # 已访问的自由格显示为浅蓝色
        for i in range(self.size):
            for j in range(self.size):
                if self.visited[i, j] and render[i, j] == self.FREE:
                    render[i, j] = self.VISITED

        # AUV 位置显示为绿色（如果不在目标上）
        ax, ay = auv_pos
        if render[ax, ay] != self.TARGET:
            render[ax, ay] = self.AUV

        return render