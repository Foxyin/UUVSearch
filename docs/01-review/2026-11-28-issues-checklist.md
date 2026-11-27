# 问题与建议总清单（2026-11-28）

来源：① TAOLUN 交接文档 `docs/00-handoff/UUVSearch-交接-20261127.md`（§1/§9 代码问题、§5 最小实验包、§7 P0、§8 不做）；② 本项目 2026-11-27 基准审计 `docs/01-review/2026-11-27-audit.md`（五项诊断）；③ 2026-11-28 复盘中新发现的工程问题。

处置列的含义：**纳入** = 已写进 `docs/02-plan/plan-2026-11-28.md` 的某节；**P1** = 加分项，Gate 过后再做；**不做** = 明确不做并写理由；**限制** = 不改代码，但在论文 limitation 里写清楚。

## A. 检测与信念模型

| ID | 问题 | 来源 | 严重度 | 处置 | 落点 |
|---|---|---|---|---|---|
| A1 | 检测是确定性的（`continuous_env.py:124` `target_detected = in fov_cells`），无 Pd 采样 | 交接 §1.2/§9 | 致命 | 纳入 | plan §2.1 |
| A2 | 信念按 `p_detect=1-0.3d/R` 更新，与确定性检测不一致（miss 后仍留质量） | 审计诊断② | 致命 | 纳入：改 odds-Bayes | plan §2.2 |
| A3 | 无 Pfa / 虚警 | 交接 §5.1/§7-1 | 高 | 纳入 | plan §2.1/§2.2 |
| A4 | UUV `search_info_map.py:38-41` 未检出用 `likelihood=PF`（应为 `1-PD`），45-49 全局归一化重复计质量 | 交接 §1.2/§9 | 致命 | 不做（不复用） | plan §2.2 注 |
| A5 | 目标先验均匀 + 静止 → 最优策略是纯覆盖，信念图价值有限 | 审计诊断③ | 中 | P1：信息先验作为扩展 | plan §2.6 |
| A6 | `uncertainty_decay=1.0` → uncertainty 通道恒等于 `1-coverage`，121 维冗余 | 审计诊断⑤ | 中 | 纳入：观测层可换熵/最近扫描 | plan §2.4 |
| A7 | AUV `sonar/noise.py` 三个算子可移植（声呐噪声/衰减） | 交接 §3.1 | 低 | P1，需重接 beam→cell 接口 | plan §2.6 |
| A8 | 确定性检测下，正确的后验 ≡ “未扫格上的均匀分布” = 1−coverage ⇒ 概率通道与覆盖通道信息等价，488 维观测里 coverage/uncertainty/probability 三个 patch 共线 | 2026-11-28 逻辑复核（新增） | 高 | 纳入：作为 H4 的理论前提 + C0/C0c 的负向自检；确定性档改精确更新 | plan §1、§2.2 |

## B. 评估协议与统计

| ID | 问题 | 来源 | 严重度 | 处置 | 落点 |
|---|---|---|---|---|---|
| B1 | 单地图、单 seed、无 CI | 交接 §1.1/§9 | 致命 | 纳入 | plan §5/§6 |
| B2 | 传统算法 50 回合、RL 100 回合，口径不一致 | 交接 §1.1 | 高 | 纳入：Gate 1 统一 | plan §6 |
| B3 | `experiments/ablation` 只有 `.gitkeep`，run_ablation 不产 CSV | 交接 §1.1/§6 | 高 | 纳入：统一走 run_suite | plan §9 |
| B4 | README 表不可由仓库 CSV 复核（自报表格） | 交接 §5.4/§7-7 | 高 | 纳入：make_tables | plan §5/§9 |
| B5 | 无 held-out 地图，无泛化证据 | 审计诊断⑤ | 高 | 纳入：M4/M5 | plan §3 |
| B6 | 无配对比较/显著性检验 | 交接 §5.4 | 高 | 纳入：common random numbers + Wilcoxon | plan §5 |
| B7 | `best.pt` 按训练 success_rate 选，对 SAC 有结构性 gap，可能锁死早期模型 | CLAUDE.md 已知局限 | 中 | 纳入：评估 best 与 final 两个 | plan §9 |
| B8 | README 的 95%/94% 被当成“RL 更优”证据；实际 lawnmower 100% | 交接 §3.2/§8 | 高 | 纳入：撤回并标历史 | plan §12/README |
| B9 | Evaluator 每步重算 FOV 画图，评估慢 | 审计 | 低 | 纳入：评估与绘图分离 | plan §9 |
| B10 | 主指标用成功率已饱和（random 87%） | 审计诊断① | 高 | 纳入：条件 TTF + 删失 | plan §5 |

## C. 基线公平性

