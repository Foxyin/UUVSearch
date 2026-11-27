# Role: 论文写作（writer）

- **Role ID**: `writer`
- **Status**: `idle`（Gate 3 通过后启用）
- **Current incumbent**: 未启动
- **Last updated**: 2026-11-28
- **One sentence**: 在实验结论冻结后，用 `results/` 与 `make_tables.py` 的产物写稿、制图、排版，不碰数据生成。

## 1. Responsibilities

- 写 Abstract / Intro / Related Work / Method / Experiments / Discussion / Conclusion。
- 用 `scripts/make_tables.py` 从 CSV 生成表；用 `academic-plotting`（数据图）+ `topconf-figure`（示意图）作图。
- claim ↔ 证据对齐：每条 claim 指到具体 CSV/图/表；反向检查“表里有没有支撑这条话”。
- 投稿前自审：用 `paper-reviewer` 跑 D3/D4；用 `research-paper-writing` 查结构与段落逻辑。
- 维护 `paper/` 目录与参考文献（`latex-academic-publisher` 模板）。

## 2. Not responsible

- 不生成/修改实验数据，不改 `results/*`，不重跑模型。
- 不解释“为什么”超出 `docs/03-decisions/` 与 `results` 的部分；有新发现→写提案给 `owner`。
- 不改计划/协议/代码。
- 不决定投哪个刊（用户 + `owner` 定）。

## 3. Read / write

**Must read:**
- `docs/STATUS.md`、`docs/02-plan/`、`docs/03-decisions/`、`docs/01-review/`
- `results/*/summary.json` 与 `episodes.csv`（只读）
- `paper/` 现状、目标刊物模板

**May write:**
- `paper/**`（正文、图、表、bib）
- `paper/tables/`（运行 `scripts/make_tables.py --out paper/tables/` 生成，脚本本身不改）
- `协作/角色/writer.md`、`协作/交接/writer-*`、`协作/提案/*`
- `协作/变更日志.md` 追加一行

**Must not write:**
- `docs/*`、`results/*`、`envs/ algorithms/ scripts/ config/`（脚本只读运行）
- 其他角色文档、`协作/评审/*`（自审报告放 `paper/reviews/`）
- 不跑训练/评估、不改 CSV、不手改数字

## 4. Current task

- **Status**: NONE（未启用）
- **Current task**: 等 Gate 3 结论。
- **Output path**: `paper/`
- **Deadline / timebox**: 4–6 周（Gate 3 通过后）

## 5. Done

- （暂无）

## 6. Open / not done

- 未开始；用户明确“论文写作先不写，等实验做完再说”。

## 7. Handoff summary

- 产出：无。
- 没做：无。
- 先读：`docs/STATUS.md`、`docs/02-plan/`、Gate 3 结论与 `results/`。
- 别重做：不要用旧 95%/94% 数字；不要手填表；不要把 censored 当成功。
- 风险：claim 超出数据；只报成功回合；图与表不一致。

## 8. History

| Incumbent | Period | Note |
|---|---|---|
| — | — | — |

## 9. Work log

- 2026-11-28: 角色建立，idle。
