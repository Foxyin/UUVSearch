# Minimal worked example

Project: a PhD student's research-direction discussion workspace. Facts live in `项目说明.md`, `当前状态.md`, and `方向.md`; there is no second “current state” per role.

## 1. Roles

| ID | Status | Job |
|---|---|---|
| `owner` | active | keep facts, decisions, closeout |
| `reviewer` | idle | review experiment/plan design |
| `red-team` | idle | challenge and alternatives |

## 2. Task triage catches a mismatch

User gives the `reviewer` a paper + an old experiment and asks “does this fit our direction?”

`reviewer` replies with five lines:

```text
我是 reviewer（审查者）。
你这轮要的是“一篇文献 + 一个旧实验的方向匹配”，不是实验设计审查。
这不属于我的正式职责；应由 auditor（资产与材料盘点）或 red-team（方向审查）接。
我可以只读，帮你看“实验设计是否支持 claim”，但不做方向匹配。
建议：先让 auditor 做材料匹配；需要审实验设计再叫我。
```

No file is written. The owner routes it to `auditor`.

## 3. Auditor produces a review, not a verdict

`auditor` writes `协作/评审/asset-review-20260101-两个资产.md`:

```text
对象：paper X + old experiment Y
任务：材料匹配
角色：auditor
是否借用：否
效力：参考

结论：有条件通过（作为独立小论文）；作为主线证据不匹配。
证据：Y 的检测是确定性的（env.py:124），没有 Pd/Pfa；README 的 baseline 表只有单 seed。
必须修改：加 Pd/Pfa、5 maps × 5 seeds、强 baseline、CI。
```

The owner reads it, decides, and records the decision in `当前状态.md`. The review itself is not a decision.

## 4. Reviewer reviews the plan, not the paper

Later the user asks `reviewer` to review the new 1-page plan. `reviewer` writes `协作/评审/review-20260105-1页纸.md` with a five-line header and a verdict. It does **not** edit the plan.

## 5. Red-team challenges, then hands off

`red-team` writes a discussion memo in `协作/讨论/red-team-20260106-替代解释.md`. One idea is relevant to the main line; it writes a 3-line bridge:

```text
桥 1：如果把“确认成本”换成“确认延迟”，主线的可证伪 claim 仍成立吗？
桥 2：需要新增哪个实验格点？
桥 3：如果不需要，标为独立项目外溢，不进主线。
```

The owner decides whether to accept the bridge. The red-team does not edit the plan.

## 6. Closeout

Before the conversation ends, `red-team` updates its role doc to `idle`, writes `协作/交接/red-team-20260106.md`, appends one line to `协作/变更日志.md`, and says:

> 本轮产出：讨论 memo + 3 条桥；未做：实验；下一任先读 memo §3 和角色文档 §6；不要重做讨论。

It does **not** say “the project is finished”.
