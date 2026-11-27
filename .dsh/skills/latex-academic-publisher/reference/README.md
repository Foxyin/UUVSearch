# LaTeX Academic Publisher — Reference Materials

## Directory Structure

```
reference/
├── templates/                    # Per-template examples
│   ├── ieee/                     # IEEEtran
│   │   ├── main-example.tex
│   │   ├── preamble-example.tex
│   │   └── metadata-example.tex
│   ├── mdpi/                     # MDPI class
│   │   ├── main-example.tex
│   │   ├── preamble-example.tex
│   │   └── metadata-example.tex
│   ├── elsevier/                 # elsarticle
│   │   ├── main-example.tex
│   │   ├── preamble-example.tex
│   │   └── metadata-example.tex
│   ├── springer/                 # svjour3
│   │   ├── main-example.tex
│   │   ├── preamble-example.tex
│   │   └── metadata-example.tex
│   ├── acm/                      # acmart
│   │   ├── main-example.tex
│   │   ├── preamble-example.tex
│   │   └── metadata-example.tex
│   ├── nature/                   # article (Nature-style)
│   │   ├── main-example.tex
│   │   ├── preamble-example.tex
│   │   └── metadata-example.tex
│   └── plain/                    # Generic article
│       ├── main-example.tex
│       ├── preamble-example.tex
│       └── metadata-example.tex
├── examples/                     # Shared references
│   ├── latexmkrc-example         # .latexmkrc config
│   ├── references-example.bib    # Example .bib file
│   ├── common-errors.md          # Error troubleshooting
│   ├── bibtex-cheatsheet.md      # BibTeX field reference
│   ├── figure-template.tex       # Figure code snippets
│   └── table-template.tex        # Table code snippets
└── scripts/                      # Automation scripts
    └── init-project.sh           # Project initializer
```

## How to Use

The skill reads SKILL.md for workflow instructions and references these templates
when generating LaTeX code. The templates provide correct syntax, package lists,
and metadata structure specific to each journal format.

## Template Customization

To add a new template:
1. Create a new folder under `templates/`
2. Add `main-example.tex`, `preamble-example.tex`, `metadata-example.tex`
3. Update the table in SKILL.md's "Supported Templates" section
