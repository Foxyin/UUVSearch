# UUVSearch 交接文档（来自 TAOLUN）

- **版本**：v1.0
- **日期**：2026-11-27
- **交接对象**：`C:\Users\17053\Desktop\UUVSearch`（独立项目，不在 TAOLUN 内）
- **来源**：TAOLUN 的 2026-11-23 材料匹配、2026-11-27 研究资产审查、2026-11-27 讨论
- **读法**：先读 §0 / §1 / §2，再读 §5 / §6 / §7；**先不要改代码**。
- **边界**：UUVSearch 是用户自己的独立项目，不要求支撑 TAOLUN 的方向 A；TAOLUN 不把 UUVSearch 计入 A 的证据或毕业硬门槛。本文件是“已知问题 + 改进建议”的交接，不是 TAOLUN 项目事实源。

---

## 0. 一句话结论

**UUVSearch 现在不是可投稿论文；先修评估，再加检测退化与能量约束，3 周内找“RL 何时赢/何时输”的边界；有边界再写论文，没有就停。不要把它改造成 A 的 confirm 底座。**

准确地说：

- **不用**改造成 TAOLUN 方向 A 的“搜索—确认”底座；
- **要**做一次“论文级改造”，否则当前证据不够发表；
- 这次改造是 UUVSearch 自己的事，不是 TAOLUN 主线。

---

## 1. 现状（先认清）

### 1.1 项目是什么

- 单 AUV、2D 栅格、RL 搜索仿真；Python。
- 地图 420 m × 420 m，14×14 栅格，分辨率 30 m。
- 声呐：圆形，`max_range=3` 格（90 m），衰减 0.3。
- 动作：只有 5 个航向变化 `[-90,-45,0,45,90]`；没有速度控制。
- 目标：单目标；发现即终止。
- 结果表（README）：`Lawnmower 100% > DQN v6 95% > SAC v7 94% > GreedyProb 90% > Random 88%`；RL 只在平均步数上更少。
- 证据等级：单地图、单 seed；传统算法 50 回合、RL 100 回合；无置信区间/显著性；`experiments/ablation` 只有 `.gitkeep`。

### 1.2 关键代码事实

- `envs/continuous_env.py:124`：
  ```python
  target_detected = self.target_pos_grid in fov_cells
  ```
  目标在 FOV 内就**确定发现**；没有按 Pd 采样，没有 Pfa/虚警。
- 这是 UUVSearch 与 A 的核心差距，也是它自己论文要补的“检测退化”。
- `UUV\src\core\search_info_map.py:38-41` 的 PD/PF 更新是错的：未检出时 `likelihood = PF`，应为 `1-PD`；第 45–49 行又做全局归一化，会重复计质量。**这段不要复用。**
- `AUV` 的 `src/uuv_framework/sonar/noise.py` 有三个可移植算子（声呐噪声/衰减相关）；只搬算子，不搬框架。
- `UUVRoad` 是另一代 2D 框架；**不要从它重写底座**。

### 1.3 它不是论文 Li et al. 2024 的复现

- 论文：3 AUV、SAC-QMIX、`PF=0.2` 标量、单静止目标、无独立确认动作、300 次测试无显著性。
- UUVSearch：单 AUV、DQN/SAC、无多 AUV/通信。
- 不能写成“复现 Li et al.”；只能做 related work/参数来源。

---

## 2. 三次结论，其实一致

### 2.1 2026-11-23 材料匹配（exp-review）

- 论文 Li et al. 2024：与 A **旁支**；不能当 A 证据；不建议复现。
- UUVSearch：
  - 作为 A 的**证据**：**不匹配**（缺 Pd/Pfa、虚警、confirm）。
  - 作为 A 的 **pilot 底座**：**需改造**。
  - 作为**独立小论文**：**可继续（有条件，非 Q1 主贡献）**。
  - 若复现论文：**建议放弃**。

### 2.2 2026-11-27 资产审查（research-audit）

- 8 组桌面资产：只有 UUVSearch / AUV-UUVRoad / UUV 与 A1 沾边；5 个低相关即停。
- UUVSearch 的**环境/声呐/地图/评估骨架可复用性高**；但**检测层不存在**，A1 要补 Pd 采样/虚警/confirm。
- 只移植 AUV `sonar/noise.py` 三算子；UUV 的 PD/PF 公式有错，不可移植。
- 论文 2 支撑中低；论文 3 低（需新建确认子环境）。

### 2.3 2026-11-27 讨论（总讨论）

