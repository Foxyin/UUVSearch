# UUVSearch

基于强化学习的无人水下航行器（UUV）自主目标搜索仿真框架。

> 在未知障碍物环境中，AUV 搭载有限探测距离的声呐，通过连续运动学和信息地图，自主搜索隐藏目标。

## 项目结构

```
UUVSearch/
├── algorithms/           # 搜索算法
│   ├── base_algo.py      #   算法抽象基类
│   ├── random_search.py  #   随机动作基线
│   ├── lawnmower.py      #   梳形覆盖路径（boustrophedon）
│   ├── dqn/              #   Deep Q-Network（DQN）
│   │   ├── agent.py
│   │   ├── network.py
│   │   └── replay_buffer.py
│   └── sac/              #   Soft Actor-Critic（SAC, 离散动作）
│       ├── agent.py
│       ├── network.py
│       └── replay_buffer.py
├── config/               # YAML 配置文件
│   ├── algo/             #   算法超参数（dqn.yaml, sac.yaml）
│   └── env/              #   环境参数（square, irregular, grid）
├── envs/                 # 仿真环境
│   ├── auv_model.py      #   AUV 一阶运动学模型
│   ├── sonar_model.py    #   声呐模型（圆形/扇形 FOV，Bresenham 遮挡）
│   ├── info_map.py       #   三层信息地图（覆盖/不确定度/目标概率）
│   ├── grid_env.py       #   离散网格环境
│   ├── continuous_env.py #   连续运动学环境（Gymnasium）
│   └── maps/             #   地图生成（方形/不规则多边形）
├── trainers/             # 训练与评估
│   ├── dqn_trainer.py
│   ├── sac_trainer.py
│   └── evaluator.py
├── scripts/              # 可执行入口
│   ├── train_dqn.py      #   DQN 训练
│   ├── train_sac.py      #   SAC 训练
│   ├── evaluate.py       #   模型评估与可视化
│   ├── render_episode.py #   单回合实时渲染
│   ├── run_ablation.py   #   消融实验批量运行
│   ├── plot_results.py   #   消融结果柱状图
│   └── run_algo.py       #   传统算法测试（random / lawnmower）
├── utils/                # 工具
│   ├── config_loader.py  #   YAML 加载与深度合并
│   ├── logger.py         #   TensorBoard 日志封装
│   └── visualizer.py     #   轨迹图 / 热力图绘制
├── experiments/          # 输出目录
│   ├── checkpoints/      #   模型权重
│   ├── logs/             #   TensorBoard 日志
│   └── figures/          #   评估图片
├── requirements.txt
└── README.md
```

## 快速开始

### 环境配置

```bash
# 使用 conda（推荐）
conda create -n UUVSearch python=3.10
conda activate UUVSearch
pip install -r requirements.txt
```

### 运行传统算法

```bash
# 网格环境 + 梳形覆盖算法
python scripts/run_algo.py --algo lawnmower --episodes 10 --render

# 连续环境 + 随机算法
python scripts/run_experiment.py --env continuous --algo random --episodes 5 --render
```

### 训练 RL 模型

```bash
# 训练 DQN（50k 步）
python scripts/train_dqn.py --exp-name dqn_test --total-steps 50000

# 训练 SAC
python scripts/train_sac.py --exp-name sac_test --total-steps 50000

# 查看训练曲线
tensorboard --logdir experiments/logs/
```

### 评估模型

```bash
# 评估 SAC 在正方形地图上的表现
python scripts/evaluate.py --algo sac \
  --checkpoint experiments/checkpoints/sac_test/step_50000.pt \
  --episodes 100

# 评估在非规则多边形上的泛化能力
python scripts/evaluate.py --algo sac \
  --checkpoint experiments/checkpoints/sac_test/step_50000.pt \
  --env-config config/env/continuous_irregular.yaml --episodes 50
```

### 消融实验

