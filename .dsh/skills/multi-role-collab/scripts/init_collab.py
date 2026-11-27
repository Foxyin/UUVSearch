#!/usr/bin/env python
"""Create a minimal multi-role collaboration skeleton in a project.

Default is dry-run. Pass --apply to write.

The script refuses to overwrite an existing ``协作/`` directory. It creates
templates and empty indexes, not project facts.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

SKILL_ROOT = Path(__file__).resolve().parents[1]
REFS = SKILL_ROOT / "references"


def read_ref(name: str) -> str:
    path = REFS / name
    if not path.exists():
        raise SystemExit(f"missing template: {path}")
    return path.read_text(encoding="utf-8")


def build_files(project: Path) -> dict[Path, str]:
    root = project / "协作"
    files: dict[Path, str] = {}

    rules = """# 协作规则

> 本文件是协作纪律，不是项目事实源。项目事实以项目入口/当前状态/个人信息/方向文档为准。

## 0. 最短版

1. 角色文档只记职责、工作、交接；不是事实源。
2. 一个文件一个写者；不是自己的文件写 `协作/提案/`。
3. 角色先做任务分诊：不属于本角色，5 行说明 + 建议角色，不写文件。
4. 首轮不落盘；任务不清先问 1–3 个问题。
5. 一次只开一个模式：discuss / review / audit / handoff。
6. 评审要标效力：正式 / provisional / 参考。
7. 角色可跨对话接任，角色 ID 不变。
8. 先收口再停；不自行宣布项目结束。
"""

    registry = """# 角色注册表

> 活跃角色 ≤3。角色 ID 固定；接任不新建 ID。

| 角色 ID | 名称 | 状态 | 当前接任 | 职责 | 角色文档 |
|---|---|---|---|---|---|
| `owner` | 主持人 | active | {{SESSION}} | 项目事实、决定、收口、注册表/评审索引 | `协作/角色/owner.md` |

## 规则

- 活跃角色 ≤3；不为每个小任务新建角色。
- 新增角色：复制 `协作/角色/_模板.md`，在角色文档写职责/边界，再在本表加一行。
- 接任者在角色文档“历任”加一行；不新建角色 ID。
- 本表只登记角色，不登记任务；任务写角色文档“当前任务”。
"""

    usage = """# 使用模板

## 新对话怎么开

1. 复制 `协作/启动提示词.md` 中对应角色段。
2. 让新会话先读 `项目说明` → `当前状态` → `角色注册表` → 自己的角色文档。
3. 第一轮只复述 6 行，不写文件。

## 一次只开一个模式

- `discuss`：讨论，输出 `协作/讨论/`。
- `review`：审查，输出 `协作/评审/`。
- `audit`：资产盘点，输出 `协作/评审/asset-review-*`。
- `handoff`：交接/对外建议，输出 `协作/交接/`。

换模式时：先写 5 行过渡（上一轮结论/这轮换什么/为什么不混/新文件/旧文件不动），再新建文件。

## 收口

角色结束/换模型前：更新角色文档状态 + 交接摘要 + `协作/交接/<role>-YYYYMMDD.md` + 变更日志一行；然后停。不要自行宣布项目结束。
"""

    readme_discuss = """# 讨论

讨论 memo，不是项目事实。命名：`<role>-YYYYMMDD-主题.md`。每条 idea 标：基于什么/与主线关系/可检验点/风险。
"""

    readme_review = """# 评审

评审文件，不是决定。命名：`review-` / `fit-review-` / `direction-review-` / `asset-review-` / `challenge-` + 日期 + 主题。
文件头 5 行：对象/任务/角色/是否借用/效力。
"""

    readme_proposal = """# 提案

不是自己的文件，先写提案；owner 接受后再改。命名：`<主题>-YYYYMMDD.md`。
"""

    readme_handoff = """# 交接

角色/项目交接快照。命名：`<role>-YYYYMMDD.md` 或 `<project>-建议-YYYYMMDD.md`。
不替代项目事实；下一任先读项目当前状态 + 本文件。
"""

    files[root / "协作规则.md"] = rules
    files[root / "角色注册表.md"] = registry
    files[root / "使用模板.md"] = usage
    files[root / "启动提示词.md"] = read_ref("startup-prompts.md")
    files[root / "变更日志.md"] = read_ref("change-log-template.md")
    owner_doc = """# Role: owner（主持人）

- **Role ID**：`owner`
- **Status**：`active`
- **Current incumbent**：{{SESSION}}
- **One sentence**：维护项目事实、决定与收口；不替用户拍板。

## 1. Responsibilities

- 维护项目入口/当前状态/个人信息/方向文档。
- 维护 `协作/角色注册表.md`、评审索引、变更日志。
- 接收提案，决定是否改核心文件。
- 角色结束时代做收口：注册表、评审索引、当前状态、变更日志。

## 2. Not responsible

- 不代替 reviewer 审被指定对象；不代替 auditor 做资产盘点；不代替 red-team 做发散。
- 不把角色文档当事实源。

## 3. Read / write

**Must read:** 项目入口、当前状态、个人信息、方向文档、角色注册表、本文件。

**May write:** 项目事实文档（经用户确认）、本文件、注册表、评审索引、变更日志、交接。

**Must not write:** 别人角色文档；评审/讨论正文（除非该角色授权）。

## 4. Current task

- 状态：active
- 当前任务：{{TASK}}

## 5. Handoff summary

- 本轮产出：
- 未做：
- 下一任先读：
- 不要重做：

## 6. Work log

- {{YYYY-MM-DD}}: 初始化。
"""
    files[root / "角色" / "owner.md"] = owner_doc
    files[root / "角色" / "_模板.md"] = read_ref("role-template.md")
    files[root / "评审" / "_模板.md"] = read_ref("review-template.md")
    files[root / "交接" / "_模板.md"] = read_ref("handoff-template.md")
    files[root / "讨论" / "README.md"] = readme_discuss
    files[root / "评审" / "README.md"] = readme_review
    files[root / "提案" / "README.md"] = readme_proposal
    files[root / "交接" / "README.md"] = readme_handoff

    return files


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", default=".", help="target project root")
    parser.add_argument("--apply", action="store_true", help="write files")
    args = parser.parse_args()

    project = Path(args.project).expanduser().resolve()
    if not project.exists() or not project.is_dir():
        print(f"not a directory: {project}")
        return 2

    root = project / "协作"
    if root.exists():
        print(f"refusing: {root} already exists")
        return 3

    files = build_files(project)
    print(f"project: {project}")
    print(f"mode: {'apply' if args.apply else 'dry-run'}")
    for path in sorted(files):
        print(f"  + {path.relative_to(project)}")

    if not args.apply:
        print("\nDry-run only. Re-run with --apply to write.")
        return 0

    for path, text in files.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8", newline="\n")
    print(f"\nCreated {len(files)} files under {root}")
    print("Next: fill project facts/current state; do not paste them into role docs.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