- UUVSearch 可以单独先发，作为“试手/开题成果/A 的 learning baseline”。
- “不用改造”只对一半：**不用改造成 A 的 confirm 底座**；**要发论文仍要做论文级改造**。
- UUV/AUV 完成度不高，别当底座；拆件复用算法/实验设计即可。

### 2.4 所以“SEARCH 说不适合，资产说可以改”不矛盾

- 旧结论回答的是：**能不能当 A 的证据/按现状用？** → 不能。
- 新结论回答的是：**能不能当 A1 的底座/拆件复用？** → 能，但要改。
- 两者都同意：**不能直接用，要改**；差的是“当证据”还是“当底座”。

---

## 3. 可复用 / 不可复用

### 3.1 可复用（复制，不要依赖）

- UUVSearch：`envs/continuous_env.py`、`sonar`、地图、概率图/覆盖图骨架、baseline 脚本、评估/可视化骨架。
- AUV：`src/uuv_framework/sonar/noise.py` 三个算子；只搬算子，接口 beam→cell 要重接。
- UUV：实验设计/评估思路/可视化可参考；代码不要。
- 算法：lawnmower、greedy probability、information-gain、DQN/SAC 可以作为 baseline 重写/验证。

### 3.2 不可复用

- UUV `search_info_map.py` 的贝叶斯更新（公式错）。
- UUV/AUV 的完整框架（完成度低、接口旧）。
- UUVRoad 作为底座（不要重写）。
- UUVSearch README 的 95%/94% 当作“RL 优于传统”的证据；它现在反而说明 lawnmower 更强。

---

## 4. 论文定位：search-only，不是 A 的 confirm

### 4.1 建议 RQ

> **在检测退化（Pd/Pfa、虚警）与能量约束下，学习型搜索何时优于、何时不优于经典搜索（lawnmower / greedy / 信息增益）？给出边界与失效条件。**

- 这是 **search-only** 经验研究；**不做 confirm/三态**。
- 贡献不是“又一个 RL 搜索”，而是：
  1. 一个可复现的 search-under-imperfect-detection 基准；
  2. 学习型 vs 经典型的边界/失效条件；
  3. 对“RL 在什么条件下值得用”的实证回答。
- 如果结果主要是“lawnmower 仍然最好”，可以写成 negative result/benchmark，但要接受 venue 更低；不要硬拗成“RL 全面胜出”。

### 4.2 与 A 的边界

- UUVSearch：search-only；A 的论文 1：search-confirm。
- A 的主 baseline 仍是 lawnmower、S8、S6；UUVSearch 只是“学习型搜索 baseline”，不能替代它们。
- A 的对比 baseline 优先用行业标准/公认方法/最新相关工作；UUVSearch 只作为学习型 baseline，不作为唯一或主 baseline。
- 不要共享同一套实验/claim；可以互相引用、复用 env/sonar，但实验分开，避免 salami slicing。
- 如果 UUVSearch 先发，A 可以写“compared with the search-only RL baseline of [ours]”；但 A 的贡献不能变成“给 UUVSearch 加 confirm”。

### 4.3 开题成果 / 毕业成果

- UUVSearch 由**别人项目**推进；TAOLUN 只留交接文档，不管理它的进度；它可以和 A1 并行，但不拖 A1。
- 如果 UUVSearch **录用/在线**，可以作为开题成果/简历成果。
- 用户 2026-11-27 口径：**可以不算 12 类成果；最好 SCI，更好是学院期刊目录上的；会议也可接受；算毕业成果即可**。
- 是否算毕业 I/II 类，要看 venue 是否在学院目录/JCR 分区。**II 类第 1 条“参照学院国际学术期刊分级分类目录”可能接受 C 类非 Q2 期刊；这是解释问题，投稿前让学院/导师书面确认**，不要自己先锁死。
- **不要把它当 Q1/Q2 硬门槛**；A 的 Q1/Q2 不能丢。UUVSearch 是“试手/开题材料”，不是替代 A 的主成果。
- 如果只是**投稿/在审**，开题是否认，要看学院/导师口径；不要默认“投了就算”。

---

## 5. 最小可发表实验包

### 5.1 自变量

- 检测退化：3 档（如 Pd 0.9/0.7/0.5；Pfa 0/0.02/0.05；虚警成簇/均匀至少一档）。
- 能量预算：3 档（如 300/600/1000 步，或按路径长度/推进功率折算）。
- 地图：≥5 张，含至少 2 张 held-out（训练没见过）。
- 目标：先单目标；有余力再 1–3 目标。目标数不是第一优先级。

