# BibTeX Entry Types & Fields Reference

## Entry Types

| Type | Use For | Required Fields |
|------|---------|----------------|
| `@article` | Journal papers | author, title, journal, year, volume, pages |
| `@inproceedings` | Conference papers | author, title, booktitle, year, pages |
| `@book` | Full books | author/editor, title, publisher, year |
| `@inbook` | Book chapters | author/editor, title, chapter/pages, publisher, year |
| `@incollection` | Contribution to book | author, title, booktitle, publisher, year |
| `@phdthesis` | PhD/Master theses | author, title, school, year |
| `@mastersthesis` | Master's theses | author, title, school, year |
| `@techreport` | Technical reports | author, title, institution, year |
| `@misc` | Everything else | (none required) |
| `@unpublished` | Unpublished works | author, title, note |
| `@proceedings` | Conference proceedings | title, year |
| `@manual` | Manuals/documentation | title |

## Common Fields

| Field | Description | Example |
|-------|-------------|---------|
| `author` | Authors (separate with `and`) | `{First A. and Second B.}` |
| `title` | Title (capitalize properly) | `{A Great Paper}` |
| `journal` | Journal name | `{Nature}` |
| `year` | Publication year | `2025` |
| `volume` | Journal volume | `42` |
| `number` | Issue number | `3` |
| `pages` | Page range | `100--120` |
| `doi` | Digital Object ID | `{10.1000/example}` |
| `url` | URL | `{\url{https://...}}` |
| `isbn` | ISBN | `{978-0-000-00000-0}` |
| `publisher` | Publisher name | `{Springer}` |
| `address` | Publisher location | `{New York, NY}` |
| `edition` | Book edition | `{3}` |
| `editor` | Book editor(s) | `{Ed. A. and Ed. B.}` |
| `eprint` | arXiv ID | `{2401.00000}` |
| `archiveprefix` | Archive name | `{arXiv}` |
| `primaryclass` | arXiv class | `{cs.AI}` |
| `howpublished` | Publication medium | `{\url{https://...}}` |
| `organization` | Conference org | `{IEEE}` |
| `school` | University | `{MIT}` |
| `institution` | Organization | `{Google Research}` |
| `note` | Additional notes | `{Accessed: 2025-01-01}` |

## Name Formatting

Always use the full format: `First Last` or `First Middle Last`

```
author = {John A. Smith and Jane B. Doe and Robert Johnson}
```

## Title Capitalization

BibTeX will lowercase everything except what you protect with braces:

```
title = {A {Deep} Learning Approach to {NLP} Tasks}
```

## Citation Styles by Template

| Template | Style | Command |
|----------|-------|---------|
| IEEE | `IEEEtran` | `\bibliographystyle{IEEEtran}` |
| MDPI | `mdpi` (built-in) | (handled by class) |
| Elsevier | `elsarticle-num` | `\bibliographystyle{elsarticle-num}` |
| Springer | `spmpsci` / `spbasic` | `\bibliographystyle{spmpsci}` |
| ACM | `ACM-Reference-Format` | `\bibliographystyle{ACM-Reference-Format}` |
| Nature | `plain` (approximate) | `\bibliographystyle{plain}` |
| Plain | `plain` / `alpha` / `unsrt` | `\bibliographystyle{plain}` |
