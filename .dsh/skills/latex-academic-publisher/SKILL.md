---
name: latex-academic-publisher
description: "Use when formatting, compiling, or generating LaTeX documents for academic publication. Trigger on keywords: LaTeX, .tex, IEEE, MDPI, Springer, Elsevier, ACM, overleaf, latexmk, bibliography, .bib, template, journal submission, camera-ready, arxiv, preprint. Use ONLY when LaTeX output or compilation is needed — do NOT trigger for general scientific writing without LaTeX."
---

# LaTeX Academic Publisher Skill

Transforms structured research content (outline, draft sections, references) into publication-ready, compilable LaTeX documents with journal-specific formatting.

---

## 1. When This Skill Activates

- User says: "compile this paper", "generate LaTeX", "format for IEEE/MDPI"
- User provides `.tex` files, `.bib` files, or asks to create a paper from an outline
- User needs to fix compilation errors, add references, or restructure a LaTeX project
- User wants to convert a draft into a specific journal template

## 2. Workflow Overview (Stage 7 — Formatting & Submission Ready)

This skill operates as the final formatting stage in the research workflow. It expects input from earlier stages (outline, content draft, references) and produces a compilable LaTeX project.

```
[Outline + Draft + References] → [LaTeX Skill] → [Journal-Ready PDF]
```

### Workflow Stages

| Step | Action | Description |
|------|--------|-------------|
| 1 | `init` | Initialize project structure with template |
| 2 | `preamble` | Generate preamble + metadata |
| 3 | `sections` | Write/import each section (one at a time) |
| 4 | `references` | Set up .bib file and citation keys |
| 5 | `figures` | Handle figures, tables, captions |
| 6 | `compile` | Compile → fix errors → final PDF |

---

## 3. Project Structure

```
{project-name}/
├── main.tex                 # Entry point (\include all sections)
├── preamble.tex             # Packages, macros, configuration
├── metadata.tex             # Title, authors, affiliations, abstract
├── sections/
│   ├── 01-introduction.tex
│   ├── 02-literature.tex
│   ├── 03-methodology.tex
│   ├── 04-results.tex
│   ├── 05-discussion.tex
│   ├── 06-conclusion.tex
│   └── appendix.tex         # optional
├── figures/                 # All figures/images (PDF, PNG, EPS)
│   └── placeholder.txt
├── tables/                  # standalone table files
├── references.bib           # BibLaTeX/BibTeX references
├── .latexmkrc               # latexmk config for compilation
├── journal-template/        # Template class/style files
│   └── {template}-template/
└── build/                   # Compilation output (PDF, logs, aux)
```

---

## 4. Supported Templates

| Template | Document Class | Journal / Venue | Priority |
|----------|---------------|-----------------|----------|
| `ieee` | `IEEEtran` | IEEE journals, conferences | ★★★★★ |
| `mdpi` | `mdpi` (article, book, proceedings) | MDPI journals (Sensors, Applied Sciences, etc.) | ★★★★★ |
| `elsevier` | `elsarticle` | Elsevier journals | ★★★★★ |
| `springer` | `svjour3` / `llncs` | Springer journals, LNCS | ★★★★ |
| `acm` | `acmart` | ACM conferences (CHI, ICSE, etc.) | ★★★★ |
| `nature` | `article` (nature class) | Nature Portfolio journals | ★★★ |
| `plain` | `article` + custom | General / Thesis / Preprint | ★★★ |

---

## 5. Template-Specific Configuration Notes

### IEEE (`IEEEtran`)
- Two-column layout, 10pt font
- Use `\bstctlcite{IEEEexample:BSTcontrol}` for citation control
- Biography section at end via `\IEEEmembership`
- Running headers via `\markboth`
- Compile: `pdflatex → bibtex → pdflatex → pdflatex`

