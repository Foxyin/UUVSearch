# UUVSearch

单 AUV 自主目标搜索的强化学习仿真基准：AUV 搭载有限探测距离的声呐，在未知障碍物环境中通过连续运动学和信息地图搜索静止目标。

> **当前阶段（2026-11-28）**：项目正在从“跑通 demo”转为“可投稿的经验研究”。旧的性能结论已于 2026-11-27 审计后撤回（见下文「历史结论撤回」），当前主线是计划 **v3.2** 的 Phase 0 → Gate 1/2/3，**Phase 0 尚未开工、没有新实验数据**。实时状态看 [`docs/STATUS.md`](docs/STATUS.md)；读代码前先读 [`docs/02-plan/plan-2026-11-28.md`](docs/02-plan/plan-2026-11-28.md)。

## 这个项目要回答什么

**RQ**：在检测退化（检测概率 Pd 下降、虚警 Pfa 上升）与能量约束下，学习型搜索（DQN/SAC）何时优于、何时不优于经典搜索（lawnmower / greedy-prob / info-gain）？

- 定位：**search-only**（只找，不做确认/三态），一篇独立的经验研究论文，不是任何其他课题的底座。
- 形态：**边界条件 / 失效条件**研究。如果最终经典覆盖仍最好，就写 negative result / benchmark，不硬拗“RL 更优”。
- 时间盒：3 周可行性 Gate + 4–6 周论文；Gate 不过就停，不自动延期。

详细依据见 [`docs/00-handoff/`](docs/00-handoff/)（前任交接）与 [`docs/01-review/2026-11-27-audit.md`](docs/01-review/2026-11-27-audit.md)（首次审计）。

## 目录导航

```
UUVSearch/
├── README.md              ← 本文件：入口、现状、工作流程
├── CLAUDE.md              ← 给 AI/协作者的工程备忘录（环境、命令、约束）
├── docs/
│   ├── README.md          ← 文档索引（按用途分目录）
│   ├── STATUS.md          ← 唯一事实源：当前状态 / 下一步 / 未决问题
│   ├── 00-handoff/        ← 只读交接文档
│   ├── 01-review/         ← 问题清单 + 审计记录
│   ├── 02-plan/           ← 活的实验计划（带版本号与变更日志）
│   ├── 03-decisions/      ← 用户拍板的决策
│   └── 04-maps/           ← 地图 PNG/ASCII 导出（Phase 0 生成）
├── 协作/                  ← 四角色协作（owner / reviewer / experimenter / writer）
│   ├── 协作规则.md        ← 单写者、分诊、模式、评审效力、Gate 流转
│   ├── 角色注册表.md      ← 角色 ID / 状态 / 接任
│   ├── 启动提示词.md      ← 四个角色的复制粘贴提示词
│   └── 角色/ 评审/ 讨论/ 提案/ 交接/
├── envs/                  ← 仿真环境
│   ├── continuous_env.py  ← 主环境（488 维观测，连续运动学）
│   ├── auv_model.py       ← 一阶运动学（1 格/步，5 航向）
│   ├── sonar_model.py     ← 圆形/扇形 FOV + Bresenham 遮挡
│   ├── info_map.py        ← 三层信息地图（覆盖/不确定度/概率）
│   └── maps/              ← 地图工厂（Square / Irregular）
├── algorithms/            ← 搜索算法（random / lawnmower / greedy_prob / dqn / sac）
├── trainers/              ← DQNTrainer / SACTrainer / Evaluator
├── scripts/               ← 命令行入口（train_* / evaluate / run_experiment / render_episode）
├── config/                ← YAML（algo + env）
├── experiments/           ← 输出（gitignored：checkpoints / logs / figures）
└── results/               ← 新协议的结构化结果（gitignored，Phase 0 起）
```

## 工作流程

