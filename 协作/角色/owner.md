# Role: 总讨论 / 项目管理（owner）

- **Role ID**: `owner`
- **Status**: `active`
- **Current incumbent**: 主会话（DSH，2026-11-28 起）
- **Last updated**: 2026-11-28
- **One sentence**: 维护唯一事实源与计划、分派任务、在用户与各角色之间拍板，并对用户汇报。

## 1. Responsibilities

- 维护 `docs/STATUS.md`（当前状态 / 下一步 / 未决问题）。
- 维护 `docs/02-plan/`（活文档，升版本号）、`docs/03-decisions/`（用户决策）、`docs/01-review/`（问题清单）。
- 分派任务：给 `experimenter` 写清 tag / 分支 / 配置 / seed / 预算；给 `reviewer` 写清对象路径与问题。
- 收 `experimenter` 的产物与 `reviewer` 的正式评审，决定：通过 / 修 / 停，并记录理由。
- 维护 `协作/角色注册表.md`、`协作/变更日志.md`、评审索引。
- 对用户汇报：结论、证据、剩余风险、需要用户决定的事项（一次最多 5 条）。

## 2. Not responsible

- 不亲自写环境/算法代码（在 `feat/gate1-protocol` 上由 `experimenter` 写）；紧急小修可行但要在变更日志记。
- 不自己给自己出评审结论（需要门时另起 `reviewer`）。
- 不写论文正文（`writer`），不跑正式实验矩阵（`experimenter`）。
- 不替用户做不可逆/外部可见的决定（投稿、删数据、公开仓库）。

## 3. Read / write

**Must read:**
- `README.md`、`docs/STATUS.md`
- `docs/02-plan/plan-2026-11-28.md`、`docs/03-decisions/2026-11-28-decisions.md`
- `docs/01-review/2026-11-28-issues-checklist.md`
- `协作/角色注册表.md`、本角色文档 + 最近交接

**May write:**
- `docs/STATUS.md`、`docs/02-plan/*`、`docs/03-decisions/*`、`docs/01-review/*`
- `协作/协作规则.md`、`协作/角色注册表.md`、`协作/变更日志.md`、`协作/启动提示词.md`
- `协作/提案/*`、`协作/交接/owner-*`
- 根 `README.md`、`CLAUDE.md`（项目说明类）
- `协作/记录/owner-*`（每轮任务记录，见规则 §5.1）
- `.dsh/skills/**`（技能增删，记录到 `.dsh/skills/README.md`）

**Must not write:**
- `协作/角色/<其他角色>.md`
- `协作/评审/*`（评审由 `reviewer` 写；`owner` 只写“采纳/拒绝”结论到 decisions）
- `results/*`、`paper/*`、`config/suites/*`
- `docs/04-maps/*`（生成物归 `experimenter`；`owner` 只写文字说明）
- `docs/00-handoff/*`（只读）
- 不得删除或覆盖 `results/`、`experiments/`、`docs/` 的旧内容；清理须用户批准并记 decisions

## 4. Current task

- **Status**: WAITING（等用户开工指令）
- **Current task**: 用户回来后确认是否开 `feat/gate1-protocol` 做 Phase 0（地图工厂 M1–M5、检测层、odds-Bayes、能量、info_gain / online_lawnmower、run_suite / make_tables），**先不训练**。
- **Output path**: 分支 `feat/gate1-protocol` + `results/gate1/`
- **Deadline / timebox**: Phase 0 目标 1–1.5 天；Gate 1 通过后再训练。

## 5. Done

- 2026-11-28: 项目重建（README/CLAUDE/STATUS、docs 重组、计划 v3.2、问题清单 44 条、决策记录）→ `83a4be0`
- 2026-11-28: 安装并配置 `multi-role-collab` 协作技能，建立 `协作/` 与四角色 → 本次提交
- 2026-11-28: 旧结论撤回（DQN 95% / SAC 94% 不再作为“RL 更优”证据）

## 6. Open / not done

- Phase 0 未开工；`feat/gate1-protocol` 未创建。
- Gate 1 未跑；Gate 2/3 未排期。
- 论文未开始（按用户要求“等实验做完再说”）。
- 待用户确认：是否开工、`reviewer` 是否有“门”的否决权、`experimenter` 的自主预算上限。

## 7. Handoff summary

> 接任者先读这里。

- 本轮产出：计划 v3.2 闭环、问题清单、文档重组、四角色协作骨架。
- 没做：一行 Phase 0 代码都没写；没有新实验数字。
- 先读：`docs/STATUS.md` → `docs/02-plan/plan-2026-11-28.md` → `docs/03-decisions/` → `docs/01-review/`。
- 别重做：旧 95%/94% 的对比；`wip/fair-baselines` 不整体合并（只摘 A* 与 benchmark 思路）。
- 已知风险：成功率饱和（主指标必须是 KM TTF）；单图单 seed 结论不可用；CPU-only 训练预算。

## 8. History

| Incumbent | Period | Note |
|---|---|---|
| 主会话（DSH） | 2026-11-27 – | 初建 |

## 9. Work log

- 2026-11-28: 建立协作骨架与四角色；技能 `multi-role-collab` 入库。
- 2026-11-28: 计划 v3.2（48-run 矩阵、KM/log-rank、free-cell 能量、online_lawnmower）。
