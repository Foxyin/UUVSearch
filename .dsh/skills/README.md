# 项目级 DSH 技能部署记录

迁移依据：`C:\Users\17053\Desktop\claude-skill-to-dsh\SKILL.md`（Claude 技能 → DSH 项目级技能）。

- 部署时间：2026-11-27
- 部署位置：`<项目>\.dsh\skills\<name>\SKILL.md`（DSH 只扫 `.dsh\skills` 与 `.agents\skills`）
- 校验方式：`GET http://127.0.0.1:49687/api/dsh-skill-explorer/list?cwd=<urlencoded>`，全部 `level=project-dsh`、`modelInvocable=True`

| 技能 | 来源 | 文件数 | 说明 |
|---|---|---|---|
| `karpathy-guidelines` | 本项目 `.claude\skills\karpathy-guidelines` | 1 | 原样迁移，frontmatter 已合规，零修补 |
| `experiment-design` | `skills_manager\download\night_owl_research_agent\skills\experiment-design` | 1 | claim→证据→实验顺序、消融矩阵、算力预算 |
| `academic-plotting` | `skills_manager\download\awesome-ai-research-writing\AI-Research-SKILLs-main\20-ml-paper-writing\academic-plotting` | 4 | 出版级配图（matplotlib/seaborn 选型 + 架构图） |
| `latex-academic-publisher` | `skills_manager\download\latex-academic-publisher` | 65 | Elsevier/IEEE/MDPI/Springer 模板、latexmk、.bib |
| `paper-reviewer` | `C:\Users\17053\Desktop\paper review\.claude\skills\paper-reviewer` | 4 | 投稿前自审 D1–D4，中英双语报告 |

## 去重说明

- `academic-plotting` 在 `papersearch\.claude` 与 `download\` 中逐字节相同，只装一份，取自 download。
- `ml-paper-writing` 两边各 51 文件为同一套，本项目未装（ML 会议向，且与 `latex-academic-publisher` 职能重叠）。
- `review-paper`（download\AI-research-feedback）frontmatter 不可解析（`argument-hint: [optional: JOURNAL] ...` 未加引号），未安装。

## 未装（有意）

`ml-paper-writing`、`nature-writing`、`nature-figure`、`nature-citation`、`humanizer`、`venue-templates`、`scientific-writing`、`stable-baselines3`、`pufferlib`、`docx/xlsx/pptx/pdf`（DSH 自带 `office-*`）。
