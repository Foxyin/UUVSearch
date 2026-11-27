# Common LaTeX Errors & Fixes

## 1. Missing Package/Class

```
! LaTeX Error: File `somepackage.sty' not found.
```

**Fix:** Install via `tlmgr install somepackage` or add CTAN path.
For template classes (IEEEtran.cls, mdpi.cls, etc.):
- Download from the journal's website
- Place in `journal-template/` directory
- Or install system-wide: `tlmgr install IEEEtran`

## 2. Undefined Control Sequence

```
! Undefined control sequence.
l.42 \somecommand
```

**Fix:** Check for missing `\usepackage{}` that defines the command.
Common missing packages:
- `\bm` → needs `\usepackage{bm}`
- `\matrrix` → typo: use `\matrix`
- `\Huge` → needs `\Huge` (capital H, not `\huge`)

## 3. Missing Bibliography

```
LaTeX Warning: Citation 'key2024' undefined on input line 42.
```

**Fix:**
1. Check the citation key exists in `references.bib`
2. Check for typos in the key
3. Recompile: `pdflatex → bibtex → pdflatex → pdflatex`
4. For biblatex: use `\printbibliography` not `\bibliography`

## 4. Overfull hbox

```
Overfull \hbox (12.345pt too wide) in paragraph at lines 42--50
```

**Fix:**
- Rephrase the sentence
- Use `\linebreak` or `\-` for hyphenation
- Allow more stretching: `\emergencystretch=1em` in preamble
- Use `\sloppy` (last resort)
- For IEEE (two-column): shorten the paragraph

## 5. Emergency Stop

```
! Emergency stop.
<read *>
```

**Fix:** Usually a missing input file or corrupted aux file.
- Delete `build/` directory and recompile
- Check all `\input{}` and `\include{}` paths exist
- Check for missing closing braces

## 6. Too Many Unprocessed Floats

```
! LaTeX Error: Too many unprocessed floats.
```

**Fix:**
- Add `\usepackage{morefloats}` to preamble
- Use `\clearpage` to flush pending floats
- Reduce the number of figures/tables in the current chapter
- Use `[H]` placement from `float` package strategically

## 7. BibTeX/Biber Errors

```
This is BibTeX, version 0.99d...
The top-level auxiliary file: main.aux
I couldn't open database file 'references.bib'
```

**Fix:** Check that `references.bib` exists and path is correct.
For biblatex + biber errors:
- Delete `.bbl`, `.bcf`, `.run.xml` files
- Run `biber build/main.bcf`
- Run `pdflatex` again

## 8. Font Encoding

```
! Package fontenc Error: Encoding file `t1enc.def' not found.
```

**Fix:** `tlmgr install ec` or use `\usepackage[T1]{fontenc}` which is standard.

## 9. PDF Inclusion

```
! LaTeX Error: Unknown graphics extension: .pdf.
```

**Fix:** Check `\usepackage{graphicx}` is loaded and `\includegraphics` path
is correct. Modern LaTeX distributions support PDF natively.

## 10. File Not Found (Windows vs Linux)

```
! I can't find file 'sections/01-introduction.tex'.
```

**Fix:** Check:
- Case sensitivity (Linux is case-sensitive)
- Forward slashes in paths (use `/` not `\`)
- File extension is `.tex` not `.txt`
