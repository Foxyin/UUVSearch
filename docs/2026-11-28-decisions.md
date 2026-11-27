# 2026-11-28 决策记录（技能、地图、算力、起点、Gate）

记录用户对 2026-11-28 确认清单的逐条答复，以及由此确定的工作口径。后续以此为准，不再重复询问已定事项。

## 1. 技能（已解决）

用户口径：文献检索不需要（在别的项目做）；**写作、实验、做图**三类有用。

项目现有 DSH 技能 7 个（`.dsh\skills\`，全部 `level=project-dsh`、`modelInvocable=True`）：

| 技能 | 角色 | 来源 |
|---|---|---|
| `karpathy-guidelines` | 写代码时的行为约束 | 本项目 `.claude` 迁移 |
| `experiment-design` | 实验规划（claim→证据→矩阵→预算） | night_owl_research_agent |
| `academic-plotting` | 数据图（matplotlib/seaborn）+ 架构图 | awesome-ai-research-writing |
| `topconf-figure` | TikZ 矢量主图（Figure 1/系统框图），不做数据图 | topconf-figure |
| `research-paper-writing` | 按节写作/改写、claim-support 对齐、投稿前自审 | paper-skills-dsh |
| `latex-academic-publisher` | Elsevier/IEEE/MDPI 模板、latexmk、.bib | latex-academic-publisher |
| `paper-reviewer` | 投稿前审稿 D1–D4，中英双语 | paper review/.claude |

未装：`paper-search`（用户不需要）、`scoop-check`、`paper-fig`（与 academic-plotting 重叠）、`paperfig`（paper-fig 上游快照）、`deep-research`/`sr-screener`（系统综述）、ResearchStudio 的 poster/reel/video 系列、`ocean-figure-refs` 与 `topconf-figure-gallery`（无 SKILL.md，仅参考图库）。

## 2. 地图（定：参数化对比）

在 SquareMap 基础上**参数化生成多张地图**做对比（尺寸 / 障碍率 / seed），其中至少 2 张作为 held-out。不手工画 5 张固定图。

待实现：`envs/maps/` 增加可配置生成入口（obstacle_ratio、尺寸、seed、可选结构化障碍），保证 `RandomState` 局部化不污染全局种子。

## 3. 算力（定：用 GPU）

用 GPU 训练。**前置条件**：当前 `D:\Anaconda\envs\UUVSearch` 里是 `torch 2.4.1+cpu`，需要先装 CUDA 版 torch（cu121 或 cu124，视驱动；RTX 4060 Laptop 8GB），并验证 `torch.cuda.is_available()` 与单进程吞吐提升后再排训练。

注意：本项目网络小（MLP 256×2、batch 64），GPU 收益主要在并行多 seed，单步未必快很多；装好后先做一次基准对比再决定是否全量上 GPU。

## 4. WIP 分支（定：可作起点，但要改）

`wip/fair-baselines`（A* + 统一 benchmark harness）可以作为 Gate 1 的底座，但必须结合交接文档建议与已发现问题修改：

- 评估协议改为 5 maps × 5 seeds + 95% CI + per-episode CSV + held-out；
- 主指标改为**条件 time-to-find**（成功率已饱和），并报告删失；
- 检测层改为可配置 Pd/Pfa，与贝叶斯更新一致（当前 env 是确定性检测，信息图却按概率更新）；
- 能量约束（步数/功率三档）；
- baseline 补齐：lawnmower / greedy prob / info-gain / random + DQN/SAC 同 obs、action、budget。

## 5. 交接文档（定：复制进项目）

已复制：`docs\UUVSearch-交接-20261127.md`（290 行，来自 `C:\Users\17053\Desktop\TAOLUN\协作\交接\`）。TAOLUN 原件只读，不改。

## 6. 目标期刊（未定，候选）

Ocean Engineering / IEEE Journal of Oceanic Engineering / JMSE / Applied Ocean Research / OCEANS 会议。先做完 Gate，再按结果强度选刊。

## 7. 时间盒与 Gate（定：照执行）

- W1 Gate 1：评估可信 —— 5 maps × 5 seeds，排名稳定；不稳定先修协议。
- W2 Gate 2：检测退化 + 能量小网格 —— 若排名完全不变，说明 RQ 无信号，换 RQ 或停。
- W3 Gate 3：有清晰边界（RL 何时赢/输）才写 4–6 页短稿；否则出技术报告并停，不自动延长。

## 8. 下一步

先出**一页计划**给用户确认（实验矩阵、地图清单、指标定义、算力预算、时间表），确认后再动代码。
