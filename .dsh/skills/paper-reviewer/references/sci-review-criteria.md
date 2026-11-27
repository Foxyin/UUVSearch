# SCI Journal Review Criteria — Comprehensive Framework

Synthesized from Elsevier, Springer Nature, PLoS ONE, and major ML conference
reviewer guidelines. Apply ALL dimensions; calibrate severity to target journal tier.

---

## 1. Originality & Contribution (Novelty)

**Core question**: What new knowledge does this paper contribute?

| Check | Assessment |
|-------|-----------|
| Is the topic timely and relevant? | Gap analysis vs. current literature |
| Is there at least one clear novelty type? | New task / pipeline / module / design finding / insight / dataset |
| Is the contribution non-trivial and non-obvious? | Would a domain expert say "obviously"? |
| Does it go beyond incremental improvement? | Marginal gains → weaker case; surprising gains → strong case |
| Is prior work adequately acknowledged? | Missing key references → red flag |

**Scoring anchors:**
- **5**: Genuinely new problem or paradigm-shifting insight
- **4**: Non-trivial advance over state-of-the-art
- **3**: Solid incremental contribution with clear value
- **2**: Well-known technique applied to new domain without adaptation
- **1**: No discernible novelty; trivial variation of existing work

## 2. Technical Soundness (Rigor)

**Core question**: Are the methods sound and the conclusions justified?

| Check | What to look for |
|-------|-----------------|
| Research design appropriate for the question? | Design-method mismatch |
| Methods described in sufficient detail for reproducibility? | Missing parameters, vague steps |
| Statistical analyses appropriate and correctly applied? | Wrong test, no correction for multiple testing |
| Controls adequate for all major claims? | Missing baselines, no ablation |
| Assumptions explicitly stated and justified? | Hidden assumptions that could invalidate results |
| Claims match what the evidence can support? | Causal claim from correlation, universal from narrow |

**Common statistical red flags:**
- No error bars / confidence intervals on quantitative results
- Single-run results for stochastic methods
- p-hacking indicators (cherry-picked metrics, no correction)
- Sample size too small for claimed effect
- Metric doesn't measure what the claim asserts

## 3. Clarity & Writing Quality

**Core question**: Can a knowledgeable reader understand and reproduce the work?

| Check | What to look for |
|-------|-----------------|
| Clear, well-organized structure? | IMRaD or appropriate alternative |
| Abstract complete and self-contained? | Missing key results, inflated claims |
| Terminology consistent throughout? | Same concept, different names |
| Notation defined at first use? | Undefined symbols, inconsistent notation |
| Each paragraph carries one clear message? | Multiple ideas in one paragraph |
| Smooth transitions between sections/paragraphs? | Abrupt jumps, missing logical bridges |
| Appropriate for the target readership? | Too much / too little background |

## 4. Significance & Impact

**Core question**: Will the community care about this work?

| Check | What to look for |
|-------|-----------------|
| Problem importance clearly articulated? | "So what?" test fails |
| Results meaningful beyond the specific dataset? | Overfitted to one benchmark |
| Potential for real-world application? | Only works in lab settings |
| Broader implications discussed? | Missing "what this enables" |
| Failure cases and limitations honestly discussed? | Cherry-picked results only |

## 5. Experimental Rigor

**Core question**: Are the experiments comprehensive and fair?

| Check | What to look for |
|-------|-----------------|
| Strong, recent baselines included under fair conditions? | Strawman baselines, cherry-picked comparisons |
| Ablation studies for all key design choices? | No isolation of component contributions |
| Multiple datasets / settings / metrics? | Single-dataset claims of generality |
| Hyperparameter sensitivity analyzed? | "Magic numbers" with no justification |
| Both strengths AND failure cases reported? | Only best-case results shown |
| Reproducibility: code, data, instructions available? | "Available upon request" without actual access |

## 6. Presentation & Format

**Core question**: Do figures, tables, and formatting meet journal standards?

| Check | What to look for |
|-------|-----------------|
| Figures self-contained with clear captions? | Legend missing, unreadable labels |
| Multi-panel figures follow information hierarchy? | Redundant panels, no logical flow |
| Tables readable and well-formatted? | Cluttered, no clear structure |
| Citation format consistent and complete? | Mixed styles, missing DOIs |
| Journal template compliance? | Wrong margins, font, section numbering |

---

## Severity Calibration by Journal Tier

| Issue severity | Top-tier (Nature/Science/Cell) | Strong field journal | Standard SCI |
|---------------|-------------------------------|---------------------|--------------|
| **Critical** | Any unsupported claim, missing key baseline, overclaiming | Fatal methodological flaw, missing essential control | Invalid conclusion, irreproducible method |
| **Major** | Minor overclaim, incomplete ablation, weak baseline | Unclear method description, missing ablation | Missing baseline, weak statistical reporting |
| **Minor** | Formatting nit, awkward phrasing | Grammar issues, inconsistent notation | Incomplete figure captions, formatting |

---

## What Gets a Paper Accepted (Consensus Across Sources)

1. **Sufficient contribution** — novel task, pipeline, module, design choices, findings, or insight
2. **Better empirical performance** than prior methods under fair, reproducible comparisons
3. **Complete evaluation** — comparison experiments + ablation studies + multiple settings
4. **Clear writing** — reproducible from the paper alone
5. **Honest limitations** — acknowledging weaknesses INCREASES credibility, not decreases it

## Common Rejection Reasons (By Frequency)

| Rank | Reason | Preventable by self-review? |
|------|--------|---------------------------|
| 1 | Claims not supported by evidence | Yes |
| 2 | Insufficient contribution (incremental) | Partially |
| 3 | Missing baselines or ablations | Yes |
| 4 | Method description not reproducible | Yes |
| 5 | Statistical flaws (p-hacking, no correction) | Yes |
| 6 | Overclaiming (universal from narrow evidence) | Yes |
| 7 | Poor writing quality (unreadable) | Yes |
| 8 | Ignoring key prior work | Partially |
