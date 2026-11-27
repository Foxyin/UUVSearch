---
name: multi-role-collab
description: Set up and run multi-role, multi-conversation collaboration for a research or engineering project without letting role documents become a second source of truth. Use when a project needs role docs, task triage, review and handoff boundaries, single-writer rules, stable role IDs, or when several AI conversations must share one project state.
whenToUse: 当项目需要多角色/多对话协作、角色文档、任务分诊、评审/交接边界、单写者、角色接任或换模型交接时使用；单个一次性任务不需要。
---

# Multi-Role Collaboration

A lightweight discipline for projects where several conversations or agents work on one shared project state. It is **not** an agent framework and does not create agents. It defines how roles read, write, review, hand off, and stop.

> New here? `QUICKSTART.md` covers install → `init_collab.py` → first role session → daily loop in one page.

## 0. One-sentence rule

**Role documents record who did what; they are not the project's source of truth.**

Project facts must live in a small set of owner-maintained files (for example: project brief, current state, personal constraints, direction memo). Every role reads those files; no role gets its own “current state”.

## 1. When to use

Use this skill when:

- more than one conversation/agent works on the same project;
- you need roles such as owner/moderator, reviewer, auditor, red-team;
- roles must hand off when a conversation is full or the model changes;
- you want review and discussion outputs to be auditable;
- you want to prevent a role from silently editing project facts.

Do **not** use it for a one-shot task, a single conversation, or a simple code change. It adds overhead and is not a substitute for project management.

## 2. Non-goals

- It does not create agents or schedule them.
- It does not enforce permissions. A skill is instructions; real enforcement needs file permissions, separate workspaces, or version control.
- It does not replace the project's own plan, experiment log, or literature map.
- It does not make a role's opinion a decision. The user/owner decides.

## 3. Minimal layout

Create at the project root:

```text
协作/
  协作规则.md          # how roles work; stable
  角色注册表.md        # role IDs, status, current incumbent
  变更日志.md          # append-only index of changes
  启动提示词.md        # copy-paste prompts for each role
  使用模板.md          # how to open/switch/close a role session
  角色/
    <role>.md          # one file per role; role-owned
  讨论/                # discussion memos; not project truth
  评审/                # reviews; not project truth
  提案/                # proposals for files the role does not own
  交接/                # handoff snapshots
```

Do not create a second `当前状态.md` per role. If a role needs a snapshot, write `协作/交接/<role>-YYYYMMDD.md` and point to the project's canonical state file.

## 4. Roles

Keep the set small. **Active roles ≤ 3** by default; a role is a hat, not a person.

| Role ID | Generic alias (optional, rename freely) | Owns | Must not |
|---|---|---|---|
| `owner` | 主持人（moderator） | project facts, decisions, closeout, role registry, review index | let a role doc override facts |
| `reviewer` | 审查者 | review of one specified object (plan, experiment, document, claim) | edit the object; decide the project |
| `auditor` | 资产盘点者 | inventory and reuse/archive assessment | move/delete assets without approval |
| `red-team` | 挑战者（外部视角） | challenge, alternatives, external advice | own the main line; edit facts |

Role IDs are stable across conversations. A successor (for example “主持人2”) is the same role, not a new role; add a row to the role's history table.

A role may **borrow** another role's perspective for one task. Record it in the role doc's work log. If the same borrow repeats, propose a permanent role change to the owner; do not silently change the registry.

## 5. Task triage (before any work)

Every role starts by classifying the request:

1. **Belongs to this role** → do it, within its write boundary.
2. **Does not belong** → reply with five lines only:
   - who I am;
   - what this request is;
   - why it is not mine;
   - which role should take it;
   - whether I can assist read-only.
   Do **not** write files or give a verdict.
3. **Unclear** → restate the request and ask 1–3 questions. Do not write.

Typical mismatch: giving a “review this experiment” prompt to a role that only reviews a specific memo, or asking an auditor to judge direction fit. Triage first; do not force the template.

## 6. Modes

One session opens **one mode**. Do not mix modes in one output.

### 6.1 `discuss`

- Purpose: generate alternatives, interpretations, bridges.
- Output: `协作/讨论/<role>-YYYYMMDD-主题.md`.
- Every idea must state: basis (fact/assumption), relation to the main line, testable point, risk.
- It is a discussion memo, not a decision and not project truth.
- If the discussion is about an external project, mark it and write a “bridge” only if it is meant to flow back into the main line.

