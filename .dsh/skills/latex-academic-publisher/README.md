# LaTeX Academic Publisher — Claude Skill

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform: Claude.ai](https://img.shields.io/badge/Platform-Claude.ai-orange.svg)](https://claude.ai)
[![LaTeX](https://img.shields.io/badge/LaTeX-ready-008080.svg)](https://www.latex-project.org)
[![Journal Templates](https://img.shields.io/badge/Journal%20Templates-7%20supported-brightgreen.svg)](#supported-document-types--templates)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
> A Claude skill that transforms structured research content into publication-ready, compilable LaTeX documents with journal-specific formatting.

---

## What This Skill Does

**LaTeX Academic Publisher** turns Claude into a dedicated LaTeX formatting and compilation companion for researchers, students, and academics. Instead of wrestling with cryptic compilation errors or manually formatting bibliographies, you get structured, stage-aware assistance that knows exactly where you are in the publication pipeline.

Whether you're starting a blank IEEE conference paper, converting a draft into an Elsevier journal template, fixing a stubborn BibTeX error, or preparing a camera-ready submission — this skill has a workflow for it.

---

## Key Features

### Project Initialization — From Zero to Compilable in One Command
Describe your paper's target journal and topic, and the skill generates a complete LaTeX project: correct document class, pre-configured preamble with journal-appropriate packages, section stubs, an empty `references.bib`, and a `.latexmkrc` tuned to the template's compilation sequence.

- **7 built-in templates**: IEEE, MDPI, Elsevier, Springer, ACM, Nature-style, and Plain
- **Smart preamble generation**: Each template gets the right packages, font encodings, and layout settings
- **Section scaffolding**: Auto-numbered `\include{}`-based section files ready to fill

### Modular Section Writing — One Section at a Time
Write your paper incrementally. The skill handles each section as a modular unit — create, edit, or rewrite `introduction.tex` without touching the rest of the document.

- Add a new section with correct `\section{}` or `\chapter{}` command
- Maintain consistent cross-referencing with auto-generated `\label{}` keys
- Use `\includeonly{}` for fast, focused compilation of a single section

### Smart Compilation & Error Recovery
No more staring at inscrutable log files. The skill handles the full compilation pipeline and translates LaTeX errors into plain-English fixes.

- **One-command compile**: Runs the correct sequence (pdflatex → bibtex → pdflatex × 2) automatically
- **Error parsing**: Reads `.log` output, categorizes errors, and suggests or applies fixes
- **Missing packages**: Detects and resolves `! LaTeX Error: File *.sty not found`
- **Undefined citations**: Cross-references `references.bib` against `\cite{}` usage
- **Watch mode**: Optional continuous compilation on file changes

### Reference Management — Bibliographies Without the Headache
Import, organize, and cite references with structured BibTeX support.

- **Import `.bib` files**: Merge external libraries into your project
- **Citation key management**: Add, check, and fix citation keys
- **Style switching**: Change bibliography style to match target journal (IEEEtran, elsarticle-num, spmpsci, ACM-Reference-Format, etc.)
- **Entry type templates**: Correct field structure for `@article`, `@inproceedings`, `@book`, `@phdthesis`, and more

### Figures & Tables — Proper Placement Every Time
Add visual elements with correct, template-aware LaTeX code.

- **Single figures**: Generates `\begin{figure}...\end{figure}` with proper scaling for single or double-column layouts
- **Multi-panel figures**: Side-by-side subfigures or N×M grids via `subcaption`
- **Tables from data**: CSV-to-LaTeX conversion with `booktabs` formatting
- **Template-aware widths**: Uses `\columnwidth`, `0.48\textwidth` (two-column), or `\textwidth` (single-column) as appropriate

### Submission Packaging — Ready to Send
Prepare your camera-ready package with a single command.

- Collects only required files (`.tex`, sections, figures, `.bib`)
- Strips comments for final version (optional)
- Outputs a clean ZIP archive in `build/`

---

## Supported Document Types & Templates

| Template | Document Class | Best For | Priority |
|----------|---------------|----------|----------|
| **IEEE** | `IEEEtran` | IEEE journals & conferences (TNNLS, CVPR, etc.) | ★★★★★ |
| **MDPI** | `mdpi` class | Sensors, Applied Sciences, Remote Sensing, etc. | ★★★★★ |
| **Elsevier** | `elsarticle` | All Elsevier journals (preprint/review/final) | ★★★★★ |
| **Springer** | `svjour3` / `llncs` | Springer journals & LNCS proceedings | ★★★★ |
| **ACM** | `acmart` | ACM conferences (CHI, ICSE, SIGGRAPH) | ★★★★ |
| **Nature** | `article` (approximation) | Nature Portfolio preprints & submissions | ★★★ |
| **Plain** | `article` + custom | Theses, reports, general academic writing | ★★★ |

---

## Supported File Types

| Input | What the Skill Does |
|-------|---------------------|
| `.tex` files | Reads structure, fixes errors, reformats for target journal |
| `.bib` / BibTeX | Imports, validates, and formats references |
| `.csv` / `.xlsx` data | Converts to publication-ready LaTeX tables |
| Figures (`.pdf`, `.png`, `.eps`) | Places with correct captioning and scaling |
| `.log` / `.blg` files | Parses compilation errors and suggests fixes |

---

## Installation

### Prerequisites

- A [Claude.ai](https://claude.ai) account (free or paid)
- LaTeX distribution installed locally (TeX Live recommended: `sudo apt install texlive-full` or `brew install --cask mactex`)
- `latexmk` (included with TeX Live)

### Choose Your Installation Method

#### Option 1: Quick Install via npx (Recommended)

You can add this skill directly to your local project environment or global skill registry using the package runner:

```bash
npx skill add your-username/latex-academic-publisher
```

*This command automatically pulls the instruction assets (`SKILL.md` and templates) from the remote repository and initializes them for your workspace.*

#### Option 2: Manual Installation from Source

1. **Clone the repository**

```bash
   git clone https://github.com/your-username/latex-academic-publisher.git
   cd latex-academic-publisher
```

2. **Open Claude.ai**

Navigate to [Claude.ai](https://claude.ai) and sign in to your account.

3. **Access the Skills panel**

Click your avatar in the bottom-left corner, then select **Skills** from the menu.

4. **Add the skill**

Click **Add Skill** → **Upload from file**, then select `SKILL.md` from your local copy of the repository.

5. **Verify the installation**

The skill should now appear in your Skills library. Start a new conversation and select **LaTeX Academic Publisher** from the skill picker to begin.

### Keeping the Skill Updated

To sync the latest improvements and template updates:

```bash
# If installed via manual clone
git pull origin main

# If managed via CLI tool
npx skill update your-username/latex-academic-publisher
```

---

## Repository Structure

```
latex-academic-publisher/
├── SKILL.md                              # Core skill instructions
├── latex-academic-publisher.skill        # Packaged skill kit
├── README.md                             # This file
└── reference/
    ├── templates/                        # Per-template LaTeX examples
    │   ├── ieee/                         # IEEEtran (main, preamble, metadata)
    │   ├── mdpi/                         # MDPI class
    │   ├── elsevier/                     # elsarticle
    │   ├── springer/                     # svjour3
    │   ├── acm/                          # acmart
    │   ├── nature/                       # article (Nature-style)
    │   └── plain/                        # Generic article
    ├── examples/
    │   ├── latexmkrc-example             # .latexmkrc compilation config
    │   ├── references-example.bib        # Reference entries (all types)
    │   ├── bibtex-cheatsheet.md          # BibTeX field reference
    │   ├── common-errors.md              # 10 common LaTeX errors + fixes
    │   ├── figure-template.tex           # Figure code snippets
    │   └── table-template.tex            # Table code snippets
    └── scripts/
        └── init-project.sh               # Project initializer script
```

---

## Quick Start

```bash
# 1. Initialize a new IEEE paper
init "my-ieee-paper" template=ieee

# 2. Write your introduction
section introduction "In this paper, we propose..."

# 3. Add references
ref import references.bib
ref cite Author2024Key

# 4. Add a figure
figure add figures/architecture.png "Proposed system architecture" fig:arch

# 5. Compile
compile

# 6. Fix any errors
fix

# 7. Package for submission
submit
```

---

## Design Philosophy

- **Guide, don't ghostwrite.** The skill helps you structure and format your LaTeX document — it won't fabricate content or hallucinate references.
- **One section at a time.** Write and compile incrementally. Never write an entire paper in one shot.
- **Compile early, compile often.** Catch errors when they're small and isolated.
- **Template fidelity.** Output matches the target journal's guidelines — font sizes, margin widths, citation styles, and section numbering.
- **No hallucinated packages.** Every `\usepackage{}` is backed by a real CTAN package. The skill won't add non-existent LaTeX commands.

---

## Contributing

Contributions are welcome and appreciated! Whether you're fixing a template, adding support for a new journal, or improving error messages — your help makes this skill better for everyone.

### Ways to Contribute

- **Report a bug** — Open an issue describing the problem, including the error log and steps to reproduce.
- **Add a template** — Have a journal class file that's not yet supported? We'd love to add it.
- **Submit a pull request** — See something you can fix or improve? We'd love to review your PR.

### Step-by-Step Contribution Guide

1. **Open an issue first** — Describe what you'd like to change and why.
2. **Fork the repository** — Create your own copy on GitHub.
3. **Clone your fork locally**

```bash
   git clone https://github.com/your-username/latex-academic-publisher.git
   cd latex-academic-publisher
```

4. **Create a feature branch**

```bash
   git checkout -b feat/add-new-template
```

5. **Make your changes** & follow the guidelines below.
6. **Commit and push**

```bash
   git add .
   git commit -m "feat: add Elsevier template with correct class options"
   git push origin feat/add-new-template
```

7. **Open a Pull Request** — Reference your initial issue in the PR description.

### Development Guidelines

- **Match the existing tone** — The skill communicates in a structured, instructive style. New instructions should follow the same voice.
- **Preserve template fidelity** — Each template must produce compilable output that matches the journal's formatting guidelines.
- **Don't break existing workflows** — Verify that template changes don't introduce regressions for other templates.
- **Document your additions** — If you add a new template, include example `main.tex`, `preamble.tex`, and `metadata.tex` files in `reference/templates/`.

### Code of Conduct

This project adheres to a simple standard: **be respectful and constructive**. Harassment, personal attacks, or unprofessional behavior will not be tolerated. All interactions — whether in issues, pull requests, or discussions — should foster a welcoming and collaborative environment.

---

## License

MIT License — free to use, modify, and distribute.
