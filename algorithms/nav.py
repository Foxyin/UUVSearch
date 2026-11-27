"""
UUVSearch - 栅格寻路与航向跟随

A*（8 邻接，禁止切角）+ 纯追踪（pure pursuit）航向控制。
传统基线共用：把"去哪"和"怎么开过去"解耦，避免用最朴素的
"朝目标格直冲"导航把基线人为削弱。

坐标约定与 envs/auv_model.py 一致：x→col，y→row，psi=0 指向 +col。
"""
import heapq

import numpy as np

_NEI = (
    (-1, 0, 1.0), (1, 0, 1.0), (0, -1, 1.0), (0, 1, 1.0),
    (-1, -1, 1.41421356), (-1, 1, 1.41421356),
    (1, -1, 1.41421356), (1, 1, 1.41421356),
)


def _octile(a, b):
    dr = abs(a[0] - b[0])
    dc = abs(a[1] - b[1])
    return max(dr, dc) + 0.41421356 * min(dr, dc)


def _cheb(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


def astar(free, start, goal):
    """free: bool ndarray(True=可通行)。返回格子列表（含起终点），不可达返回 None。"""
    rows, cols = free.shape
    start = (int(start[0]), int(start[1]))
    goal = (int(goal[0]), int(goal[1]))
    if not (0 <= start[0] < rows and 0 <= start[1] < cols and free[start]):
        return None
    if not (0 <= goal[0] < rows and 0 <= goal[1] < cols and free[goal]):
        return None
    if start == goal:
        return [start]

    g = {start: 0.0}
    parent = {start: None}
    heap = [(_octile(start, goal), 0.0, start)]
    closed = set()
    while heap:
        _, gc, cur = heapq.heappop(heap)
        if cur in closed:
            continue
        closed.add(cur)
        if cur == goal:
            break
        r, c = cur
        for dr, dc, cost in _NEI:
            nr, nc = r + dr, c + dc
            if not (0 <= nr < rows and 0 <= nc < cols) or not free[nr, nc]:
                continue
            if dr != 0 and dc != 0:
                if not (free[r + dr, c] and free[r, c + dc]):
                    continue
            ng = gc + cost
            if ng < g.get((nr, nc), 1e18):
                g[(nr, nc)] = ng
                parent[(nr, nc)] = cur
                heapq.heappush(heap, (ng + _octile((nr, nc), goal), ng, (nr, nc)))
    if goal not in parent:
        return None
    path = []
    cur = goal
    while cur is not None:
        path.append(cur)
        cur = parent[cur]
    path.reverse()
    return path


class AStarNavigator:
    """带重规划的 A* + 纯追踪导航器。free 掩码可原地更新（在线建图时用）。"""

    def __init__(self, free, action_angles=(-90, -45, 0, 45, 90), lookahead=2, clearance=1):
        self.free = free
        self.angles = np.asarray(action_angles, dtype=float)
        self.lookahead = int(lookahead)
        self.clearance = int(clearance)
        self.goal = None
        self.path = None
        self.idx = 0
        self.origin = None

    def reset(self):
        self.goal = None
        self.path = None
        self.idx = 0
        self.origin = None

    def _plan_mask(self):
        """带安全间隙的可通行掩码：离障碍物 < clearance 的格子不用于规划，
        避免路径贴着墙角走、一步航向误差就撞墙。"""
        if self.clearance <= 0:
            return self.free
        rows, cols = self.free.shape
        m = self.free.copy()
        obs = np.argwhere(~self.free)
        for (r, c) in obs:
            r0, r1 = max(0, r - self.clearance), min(rows, r + self.clearance + 1)
            c0, c1 = max(0, c - self.clearance), min(cols, c + self.clearance + 1)
            m[r0:r1, c0:c1] = False
        return m

    def _replan(self, pos, goal):
        self.goal = goal
        mask = self._plan_mask()
        # 起终点必须是通行的；否则退回无间隙掩码
        mask[pos] = True
        if 0 <= goal[0] < mask.shape[0] and 0 <= goal[1] < mask.shape[1]:
            mask[goal] = True
        self.path = astar(mask, pos, goal)
        if self.path is None and self.clearance > 0:
            self.path = astar(self.free, pos, goal)
        self.idx = 0

    def _step_f(self, pf, psi):
        """连续位姿前进一步（单位：格），返回 (row_f, col_f)。"""
        return (pf[0] + float(np.sin(psi)), pf[1] + float(np.cos(psi)))

    def _cell(self, pf):
        return (int(pf[0]), int(pf[1]))

    def _passable(self, p):
        rows, cols = self.free.shape
        r, c = p
        return 0 <= r < rows and 0 <= c < cols and bool(self.free[r, c])

    def _move_ok(self, p_from, p_to):
        """复刻 env.step 的碰撞判定：目标格通行；对角移动还要两个侧邻格通行。"""
        rows, cols = self.free.shape
        r, c = p_to
        if not (0 <= r < rows and 0 <= c < cols and self.free[r, c]):
            return False
        r0, c0 = p_from
        if abs(r - r0) == 1 and abs(c - c0) == 1:
            if not (0 <= r0 < rows and 0 <= c0 < cols):
                return False
            if not self.free[r0, c] or not self.free[r, c0]:
                return False
        return True

    def goto(self, pos, psi, goal):
        """返回动作编号；不可达时返回 None。

        pos 为连续格坐标 (row_f, col_f)（如 (8.5, 11.5)），与 env 的
        `int(y/res)` 取格方式一致。运动学是一步滞后：本步位移由当前航向
        决定，动作只改变下一步航向；所以这里从本步落点 p1 出发做 A*、
        以 p1 为参考点算期望航向，并在"下一步落点可通行"的动作里挑。
        """
        goal = (int(goal[0]), int(goal[1]))
        p0 = self._cell(pos)
        p1f = self._step_f(pos, psi)
        p1 = self._cell(p1f)
        if not self._move_ok(p0, p1):  # 本步已撞墙（不可避免），按当前格规划
            p1 = p0
            p1f = pos

        if goal != self.goal or self.path is None or self.origin != p1:
            self.origin = p1
            self._replan(p1, goal)
            if self.path is None:
                return None

        while self.idx < len(self.path) - 1 and _cheb(p1, self.path[self.idx]) <= 1:
            self.idx += 1

        j = min(self.idx + self.lookahead, len(self.path) - 1)
        tgt = self.path[j]
        desired = np.arctan2(tgt[0] - p1f[0], tgt[1] - p1f[1])
        dpsi = (desired - psi + np.pi) % (2 * np.pi) - np.pi
        order = np.argsort(np.abs(self.angles - np.rad2deg(dpsi)))

        # 先在"两步都不撞"的动作里挑，再退到"一步不撞"，都不行给最接近的
        fallback = None
        for a in order:
            a1 = psi + np.deg2rad(self.angles[a])
            p2f = self._step_f(p1f, a1)
            p2 = self._cell(p2f)
            if not self._move_ok(p1, p2):
                continue
            if fallback is None:
                fallback = int(a)
            a2 = a1 + np.deg2rad(self.angles[a])
            p3 = self._cell(self._step_f(p2f, a2))
            if self._move_ok(p2, p3):
                return int(a)
        if fallback is not None:
            return fallback
        return int(order[0])
