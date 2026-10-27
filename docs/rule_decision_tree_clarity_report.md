# Rule Decision Tree — targeted clarity fix

Date: 2026-10-22. Location: Transparency Mode → 06 Rule Base → Overview → Explore a Rule — Visual Decision Tree.

The existing six-node component is retained. Changes are limited to inspector comparison wording, evidence-role explanations and concise evidence presentation, connector messages, and the requested decision summary.

## Files changed

- `static/app.js`
- `static/style.css`
- `tests/test_rule_decision_tree.py`
- `tests/transparency_browser_check.cjs`
- `docs/rule_decision_tree_clarity_report.md`

## Before and after

### 1. Condition comparisons

Before: `central_direction_candidates: 5`, a technical absence condition, and `EVALUATED_NOT_TRIGGERED` appeared without a direct explanation of the comparison.

After, for `INTRO.CLAUSE.NO_SUBJECT_PREDICATE_CANDIDATE`:

- Purpose: checks whether the Introduction lacks a qualifying subject–predicate structure.
- Required: no central-direction candidates (finite ROOT predicates with a linked subject).
- Actually recorded: **5** such candidates.
- Reason: qualifying evidence was found, so the absence condition was not satisfied.
- Outcome: the rule did not trigger and produced no Rule Event.

The same required/observed/reason presentation covers supported text counts, lexical matches, paragraph development, closure and other mapped comparisons. Missing intermediate evidence is named rather than filled in.

The section **Why did this rule produce this result?** appears below the six-node diagram. It updates with the selected rule and uses current response values, not a hardcoded essay or count.

### 2. Highlight meaning and relevance

Before: all 15 verified spans across five sentences appeared similarly highlighted for the missing-structure rule.

After: an explanation immediately above the writing identifies those spans as **evidence contradicting an absence condition**, explicitly saying they are **not detected writing mistakes**. Only direct subject/predicate spans are emphasized for that rule: **10 relevant spans**, while all **15 verified spans** remain available in technical details.

The default displays at most **2 contexts and 6 relevant highlights**. **Show all relevant verified evidence** expands the remaining contexts/highlights. Text remains exact and offsets remain Unicode-code-point based. No analysis evidence is deleted; the Copy Full Analysis output remains identical before/after inspection.

Other descriptions distinguish support for a triggered condition, general context, inspection-only evidence, and unavailable verified highlights. Triggered absence conditions do not mark contextual words as proof that something is missing.

### 3. Connector wording

Before: `No supported connector`.

After, according to retained evidence:

- Non-triggered rule with a known absent event: **No Rule Event was produced because this rule did not trigger.** The feedback explanation says there is therefore no emitted event to link.
- Emitted but uncited event, with retained provenance: **This observation was recorded, but the selected feedback does not cite this Rule Event.**
- Cited event: **This Rule Event supports the selected feedback.** Actual fields/branches remain inspectable.
- Missing provenance: **The available analysis does not record a feedback connection for this finding.**
- NOT_APPLICABLE: explains that the rule was not applicable to the available inputs, not evaluated false.
- NOT_RECORDED/FAILED: explains that evaluation or a valid outcome cannot be established.

Technical connector source paths remain in expandable details. Messages replacing an absent connector do not create new arrows.

## Verified sources and fields

| Check | Actual retained source | Verified implementation |
| --- | --- | --- |
| Introduction subject–predicate presence/absence | `analysis.observable_structure.central_direction_candidates` | `IntroductionRuleBase.analyze` filters `_clause_candidates` to `is_root_clause`; `_rule_events` branches on that filtered list. These are not every predicate token or every clause candidate. |
| Possible incomplete subordinator | `analysis.observable_structure.incomplete_subordinator_candidates`; retained sentence tokens/dependencies | `_incomplete_subordinator_evidence` and `_rule_events`; existing `causalSubordinatorConditions` explains source alternatives without running NLP. |
| Text present | `analysis.text_presence.alphabetic_word_count` | `_rule_events`: at least one alphabetic token. |
| No focus match | `analysis.lexical_topic_evidence.matches` | `_all_matches` / `_rule_events`; direct/lemma occurrences, not unique focus-term counts. |
| Introduction development | `analysis.development_evidence.predicate_count` | `_development_finding`: two or more supported clauses after excluding flagged sentences. |
| Body paragraph development | `analysis.paragraphs[paragraph_index=n].clause_structure_candidates`; `supporting_detail_candidates.candidates` | `BodyRuleBase._supporting_detail_candidates`: retains candidates when the clause count is at least two; `_rule_events` uses that finding. |
| Conclusion closure | `analysis.closure_candidates.candidates` | `ConclusionRuleBase._closing_candidates`: final ROOT-clause candidate or recorded closing expression; `_rule_events` uses the list. |
| Continuity | Corresponding `analysis.*_continuity.status` | Existing source-verified causal comparison; availability does not establish successful connection of ideas. |
| Feedback connection | `feedback['Feedback Provenance']`; selected stage `feedback_decisions.fields[field].rule_ids` | Exact matching Rule IDs and a retained emitted event remain required. |