### 6.2 `review`

- Purpose: audit a document, experiment design, or claim.
- Output: `协作/评审/<type>-YYYYMMDD-主题.md`.
- Use evidence (file:line, data, citation). Give a verdict and required changes.
- Do not edit the object under review.
- A review is advice; the owner decides.

### 6.3 `audit`

- Purpose: inventory assets (code, data, papers, experiments), judge reuse and gaps.
- Output: `协作/评审/asset-review-YYYYMMDD-主题.md`.
- Use a fast triage first: README/tree/one entry/one result table; stop low-relevance assets.
- Do not run code or move/delete without explicit approval.

### 6.4 `handoff`

- Purpose: give another project or a successor a self-contained brief.
- Output: `协作/交接/<project>-建议-YYYYMMDD.md` or `协作/交接/<role>-YYYYMMDD.md`.
- Include: what was done, what was not, what to read, what not to redo, changed files, fact version.
- External advice is not project truth.

## 7. Single writer

**One file, one writer.** Default ownership:

| File | Writer |
|---|---|
| project facts / current state / brief | `owner` |
| role registry / review index / change log | `owner` |
| role document | that role |
| review / discussion / handoff | the role that produced it |
| proposal | any role (in `协作/提案/`) |

If you do not own a file: write a proposal in `协作/提案/`, do not edit the file. The owner accepts/rejects and records it.

## 8. Review naming and validity

Name reviews by type, not by mood:

- `review-YYYYMMDD-主题.md` — experiment design.
- `fit-review-YYYYMMDD-主题.md` — paper/asset fit.
- `direction-review-YYYYMMDD-主题.md` — direction judgment.
- `asset-review-YYYYMMDD-主题.md` — asset inventory.
- `challenge-YYYYMMDD-主题.md` — challenge/review from red-team.

Each review starts with five lines:

```text
对象：
任务：
角色：
是否借用：
效力：正式 / provisional / 参考
```

- **正式**: the review was commissioned for this exact object and the role was correct.
- **provisional**: the object/task was mismatched, or the review is a first pass; keep it, but do not treat it as a verdict.
- **参考**: informal advice; not a gate.

A provisional review can still contain real findings. Preserve the evidence, but do not let it decide the project.

## 9. Startup

A new role session reads, in order:

1. project entry / brief;
2. current state;
3. personal constraints or scope;
4. the active direction memo (if any);
5. role registry + its own role doc + the latest handoff.

Then it replies with six lines:

```text
我是谁：
我这轮的任务：
我可以写：
我不能写：
我读到的当前状态：
我建议先做：
```

First session or unclear task: **do not write files**. Read, restate, ask 1–3 questions. Write only after the user confirms the task and output path.

## 10. Closeout and handoff

Before a session stops, or before changing model/conversation:

1. finish the current mode's output;
2. update the role doc: status (`active` / `idle` / `retired`), current incumbent, handoff summary;
3. write `协作/交接/<role>-YYYYMMDD.md` (or a handoff section in the role doc);
4. append one line to `协作/变更日志.md`;
5. tell the user what was produced and what remains.

Do not declare the **project** finished. Only the owner/user can do that. If the conversation is being deleted, say what is already on disk and what the next session should read.

## 11. Anti-patterns

- Role doc becomes a second source of truth.
- A role edits a file it does not own “just this once”.
- A review of the wrong object is treated as a verdict.
- The same role does discuss + review + handoff in one output.
- Too many roles (more than 3 active) with overlapping scope.
- A successor creates a new role ID instead of continuing the old one.
- The review index / registry is left stale after a role ends.
- A role declares the project done.

## 12. Init script

`scripts/init_collab.py` creates the skeleton in a target project. It defaults to dry-run; pass `--apply` to write. It refuses to overwrite an existing `协作/` directory.

```powershell
python scripts\init_collab.py --project "C:\path\to\project"
python scripts\init_collab.py --project "C:\path\to\project" --apply
```

It creates empty templates, not project facts. Fill the project brief/current state yourself.

## 13. References

- `references/role-template.md` — role document template.
- `references/startup-prompts.md` — copy-paste prompts for owner/reviewer/auditor/red-team.
- `references/review-template.md` — review file template.
- `references/handoff-template.md` — handoff template.
- `references/change-log-template.md` — append-only change log.
- `references/examples.md` — one minimal worked example.

Keep this skill generic. Do not paste a specific project's facts, names, or roadmap into it; put those in the project's own canonical files.