```
Phase 0（1–1.5 天，不训练）
  地图工厂参数化 M1–M5 · 检测层(Pd/Pfa) · odds-Bayes · 能量 · info_gain 基线
  scripts/run_suite.py 统一评估 + make_tables.py 出表
        ↓
Gate 1（W1，不训练）6 个经典方法（含无全图的 online_lawnmower）× 5 图 × 5 seeds
  通过 = 排名稳定 + 覆盖基线接近每图的 oracle 下界；不通过先修协议
        ↓
Gate 2（W2）48-run 小网格训练（检测退化 × 能量 × 信念观测/覆盖观测）
  通过 = 至少一个变量显著改变方法排名；否则换 RQ 或停
        ↓
Gate 3（W3）边界热图 + 失败案例 → 4–6 页短稿 / 技术报告
```

每个 Gate 的通过标准、实验矩阵、指标定义见计划 v3.2 的 §5–§7。

## 环境与运行

**解释器**（默认 `python` 没有装 gymnasium，必须用这个）：

```
D:\Anaconda\envs\UUVSearch\python.exe     # Python 3.8.20, torch 2.4.1+cpu, gymnasium 1.1.1
```

- 所有脚本从**项目根目录**运行；脚本内部会把仓库根加入 `sys.path`。
- 本机 torch 是 CPU 版；实验网格靠多进程并行（`OMP_NUM_THREADS=1`，8–10 进程），不装 CUDA（理由见 `docs/03-decisions/`）。

```powershell
cd C:\Users\17053\Desktop\UUVSearch

# 传统算法（连续环境）
D:\Anaconda\envs\UUVSearch\python.exe scripts\run_experiment.py --env continuous --algo lawnmower --episodes 20 --seed 0

# 训练（示例，旧协议）
D:\Anaconda\envs\UUVSearch\python.exe scripts\train_dqn.py --exp-name dqn_v6 --total-steps 400000

# 评估
D:\Anaconda\envs\UUVSearch\python.exe scripts\evaluate.py --algo dqn --checkpoint experiments\checkpoints\dqn_v6\best.pt --episodes 100 --seed 0

# TensorBoard
tensorboard --logdir experiments/logs/
```

> Phase 0 完成后统一入口改为 `scripts/run_suite.py --suite gate1 --config config/suites/gate1.yaml`。

## 仿真环境核心设定

| 项 | 值 |
|---|---|
| 地图 | 14×14，420 m × 420 m，分辨率 30 m/格，障碍率 10%（种子 42 固定图） |
| 声呐 | 圆形 FOV，半径 3 格（90 m），Bresenham 视线遮挡 |
| 运动学 | 1 m/s × 30 s/步 = 1 格/步；动作 = 航向变化 {−90,−45,0,+45,+90}° |
| 观测 | 4 个 11×11 patch（覆盖/不确定度/概率/障碍）+ 4 维状态 = **488 维** |
| 奖励 | 新覆盖 +1.0/格，重访 0，找到目标 +100，碰撞 −2，每步 −0.05 |
| 回合 | 找到目标即终止；否则到能量预算（`1.5× / 2.5× / 4× free_cells`）或无发现上限 |

已知的模型问题（检测确定性、信念更新与环境不一致、uncertainty 通道冗余、障碍 patch 是特权信息等）见 [`docs/01-review/2026-11-28-issues-checklist.md`](docs/01-review/2026-11-28-issues-checklist.md)，修复方案见计划 §2。

## 算法清单

| 算法 | 类型 | 说明 |
|---|---|---|
| Random | 基线 | 均匀随机，下界 |
| Lawnmower | 经典 | 梳形全覆盖，需完整地图（**oracle**）；swath = 2×声呐半径 + A* 导航 |
| OnlineLawnmower | 经典 | 只用已知自由格的在线梳形覆盖，A* 重规划；**公平的强覆盖基线（Phase 0 新增）** |
| GreedyProb | 经典 | 局部 11×11 概率贪心，使用真值可通行掩码（特权） |
| InfoGain | 经典 | 熵减贪心，**Phase 0 新增** |
| BayesMyopic | 经典 | 自维护 odds 后验，取最大后验格，A* 导航 |
| DQN | RL | Double DQN + target net + ε 线性衰减 |
| SAC | RL | 离散 SAC + 自动熵（target_entropy_scale=0.2） |

