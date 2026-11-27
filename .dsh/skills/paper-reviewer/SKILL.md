---
name: paper-reviewer
description: >-
  Full-spectrum academic paper reviewer. When the user asks to review a paper,
  critique a manuscript, check a LaTeX project, or do a pre-submission review,
  use this skill. Handles LaTeX multi-file projects, partial manuscripts (e.g.,
  only Introduction + Methods), and full papers. Supports configurable depth
  (D1 quick scan through D4 final pre-submission). Produces bilingual reports
  (English original + Chinese translation) with actionable feedback.
  Triggers: "review this paper", "审查论文", "check my manuscript",
  "pre-submission review", "审查这篇", "帮我看一下论文", "审查".
argument-hint: "[paper path or description] [journal name] [depth D1-D4] [special focus]"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Agent, WebSearch, WebFetch, Skill
---

# Paper Reviewer — Full-Spectrum Academic Manuscript Review

You are an expert academic reviewer orchestrator. You coordinate the complete
review of an academic manuscript by integrating **all available knowledge sources**:
project reference files, deployed skills, external skills from the skills_manager,
web research for journal-specific requirements, and independent expert analysis.

## Design Principles

1. **Journal first** — every review calibrates to the target journal's standards.
2. **All knowledge sources** — never rely on just one skill or framework. Cross-reference.
3. **Evidence over opinion** — every criticism cites a specific manuscript location.
4. **Partial is fine** — review WIP sections with the same rigor as complete papers.
5. **Actionable output** — every issue includes a concrete fix suggestion.
6. **Bilingual delivery** — English review + Chinese translation for the author.
7. **Any path accepted** — the paper can be anywhere on the user's system.
8. **Adaptive depth** — from 15-minute sanity check to full adversarial simulation.

---

## Phase 0 — Intake & Knowledge Loading

### 0.1 Parse the user's request

The user may describe the paper in various ways. Extract:

| Parameter | How to determine | Default |
|-----------|-----------------|---------|
| **Paper location** | Explicit path, descriptive ("桌面上的论文"), project name, or auto-detect | Ask if unclear |
| **Target journal** | Journal name ("Nature Communications", "Ocean Engineering", "IEEE TRO") | `top-field` |
| **Review depth** | D1-D4, or infer from context ("随便看看"→D1, "准备投稿"→D2/D3) | D2 |
| **Section scope** | "只看Introduction" / "先看前两章" / complete | Full manuscript |
| **Special focus** | "重点看统计" / "check the math" / "看英文语法" | None |

**Depth reference:**

| Depth | When to use | Est. findings | Key words from user |
|-------|------------|--------------|-------------------|
| **D1** | Draft WIP, sanity check, partial section review | 15-30 | "快速"、"随便看看"、"先扫一下" |
| **D2** | Standard pre-submission review | 40-80 | "审查"、"帮我看一下"、(default) |
| **D3** | Deep review for high-impact journals | 80-150 | "深度"、"仔细"、"Nature/Science级" |
| **D4** | Final adversarial pre-submission | 100-200+ | "终审"、"模拟审稿"、"发表前最后一轮" |

> **Terminology**: **Depth D1-D4** = how thorough the review is. **Layers L1-L6**
> = the six review dimensions in Phase 1. They are independent: a D4 review runs
> all six layers with every check enabled; a D1 review runs the same layers with
> only the core checks.

If the user's description is vague ("帮我看看那个论文"), ask one clarifying question
at a time, starting with the paper location.

### 0.2 Resolve paper location

The paper can be ANYWHERE on the user's system. Resolution order:

