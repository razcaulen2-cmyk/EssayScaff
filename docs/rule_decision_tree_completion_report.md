# Process 06 — Visual Rule Decision Tree completion report

Date: 2026-10-22

## Location and files

**Transparency Mode → 06 Rule Base → Overview → Explore a Rule — Visual Decision Tree**.

Triggered, Not Triggered and Evaluation Trace each have an expandable **Explore these rules in the Visual Decision Tree** list. Selecting an entry activates the same Overview component, selects that rule, and focuses the selector. Existing tables and all 45 sub-tabs remain available.

Files changed in this phase:

- `static/app.js`: cached-response model, reusable six-node explorer, verified source display, three tab entry points, Stage Observations limitation paths.
- `static/style.css`: bounded desktop graph/details layout, mobile stacking, node accents, selected state and source formatting.
- `tests/test_rule_decision_tree.py`: real HTTP Introduction and shared causal corpus; model, connection, selection, span, limitation and missing-cache regressions.
- `tests/transparency_browser_check.cjs`: actual Chrome rule selection, provenance-edge, dependency-tree, read-only, responsive geometry and screenshot checks.
- `docs/rule_decision_tree_completion_report.md`: this report.

## Baseline recorded before edits

Working project: `C:\Users\My Pc\Desktop\EssayScaff-V2`.

`& ".venv\Scripts\python.exe" -m pytest -q --tb=short`

**506 passed in 102.17s.**

`& ".venv\Scripts\python.exe" -B tests/transparency_browser_check.py`

Passed; `javascriptErrors: []`; isolated writing sessions, revisions and submissions all zero.
Baseline artifacts: `C:\Users\My Pc\AppData\Local\Temp\opencode\essayscaff-transparency-r84_5s1h`.

## Model and supported relationships

`buildRuleDecisionTree` consumes a returned evaluation record and the current cached response. The selector uses `analysis.rule_evaluation_trace`, falling back to the selected stage's retained trace when available. It never constructs an Introduction-only rule inventory.

Six selectable nodes represent:

1. Original analyzed writing.
2. Related retained observations and measured values.
3. Returned condition metadata and source-verified comparisons.
4. The exact recorded evaluation status and decision basis.
5. The matching Rule Event, or an explicit absent/unavailable/false-record state.
6. Recorded feedback usage.

The existing `causalRuleModel`, `transparencyRuleInputs`, `causalSpan`, `transparencyTextSources`, subordinator explanation and structured-record helpers are reused. No natural-language condition parser or new rule execution is introduced.

Connectors have explicit meanings and supporting source paths. They describe source context, retained-input comparisons, reconstructed-status explanations, same-ID event associations, or recorded field-level provenance. Unsupported relationships have **No supported connector** rather than an arrow. They do not claim runtime execution order.

The evaluation trace is explicitly labeled as reconstructed **after feedback selection**, based on `EssayAnalysisService.analyze` and `research_inspector.build_rule_evaluation_trace`. It cannot be depicted as an input to FeedbackService.

## Evidence selection and offsets

The model selects the existing rule-specific input mapping: for example, incomplete-subordinator candidates, development evidence, lexical matches, a dynamically identified Body paragraph's supporting-detail evidence, or the applicable Conclusion comparison.

- Text presence and whole-section lexical rules display the exact whole-stage context.
- Introduction clause evidence can select verified containing sentences.
- `BODY.P<n>.*` rules display the exact matching paragraph when its offsets verify.
- Cross-stage rules show the current section and relevant supplied prior-section text separately.
- Highlights require exact text equality against a bounded, end-exclusive Unicode-code-point slice. Whitespace and punctuation are retained with `pre-wrap`.
- Cross-stage records use different coordinate spaces, so the explorer does not merge their highlights. Their source-labeled records remain available in details.
- Missing or conflicting source text produces an explicit unavailable state rather than a reconstructed essay.

## Decisions and conditions

The returned status is authoritative. `TRIGGERED`, `EVALUATED_NOT_TRIGGERED`, `NOT_APPLICABLE`, `NOT_RECORDED`, `FAILED` and unfamiliar future statuses are preserved without conversion to Boolean results.

Source comparisons carry **SOURCE-VERIFIED DERIVATION** labeling. They explain retained inputs; they are not represented as individually recorded execution steps. The returned condition, configuration, implementation location and decision basis remain available in the expandable technical panel.

Keyword-list details distinguish the required conjunction and its internal OR threshold. Subordinator details reuse the source-verified marker/attachment alternatives and explicitly state that helper-reached flags and short-circuit logs are not retained.

An absent Rule Event collection is different from a retained collection with no matching event. An explicit false event flag cannot produce a feedback connector. Non-triggered outcomes are not presented as successful writing assessments.

## Feedback provenance

Connections are resolved by exact Rule ID from:

- `feedback['Feedback Provenance']`, including compact records;
- `research_trace.stages[stage].feedback_decisions.fields[field].rule_ids`, with the retained selection branch when present.

A feedback edge additionally requires a matching event without an explicit false `triggered` or `fired` flag.

The three outcomes are:

- **Used by selected feedback**: a supported event and a recorded field citation.
- **Recorded as an observation**: an event exists but no retained selected field cites its ID.
- **No event emitted / no recorded decision link**: no supported emitted-event link can be drawn.

Field-level provenance does not establish which individual list item an event caused. Missing provenance does not prove that the underlying observation was never read. WordNet candidate events remain informational; the existing source confirms that FeedbackService does not use those candidates for message selection.

