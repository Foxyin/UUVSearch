"""
UUVSearch - Oracle 覆盖搜索（上界基线）

在"完全已知地图"的假设下做区域覆盖（CPP）：
  * 犁式（boustrophedon）航线：扫描行间距 = 2*声呐半径（保证圆盘 FOV 无缝覆盖）
  * 行内被障碍物打断 → 拆成连续自由段，逐段扫描
  * 段顺序：从当前位姿出发贪心最近邻
  * 导航：A* + 纯追踪（algorithms/nav.AStarNavigator），而非"朝目标格直冲"

这是"覆盖最优搜索"的上界参照：地图信息是作弊的，用于回答
"RL 距离覆盖最优还有多远"，而不是当作可公平比较的对手。
"""
import numpy as np

from algorithms.base_algo import BaseAlgorithm
from algorithms.nav import AStarNavigator, _cheb


def _lane_segments(free, swath):
    """按行切出连续自由段：[(r, c0, c1), ...]

    扫描行从第 1 行开始，间距 swath；若最后一行没被覆盖到，补一条末行航线
    （否则贴边的几行永远扫不到，成功率上不去）。
    """
    rows, cols = free.shape
    lanes = list(range(1, rows, max(1, swath)))
    if rows - 1 - lanes[-1] >= 1:
        lanes.append(rows - 1)
    segs = []
    for r in lanes:
        c = 1
        while c < cols:
            if free[r, c]:
                c0 = c
                while c < cols and free[r, c]:
                    c += 1
                segs.append((r, c0, c - 1))
            else:
                c += 1
    return segs


def _snake_waypoints(segs, start):
    """犁式排序：按行蛇形推进，相邻行反向，减少空驶；两个起始方向取代价小者。

    返回 [(entry, exit), ...] 的航点序列。
    """
    by_row = {}
    for (r, c0, c1) in segs:
        by_row.setdefault(r, []).append((c0, c1))
    rows = sorted(by_row)
    best = None
    for seq in (rows, list(reversed(rows))):
        for first_fwd in (True, False):
            cur = start
            wps = []
            cost = 0.0
            fwd = first_fwd
            for r in seq:
                parts = list(by_row[r])
                # 行内多段：从当前位置贪心最近段，避免横穿整行去够远端
                while parts:
                    pick = None
                    for k, (c0, c1) in enumerate(parts):
                        a, b = (r, c0), (r, c1)
                        d = min(_cheb(cur, a), _cheb(cur, b))
                        if pick is None or d < pick[0]:
                            pick = (d, k)
                    _, k = pick
                    c0, c1 = parts.pop(k)
                    a, b = (r, c0), (r, c1)
                    entry, exit_ = (a, b) if _cheb(cur, a) <= _cheb(cur, b) else (b, a)
                    cost += _cheb(cur, entry)
                    wps.append(entry)
                    if exit_ != entry:
                        wps.append(exit_)
                    cur = exit_
                fwd = not fwd
            if best is None or cost < best[0]:
                best = (cost, wps)
    return best[1]


class OracleCoverageSearch(BaseAlgorithm):
    def __init__(self, config: dict):
        super().__init__(config)
        self.map_obj = config["map_obj"]
        self.free = (self.map_obj.grid != 1).copy()
        self.angles = np.asarray(config.get("action_angles", [-90, -45, 0, 45, 90]), dtype=float)
        sonar = config.get("sonar", {}) or {}
        rng = int(sonar.get("max_range", 3))
        self.swath = max(1, 2 * rng)
        self.nav = AStarNavigator(self.free, self.angles, lookahead=2, clearance=2)
        self.waypoints = None
        self.wi = 0
        self._wi_steps = 0

    def reset(self):
        self.nav.reset()
        self.waypoints = None
        self.wi = 0
        self._wi_steps = 0

    def _plan(self, pos):
        segs = _lane_segments(self.free, self.swath)
        self.waypoints = _snake_waypoints(segs, pos)
        self.wi = 0
        self._wi_steps = 0

    def select_action(self, obs):
        pos = self._pos(obs)
        psi = float(np.arctan2(obs[-2], obs[-1]))
        if self.waypoints is None:
            self._plan(pos)
        n0 = self.wi
        while self.wi < len(self.waypoints) and _cheb(pos, self.waypoints[self.wi]) <= 1:
            self.wi += 1
        if self.wi != n0:
            self._wi_steps = 0
        else:
            self._wi_steps += 1
            if self._wi_steps > 30:  # 够不到就放弃该航点，避免死循环
                self.wi += 1
                self._wi_steps = 0
        if self.wi >= len(self.waypoints):
            return 2
        a = self.nav.goto(pos, psi, self.waypoints[self.wi])
        if a is None:  # 不可达（理论上不会）：跳过该航点
            self.wi += 1
            self._wi_steps = 0
            return 2
        return a

    def _pos(self, obs):
        """连续格坐标 (row_f, col_f)，与 env 的 state=(col+0.5)*res 对应。"""
        length = float(self.config.get("map_length", 420.0))
        res = float(self.config.get("resolution", 30.0))
        return (float(obs[-3]) * length / res, float(obs[-4]) * length / res)