### 5.2 方法 / baseline

- 学习型：现有 DQN、SAC（同一 observation/action/budget；不要只挑最好的 seed）。
- 经典型：lawnmower、greedy probability、information-gain/greedy entropy、random。
- 可选上界：oracle（已知目标位置的最短路径）只作参考，不作为可部署方法。
- 所有方法同地图、同 seed 集、同预算；**paired/common random numbers**。

### 5.3 指标

- 成功率；time-to-find；总步数/路径长度；能耗（至少路径长度 proxy，最好推进功率 proxy）；覆盖率。
- 若加入 Pfa：虚警接触数、因虚警浪费的步数/能量。
- 均值 + 95% CI；per-episode CSV；失败案例表。

### 5.4 统计与可复现

- ≥5 seeds × ≥5 maps；held-out 地图；配对比较；95% CI；必要时 Wilcoxon/paired test。
- 每条结果能由一条命令重跑；配置、seed、代码 commit、原始 per-episode CSV 齐全。
- README 表必须能由仓库内 CSV 复核，不再用“自报表格”。

### 5.5 消融

- 检测模型：确定发现 vs Pd 采样 vs Pd+Pfa。
- 能量预算：松/中/紧。
- 奖励：现有 reward vs 只保留 find/coverage。
- 地图规模/传感器半径：至少一档扰动，避免只在一个 14×14 网格成立。

---

## 6. 3 周 pilot + 4–6 周论文（时间盒）

### 第 1 周：先把评估做可信

- 统一传统/RL 的回合数、地图、seed 集；重跑 README 表（5 maps × 5 seeds）。
- 修复 `experiments/ablation` 不产 CSV 的问题；输出 per-episode CSV。
- 确认现有 checkpoint 与 README 表对应；写一条“一键复现”命令。

**Gate 1**：如果 5 seeds/5 maps 下 README 的排名不稳定，先别加新模型；先把评估协议修好。

### 第 2 周：加检测退化与能量

- 实现 Pd(distance/angle) 采样 + Pfa/虚警场（先均匀，再一档成簇）；记录每次检测的 Pd/Pfa。
- 加能量预算/路径成本；确保所有方法同预算。
- 跑 3 检测档 × 3 能量档 × 5 maps × 5 seeds 的小网格；先看趋势，不急着写论文。

**Gate 2**：如果检测退化完全不让排名变化，说明这个 RQ 在这个仿真里没有信号；考虑换 RQ 或停。

### 第 3 周：边界与失败案例

- 找“RL 在哪些格点赢/输”的边界；做 failure case 分析。
- 如果有一条清晰边界或反直觉结论：写 4–6 页短稿/会议论文；否则写技术报告，停止投入。
- 不把 3 周自动延长到 2–3 个月；延长需要明确证据和用户/导师确认。

### 如果 Gate 1–3 都过：4–6 周论文

- 补全 5×5×3×3 网格、CI、held-out、失败案例、消融。
- 写作：问题→相关工作→方法/基准→实验→边界→限制。
- 目标：会议/短稿/Q2；不按 Q1 准备；先确认能否计 I/II。
- 投稿前用 `citation-management` 核对 DOI/BibTeX；图用 `scientific-visualization`。

---

## 7. 具体改动清单

### P0（不做就不能投）

1. **检测层**：`target_detected = in_fov` → 按 Pd 采样 + Pfa/虚警场；记录检测事件。
2. **能量**：步数/路径 → 能量预算或推进功率 proxy；所有方法同预算。
3. **评估**：单地图/单 seed → 5 maps × 5 seeds、CI、per-episode CSV、held-out。
4. **baseline**：lawnmower、greedy prob、info-gain、random；RL 同 obs/action/budget。
5. **指标**：成功率、time-to-find、能量、覆盖率；有 Pfa 时加虚警接触/浪费。
6. **消融**：确定发现 vs Pd vs Pd+Pfa；能量松/中/紧；地图/声呐半径扰动。
7. **文档**：README 表由 CSV 复核；一条命令复现；记录 commit/seed/config。

### P1（加分，不要先做）

- 多目标（1–3 个）；不是第一优先级。
- 动作空间从 5 航向扩到 8/连续（会改 env，谨慎）。
- 奖励整形/课程学习；先把评估和检测退化做对。
- 真实声呐数据只用于参数范围标定，不做“真实数据验证”。

---

## 8. 不要做