## Uncertainty and prohibited conclusions

Stage Observations adds expandable **Limitation Explanation Paths**:

**Underlying method → What was observed → What remains unknown → Why the stronger conclusion is unsupported**.

The paths reuse the exact-wording `CAUSAL_SCOPE_REASONS` explanations. They identify static methodological limitations and unconditional stage-scope statements, rather than inventing uncertainty-detector decisions. Unknown wording or absent arrays is explicitly marked as lacking a source explanation or record. Existing causal limitation explanations remain in place.

Actual `*.LIMITATION.*` and `*.GOAL.*` evaluation records remain selectable and are labeled as unconditional stage-scope events. Their real event/provenance records are still inspectable.

## Real Introduction verification

The new fixture uses the exact five-sentence Introduction, assignment question and five focus terms supplied in the request, through the real student analysis API.

| Rule | Actual status |
| --- | --- |
| `INTRO.TEXT.PRESENT` | TRIGGERED |
| `INTRO.CLAUSE.SUBJECT_PREDICATE_CANDIDATE` | TRIGGERED |
| `INTRO.CLAUSE.POSSIBLE_INCOMPLETE_SUBORDINATOR` | TRIGGERED |
| `INTRO.DEVELOPMENT.MULTIPLE_CLAUSE_PREDICATES` | TRIGGERED |
| `INTRO.TEXT.KEYWORD_LIST_CANDIDATE` | EVALUATED_NOT_TRIGGERED |
| `INTRO.TOPIC.NO_FOCUS_MATCH_OBSERVED` | EVALUATED_NOT_TRIGGERED |

The rendered text-presence comparison shows **63 alphabetic tokens**, required `count > 0`. The no-focus-match comparison shows **10 match occurrences**, required `count == 0`; occurrences are not mislabeled as unique terms. The incomplete-subordinator tree contains the exact sentence **“Although smartphones can also interrupt lessons.”**, at `[286, 334)`, and links to the retained `possible_incomplete_subordinator` feedback branch. Text presence is not linked to Primary Feedback automatically.

## Body and Conclusion support

The shared real causal corpus exercises dynamic paragraph/sentence-pair IDs, supporting-detail candidate and absence cases, adjacent continuity, WordNet observations, Conclusion closure, synthesis, new material, continuity, unavailable prior sections and non-triggered rules. Browser selection additionally traverses all **14 Introduction, 20 Body and 26 Conclusion** records returned by its three samples.

New or partially retained rules still display their actual record, event and supported provenance; unknown intermediate mappings are labeled NOT RECORDED instead of being assigned an unrelated condition.

## Final verification

- `node --check static/app.js` — passed.
- `& ".venv\Scripts\python.exe" -m pytest -q --tb=short` — **508 passed in 102.78s**.
- `& ".venv\Scripts\python.exe" -B tests/transparency_browser_check.py` — passed in Chrome **155.0.8059.85**, `javascriptErrors: []`.
- All 45 sub-tabs remain functional; existing tables and causal regressions pass.
- The Dependency Tree still renders SVG edges and opens token-span details.
- Rule selection and node inspection preserve response/state snapshots, with zero additional analysis requests or persistence writes.
- Desktop 1440×1100 and mobile 390×844 graph captures verify non-overlapping nodes and no page-wide horizontal overflow.
- Existing Writing Tutor, native editing, stale-response, clipboard, teacher Inspector and immersive-focus checks pass.
- Existing protected-output fingerprint and protected-file nonmutation tests pass without changed expected hashes.
- Isolated persistence counts: writing sessions **0**, revisions **0**, submissions **0**.

## Screenshots

Final artifact directory:

`C:\Users\My Pc\AppData\Local\Temp\opencode\essayscaff-transparency-6qti04m7`

There are 20 new graph/condition captures (five rules × desktop/mobile × graph/conditions). Key captures:

| Evidence | File |
| --- | --- |
| `INTRO.TEXT.PRESENT` | `rule-tree-text-present-desktop.png` |
| Incomplete subordinator | `rule-tree-incomplete-subordinator-desktop.png` |
| Non-triggered rule, measured comparison | `rule-tree-non-triggered-desktop-conditions.png` |
| Dynamic Body supporting-detail rule | `rule-tree-body-desktop.png` |
| Conclusion new-material observation | `rule-tree-conclusion-desktop.png` |
| Mobile graph | `rule-tree-text-present-mobile.png` |
| Mobile conditions | `rule-tree-non-triggered-mobile-conditions.png` |

The screenshots were visually reviewed. A global primary-button style conflict was corrected before the final run. The final graph uses light node backgrounds, colored category accents and a distinct selected outline.

## Remaining evidence limits and protected scope

The frontend cannot provide an unrecorded Boolean execution log, earlier-stage concept inventories omitted by response compaction, list-item-level feedback causality, or context-disambiguated WordNet meaning. Missing or ambiguous evidence remains explicit. Long technical records are expandable; long exact source text scrolls within its bounded source viewer.

Only the frontend visualization, its styles/tests and this report were edited. No changes were made to NLPService/spaCy, TopicService, WordNet, StageEvidence, any Rule Base, FeedbackService, Research Inspector calculations, EssayAnalysisService, lesson mappings, Writing Tutor logic, authentication, database behavior, or protected research fingerprints. No dependencies were added. No commit or push was performed. This phase ends at Process 06.
