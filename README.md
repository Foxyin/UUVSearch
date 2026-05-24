# UUVSearch

基于强化学习的无人水下航行器（UUV）自主目标搜索仿真框架。

> 在未知障碍物环境中，AUV 搭载有限探测距离的声呐，通过连续运动学和信息地图，自主搜索隐藏目标。

## 项目结构

```
UUVSearch/
├── algorithms/           # 搜索算法
│   ├── base_algo.py      #   算法抽象基类（传统算法）
│   ├── random_search.py  #   随机动作基线
│   ├── lawnmower.py      #   梳形覆盖路径（boustrophedon）
│   ├── dqn/              #   Deep Q-Network
│   │   ├── agent.py
│   │   └── network.py
│   └── sac/              #   Soft Actor-Critic（离散动作）
│       ├── agent.py
│       └── network.py
├── config/               # YAML 配置文件
│   ├── algo/             #   算法超参数（dqn.yaml, sac.yaml）
│   └── env/              #   环境参数（square, irregular, grid）
├── envs/                 # 仿真环境
│   ├── auv_model.py      #   AUV 一阶运动学模型
│   ├── sonar_model.py    #   声呐模型（圆形/扇形 FOV，Bresenham 遮挡）
│   ├── info_map.py       #   三层信息地图（覆盖/不确定度/目标概率）
│   ├── grid_env.py       #   离散网格环境（Gymnasium）
│   ├── continuous_env.py #   连续运动学环境（Gymnasium）
│   └── maps/             #   地图生成（方形/不规则多边形）
├── trainers/             # 训练与评估
│   ├── dqn_trainer.py
│   ├── sac_trainer.py
│   └── evaluator.py      #   RL 模型评估器
├── utils/                # 共享工具
│   ├── config_loader.py  #   YAML 加载与深度合并
│   ├── replay_buffer.py  #   经验回放缓冲区（DQN/SAC 共用）
│   ├── logger.py         #   TensorBoard 日志封装
│   └── visualizer.py     #   轨迹图 / 热力图绘制
├── scripts/              # 可执行入口
│   ├── train_dqn.py      #   DQN 训练
│   ├── train_sac.py      #   SAC 训练
│   ├── evaluate.py       #   RL 模型评估与可视化
│   ├── render_episode.py #   单回合实时渲染
│   ├── run_experiment.py #   传统算法统一运行器（grid + continuous）
│   ├── run_algo.py       #   网格环境传统算法测试
│   ├── run_ablation.py   #   消融实验批量运行
│   └── plot_results.py   #   消融结果柱状图
├── experiments/          # 输出目录（gitignored）
│   ├── checkpoints/      #   模型权重
│   ├── logs/             #   TensorBoard 日志
│   └── figures/          #   评估图片
├── requirements.txt
└── README.md
```

## 快速开始

### 环境配置

```bash
conda create -n UUVSearch python=3.10
conda activate UUVSearch
pip install -r requirements.txt
```

### 运行传统算法

```bash
# 网格环境 + 梳形覆盖算法
python scripts/run_algo.py --algo lawnmower --episodes 10 --render

# 连续环境 + 梳形覆盖算法
python scripts/run_experiment.py --env continuous --algo lawnmower --episodes 10

# 可复现评估（固定 seed）
python scripts/run_experiment.py --env continuous --algo random --episodes 20 --seed 0
```

### 训练 RL 模型

```bash
# 训练 DQN
python scripts/train_dqn.py --exp-name dqn_v6 --total-steps 400000

# 训练 SAC
python scripts/train_sac.py --exp-name sac_v7 --total-steps 400000

# 查看训练曲线（含 success_rate）
tensorboard --logdir experiments/logs/
```

### 评估模型

```bash
# 评估 SAC 在正方形地图上的表现
python scripts/evaluate.py --algo sac --checkpoint experiments/checkpoints/sac_v7/best.pt --episodes 100

# 评估在非规则多边形上的泛化能力
python scripts/evaluate.py --algo sac \
  --checkpoint experiments/checkpoints/sac_v7/best.pt \
  --env-config config/env/continuous_irregular.yaml --episodes 50
```