- 不要改造成 A 的 confirm/三态/确认成本；那是 A 的 paper 1，混在一起会 salami slicing。
- 不要复现 Li et al. 2024（3 AUV + QMIX + 通信，成本高、不是这条线）。
- 不要按 Q1 预期；先按会议/短稿/Q2 准备，且先确认能否计 I/II。
- 不要用旧 README 的 95%/94% 当“RL 优于传统”的证据。
- 不要在没有 Gate 1/Gate 2 的情况下直接跑 2–3 个月。
- 不要复制 UUV `search_info_map.py` 的贝叶斯更新；公式错。
- 不要把 UUVSearch 的结果直接当 A 的证据；它是独立项目。

---

## 9. 代码级问题清单

- `envs/continuous_env.py:124`：确定性检测；无 Pd/Pfa。
- `UUV\src\core\search_info_map.py:38-41`：未检出 `likelihood=PF`，应为 `1-PD`。
- `UUV\src\core\search_info_map.py:45-49`：逐格后验后全局归一化，重复计质量。
- `AUV\src\uuv_framework\sonar\noise.py`：可移植三算子；接口 beam→cell 要重接。
- `UUVSearch`：单地图/单 seed；`experiments/ablation` 空；README 表不可由 CSV 复核。
- `UUVSearch`：5 个离散航向、无速度；做“抵近—保持—放弃”不够，但 search-only 论文可以先不改。

---

## 10. 需要用户决定的事（不是 UUVSearch 自己能定的）

1. **开题论文口径**：徐老师说的“发个论文”是投稿、在审，还是录用？**用户 2026-11-27：先不决定，等明年再说**；不阻塞 UUVSearch 的 3 周可行性。
2. **UUVSearch 论文的定位**：用户口径：**可以不算 12 类成果；最好 SCI，更好是学院期刊目录；会议也可接受；算毕业成果即可**。可能按 II 类第 1 条“学院目录”计（C 类非 Q2 待学院确认）；**不按 Q1/Q2 硬门槛**。
3. **顺序**：UUVSearch 由**别人项目**推进，可和 A1 并行，但不拖 A1；建议 A1 2–3 周 + UUVSearch 3 周可行性；若开题要求录用，再让 UUVSearch 优先。
4. **A 能否引用未发表的 UUVSearch**：如果 UUVSearch 还没发表，A 不能把它当“已发表 baseline”；要么等它发表，要么 A 自己重实现一个 baseline。
5. **salami 边界**：UUVSearch search-only，A search-confirm；实验/claim 分开；作者/署名**和老师讨论**，用户定。
6. **时间上限**：UUVSearch 最多 3 周可行性 + 4–6 周论文；超过就停，不能拖 A1。
7. **是否把本文件复制到 UUVSearch 根目录**：方便该项目先读；TAOLUN 保留原件。
8. **是否允许 UUVSearch 复用 A1 的代码/数据**：建议只复用 env/sonar，不共享实验/结果。

---

## 11. 给 UUVSearch 项目的执行顺序

1. 先读本文件 §0/§1/§2/§8。
2. 跑现有评估：5 maps × 5 seeds，确认 README 表能否复现；输出 per-episode CSV。
3. 写 1 页计划：RQ、实验矩阵、baseline、指标、时间盒；给用户确认。
4. 只做 P0：检测退化 + 能量 + 评估；不要先改模型结构。
5. 3 周 Gate 1–3；有边界再写论文，没有就停。
6. 每次改动记录：commit、config、seed、CSV；不要覆盖旧结果。
7. 不要改 TAOLUN 的文件；需要 TAOLUN 的数据/结论，让用户转交。

---

## 12. 相关文件（TAOLUN 内）

- `协作/评审/材料匹配-20261123-多AUV区域搜索与UUVSearch.md`：2026-11-23 材料匹配（论文 + 旧实验）。
- `协作/评审/研究资产审查-20261127-八个桌面资产初筛.md`：8 组资产初筛 + 3 个深看。
- `协作/评审/研究资产审查-20261127-论文2-3映射与验证.md`：论文 2/3 装置映射。
- `协作/交接/研究资产审查-20261127-结项.md`：资产审查结项（含未完成/下一任）。
- `协作/交接/UUVSearch-改进建议-20261123.md`：第一版独立项目建议。
- `协作/交接/实验审查-2026-11-23-结项.md`：实验审查首会话结项（材料匹配来源）。

---

## 13. 变更日志

- 2026-11-27：v1.0，合并 2026-11-23 材料匹配、2026-11-27 资产审查、2026-11-27 讨论；明确“不改造成 A 底座，但要论文级改造”；列 P0/P1、3 周 Gate、用户待决定项。
