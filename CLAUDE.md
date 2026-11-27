# CLAUDE.md — 工程备忘录

给 AI 协作者/新人的项目事实与操作纪律。**先读 [`README.md`](README.md) 了解项目定位，再读 [`docs/02-plan/`](docs/02-plan/) 了解当前计划。**

## 项目是什么

UUVSearch：单 AUV 自主目标搜索的 RL 仿真基准。AUV 在未知障碍环境中用有限探测距离的声呐搜索静止目标，动作是 5 档航向变化，观测是 4 个局部 patch + 自身状态。

**当前定位**（2026-11-28 起）：search-only 经验研究，回答“检测退化 + 能量约束下，RL 何时优于经典搜索”。目标是一篇独立论文（3 周 Gate + 4–6 周写作）。**不是**其他课题的 confirm/三态底座，**不是** Li et al. 2024 的复现。

## 运行环境（重要）

- 默认 `python`（`D:\Anaconda\python.exe`）**没有 gymnasium**。必须用：
  `D:\Anaconda\envs\UUVSearch\python.exe`（Python 3.8.20，torch 2.4.1+**cpu**，gymnasium 1.1.1，numpy 1.24.4）
- 所有脚本从仓库根目录运行；脚本内部会 `sys.path.insert(0, <repo>)`。
- 本机有 RTX 4060 Laptop，但该环境 torch 是 CPU 版。实验网格用**多进程 CPU 并行**（`OMP_NUM_THREADS=1`、`MKL_NUM_THREADS=1`，8–10 进程），不要为此新建 conda 环境（理由见 `docs/03-decisions/`）。
- 速度参考：DQN 单进程 ≈97 步/s；200k 步/run ≈35 min；8 进程并行。
- 控制台是 GBK：**不要**用 `Get-Content | Set-Content` 处理含中文的源码（会乱码），改文件一律用编辑工具的 write/edit。

## 目录结构

```
envs/            continuous_env.py（主环境，488 维）· grid_env.py（原型）
                 auv_model.py（1 格/步，5 航向）· sonar_model.py（圆/扇 FOV + 遮挡）
                 info_map.py（覆盖/不确定度/概率三层）· maps/（Square / Irregular）
algorithms/      random_search · lawnmower · greedy_prob · dqn/ · sac/
trainers/        dqn_trainer · sac_trainer · evaluator
scripts/         train_dqn · train_sac · evaluate · run_experiment · run_algo · run_ablation · render_episode
config/          algo/*.yaml · env/*.yaml
docs/            README（索引）· 00-handoff · 01-review · 02-plan · 03-decisions · 04-maps
```

## 环境与模型的既有事实（改代码前必看）

- 观测 = 4×11×11 patch（coverage, uncertainty, probability, obstacle）+ `[x_norm, y_norm, sin ψ, cos ψ]` = **488 维**。
- 动作 = `ACTION_ANGLES = [-90,-45,0,45,90]` 度；`auv_model.step` **先用旧 ψ 移动、再转向**（动作有 1 步滞后）。
- 检测（旧协议）：`continuous_env.py` 里 `target_detected = self.target_pos_grid in fov_cells`，**进 FOV 即发现，无 Pd/Pfa**。
- 信念更新：`info_map._bayesian_update` 用 `p_detect = 1 - 0.3d/R` 做乘性更新——**与确定性检测不一致**（这是要修的 A2）。
- `uncertainty_decay = 1.0` ⇒ uncertainty 通道恒等于 `1 − coverage`（121 维冗余，A6）。
- 障碍 patch 半径 5 > 声呐半径 3 ⇒ 特权避障信息（A6/D4）。
- 碰撞：回退原位 + 随机 ±90–180° 旋转 + 罚分（会连锁，C7）。
- 目标从 `grid == 0` 均匀采样；`SquareMap` 用局部 `RandomState(42)`，不污染全局种子。
- 所有已知问题与处置见 [`docs/01-review/2026-11-28-issues-checklist.md`](docs/01-review/2026-11-28-issues-checklist.md)。

## 分支与改动纪律

- `main`：只放已确认的文档与稳定代码。
- 主线开发从 `main` 开 `feat/gate1-protocol`（Phase 0）。
- `wip/fair-baselines`（A* 导航 + 公平基线 + benchmark harness）**只作参考**，可摘实现思路，不整体合并。
- 不改 `docs/00-handoff/`（只读）；不改 TAOLUN 目录任何文件。
- 每个实验改动都要留下 commit + 配置 + seed + `results/<tag>/episodes.csv`；新结果不覆盖旧结果。

## 评估纪律（旧结论已撤回）

- **不要**再引用“DQN 95% / SAC 94% 优于 Lawnmower”这类数字：那是匹配声呐宽的基线缺失 + 单 seed + 不同回合数造成的。
- 主指标：条件 time-to-find（成功回合的步数/能量）+ 删失率；成功率只作次要指标（已饱和：random ≈83–87%）。
- 同一配置 ≥3 训练 seed，报全部 seed，不挑最好；方法间用 common random numbers 配对。
- 同时评估 `best.pt` 与 `final.pt`（best 按训练 success_rate 选，SAC 有训练/评估 gap）。
- 表格由 `scripts/make_tables.py` 从 CSV 生成，**不要手填**。

## 常用命令

```powershell
$py = "D:\Anaconda\envs\UUVSearch\python.exe"
cd C:\Users\17053\Desktop\UUVSearch

& $py scripts\run_experiment.py --env continuous --algo lawnmower --episodes 20 --seed 0
& $py scripts\train_dqn.py --exp-name dqn_v6 --total-steps 400000
& $py scripts\train_sac.py --exp-name sac_v7 --total-steps 400000
& $py scripts\evaluate.py --algo dqn --checkpoint experiments\checkpoints\dqn_v6\best.pt --episodes 100 --seed 0
& $py scripts\render_episode.py --algo sac --checkpoint experiments\checkpoints\sac_v7\best.pt --max-steps 200
tensorboard --logdir experiments/logs/
```

Phase 0 之后统一入口：`& $py scripts\run_suite.py --suite gate1 --config config\suites\gate1.yaml`。

## TensorBoard 指标

| Tag | 含义 | 期望 |
|---|---|---|
| train/success_rate | 最近 100 回合滑动成功率 | 上升（注意已饱和，别当主指标） |
| train/episode_reward | 每回合累计奖励 | 由负转正 |
| train/epsilon | DQN 探索率 | 1.0 → 0.1 线性 |
| train/alpha | SAC 熵温度 | 稳定在 [0.01, 10] |
| train/loss_critic | SAC critic MSE | <100，找到目标时尖峰 |

## 下一步（截至 2026-11-28）

1. 用户确认计划 v3.1 §11 的 5 个设计点（虚警语义、C0c/C3c、训练图、结构化图种类、短稿 venue）。
2. Phase 0：地图工厂 M1–M5 + 检测层（Pd/Pfa）+ odds-Bayes + 能量 + `info_gain` 基线 + `run_suite.py` / `make_tables.py`。
3. Gate 1 跑 7 方法 × 5 图 × 5 seeds（不训练），确认排名稳定后再进 Gate 2 训练。

不要跳步：Gate 1 不通过就先修协议，不要直接训练大量模型。
