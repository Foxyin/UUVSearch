# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

UUVSearch — 基于强化学习的无人水下航行器（UUV）自主目标搜索仿真框架。AUV 搭载有限探测距离的声呐，在未知障碍物环境中通过连续运动学和信息地图自主搜索固定目标（水雷、管线、鱼雷等）。

## Architecture

```
algorithms/     → 搜索算法（传统基线与 RL）
  base_algo.py  → 传统算法抽象基类（RL 算法不继承此类）
  random_search / lawnmower / greedy_prob → 传统基线
  dqn/ sac/     → RL 算法（DQNAgent / SACAgent，独立接口）
envs/           → Gymnasium 仿真环境
  continuous_env.py → 主实验环境（连续运动学，487维观测）
  grid_env.py       → 快速原型环境（离散网格，dict观测）
  auv_model.py      → 一阶运动学（psi方向=移动方向，y轴向下=grid row增加）
  sonar_model.py    → 圆形/扇形FOV，Bresenham射线遮挡
  info_map.py       → 三层信息地图（覆盖+不确定度+目标概率）
  maps/             → 地图工厂（SquareMap / IrregularMap）
trainers/       → DQNTrainer / SACTrainer / Evaluator（仅支持RL）
scripts/        → 命令行入口
config/         → YAML配置（algo超参 + env参数）
utils/          → config_loader（深度合并）/ replay_buffer / logger / visualizer
```

## Key Design Decisions

- **观测空间**: 4个11×11 patch（coverage+uncertainty+probability+obstacle, 484维）+ 归一化状态3维 = 487维
- **连续环境**: 5个航向变化动作[-90°, -45°, 0°, +45°, +90°], time_step=30s→30m/步=1格
- **奖励**: coverage_gain=1.0, revisit_gain=0.1, find_target=100, collision=-2.0, step_penalty=-0.05
- **DQN ε**: 线性衰减, epsilon_decay_steps=150000 (1.0→0.05)
- **SAC**: 离散动作, 梯度裁剪max_norm=10.0, α钳位≤10, τ=0.003
- **碰撞**: 回退原位 + 随机旋转90-180°打破死循环
- **声呐heading**: `np.rad2deg(psi) % 360`（与运动方向同向，无取负号）
- **固定目标**: uncertainty_decay=1.0（不恢复，已扫区域确信无目标）
- **传统基线梯度**: Random（不用信息）→ GreedyProb（用概率图）→ Lawnmower（用完整地图，全覆盖上界）
- **RL vs 传统对比**: 在同一ContinuousSearchEnv下进行。Lawnmower使用了完整地图是"作弊"上界

## Common Commands

```bash
# 训练（所有脚本从项目根目录运行）
python scripts/train_dqn.py --exp-name dqn_v4 --total-steps 200000
python scripts/train_sac.py --exp-name sac_v4 --total-steps 200000

# 评估
python scripts/evaluate.py --algo sac --checkpoint experiments/checkpoints/<path>/step_XXXXX.pt --episodes 100

# 传统算法测试
python scripts/run_experiment.py --env continuous --algo lawnmower --episodes 50 --seed 42
python scripts/run_algo.py --algo greedy_prob --episodes 30 --render

# 消融实验（带标准差）
python scripts/run_ablation.py --algo sac --total-steps 100000 --episodes 50 --repeat 5
python scripts/plot_results.py --csv experiments/ablation/results_sac.csv

# 可视化
python scripts/render_episode.py --algo sac --checkpoint <path> --max-steps 200
tensorboard --logdir experiments/logs/
```

## TensorBoard 指标

| Tag | 含义 | 正常范围 |
|-----|------|----------|
| train/success_rate | 最近100回合滑动成功率 | 0→应上升至80%+ |
| train/episode_reward | 每回合累计奖励 | -1000(全撞墙)→应转正 |
| train/epsilon | DQN探索率 | 1.0→0.05线性下降 |
| train/alpha | SAC熵温度 | 0.2→应稳定在0.5-10之间 |
| train/loss_critic | SAC Critic MSE | <100为佳，找到目标时会尖峰 |

## 已知局限

1. **概率更新为简化启发式**（×0.5/×2.0），非真贝叶斯。`sonar_model.get_detection_probability(distance)`已就绪待调用
2. 单地图训练（SquareMap seed=42）
3. Evaluator仅支持RL（需`deterministic`参数），传统算法用run_experiment.py评估
4. DQN success_rate在ε触底后从峰值回落（92%→77%），需调整ε_min或探索策略

## 基线性能 (continuous env, seed=42, max_steps=300)

| 算法 | 成功率 | 平均步数 | 说明 |
|------|--------|----------|------|
| Random | 80% | 124 | 下界 |
| GreedyProb | 87% | 81 | 信息驱动（修复后） |
| Lawnmower | 100% | 35 | 上界（需完整地图） |

## 注意事项

- 观测结构: 4 patch (cov/unc/prob/obstacle) × 121 + 状态 × 3 = 487维
- **GreedyProb 的观测解析公式必须为 `(len(obs)-3)/4`**（与观测patch数一致）
- 观测含障碍物通道（privileged避障信息，论文中需标注为"短程避障声呐"）
- SquareMap._place_obstacles使用局部RandomState(42)，不影响全局种子
- 网格环境与连续环境的动作空间不同（8方向 vs 5航向），实验对比以连续环境为准
- SAC agent在`update()`中读写alpha时需注意detach和clamp顺序
- ReplayBuffer使用np.random.RandomState，支持seed()设置可复现
