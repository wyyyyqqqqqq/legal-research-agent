# Counter-Analysis Checklist

Every key conclusion in a mode-shaped deliverable must be tested against
at least one of the six counter-analysis dimensions before publication.

## Dimensions

### 1. Alternative Interpretation
- Is there a plausible alternative reading of the statute or regulation?
- Has any court, regulator, or commentary adopted a different reading?
- Could the provision be read more narrowly or more broadly?

### 2. Minority or Dissenting View
- Are there dissenting opinions in relevant case law?
- Does any credible secondary source argue the opposite position?
- Has any regulator taken a different stance from the majority view?

### 3. Jurisdictional Risk
- Would the conclusion hold if a different court or regulator reviewed it?
- Are pending amendments or guidance likely to change the outcome?
- Is there a split between lower and higher courts, or between agencies?

### 4. Factual Sensitivity
- Would the conclusion change if key facts were slightly different?
- What threshold conditions (monetary, temporal, scope) could shift the analysis?

### 5. Practical Enforcement Risk
- Is the provision actively enforced or largely dormant?
- What is the realistic enforcement probability?
- Are there safe harbors or compliance program mitigants?

### 6. Similar-Statute Confusion
- Are there two or more statutes in the same jurisdiction covering the same subject?
- Could operative language, safe harbors, or definitions be confused across statutes?
- Do the statutes share adjacent code sections or near-identical names?
- High-risk pattern: shared code-section ranges (e.g., Cal. Civ. Code §§1798.80-1798.84,
  Korean PIPA vs. Credit Information Act). Subsection-level citation verification required.

## Per-Mode Minimums

| Output mode | Minimum counter-analysis |
|---|---|
| `executive_brief` | At least 1 counter-argument per key conclusion (brief). |
| `comparative_matrix` | At least 1 counter-argument per material divergence point. |
| `enforcement_case_law` | At least 1 dissenting or minority view per enforcement trend. |
| `black_letter_commentary` | At least 1 counter-argument per article-level conclusion (detailed). |
| `canonical` | Same as `black_letter_commentary` — preserves the agent's existing analysis discipline. |

## Output Format

For each key conclusion, append a structured counter-analysis block:

```text
**Counter-Analysis:**
- **Alternative interpretation:** <description> — <source if available>
- **Risk level:** High / Medium / Low
- **Mitigant:** <what reduces this risk, if anything>
```

When a counter-analysis dimension is rated **High**, flag it inline with
`[Material Risk]`, surface it in the Conclusion Summary or Executive
Summary, and (for `black_letter_commentary`) add a dedicated Risk
Considerations paragraph under the affected article.