### MDPI (`mdpi` class)
- Requires `mdpi.cls` (auto-downloaded if missing)
- Single-column for review, two-column for published
- Use `\Title`, `\Author`, `\Affiliations`, `\Abstract` macros (not standard LaTeX)
- Compile: `pdflatex → bibtex → pdflatex → pdflatex`

### Elsevier (`elsarticle`)
- Options: `preprint`, `review`, `1p`, `3p`, `5p`, `final`
- Preferred citation: `\bibliographystyle{elsarticle-num}`
- Use `\author`, `\ead` for email, `\cortext` for corresponding
- Compile: `pdflatex → bibtex → pdflatex → pdflatex`

### Springer (`svjour3`)
- Options: `smallextended`, `envcountsame`
- Preferred citation styles: `spmpsci`, `spbasic`
- Use `\inst{}` for affiliations, `\fnm`/`\sur` for structured names
- Compile: `pdflatex → bibtex → pdflatex → pdflatex`

### ACM (`acmart`)
- Options: `acmconf`, `journal`, `sigconf`
- Uses `\acmConference`, `\acmBooktitle`, `\acmDOI` macros
- Rights management via `\setcopyright{acmcopyright}`
- Compile: `pdflatex → bibtex → pdflatex → pdflatex`

---

## 6. Commands / Actions

### `init`
Create a new LaTeX project from scratch.

```
Usage: init <project-name> [template=ieee|mdpi|elsevier|springer|acm|nature|plain]
```

Generates:
- Full directory structure (sections/, figures/, tables/, build/)
- Template-specific `main.tex` with correct document class and packages
- Template-specific `preamble.tex` with optimized packages
- `metadata.tex` with placeholder fields
- `.latexmkrc` configured for the template
- Empty `references.bib`

### `preamble`
Generate or update `preamble.tex` with packages tailored to the template.

Packages included per template:
- **Core**: `amsmath`, `amssymb`, `amsthm`, `graphicx`, `hyperref`, `xcolor`, `geometry`, `setspace`, `caption`, `subcaption`
- **Tables**: `booktabs`, `tabularx`, `multirow`, `array`
- **Figures**: `graphicx`, `float`, `caption`, `subcaption`
- **Bibliography**: `biblatex` (IEEE: `backend=biber,style=ieee`; MDPI: `backend=biber`; etc.)
- **Algorithms**: `algorithm`, `algorithmic` (if needed)
- **Math**: `amsmath`, `amssymb`, `mathtools`, `bm`

### `section`
Add or edit a specific section.

```
Usage: section <name> [content]
```

- Creates file in `sections/{nn}-{name}.tex` (auto-numbered)
- Adds `\include{sections/{nn}-{name}}` to `main.tex`
- If content is provided, writes initial draft; otherwise opens for editing
- Each section is handled as a modular unit — write one at a time

### `ref`
Manage references.

```
Usage: ref add <citation-key> <bibtex-entry>
Usage: ref import <file.bib>
Usage: ref cite <citation-key>    → inserts \cite{key} at cursor
Usage: ref style <style-name>     → changes bibliography style
```

### `figure`
Add and manage figures.

```
Usage: figure add <image-path> [caption] [label]
Usage: figure grid <image-paths...> [cols=2] [caption]
```

Generates proper `\begin{figure}...\end{figure}` environment with:
- Correct path resolution (`figures/`)
- Template-appropriate width (`\columnwidth`, `0.48\textwidth` for two-column)
- Caption + label
- Subfigure support via `subcaption` package

### `table`
Add and manage tables.

```
Usage: table add [--data <csv>] [caption] [label]
Usage: table from-csv <csv-path> [caption] [label]
```

Generates:
- `\begin{table}...\end{table}` with `tabularx` or `booktabs`
- CSV data auto-converted to `tabular` environment
- Proper formatting per template

### `compile`
Compile the LaTeX project to PDF.

```
Usage: compile [watch=false] [clean=false]
```