## 历史结论撤回（2026-11-27）

以下旧结论**不再作为证据使用**，仅作历史记录：

| 旧说法 | 审计后的事实 |
|---|---|
| “DQN 95% / SAC 94% 接近 Lawnmower 100%，RL 逼近覆盖上界” | Lawnmower 的 swath 硬编码为 2（未匹配声呐半径 3），waypoint 每格一个、导航用最近航向（动作还有 1 步滞后），所以经典基线被人为削弱；换成 A* + 匹配 swath 后差距大幅缩小 |
| “真贝叶斯更新” | 环境检测是确定性的（进 FOV 即发现），信念却按 `p_detect=1-0.3d/R` 更新，模型与数据生成过程不一致 |
| “信息地图有价值” | 目标先验均匀 + 静止 ⇒ 最优策略就是纯覆盖，概率通道在当前设定下几乎不起作用 |
| “成功率 95%” | 随机策略也有 87%，成功率已饱和；有区分度的是 **time-to-find**（KM 中位 + 删失率） |

审计细节与 7 算法实测表：`docs/01-review/2026-11-27-audit.md`。

## 角色协作（四角色）

项目用 [`multi-role-collab`](.dsh/skills/multi-role-collab/SKILL.md) 的纪律，把工作拆成四个**角色**（不是四个模型，是四顶帽子；同一模型可换帽子，但一个会话只戴一顶）：

| 角色 | 负责 | 不负责 | 允许的技能 |
|---|---|---|---|
| `owner`（总讨论/PM） | 事实源 `docs/STATUS.md`、计划、决策、分派、拍板、对用户汇报 | 不写实验代码、不自我审查、不写论文正文 | multi-role-collab、experiment-design、karpathy-guidelines |
| `reviewer`（审查） | 独立审一个**指定对象**（计划/代码/结果表/论文 claim），给证据 + 必改项 | 不改对象、不跑实验、不做项目决定 | paper-reviewer、experiment-design（对照）、karpathy-guidelines |
| `experimenter`（实验） | 在 `feat/gate1-protocol` 实现协议、跑指定矩阵、落 `results/<tag>/` | 不改计划、不解释结论、不自行扩矩阵、不合 main | karpathy-guidelines、experiment-design（只读矩阵/预算） |
| `writer`（论文写作，Gate 3 后启用） | 写稿、制图、排版，只用 `results/` 与 `make_tables.py` | 不改数据、不改代码、不定刊物 | research-paper-writing、latex-academic-publisher、academic-plotting、topconf-figure、paper-reviewer |

规则与启动提示词见 [`协作/协作规则.md`](协作/协作规则.md) 与 [`协作/启动提示词.md`](协作/启动提示词.md)。核心三条：**角色文档不是事实源**；**一个文件一个写者，不是自己的文件写提案**；**不自我审查**。

## 扩展指南

- **新地图**：继承 `envs/maps/base_map.py:BaseMap`，实现 `get_mask()`，在 `envs/maps/__init__.py` 注册，再加 YAML。
- **新经典算法**：继承 `algorithms/base_algo.py:BaseAlgorithm`，实现 `select_action(obs)` / `reset()`，在 `algorithms/__init__.py` 注册。
- **新 RL 算法**：实现 `select_action / store_transition / update / save / load`，配 `trainers/` 与 `scripts/` 入口。
- **声呐参数**：`config/env/*.yaml` 的 `sonar.max_range` / `sector_angle`。

## 依赖

Python 3.8+（当前环境 3.8.20），PyTorch 2.4，Gymnasium 1.1；完整列表见 `requirements.txt`。
