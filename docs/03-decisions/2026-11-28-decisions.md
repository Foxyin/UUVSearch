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

用 GPU 训练。**2026-11-28 复核**：用户判断正确，机器上确实已有 CUDA 版 torch —— `cyclegan` env = torch 2.3.0+cu118、`py3.8` env = 2.2.2+cu118，均 `cuda.is_available()=True`；但 `UUVSearch` env 仍是 `2.4.1+cpu`，且上述两个 env 都没装 gymnasium。

实测（RTX 4060 Laptop 8GB，驱动 610.91；MLP 488→256→256→5，batch 64，1000 次 update）：CPU 12.18 ms/update、GPU 3.38 ms/update ≈ **3.6×**。

结论：给 `UUVSearch` env 装 `torch==2.4.1+cu118`（2.7 GB；C: 剩 51.8 GB）。pip 临时目录需改到项目 `.tmp`，否则沙箱拒绝写 `%TEMP%`（实测 `PermissionError`）。装好后先复测 micro-benchmark 再排训练。

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

## 9. 交接文档 §10 未答项（2026-11-28 第二轮答复）

1. **开题口径**：不影响本项目的排期。
2. **与 A1 的顺序**：「不用管我安排让你干你就干」——按指令执行，**先把 UUVSearch 投出去再说**（UUVSearch 优先）。
3. **A 能否引用未发表结果**：未明确；按“先投这个”推进，投稿后再谈。
4. **署名/salami**：署名最后定；实验与 claim 与 A 分开。
5. **能否复用 A1 代码/数据**：可以，边界照交接文档（只复用 env/sonar，不共享实验与结果）。

## 10. 算力最终口径（2026-11-28 第三轮）

用户：「pytorch 现在能用 GPU 吗？哪个好用用哪个，CPU 好就用 CPU。」

- `UUVSearch` env 的 torch 是 `2.4.1+cpu`，**该环境当前用不了 GPU**；机器有 RTX 4060 Laptop 8GB，`cyclegan`/`py3.8` 有 cu118 版但缺 gymnasium。
- 按实测吞吐：CPU 8–10 进程并行 ≈800 步/s；GPU 单进程 ≈220 步/s（网络太小）。**结论：实验网格用 CPU 并行，暂不装 CUDA torch**；仅当单 run 交互调试/模型变大时再评估。

## 11. 第三轮答复（2026-11-28，分支/地图/曲线/计划性质）

1. **WIP 分支**：保留为分支，只作参考；**不整体合并**。主线要按接下来确认的最终计划重做——“它只是看 TAOLUN 之前的一次独立尝试，可以参考，但主线要有自己的思路和计划”。→ 主线从 `main` 开 `feat/gate1-protocol`。
2. **地图**：结构化障碍**要设计和加**（管线/礁石带/走廊），不只随机障碍。
3. **Pd 曲线**：两种都留成配置（linear 默认 + steep），不二选一。
4. **Gate 1 旧模型**：可作为协议校准，标注分布外、不作结论（认可）。
5. **计划性质**：计划是**活文档**——“计划后面可能会改，毕竟真做实验可能发现新的，或者有审计的时候”。→ 计划文件带版本号 + 变更日志；每次改动记录「改了什么/为什么/影响哪些 Gate」。

## 12. 第四轮答复（2026-11-28，计划 v3.1 §11 五个设计点）

1. **obs 对照**：**现在就把 C0c/C3c 加进 Gate 2**（多 12 run，约 1 h）。理由：这是 H4“信念观测何时有用”的直接证据，缺了会分不清“信念没用”还是“信念通道没接对”。
2. **训练图**：**先只用 M1**；记住后续（Gate 3 或 P1）要补 **M1–M3 轮换**的稳健性检查，不是这一轮做。
3. **结构化地图**：**先做一种：管线 + 礁石带**；走廊迷宫留待 Gate 1/3 视结果再补。
4. **论文写作**：**先不写**，等实验做完再说。Gate 3 的“短稿 or 技术报告”判据不变，只是写作排期后移。
5. **虚警语义**：待解释 A/B 两种方案后再定（见下条答复，未决）。