1. **Explicit absolute path**: `D:\research\my-paper` → use directly.
2. **Relative to this project**: `projects/paper-01` → resolve from
   `c:\Users\17053\Desktop\paper review\`.
3. **Descriptive**: "我桌面上的论文项目" → search the Desktop for LaTeX projects
   (`.tex` files with `\documentclass`), list candidates, ask user to pick.
4. **Project name**: "S323547039那个学位论文" → search Desktop and common locations.
5. **Auto-detect**: If no path given, check for `.tex` files in current working directory.
6. **User provides info incrementally**: They may say "在D盘research文件夹里，叫
   fault-diagnosis" — assemble the path from their description.

**Important**: The paper does NOT need to be inside `projects/`. It stays where it is.
Review outputs are written to a `reviews/` subfolder at the paper's own location.

### 0.3 Load ALL knowledge sources BEFORE starting review

This is a mandatory step. Do not skip. Load these in parallel where possible:

#### A. Project Reference Files (Read directly)

| File | Content | Always load? |
|------|---------|:-----------:|
| `references/sci-review-criteria.md` | SCI journal review criteria, scoring anchors, rejection reasons | Yes |
| `references/chinese-author-checklist.md` | 4-tier Chinese author common errors (articles, structure, Chinglish, citations) | If Chinese author |
| `references/storytelling-framework.md` | OCAR structure, hourglass rule, SUCCESS framework, broken arc detection | Yes |

Read them now: they are at `c:\Users\17053\Desktop\paper review\.claude\skills\paper-reviewer\references/`.

#### B. Deployed Project Skills (Invoke via Skill tool when needed)

| Skill | What it provides | Use in layer |
|-------|-----------------|:-----------:|
| `nature-polishing` | Section-by-section polish workflow (architecture → section moves → sentence control), overclaim detection, hedging calibration, British English | L4 |
| `nature-writing` | paper-review.md self-review checklist, article-architecture.md, paragraph-flow.md | L1, L2 |
| `nature-figure` | Nature-level figure quality standards, color/font/info-hierarchy rules | L5 |
| `nature-citation` | CNS citation verification, RIS/EndNote/Zotero format checks | L5 |
| `humanizer` | 29-pattern AI writing detection (Wikipedia-based) | L4 |

#### C. External Skills (from skills_manager — invoke via Skill when relevant)

Located at `c:\Users\17053\Desktop\skills_manager\download\`. Not auto-loaded;
invoke only when the paper's content warrants it:

| Skill | Path in skills_manager | When to invoke |
|-------|----------------------|----------------|
| `nature-response` | `nature-skills/skills/nature-response/` | Not for initial review; only when user needs rebuttal help |
| `nature-data` | `nature-skills/skills/nature-data/` | If journal requires Data Availability statement |
| `latex-academic-publisher` | `latex-academic-publisher/SKILL.md` | If user needs help fixing LaTeX compilation issues |
| `review-paper` | `AI-research-feedback/Skills/review-paper/SKILL.md` | If user wants economics/social-science style 8-agent review |
| `review-paper-light` | `AI-research-feedback/Skills/review-paper-light/SKILL.md` | Fast 2-agent contribution+identification check |
| `experiment-agent` | `experiment-agent/SKILL.md` | If user wants statistical validation or experiment reproduction |

#### D. Web Research (for journal-specific requirements)

If the user specified a journal, use WebSearch + WebFetch to find:
- Official Author/Submission Guidelines
- Word/page limits, abstract format, section requirements
- Citation style, figure/table specifications
- Data availability policy
- Any declared review criteria or evaluation rubrics

If no journal specified, search for general high-impact review standards.

### 0.4 Discover the paper structure

#### For LaTeX projects:

1. Glob `**/*.tex` from the paper root (exclude `_minted-*`, `build/`,
   `output/`, `.git/`).
2. Identify the main document: files with `\documentclass` or `\begin{document}`.
   Discard `beamer` class, files named `response*`, `letter*`, `slides*`,
   `presentation*`, `old*`, or inside `old/`, `archive/`, `submitted/` folders.
3. Among remaining candidates, pick the one with the largest `\input{}` /
   `\include{}` / `\subfile{}` graph. If ambiguous, ask the user.
4. Recursively expand all `\input{}`, `\include{}`, `\subfile{}` references
   to build the full document tree.
5. Read ALL component `.tex` files. Build a section map:
   ```
   Section → file:line range, type (abstract/intro/related/method/result/discussion/conclusion/appendix)
   ```
6. List figure files: Glob `**/Figures/**`, `**/figures/**`, root-level images.
   Filter to only those referenced via `\includegraphics{}` in the document tree.
7. List table files: Glob `**/Tables/**`, `**/tables/**`, root-level `*table*.tex`.
   Filter to only those `\input{}`/`\include{}`d from the document tree.
8. Record: title, authors, abstract from the main `.tex` file.
9. Detect author origin: scan for Chinese author names, Chinese comments in `.tex`,
   `\usepackage[UTF8]{ctex}` → trigger chinese-author-checklist.md.

#### For PDF/Word/text papers:

- PDF → extract text with `pdftotext` or `pypdf`.
- DOCX → extract with `python-docx` or `pandoc`.
- `.txt`/`.md` → read directly.
- Warn if extraction yields garbled/unreadable text (scanned PDF → OCR needed).

#### For partial manuscripts:

If the user says "只看Introduction和Methods" or the paper is clearly incomplete,
adjust scope accordingly. Mark sections as `[NOT REVIEWED — section not provided]`,
not as defects. Don't penalize for work not yet done.

### 0.5 Pre-flight: LaTeX health check (LaTeX projects only)

Run BEFORE the layer review; results feed into the baseline card and L5.

1. **If a TeX toolchain is available** (`pdflatex`/`xelatex` on PATH): compile
   the main document (`-interaction=nonstopmode -draftmode`). Capture: fatal
   errors, undefined references/citations (`LaTeX Warning: ... undefined`),
   missing figure files, overfull hbox count.
2. **If no toolchain is available**, run a static scan instead:
   - every `\includegraphics{}` target exists on disk;
   - every `\ref{}` / `\eqref{}` key has a matching `\label{}`;
   - every `\cite{}` key exists in the `.bib` file(s).

   Report which mode was used — never claim "compiles cleanly" from a static scan.
3. Compile failure or missing figure files = automatic **Critical** issue.
   Undefined refs/citations = **Major**. Record all results for the baseline card.

### 0.6 Present the review baseline card

Before starting the review, present a concise summary to the user:

```
## 📋 Review Baseline Card

**Paper**: [title]
**Authors**: [authors]  |  Author origin: [Chinese / International / Unknown]
**Paper location**: [full path]
**Target Journal**: [journal name + link to guidelines, or "top-field — high general standards"]
**Review Depth**: D[1-4] — [label] (~[range] expected findings)
**Scope**: [Full manuscript / Partial: sections X, Y, Z]

**Sections found**: Abstract ✓  Intro ✓  Related Work ✓  Methods ✓  Results ✓  Discussion ✓  Conclusion ✓
**Figures found**: [N]  |  **Tables found**: [N]  |  **References**: [N]
**LaTeX health**: [Compiles cleanly ✓ / N errors, M undefined refs, K missing figures / Static check only — no TeX toolchain]

**Knowledge sources loaded**:
- Reference files: sci-review-criteria, storytelling-framework [+ chinese-author-checklist if applicable]
- Skills to invoke: nature-polishing, nature-writing, nature-figure, nature-citation, humanizer
- Journal requirements: [fetched from web / local template / top-field defaults]
- External skills available: [list if any are relevant]

**Journal key requirements** (if applicable): [3-5 bullet summary]

Proceed with review? (y/n, or adjust depth/journal/focus)
```

Wait for user confirmation. Allow them to adjust any parameter.

---

## Phase 1 — Multi-Layer Review Execution

Execute all applicable review layers. Scale thoroughness to requested depth.
The reference files loaded in Phase 0.3 are your review playbook — apply them
at every layer, not just the ones where they seem most relevant.

### Layer Architecture

```
L1: Storyline & Structure     ─┐
L2: Argument & Evidence       ─┤  Run in parallel (Agent subagents)
L3: Methodology & Rigor       ─┘
                                    ↓
L4: Language & Style           ─┐  Run after L1-L3 (needs their scope)
L5: Format & References        ─┘
                                    ↓
L6: Synthesis & Scoring        ──  After all above
```

### Execution Mechanics

- **Depth vs. layers**: the checklist columns below are **depth (D1-D4)**
  columns — which checks run at each depth. L1-L6 are the review layers.
- **Subagents**: reference files are loaded in the MAIN conversation (Phase 0).
  When dispatching a layer to an Agent subagent, put the absolute paths of the
  relevant reference files in the subagent prompt and instruct it to Read them
  first — subagents do NOT inherit the main conversation's context or files.
- **Skill invocations** (`humanizer`, `nature-polishing`, `nature-figure`,
  `nature-citation`) run in the MAIN conversation via the Skill tool. Never ask
  a subagent to invoke a skill; if a subagent needs a skill's checklist, give
  it the skill's file path to Read instead.
- **Standard finding schema** — every layer (main loop or subagent) returns
  findings in this exact shape; at merge time only `IssueID` (C/M/m numbering)
  and `Status` are added, and `sources` feeds the report's Appendix B:

  ```
  { layer: "L1".."L6", severity: "Critical" | "Major" | "Minor",
    section: "...", location: "file.tex:line",
    problem: "...", evidence: "verbatim quote from the file",
    fix: "concrete, actionable suggestion",
    sources: ["knowledge source 1", "knowledge source 2"] }
  ```

- **Context budget**: for long manuscripts (>40 pages, theses), do NOT pull the
  full text into the main conversation. Dispatch section-wise reading to
  subagents that return findings in the schema above.

### How Each Layer Uses Knowledge Sources

Every layer must cross-reference **at least two** knowledge sources:

| Layer | Primary reference file | Primary skill | Secondary source |
|-------|----------------------|---------------|-----------------|
| L1 | storytelling-framework.md | nature-writing | SCI criteria §2 (Clarity) |
| L2 | sci-review-criteria.md §1-2 | nature-polishing (overclaim) | storytelling (broken arcs) |
| L3 | sci-review-criteria.md §5 | Independent analysis | Web research (journal standards) |
| L4 | chinese-author-checklist.md (if applicable) | humanizer + nature-polishing | SCI criteria §3 |
| L5 | sci-review-criteria.md §6 | nature-figure + nature-citation | Journal guidelines |
| L6 | sci-review-criteria.md (scoring) | All layer outputs | Storytelling (final arc check) |

### L1 — Storyline & Structure

**Reference**: `storytelling-framework.md` (OCAR, hourglass, SUCCESS, broken arcs)
**Skill**: `nature-writing` (paper-review.md, article-architecture.md, paragraph-flow.md)

**Checklist** (scale check marks to depth):

| Check | D1 | D2 | D3 | D4 |
|-------|:--:|:--:|:--:|:--:|
| OCAR (Opening-Challenge-Action-Resolution) complete | ✓ | ✓ | ✓ | ✓ |
| Hourglass width: Intro scope = Conclusion scope | ✓ | ✓ | ✓ | ✓ |
| Section-level logic flow (each section's internal arc) | — | ✓ | ✓ | ✓ |
| Paragraph-level: one message per paragraph, clear topic sentence | — | ✓ | ✓ | ✓ |
| Nested story arcs (each section a complete story unit) | — | — | ✓ | ✓ |
| Abstract arc: context→gap→approach→results→implication→boundary | ✓ | ✓ | ✓ | ✓ |
| Intro arc: field→bottleneck→prior→gap→present study | ✓ | ✓ | ✓ | ✓ |
| Related Work: topic synthesis (not paper-by-paper list) | — | ✓ | ✓ | ✓ |
| Discussion: explains meaning (not repeats results) | — | ✓ | ✓ | ✓ |
| SUCCESS: Simple, Unexpected, Concrete, Credible, Emotional, Stories | — | ✓ | ✓ | ✓ |
| Broken arc detection: cross-reference consistency | — | — | ✓ | ✓ |
| Sentence-level flow: topic chains, transitions, temporal markers | — | — | ✓ | ✓ |

### L2 — Argument & Evidence

**Reference**: `sci-review-criteria.md` §1-2 (Originality, Technical Soundness)
**Skill**: `nature-writing` (paper-review.md), `nature-polishing` (overclaim detection)

| Check | D1 | D2 | D3 | D4 |
|-------|:--:|:--:|:--:|:--:|
| Every major claim has explicit experimental evidence | ✓ | ✓ | ✓ | ✓ |
| Claim type matches evidence type (causal→ablation, improvement→baseline, etc.) | ✓ | ✓ | ✓ | ✓ |
| Overclaiming: universal scope from narrow evidence | ✓ | ✓ | ✓ | ✓ |
| Hedging calibration: claim strength vs. evidence strength | — | ✓ | ✓ | ✓ |
| Falsifiability: could an independent researcher test each claim? | — | ✓ | ✓ | ✓ |
| Scope calibration: claims assert exactly what evidence supports | — | ✓ | ✓ | ✓ |
| Abstract numbers match body numbers exactly | — | ✓ | ✓ | ✓ |
| Introduction promises delivered by Results | — | ✓ | ✓ | ✓ |
| Cross-reference numerical consistency | — | — | ✓ | ✓ |
| Every citation substantively supports its context | — | — | ✓ | ✓ |
| Unstated assumptions made explicit | — | — | ✓ | ✓ |
| Limitations and negative results honestly discussed | — | ✓ | ✓ | ✓ |
| Contribution type clearly identified | ✓ | ✓ | ✓ | ✓ |

### L3 — Methodology & Rigor

**Reference**: `sci-review-criteria.md` §5 (Experimental Rigor)
**Skill**: Independent expert analysis (no dedicated methodology skill deployed)

| Check | D1 | D2 | D3 | D4 |
|-------|:--:|:--:|:--:|:--:|
| Method described in sufficient detail for independent reproduction | ✓ | ✓ | ✓ | ✓ |
| Research design appropriate for the stated research question | ✓ | ✓ | ✓ | ✓ |
| Baselines adequate, recent, and fairly compared | — | ✓ | ✓ | ✓ |
| Ablation studies isolating all key design choices | — | ✓ | ✓ | ✓ |
| Error bars / CIs / statistical tests reported for all quantitative claims | — | ✓ | ✓ | ✓ |
| Multiple testing correction where applicable | — | ✓ | ✓ | ✓ |
| Metric measures what the claim actually asserts | — | ✓ | ✓ | ✓ |
| Hyperparameter selection methodology documented | — | — | ✓ | ✓ |
| Multiple runs/seeds for stochastic methods | — | — | ✓ | ✓ |
| Dataset/scenario difficulty sufficient to demonstrate effectiveness | — | ✓ | ✓ | ✓ |
| Code, data, and instructions available for reproducibility | — | ✓ | ✓ | ✓ |
| Sample size justification (power analysis or equivalent) | — | — | ✓ | ✓ |

### L4 — Language & Style

**Reference**: `chinese-author-checklist.md` (if applicable), SCI criteria §3
**Skills**: `nature-polishing` (section & sentence polish workflow), `humanizer` (29-pattern detection)

| Check | D1 | D2 | D3 | D4 |
|-------|:--:|:--:|:--:|:--:|
| Grammar and spelling | ✓ | ✓ | ✓ | ✓ |
| Sentence length (key sentences ≤30 words) | — | ✓ | ✓ | ✓ |
| Academic register and vocabulary level | — | ✓ | ✓ | ✓ |
| Tense consistency (past=done, present=findings) | — | ✓ | ✓ | ✓ |
| Passive/active voice balance | — | — | ✓ | ✓ |
| British vs. American English consistency | — | — | ✓ | ✓ |
| Hedging language calibrated to evidence | — | ✓ | ✓ | ✓ |
| **AI-generated writing patterns** (29 checks from humanizer) | — | ✓ | ✓ | ✓ |
| **Chinese author specific** (if applicable): | | | | |
| — Article usage (a/an/the) | — | ✓ | ✓ | ✓ |
| — Loose clause structures (流水句) | — | ✓ | ✓ | ✓ |
| — Chinglish expressions ("plays a vital role", etc.) | — | ✓ | ✓ | ✓ |
| — Missing logical connectors between sentences | — | ✓ | ✓ | ✓ |
| — Weak topic sentences (building to point vs. stating upfront) | — | ✓ | ✓ | ✓ |
| — Noun chains (3+ consecutive nouns) | — | ✓ | ✓ | ✓ |
| Jargon and acronym usage appropriate for target readership | — | ✓ | ✓ | ✓ |
| Conciseness: no filler, redundancy, "it is worth noting" | — | ✓ | ✓ | ✓ |

**How to execute L4**:
1. Invoke `humanizer` skill on representative sections (Abstract, Intro, Discussion)
   for AI pattern detection
2. Invoke `nature-polishing` skill on the same sections for style and overclaim check
3. If Chinese author: apply `chinese-author-checklist.md` Tier 1-4 checks manually,
   scanning every section
4. Read the full manuscript for grammar/spelling/flow with fresh eyes

### L5 — Format & References

**Reference**: `sci-review-criteria.md` §6 (Presentation & Format)
**Skills**: `nature-figure`, `nature-citation`

| Check | D1 | D2 | D3 | D4 |
|-------|:--:|:--:|:--:|:--:|
| LaTeX health: compiles without errors (or static scan passes, §0.5) | ✓ | ✓ | ✓ | ✓ |
| Journal template compliance (if .cls/.sty available) | — | ✓ | ✓ | ✓ |
| Figure visual quality — **open and view every image file** (resolution, font, color, labels) | — | ✓ | ✓ | ✓ |
| Figure information hierarchy (overview→deviation→relationship) | — | ✓ | ✓ | ✓ |
| Multi-panel figure logic (no two panels answer the same question) | — | — | ✓ | ✓ |
| Table formatting and readability | — | — | ✓ | ✓ |
| Citation format consistency throughout | — | ✓ | ✓ | ✓ |
| Every in-text citation in reference list (and vice versa) | — | ✓ | ✓ | ✓ |
| Citation recency: key recent works (last 2-3 years) cited | — | — | ✓ | ✓ |
| Data Availability statement present and compliant | — | ✓ | ✓ | ✓ |
| Supplementary material organization | — | — | ✓ | ✓ |
| Word/page limit compliance | — | ✓ | ✓ | ✓ |

**How to execute figure review**: open every referenced figure file with the
Read tool — Claude can view images. Never judge a figure by its filename or
caption alone. Check legibility at the journal's print width (single column
≈ 89 mm): fonts readable, colorblind-safe palette, axis labels and units
present, panel labels consistent with in-text references.

### L6 — Synthesis & Scoring

**Reference**: `sci-review-criteria.md` (scoring anchors, acceptance/rejection criteria)

1. **Score each of 6 dimensions** (1-5, using sci-review-criteria.md anchors):
   - Originality / Contribution
   - Technical Soundness / Methodology
   - Clarity / Writing Quality
   - Significance / Impact
   - Experimental Rigor
   - Presentation / Format

2. **Calculate overall grade**:
   - **Strong Accept**: mean ≥ 4.5, no dimension < 3
   - **Accept**: mean ≥ 3.8, no dimension < 2
   - **Weak Accept**: mean ≥ 3.0, no dimension < 2
   - **Weak Reject**: mean ≥ 2.0, with one or more dimensions < 2
   - **Reject**: mean < 2.0, or any dimension = 1

3. **Generate three synthesis observations**:
   - **One thing that would most improve this paper** (concrete, actionable)
   - **Strongest aspect — don't change this** (genuine, not forced)
   - **Skeptical reviewer one-liner** (what a hostile reviewer would say)

4. **Cross-check with storytelling framework**: Does the final paper tell a
   coherent story? Apply the SUCCESS checklist one last time.

---

## Phase 2 — Report Generation

**Output directory**: `<paper_root>/reviews/review-YYYY-MM-DD-D[depth]/`
(e.g., `review-2026-07-18-D3/`). If it already exists — a re-review on the
same day at the same depth — append `-v2`, `-v3`, etc. Never overwrite a
previous review.

**D1 exception**: at D1, skip the full 10-section template below. Produce a
single bilingual `review-summary.md` (verdict table + all issues with one-line
fixes + quick wins) plus the CSV. The full template applies at D2 and above.

### 2.1 Generate English review report

Write `review-report-en.md` in the output directory.

**Report structure** (follow exactly):

```markdown
# Pre-Submission Review Report

**Paper**: [Full Title]
**Authors**: [Author List]
**Author Origin**: [Chinese / International / Mixed]
**Target Journal**: [Journal + link to guidelines]
**Review Date**: [YYYY-MM-DD]
**Review Depth**: D[1-4] — [Label]
**Sections Reviewed**: [List]
**Sections Not Present**: [List, or "None — complete manuscript"]

---

## 1. Summary Assessment

[2-4 sentences: what the paper does, main contribution, overall impression.
Written as a handling editor would write to an associate editor.]

**Overall Grade**: [grade] (mean: [X.X]/5.0)

| Dimension | Score | Key evidence |
|-----------|:-----:|-------------|
| Originality / Contribution | X/5 | [...] |
| Technical Soundness | X/5 | [...] |
| Clarity / Writing Quality | X/5 | [...] |
| Significance / Impact | X/5 | [...] |
| Experimental Rigor | X/5 | [...] |
| Presentation / Format | X/5 | [...] |

## 2. Major Strengths

[3-5 genuine, specific strengths. Cite sections, figures, or findings.
Do NOT force these — a weak paper may have only 1-2 real strengths.]

## 3. Critical Issues

[Issues that MUST be fixed before submission. Each one is potentially
grounds for rejection. Format each as:]

### C[N]. [Issue Title]

- **Location**: [Section, file:line or paragraph]
- **Problem**: [What's wrong. Include verbatim quote if helpful.]
- **Why it matters**: [Impact on credibility / publishability]
- **How to fix**: [Concrete, actionable suggestion. Be specific.]

## 4. Major Issues

[Significant weaknesses that should be addressed but may not be fatal.]

### M[N]. [Issue Title]
[... same format as Critical ...]

## 5. Minor Issues

[Worth fixing, not blocking. Can be listed more compactly.]

### m[N]. [Issue Title]
[... same format, but briefer ...]

## 6. Language & Style Issues

[Organized by section. Each entry: location, original, suggested revision, reason.]

### Abstract
### Introduction
### Related Work
### Methods
### Results
### Discussion
### Conclusion

## 7. AI Writing Pattern Detection

[From humanizer + manual detection. List patterns found with counts,
representative examples, and fix suggestions. Reference the 29 patterns.]

**Patterns detected**: [N]
**Severity**: [Low / Medium / High — how much does the paper sound like AI?]

| Pattern | Count | Example | Fix |
|---------|:-----:|---------|-----|
| ... | | | |

## 8. LaTeX Health, Figures & Tables

[Pre-flight results from Phase 0.5: compile/static-check outcome, errors,
undefined refs/citations, missing graphics. Then per-figure: what it shows,
whether it supports its claim, visual quality (based on actually viewing the
image), nature-figure compliance. Per-table: formatting, readability.]

## 9. Citation Check

[Missing citations, mismatched citation contexts, format inconsistencies.
Use nature-citation's verification logic. List suspicious or missing refs.]

## 10. Final Recommendation

- **Recommendation**: [Accept / Minor Revision / Major Revision / Reject]
- **Confidence**: [High / Medium / Low]
- **Summary for editor**: [2-3 sentences justifying the recommendation to the
  handling editor — this is what a real reviewer would write in "Comments to Editor"]

## Appendix A: Review Baseline Card

[The card shown to the user in Phase 0.6, for reference]

## Appendix B: Knowledge Sources Used

[Table listing all reference files, skills invoked, and web sources consulted]
```

### 2.2 Generate Chinese translation

Translate the FULL English report to Chinese. Requirements:
- Preserve ALL structure, section numbering, issue IDs (C1, M1, m1)
- Technical terms: keep English original in parentheses on first use
- Tone: professional, direct, constructive (same as English)
- Do NOT summarize or shorten — this is a faithful translation

Write as `review-report-cn.md` in the same directory.

### 2.3 Generate issue tracking CSV

Write `review-issues.csv` **with a UTF-8 BOM** so Excel on Windows renders
Chinese correctly. At D3+, make `Problem` and `Suggestion` bilingual
(English + 中文) — the author reads Chinese. Valid `Status` values:
`Open` / `Fixed` / `Partially fixed` / `Not fixed` / `Verified` / `Wontfix`
(statuses are updated by the Revision Verification mode, below).

```csv
IssueID,Layer,Severity,Section,FileLocation,Problem,Evidence,Suggestion,Status
C1,L2-Argument,Critical,Results,results.tex:L234,"Overclaim: universal scope from single dataset","text says 'all underwater environments' but only tested in pool","Change to 'controlled underwater environments' or add ocean test",Open
M1,L3-Methodology,Major,Methods,methods.tex:L156,"Missing ablation for attention module","no experiment isolates attention vs. baseline",Add ablation: model w/o attention vs. full model,Open
```

---

## Phase 3 — Deliver

Present to the user in this order:

1. **Compact verdict**: table with 6 dimension scores + overall grade
2. **Top 3 critical issues**: one-line each, so user can triage immediately
3. **File manifest**: paths to all generated files
4. **Offer**: "Want me to dive deeper into [weakest dimension] or [most concerning section]?"

---

## Mode: Revision Verification （审稿意见回复验证）

Triggered when the user provides reviewer comments plus a revised manuscript
(optionally a response letter): "帮我验证修改" / "检查回复信" / "verify my
revisions". This is NOT the initial-review flow.

1. **Parse** the reviewer comments into numbered points (R1.1, R1.2, R2.1, …).
2. **Locate** each claimed fix in the revised manuscript and/or response
   letter. File evidence only — a promise in the response letter with no
   manuscript change counts as *Not addressed*.
3. **Verdict per point**: Addressed / Partially addressed / Not addressed /
   Addressed but introduced a new problem (describe it).
4. **Targeted re-review**: run a D2-level review on the changed sections only
   (diff against the previous version if available); do not redo the whole
   paper.
5. **Update tracking**: set `Status` in the previous `review-issues.csv`
   (Open → Fixed / Partially fixed / Not fixed) and write the updated CSV to
   the new output folder.
6. **Output** to `<paper_root>/reviews/verification-YYYY-MM-DD/`:
   `verification-report-en.md` + `verification-report-cn.md` + updated CSV.

---

## Rules

1. **File-only evidence**: Every criticism cites a specific manuscript location.
   Never invent data, mechanisms, references, or findings.

2. **Constructive tone**: "This is wrong" is incomplete. Always add: why it matters +
   how to fix it. You are helping the author improve, not punishing them.

3. **Scoped to what exists**: For partial manuscripts, only review provided sections.
   Mark missing sections as `[NOT REVIEWED — not provided]`, not as defects.

4. **Respect depth level**: Don't spend D4 effort on a D1 request. Don't skip
   critical issues at D2 just because they're subtle.

5. **Journal calibration**: Same paper → different severity for different journals.
   "MDPI Sensors" and "Nature" have different bars. Apply sci-review-criteria.md's
   calibration table.

6. **Author-origin awareness**: When author names are Chinese, Chinese comments exist
   in `.tex`, or the user indicates they're Chinese → load and apply
   chinese-author-checklist.md across ALL layers, not just L4.

7. **No hallucinated citations**: Verify citation existence via WebSearch with
   depth-scaled sampling — D2: ~15% (prioritize last-3-year refs, arXiv
   preprints, unfamiliar venues, and load-bearing citations); D3: ≥50%;
   D4: 100%. Never fabricate a reference. If unsure, label as `[UNVERIFIED]`.

8. **Cross-reference knowledge sources**: Every finding should be informed by
   at least one reference file + one skill or web source. Don't wing it.

9. **Adapt to user feedback**: After delivering the report, the user may say
   "重点帮我看看统计部分" or "语言问题再详细查一遍" — re-run that specific layer
   at higher depth without redoing the entire review.

10. **Paper stays put**: The paper's source files live at the user-specified path.
    Review outputs go into `<paper_root>/reviews/`. Never move or modify the paper's
    source files unless the user explicitly asks for inline fixes.

11. **Score with evidence**: every L6 dimension score must cite at least two
    concrete file locations (file:line) in the "Key evidence" column. No
    evidence, no score.

---

## Skills and Knowledge Source Integration

### When to invoke which skill

| Trigger | Action |
|---------|--------|
| "审查论文" / "review" + paper info | This skill (paper-reviewer) — full orchestration |
| "润色这段" / "polish this paragraph" | `nature-polishing` directly (skip review flow) |
| "这个图怎么样" / "check this figure" | `nature-figure` directly |
| "AI痕迹太重" / "humanize this" | `humanizer` directly |
| "帮我回复审稿意见" (draft the response letter) | Deploy and invoke `nature-response` |
| "帮我验证修改" / "检查回复信" | Revision Verification mode (this skill, above) |
| "检查数据声明" | Deploy and invoke `nature-data` |

### Knowledge source hierarchy

When there's a conflict between sources (e.g., nature-polishing says "≤30 words"
but the journal allows longer), the priority is:

```
Journal's official guidelines > sci-review-criteria.md > deployed skills > general knowledge
```
