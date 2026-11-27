# Chinese-Authored English Paper — Common Issues Checklist

Based on the 2025 PLOS ONE study (732 Chinese STEM academics) and analyses of
submitted manuscripts to Rice Science, MDPI, and Elsevier journals.

Activate this checklist when: author names are Chinese, Chinese comments appear
in .tex files, or the user indicates they are a Chinese author.

---

## Tier 1: Pervasive Grammatical Issues

### 1.1 Articles (a/an/the)
**Why**: Mandarin Chinese has no article system. This is the #1 most common error.

| Error type | Example | Fix |
|-----------|---------|-----|
| Missing article | "Result shows that method works" | "The result shows that the method works" |
| Unnecessary article | "The deep learning is powerful" | "Deep learning is powerful" |
| Wrong article | "A accuracy of the model" | "The accuracy of the model" |

### 1.2 Subject-Verb Agreement
**Why**: Chinese verbs don't inflect for number/person.

| Error type | Example | Fix |
|-----------|---------|-----|
| Plural subject + singular verb | "The results shows that" | "The results show that" |
| Singular subject + plural verb | "The model demonstrate" | "The model demonstrates" |

### 1.3 Tense Confusion
**Why**: Chinese doesn't mark tense grammatically.

| Context | Correct tense |
|---------|--------------|
| What was done (methods, procedures) | Past tense |
| What was found (results) | Past tense |
| What is true now (findings, implications) | Present tense |
| What others have done (literature review) | Present perfect or past |
| What the paper does (paper description) | Present tense |

---

## Tier 2: Structural & Discourse Issues

### 2.1 Loose Clause Structures (流水句)
**Why**: Chinese favors paratactic structures (clauses linked by meaning, not grammar).
English requires hypotactic structures (explicit subordination).

**Before (Chinglish)**:
> The experiment was conducted, the results were analyzed, the conclusion was drawn.

**After (English)**:
> After conducting the experiment and analyzing the results, we drew the following conclusion.

### 2.2 Missing Logical Connectors
**Why**: Chinese relies more on implicit logical connections; English requires explicit ones.

**Check for**: Missing "however", "therefore", "furthermore", "in contrast", "specifically",
"consequently" between sentences and paragraphs.

### 2.3 Weak Topic Sentences
**Why**: Chinese writing often builds to the point; English states it upfront.

**Check**: Does each paragraph start with a clear topic sentence? Or does it circle before
arriving at the point?

### 2.4 Redundancy and Overly Complex Paragraphs
**Why**: Reported by 34.2% of Chinese researchers as a cause for rejection.

| Pattern | Example | Fix |
|---------|---------|-----|
| Tautology | "completely eliminate entirely" | "eliminate" |
| Noun chains | "the underwater vehicle propulsion system fault diagnosis method" | Break up or use prepositions |
| Repeated ideas | Same claim in Abstract, Intro, Results, Discussion (verbatim) | Vary phrasing; state once definitively |

---

## Tier 3: Vocabulary & Register Issues

### 3.1 Chinglish (中式英语)
**Why**: Negative transfer from Chinese language thinking.

| Chinglish | Better English |
|-----------|---------------|
| "has very important significance" | "is important" or "is significant" |
| "plays a vital role in" | "enables" or "contributes to" |
| "through the method of" | "by" or "using" |
| "carry out research on" | "study" or "investigate" |
| "make an improvement to" | "improve" |
| "in the process of" | "during" or "while" |
| "has the ability to" | "can" |

### 3.2 Overuse of "Can" and "Will"
Chinese authors overuse "can" where English would use "may", "might", or simple present.

### 3.3 Inappropriate Sentence Subjects
Chinese often uses impersonal constructions where English prefers clear agents.

**Before**: "It can be seen from Figure 3 that the performance is improved."
**After**: "Figure 3 shows that the performance improves by 15%."

---

## Tier 4: Citation & Literature Issues

### 4.1 Citation Clustering
Chinese-authored papers often cite 3-5 references at once `[1-5]` without explaining
how each specifically relates to the point.

**Fix**: Cite individually with context — "Smith (2020) showed X, while Jones (2021)
extended this to Y."

### 4.2 Missing International Literature
Over-citation of Chinese-language or regional journals while missing key international
work in the same area.

---

## Quick Detection Heuristic

When scanning a paper by a Chinese author, if you see ≥3 of these in one page,
the paper likely needs significant language revision:

1. Missing or wrong article (a/an/the) → 3+ per page
2. "plays a vital role" / "has important significance" / "through the method of"
3. Loose clauses without logical connectors between sentences
4. Abstract contains "The experimental results show that..." without specific numbers
5. Same sentence structure repeated 3+ times in a paragraph