### 消融实验

```bash
# 单次运行
python scripts/run_ablation.py --algo sac --total-steps 100000 --episodes 50

# 多次运行 + 标准差（5 次不同 seed）
python scripts/run_ablation.py --algo sac --total-steps 100000 --episodes 50 --repeat 5

# 生成对比柱状图（自动检测 error bar）
python scripts/plot_results.py --csv experiments/ablation/results_sac.csv
```

### 可视化渲染

```bash
python scripts/render_episode.py --algo sac \
  --checkpoint experiments/checkpoints/sac_v7/best.pt \
  --max-steps 200
python scripts/render_episode.py --algo dqn \
  --checkpoint experiments/checkpoints/dqn_v6/best.pt \
  --save-video demo.mp4
```

## 核心设计

### 信息地图（三层）

| 层 | 含义 | 更新方式 |
|----|------|----------|
| **覆盖图** | 已探测的自由格子 | FOV 内标记为 1 |
| **不确定度图** | 对环境的未知程度 | 探测后归零（当前不随时间增长） |
| **目标概率图** | 目标在各位置的后验概率 | 贝叶斯更新：`P_detect(d)` 驱动（连续）/ 启发式回退（网格） |

> **注意**：概率更新已升级为距离相关真贝叶斯（连续环境），网格环境保留旧启发式作为回退。

### 奖励函数（连续环境）

消融实验的四种奖励配置：

| 配置 | coverage_gain | revisit_gain | find_target | collision_penalty | step_penalty |
|------|:---:|:---:|:---:|:---:|:---:|
| `full`                  | 1.0 | 0.0 | 100 | -2.0 | -0.05 |
| `no_exploration_reward` | 0 | 0 | 100 | -2.0 | -0.05 |
| `no_target_reward`      | 1.0 | 0.0 | 0 | -2.0 | -0.05 |
| `target_reward_only`    | 0 | 0 | 100 | -1.0 | -0.01 |

### 观测空间

RL 智能体的观测由四个局部 patch 和归一化状态组成：
- **局部覆盖图 patch**：(2R+1)×(2R+1) 的 coverage 矩阵
- **局部不确定度 patch**：同上
- **局部概率 patch**：同上
- **局部障碍物 patch**：同上（短程避障声呐，论文中需标注为 privileged information）
- **归一化状态向量**：[x/map_length, y/map_length, sin(psi), cos(psi)]

拼接为扁平向量，输入维度 = 4×(2R+1)² + 4（4 patch + 状态，默认 R=5，共 488 维）。

### 环境对比

| | 网格环境 (GridEnv) | 连续环境 (ContinuousSearchEnv) |
|---|---|---|
| **运动** | 逐格移动 | 一阶运动学（v·dt = 30m/步） |
| **动作** | 8 方向（罗盘） | 5 航向变化（-90°~+90°） |
| **观测** | dict（含 auv_pos, coverage 等） | 1D array（488 维，4 patch） |
| **用途** | 传统算法快速验证 | RL 训练 + 正式实验 |
| **Gymnasium** | ✅ 继承 gym.Env | ✅ 继承 gym.Env |

## 已实现算法

| 算法 | 类型 | 网格环境 | 连续环境 | 特点 |
|------|------|:---:|:---:|------|
| Random | 基线 | ✅ 8 动作 | ✅ 5 动作 | 均匀随机 — 搜索效率的下界 |
| Lawnmower | 传统 | ✅ 8 方向 | ✅ 5 航向 | 预知全图，梳形全覆盖 — 效率上界 |
| GreedyProb | 传统 | ✅ 8 方向 | ✅ 5 航向 | 信息驱动，走向概率最高处 — 测试信息地图价值 |
| DQN | Value RL | — | ✅ 5 动作 | target network + ε-greedy（线性衰减） |
| SAC | Actor-Critic RL | — | ✅ 5 动作 | 双 Critic + 自动熵调节（target_entropy_scale=0.2，优化确定性gap） |