## Evidence accuracy

- Existing source-verified `causalRuleModel` comparisons are reused; natural-language condition strings are not parsed into Boolean decisions.
- Counts/statuses from the response are labeled OBSERVED; explanation comparisons are labeled SOURCE-VERIFIED DERIVATION.
- Compound rules are not collapsed into a fabricated all-conditions execution log. Additional existing comparisons remain available.
- For the standalone sentence **Although smartphones can also interrupt lessons.**, real retained annotations show `Although` as `SCONJ/mark`, attached to `interrupt`. The existing source-derived comparison explains the only-main-clause-predicate alternative after the separate-clause safeguard. The explanation remains a parser-based review candidate, not a confirmed error.
- Event/feedback edge eligibility is unchanged. Missing provenance is no longer worded as a confirmed absence of use.
- Missing inputs and contradictory cached comparison/status values are disclosed rather than reconciled by inventing conditions.

## Tests and results

Baseline before changes:

`& ".venv\Scripts\python.exe" -m pytest -q --tb=short`

**508 passed in 107.13s.**

Final checks:

- `node --check static/app.js` — passed.
- `& ".venv\Scripts\python.exe" -m pytest -q --tb=short` — **509 passed in 88.83s**.
- `& ".venv\Scripts\python.exe" -B tests/transparency_browser_check.py` — passed in Chrome **155.0.8059.85**, **javascriptErrors: []**.

Focused permanent coverage includes the exact five-candidate Introduction, the standalone smartphone subordinator sentence, text presence, no focus match, a real triggered Body development rule, a real Conclusion closure rule, informational WordNet events, missing feedback provenance and NOT_APPLICABLE states. It verifies the two-context/six-highlight default, expansion, relevant span selection, report equality and absence of false feedback edges.

Chrome additionally verifies the missing-structure summary and evidence-role wording, expansion, all existing 45 sub-tabs, Dependency Tree SVG/interaction, six-node rule selection, no page-wide horizontal overflow, non-overlapping nodes, and unchanged response/state snapshots with no additional analysis or persistence requests during inspection.

Desktop captures: 1440×1100. Mobile captures: 390×844. Existing Writing Tutor, current/previous snapshot, clipboard, teacher Inspector, immersive-focus and protected fingerprint regressions pass. Isolated writing sessions/revisions/submissions remain **0 / 0 / 0**.

## Screenshots

Directory: `C:\Users\My Pc\AppData\Local\Temp\opencode\essayscaff-transparency-68wu5_e6`.

- Non-triggered rule with evidence-role explanation: `rule-tree-missing-structure-desktop.png`
- Non-triggered mobile summary: `rule-tree-missing-structure-mobile-summary.png`
- Triggered rule: `rule-tree-incomplete-subordinator-desktop.png`
- Triggered attachment explanation/summary: `rule-tree-incomplete-subordinator-desktop-summary.png`
- Body comparison: `rule-tree-body-desktop-conditions.png`
- Conclusion: `rule-tree-conclusion-desktop.png`
- Additional desktop/mobile conditions and summary captures are in the same directory.

The non-triggered desktop, mobile summary, triggered summary and Body comparison screenshots were visually reviewed.

## Protected scope

No backend/research code, rule behavior, thresholds, lesson mappings, student feedback messages, Writing Tutor logic, authentication, database, draft or submission behavior was changed. Existing protected fingerprints were not edited and their regressions pass. No new dependency, NLP algorithm, visualization framework or main tab was added. No commit or push was performed. Work stops at this targeted clarity fix for review.