| ID | 问题 | 来源 | 严重度 | 处置 | 落点 |
|---|---|---|---|---|---|
| C1 | lawnmower `swath_width=2` 硬编码，与声呐半径 3 不匹配 | 审计诊断④ | 致命 | 纳入：swath=2R | plan §4 |
| C2 | lawnmower 每格一个 waypoint + 最近航向控制器（1-step 滞后）→ 移动效率低 | 审计 | 中 | 纳入：A* + pure pursuit | plan §4 |
| C3 | greedy_prob 只在 11×11 patch 内贪心，且用真值 `map_obj.is_free`（特权） | 审计诊断④ | 中 | 保留但标注为“特权局部贪心” | plan §4 |
| C4 | 缺 info-gain / greedy entropy 基线 | 交接 §5.2 | 高 | 纳入：新增 `algorithms/info_gain.py` | plan §4 |
| C5 | 缺 oracle 上界（已知目标最短路径） | 交接 §5.2 | 低 | 纳入：oracle_TTF 参考 | plan §4 |
| C6 | RL 只报最好 seed | 交接 §5.2 | 高 | 纳入：≥3 seed 全报 | plan §5/§7 |
| C7 | 碰撞回退+随机 90–180° 旋转造成连锁失败（oracle 9.7 次/回合 vs RL 3–4 次） | 审计 | 中 | 纳入：统一碰撞口径 + 敏感性 | plan §2.5 |

## D. 环境与物理

| ID | 问题 | 来源 | 严重度 | 处置 | 落点 |
|---|---|---|---|---|---|
| D1 | 只有 5 个航向、无速度控制，无法“抵近—保持—放弃” | 交接 §9 | 中 | 不做（search-only 可接受） | plan 限制 |
| D2 | `auv_model.step` 先用旧 psi 移动再转向 → 动作有 1 步滞后 | 审计 | 中 | 保留（可比性），文档标注 | plan §2.5 |
| D3 | 无能量/路径成本 | 交接 §5.1/§7-2 | 高 | 纳入：EnergyModel 三档 | plan §2.3 |
| D4 | 障碍 patch 是 11×11，远大于声呐半径 3 → 特权避障信息 | 审计诊断⑤ | 中 | 纳入：消融“声呐限障”+ limitation | plan §2.4/§8 |
| D5 | 目标从 `grid==0` 采样，border 也算 free | 审计 | 低 | 保持，文档标注 | plan §3 注 |

## E. 可复现与工程

| ID | 问题 | 来源 | 严重度 | 处置 | 落点 |
|---|---|---|---|---|---|
| E1 | 无一条命令复现 | 交接 §5.4/§7-7 | 高 | 纳入 | plan §9 |
| E2 | 无 commit/config/seed 记录 | 交接 §11-6 | 高 | 纳入：meta.json | plan §9 |
| E3 | 新结果覆盖旧结果 | 交接 §11-6 | 中 | 纳入：`results/<date>-<tag>/` | plan §9 |
| E4 | seed 只在 `--seed` 提供时设置，np/torch/env/buffer 不一致 | 审计 | 中 | 纳入：统一 seed 纪律 | plan §9 |
| E5 | SquareMap 用局部 `RandomState(42)`，不污染全局种子 | 审计 | — | 保留 | plan §3 |
| E6 | 能量预算若用绝对步数，则 20×20 图上等于没给预算，跨图不可比 | 2026-11-28 逻辑复核（新增） | 高 | 纳入：预算按 free_cells 倍数 | plan §2.3 |
| E7 | “只对成功回合计 TTF”有长度偏差（难回合被删失剔除） | 2026-11-28 逻辑复核（新增） | 高 | 纳入：KM + log-rank 为主 | plan §5 |
| E8 | 缺“无全图”的强覆盖基线，lawnmower 是 oracle，不是公平对手 | 2026-11-28 逻辑复核（新增） | 高 | 纳入：新增 online_lawnmower | plan §4 |

## F. 定位与边界（不做的事）

| ID | 事项 | 来源 | 处置 |
|---|---|---|---|
| F1 | 不写成 Li et al. 2024 的复现 | 交接 §1.3/§8 | 只作 related work |
| F2 | 不改造成 TAOLUN 方向 A 的 confirm/三态底座 | 交接 §0/§8 | 不做 |
| F3 | 不按 Q1/Q2 硬门槛准备 | 交接 §4.3/§8 | 按会议/短稿/Q2 准备 |
| F4 | 不与 A 共享实验/claim/图表（salami） | 交接 §4.2 | 实验分开 |
| F5 | 不长于 3 周可行性 + 4–6 周论文 | 交接 §6 | 硬上限 |
| F6 | 不复用 UUV 的贝叶斯实现；不从 UUVRoad 重写底座 | 交接 §3.2/§9 | 不做 |

## 结论：覆盖情况

- 致命项 A1/A2/A4/B1/C1 —— 全部有明确落点，且 A4/F6 是“明确不做”。
- 高/中项全部纳入 plan，其中 A5/A7 标为 P1。
- 第一轮补漏：A6、C7、D2、D4、E4（v3.1）。
- 第二轮逻辑复核新增：A8（确定性下信念与覆盖等价）、E6（能量预算随图缩放）、E7（删失偏差）、E8（缺无全图基线）——v3.2 已补，并顺带修正矩阵算术（48 run）、Gate 1 回合数（25 ep/方法）等 4 处数字错误。