```bash
# 验证各奖励分量的贡献
python scripts/run_ablation.py --algo sac --total-steps 15000 --episodes 50

# 生成对比柱状图
python scripts/plot_results.py --csv experiments/ablation/results_sac.csv
```

### 可视化渲染

```bash
# 实时观看 AUV 搜索过程
python scripts/render_episode.py --algo sac \
  --checkpoint experiments/checkpoints/sac_test/step_50000.pt \
  --max-steps 200
```

## 核心设计

### 信息地图（三层）

| 层 | 含义 | 更新方式 |
|----|------|----------|
| **覆盖图** | 已探测的自由格子 | FOV 内标记为 1 |
| **不确定度图** | 对环境的未知程度 | 探测后归零 |
| **目标概率图** | 目标在各位置的后验概率 | 简化贝叶斯更新：探测到 ×2，未探测 ×0.5，全局归一化 |

### 奖励函数（连续环境）

| 分量 | 默认值 | 含义 |
|------|--------|------|
| `coverage_gain` | +1.0/格 | 首次覆盖新格子 |
| `revisit_gain` | +0.1/格 | 重复访问（微弱正奖励） |
| `find_target` | +100 | 探测到目标 |
| `collision_penalty` | -2.0 | 碰撞边界或障碍物 |
| `step_penalty` | -0.05 | 每步微小惩罚，鼓励效率 |

### 观测空间

RL 智能体的观测由三部分组成：
- **局部覆盖图 patcher**：(2R+1)×(2R+1) 的 coverage 矩阵
- **局部不确定度 patcher**：同上
- **局部概率 patcher**：同上
- **归一化状态向量**：[x/map_length, y/map_length, psi/2π]

拼接为扁平向量，输入维度 = 3×(2R+1)² + 3。

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
        return self.grid != 1  # 自由格子掩码
```

### 添加新算法

**传统算法**（适用于网格环境）：

1. 在 `algorithms/` 下新建文件，继承 `BaseAlgorithm`
2. 实现 `select_action(obs)` 和 `reset()`
3. 在 `algorithms/__init__.py` 的 `_ALGO_REGISTRY` 中注册

```python
# 示例：algorithms/my_algo.py
from .base_algo import BaseAlgorithm

class MyAlgorithm(BaseAlgorithm):
    def select_action(self, obs: dict) -> int:
        # obs 包含 "auv_pos", "target_found", "coverage" 等
        return 3  # 返回 0-7 的动作编号

    def reset(self):
        pass  # 回合重置逻辑
```

**RL 算法**：

1. 在 `algorithms/` 下新建目录，包含 `agent.py`、`network.py`
2. 实现与 `DQNAgent`/`SACAgent` 一致的接口：`select_action(obs)`、`store_transition(...)`、`update()`、`save(path)`、`load(path)`
3. 在 `trainers/` 下新建训练器
4. 在 `scripts/` 下新建训练入口脚本

### 调整奖励函数

直接修改 `config/env/*.yaml` 中的 `rewards` 字段，或通过消融脚本配置 `ABLATION_GROUPS`。

### 调整声呐参数

修改 YAML 中的 `sonar` 字段：
```yaml
sonar:
  type: "circle"        # "circle" 或 "sector"
  max_range: 5          # 探测半径（网格数）
  sector_angle: 120     # 扇形角度（仅 sector 模式）
```

## 已实现算法

| 算法 | 类型 | 动作空间 | 环境 | 特点 |
|------|------|----------|------|------|
| Random | 基线 | 8 离散 | 网格 | 均匀随机 |
| Lawnmower | 传统 | 8 离散 | 网格 | 梳形覆盖 + 脱困 |
| DQN | Value-based RL | 5 离散 | 连续 | target network + ε-greedy |
| SAC | Actor-Critic RL | 5 离散 | 连续 | 双 Critic + 自动熵调节 |

## 依赖

- Python 3.8+ (当前环境 3.8.20)
- PyTorch 2.4
- Gymnasium 1.1
- 完整列表见 [requirements.txt](requirements.txt)