- Uses `latexmk` with `.latexmkrc` config
- Template-appropriate compilation sequence:
  - **BibLaTeX**: `latexmk -pdf -bibtex -latexoption=-interaction=nonstopmode`
  - **BibTeX**: `pdflatex → bibtex → pdflatex × 2`
- On error: Parse `.log` file, identify errors, suggest or apply fixes
- On success: Copy PDF to `build/{project-name}.pdf`
- Optional: `watch=true` for continuous compilation

### `fix`
Parse compilation errors and fix them.

```
Usage: fix [log-file=build/main.log]
```

- Reads `.log` file
- Identifies and categorizes errors:
  - Missing packages → `\usepackage{}` + notify user
  - Undefined citations → check `references.bib`
  - Undefined references → recompile (need 2+ passes)
  - Syntax errors → locate line + suggest correction
- Applies fixes interactively (ask user before each change)

### `submit`
Prepare submission package.

```
Usage: submit [format=zip]
```

- Collects only required files (main.tex, sections/, figures/, references.bib)
- Strips comments for final version (optional)
- Generates `build/{project-name}-submission.zip`

---

## 7. Compilation Configuration (`.latexmkrc`)

Default `.latexmkrc` content:

```perl
$pdf_mode = 1;                        # pdflatex
$postscript_mode = 0;
$dvi_mode = 0;
$bibtex_use = 2;                      # use biber if available
$clean_ext = "bbl bcf run.xml out aux log blg brf fls fdb_latexmk";
$out_dir = "build";
$max_repeat = 5;
$silent = 0;

# Make sure build directory exists
push @generated_exts, "build";
```

---

## 8. Integration with Scientific Research Helper

This skill bridges the gap between content creation (stages 1–6) and publication.

| Research Stage | This Skill's Role |
|---------------|-------------------|
| After literature review | Generate structured `references.bib` from notes |
| After outline | Generate `main.tex` + section stubs |
| After content draft | Fill each section `.tex` file |
| After figure creation | Place and caption figures in proper format |
| Ready to submit | Compile, fix, package for submission |

### Data Flow

```
scientific-research-helper output
  ├── Paper outline          →  init <project> + section stubs
  ├── Section drafts         →  section <name> (write content)
  ├── Reference list         →  ref import <file.bib>
  ├── Figure descriptions    →  figure add <path> <caption>
  └── Journal target         →  template selection at init
```

---

## 9. Best Practices

- **One section at a time**: Write and compile incrementally. Never write the entire paper in one shot.
- **Compile early, compile often**: Run `compile` after every section to catch errors early.
- **Use `\include` not `\input`**: Enables `\includeonly{}` for fast compilation of single sections.
- **Keep figures in `figures/`**: Relative paths from `main.tex`.
- **Biber vs BibTeX**: Prefer `biber` + `biblatex` for Unicode and advanced features; use `bibtex` + `natbib` only for template compatibility.
- **Version control**: Initialize git repo in the project directory.
- **Never edit `.aux` or `.bbl` files**: These are auto-generated; edit only `.tex`, `.bib`, and `.cls` files.

---

## 10. Tips for Common Issues

| Problem | Solution |
|---------|----------|
| `! LaTeX Error: File *.cls not found.` | Template class not installed. Use `init` with correct template or manually place `.cls` in `journal-template/`. |
| `! Undefined control sequence` | Missing package in `preamble.tex`. Add `\usepackage{...}` or check command spelling. |
| `Citation '...' undefined` | Key missing from `references.bib`. Check spelling or run `ref add`. |
| `Overfull \hbox` | Text exceeds column width. Reword, use `\linebreak`, or allow `\sloppy`. |
| `! Emergency stop.` | Usually a missing file. Check `\include` paths in `main.tex`. |
| `! Package biblatex Error: '\bibliographystyle' invalid.` | Use `\printbibliography` instead of `\bibliographystyle` + `\bibliography` with biblatex. |