> 三个传统算法形成基线梯度：Random（不用信息）→ GreedyProb（用信息地图）→ Lawnmower（用完整地图）。RL 算法在不依赖完整地图的条件下逼近 Lawnmower 的效率，即为有效学习。

## 扩展指南

### 添加新地图

1. 在 `envs/maps/` 下新建文件，继承 `BaseMap`，实现 `__init__` 和 `get_mask()`
2. 在 `envs/maps/__init__.py` 的 `_MAP_REGISTRY` 中注册
3. 在 `config/env/` 下添加对应 YAML 配置文件

```python
# 示例：envs/maps/my_map.py
from .base_map import BaseMap

class MyMap(BaseMap):
    def __init__(self, config):
        super().__init__(config)
        self.size = config["grid_size"]
        self.grid = ...  # 构造网格

    def get_mask(self):
        return self.grid != 1
```

### 添加新算法

**传统算法**（与 `base_algo.py` 兼容）：

1. 在 `algorithms/` 下新建文件，继承 `BaseAlgorithm`
2. 实现 `select_action(obs)` 和 `reset()`
3. 在 `algorithms/__init__.py` 的 `_ALGO_REGISTRY` 中注册

**RL 算法**：

1. 在 `algorithms/` 下新建目录（含 `agent.py`、`network.py`）
2. 实现接口：`select_action(obs)`、`store_transition(...)`、`update()`、`save(path)`、`load(path)`
3. 在 `trainers/` 下新建训练器
4. 在 `scripts/` 下新建训练入口脚本

### 调整声呐参数

```yaml
sonar:
  type: "circle"        # "circle" 或 "sector"
  max_range: 5          # 探测半径（网格数）
  sector_angle: 120     # 扇形角度（仅 sector 模式）
```

## 已知局限与未来工作

### ✅ 真贝叶斯更新（已完成 2026-05-23）

概率更新已升级为距离相关的真贝叶斯：探测到 → `P_detect(d)`，未探测到 → `1 - P_detect(d)`。近处高置信、远处保留怀疑。实现于 `info_map._bayesian_update()`，连续环境自动启用，网格环境回退旧启发式。

### 当前阶段（其他待改进项）

| 问题 | 说明 | 改进方向 |
|------|------|----------|
| **单地图训练** | 所有实验共享同一张种子 42 的地图 | 后续实验用多张地图交叉验证 RL 泛化能力 |
| **传统算法与 RL 独立评估** | `Evaluator` 仅支持 RL agent（`deterministic` 参数），传统算法用 `run_experiment.py` | 统一评估管线或文档说明分工 |
| **脚本路径依赖** | 部分脚本要求从项目根目录运行（CWD 相对路径） | 统一使用 `__file__` 相对路径解析 |

### 展望

| 方向 | 说明 |
|------|------|
| **新 RL 算法** | 基于此框架研发专用搜索 RL 模型，在连续环境中超越 DQN/SAC 基线 |
| **多地图泛化** | 正方形→不规则多边形→随机障碍物密度，验证策略迁移能力 |
| **多 AUV 协同** | 扩展环境支持多航行器协同搜索，研究通信约束下的分布式策略 |
| **真实声呐模型** | 从二元探测升级为频率相关声传播模型（射线追踪/抛物方程） |
| **元学习** | 在多种地图类型上训练元策略，快速适应新环境 |

## 运行说明

所有脚本需从项目根目录执行：

```bash
cd UUVSearch
python scripts/<script_name>.py [args...]
```

## 依赖

- Python 3.8+ (当前 conda 环境 3.8.20，建议 ≥3.10)
- PyTorch 2.4
- Gymnasium 1.1
- 完整列表见 [requirements.txt](requirements.txt)
