# 工作分解（WBS）— 从 Phase 0 到投稿

- 版本：1.0（2026-11-28）
- 归属：`owner` 维护；状态同步 `docs/STATUS.md`
- 原则：每个工作项有**唯一产出物、唯一负责角色、可验收**；论文数字只能来自 `results/` 的 CSV。

## 0. 总览

| 阶段 | 目标 | 日历 | 门 |
|---|---|---|---|
| 已完成 | 审计、问题清单、计划 v3.2、协作机制 | — | — |
| P0 | 协议与基础设施（不训练） | 1–1.5 天 | Phase 0 验收 |
| G1 | 评估可信（经典方法） | 0.5 天 | Gate 1 |
| G2 | 主矩阵 + 训练/零样本评估 | 1 天机时 + 1 天分析 | Gate 2 |
| G3 | 边界、失败案例、消融 | 5–7 天 | Gate 3 |
| W | 论文与投稿 | 4–6 周 | 投稿 |
| E | 工程与运维 | 全程 | — |

关键路径：**P0 → G1 → G2 → G3 → W**。任何 Gate 不过，不进入下一阶段（见计划 §6）。

## 1. P0 协议与基础设施（`experimenter`，1–1.5 天）

| ID | 工作 | 产出 | 验收 | 依赖 |
|---|---|---|---|---|
| T-P0-01 | 开分支与目录骨架 | `feat/gate1-protocol`、`config/suites/`、`results/` 布局 | 分支可提交，脚本可跑 | — |
| T-P0-02 | 地图工厂 M1–M5 | `envs/maps/{random,structured,maze}.py`、`config/maps.yaml`、`docs/04-maps/*.png/.txt` | 5 图固定 seed 可复现；自由格数与连通性检查 | — |
| T-P0-03 | 检测层 | `envs/detection.py`、`continuous_env.py` 接线、`detection:` 配置 | deterministic 无虚警；sampled 的 Pd/Pfa 与配置一致；`events.csv` 行数可对账 | P0-01 |
| T-P0-04 | 信念更新 | `envs/info_map.py` odds 形式 + 精确更新 + coverage 模式 | `Σp=1`；确定性下 beliefs ≡ 1−coverage（自检） | P0-03 |
| T-P0-05 | 能量与预算 | 环境能量累计、`budget`、`max_steps=ceil(2×budget)`、censored 标记 | 能量与动作/碰撞可对账；超预算正确截断 | P0-03 |
| T-P0-06 | 观测配置 | `obs.mode: belief\|coverage`、488 维不变 | C0c/C3c 切换只改 probability patch | P0-04 |
| T-P0-07 | 基线补齐 | `online_lawnmower`、`info_gain` | 两者只用合法信息；回归测试通过 | P0-02 |
| T-P0-08 | 评估协议 | KM 中位 TTF、log-rank、Wilson、配对 CRN、`episodes.csv/summary.json/meta.json` | 同一 seed 重跑结果逐位一致 | P0-01 |
| T-P0-09 | 统一入口 | `scripts/run_suite.py --suite gate1`、`scripts/make_tables.py` | 一条命令跑完；表可从 CSV 重建 | P0-08 |
| T-P0-10 | 单测与回归 | `tests/`、旧 smoke | `pytest` 全绿；旧 5 图 smoke 不回归 | P0-02…09 |
| T-P0-11 | Phase 0 记录 | `协作/记录/experimenter-*.md` | 七项齐全 | 全部 |

**Phase 0 验收**：一条命令产出 `results/gate1/`；`beliefs ≡ 1−coverage` 自检通过；C0 vs C0c 差异在噪声内。

## 2. G1 评估可信（`experimenter` 跑，`owner` 判，0.5 天）

| ID | 工作 | 产出 | 验收 |
|---|---|---|---|
| T-G1-01 | 6 经典方法 × 5 图 × 25 ep | `results/gate1/` | 无缺失 run；CSV 完整 |
| T-G1-02 | 排名稳定性 | 表 + 每图 oracle_coverage 比值 | 每图 `oracle_coverage ≤ 1.3 × oracle_TTF` |
| T-G1-03 | Gate 1 判定 | `docs/STATUS.md` 一行 + decisions | 过 = 进 G2；不过 = 修协议（≤1 天）再判 |

## 3. G2 主矩阵（`experimenter` 跑，1 天机时 + 1 天分析）

| ID | 工作 | 产出 | 验收 |
|---|---|---|---|
| T-G2-01 | 训练 48 run（C0/C0c/C1/C2/C3/C3c ×6 seed + C4 12） | `results/gate2/<cond>_s<seed>/` | 每 run 200k 步；seed 全报；best/final 双 checkpoint |
| T-G2-02 | 零样本评估（5 图 × 50 ep × 7 方法） | `results/gate2/eval/` | 评估与训练分离；固定评估 seed 集 |
| T-G2-03 | 统计 | 配对表 + paired Wilcoxon + Holm + bootstrap CI | 中位数差 CI 可复算 |
| T-G2-04 | Gate 2 判定 | decisions 一段 | 有边界 = 进 G3；无边界 = 转 benchmark/negative（决策点） |

## 4. G3 边界与失败分析（`experimenter` + `owner`，5–7 天）

| ID | 工作 | 产出 | 验收 |
|---|---|---|---|
| T-G3-01 | 边界热图 | Pd×Pfa×能量 的 RL−经典 差值热图 | 每格 ≥3 seed |
| T-G3-02 | 失败案例 3–5 个 | 回放图 + 机制解释 | 每个案例能指出失败原因（碰撞/虚警误导/探索不足） |
| T-G3-03 | 消融 | 奖励、obs、地图规模、声呐半径、Pd 曲线、成簇 Pfa | 每条消融 ≤6 run |
| T-G3-04 | Gate 3 判定 | decisions + STATUS | 有清晰边界 → 短稿；否则技术报告并停 |

## 5. 论文（`writer`，4–6 周）

| ID | 工作 | 产出 | 验收 |
|---|---|---|---|
| T-W-01 | 文献与定位 | related work 8–12 篇 + delta 陈述 | 每篇一句话差异；不与 TAOLUN/A 项目混用 |
| T-W-02 | 图表 | 框架图（topconf-figure）、地图、TTF 曲线、热图、主表 | 图可追溯到 sources/ 或 CSV |
| T-W-03 | 初稿 | IMRaD（Abstract/Intro/Related/Method/Exp/Conclusion） | 每个 claim 对应 results 文件 |
| T-W-04 | 内部评审 | `reviewer` D4 报告 | 必改项清零 |
| T-W-05 | 投稿包 | LaTeX（latex-academic-publisher）、cover letter、repro 说明 | 本地 latexmk 编译通过 |
| T-W-06 | 投稿 | 系统提交号 | — |

## 6. 工程与运维（`owner`，全程）

| ID | 工作 | 产出 | 验收 |
|---|---|---|---|
| T-E-01 | git/分支/发布 | `main` 干净、功能分支可追溯 | 每次合并有记录 |
| T-E-02 | 文档同步 | STATUS/README/CLAUDE/问题清单 | 事实源一致 |
| T-E-03 | 复现包 | `requirements-lock.txt`、一页复现说明 | 新机器按说明能跑 Gate 1 |
| T-E-04 | 数据/代码归档 | tag + 归档决策（Zenodo?） | 投稿前定 |
| T-E-05 | 机制迭代 | 角色记录 → 规则修订 | 每 2 周一次 |

## 7. 风险与备选

| 风险 | 触发 | 备选 |
|---|---|---|
| Gate 1 排名不稳 | CI 重叠、图间翻转 | 扩 seed / 改协议，1 天内重判 |
| Gate 2 无边界 | 条件间差异 < 噪声 | 转 benchmark/negative result 短稿（2 周） |
| 训练太慢 | 48 run > 2 天 | 减至 3 seed 主矩阵，其余补零样本 |
| 检测层实现偏差 | beliefs ≠ 1−coverage | 先修实现，不进 G1 |
| 写作与实验抢人 | 同一会话切角色 | 严格按记录/交接切换，不复用上下文 |

## 8. 现在需要做的（等审查收口后）

1. `owner`：把审查必改项并入计划 v3.3，更新 STATUS。
2. 开 `experimenter`：T-P0-01 → T-P0-11（Gate 1 及以内自主，不用逐项报批）。
3. 两个权限问题已定（2026-11-28）：`reviewer` 无否决权、必改项未修完不能过；`experimenter` Gate 2 起训练前报批。
