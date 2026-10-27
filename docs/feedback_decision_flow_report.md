# Phase 2 — Process 07: Interactive Feedback Decision Flow (completion report)

## 1. Purpose and scope

Process 07 now contains "Explore Feedback — Visual Decision Flow", a read-only,
beginner-first visualization of how one feedback field was produced by the cached
analysis response: Rule Events → Feedback Conditions → Selected Branch →
Feedback Output → Writing Tutor Display. It reads only what the response already
retains; it never re-runs analysis, never rewrites a field, and never claims a
per-branch runtime evaluation the backend did not record. Backend files
(FeedbackService, Rule Bases, essay analysis, NLP, TopicService, lessons, Writing
Tutor logic) were not modified.

## 2. Placement — no new sub-tab

The explorer mounts inside the existing **Process 07 → Feedback Engine → Overview**
panel (`renderNlpTransparency`, static/app.js:2151) as a sibling section after the
field tables, together with the cross-link disclosures
(`renderFeedbackFlowEntries`, static/app.js:3196). Sub-tab count stays exactly
**45** (`STUDENT_TRANSPARENCY_SUBTABS` + `HORIZONTAL_TRANSPARENCY_TABS` untouched;
browser check asserts `[data-sub-tab]` length 45 per render).

## 3. Input data

`buildFeedbackDecisionFlow(field, result, data)` (static/app.js:2695) derives
everything from the same cached response the transparency panels already show:

- `analysis.rule_evidence` / `analysis.rule_evaluation_trace` (emitted events, names)
- `research_trace.stages[STAGE].feedback_decisions.fields[field]`
  (`selection_branch`, `selection_condition`, `rule_ids`,
  `selected_message_count`, `unselected_alternatives`, priority order)
- `feedback[field]` (exact messages) and `feedback["Feedback Provenance"]`
- `studentFeedbackPresentation` for the Writing Tutor display model
- `feedback.interpretation_limit` and decision `limitation` records

## 4. Flow structure (five nodes, labeled edges)

Nodes, in order, with kind modifiers and CSS classes (`.feedback-flow-node`
variants):

| # | Key | Title | Kind |
|---|-----|-------|------|
| A | `events` | A · Recorded Rule Events | evidence |
| B | `conditions` | B · Feedback Conditions | condition |
| C | `branch` | C · Selected Feedback Branch | decision |
| D | `output` | D · Actual Feedback Output | output |
| E | `tutor` | E · Writing Tutor Display | feedback |

Edges are only drawn when the response supports them (`events→conditions` needs a
non-constant condition plus retained inputs, `conditions→branch`/`branch→output`
need a recorded branch and value, `output→tutor` always from the same cached
value). Every connector carries its edge label as tooltip text; when an edge is
legitimately absent the connector text says NOT APPLICABLE / NOT RECORDED instead
of inventing a link (static/app.js:2869). The browser check asserts
linked-connector count == model edge count for every field of every sample.

## 5. Node content

Each node shows: heading, one-line summary, `Source: …` line, the six fixed
questions (`What is this?`, `Why does it matter?`, `What did EssayScaff record?`,
`How was it used?`, `Where did it come from?`, `What are its limitations?`) rendered
as recorded facts via `causalFacts`, node-specific tables/disclosures, and a lazy
"Detailed technical records — this field only" record (decision, provenance for the
field, emitted events, item alignment, display model, connections). Tests assert
all six question rows plus the source line for every node of every field.

## 6. Recorded branches and source-derived purpose

`FEEDBACK_FLOW_BRANCH_PURPOSES` (static/app.js, Process 07 block) documents every
branch value observed in the corpus, including
`general_observable_body_evidence` (body_generic Primary),
`first_paragraph_without_additional_clause_candidate` (body_mixed Primary),
`possible_incomplete_subordinator` (intro_incomplete Primary, citing
`INTRO.CLAUSE.POSSIBLE_INCOMPLETE_SUBORDINATOR`),
`synthesis_structure_candidate` (conclusion_rewording Primary),
`unobserved_prior_concepts` (conclusion_new Primary) and
`closure_candidate` (missing_context Next Step). The model branch is asserted equal
to the response's `selection_branch` for all five fields of all samples, and the
purpose table must cover the branch (no "not in purpose table" text). The WordNet
event emitted by `body_wordnet` is informational: no field ever marks it CITED.

## 7. Priority honesty wording (fixed texts)

- Branch recorded (default): "The selected feedback branch is recorded, but
  individual evaluations of other possible branches were not retained."
- Stage constant (Current Goal): "Current Goal is a stage constant: there is no
  branch evaluation to retain, and no writing condition participates."
- Branch missing: "No selection branch is recorded for this field, so neither a
  selection nor any evaluation of other branches is available. Nothing is inferred
  in its place."

The summary section states `OBSERVED` for recorded values and
`SOURCE-VERIFIED DERIVATION — no per-branch runtime evaluations were recorded` for
comparisons. Tests assert these texts and assert the explorer never contains
"rejected at runtime" or "checked and rejected".

## 8. Citation states and discrepancies

Each emitted event is classified per field: `CITED` (in decision and/or
provenance), `NOT_CITED` (only when **both** records are complete), `UNKNOWN`
otherwise — completeness is derived from the response, never guessed. Discrepancy
notes (branch order anomalies, decision/provenance mismatches) all end with
"neither value has been overwritten." Missing-decision and missing-provenance
probes verify: provenance alone still cites (via decision), decision alone still
cites, `uncited` stays 0 without both records, and remaining events become
UNKNOWN.

## 9. Item alignment (list fields)

When a list field's decision count, message count and provenance records all
match, the explorer derives alignment honestly (`itemAlignment.available`) and
labels it "SOURCE-VERIFIED DERIVATION … count-checked field-level provenance, not
a runtime per-item log". Selecting an item shows the aligned Rule ID, condition,
evidence type and limitations. Single-message fields state alignment does not
apply; empty/missing/mismatched cases show the written reason instead
(`unavailable`). Observed states in the browser run: `not-applicable` (Current
Goal, Primary Feedback, Next Step), `available` (What's Working for all three
samples; Needs Attention for Body/Conclusion), `unavailable` (intro Needs
Attention — empty list; and What's Working without provenance in the probe).

## 10. Writing Tutor display model

Node E mirrors the existing presentation model only: `PREPARED_LESSON`,
`NEUTRAL_REVIEW`, `GENERAL_REVIEW`, `SECONDARY_LESSONS`, `NO_SECONDARY_LESSON`,
`LIST_DISPLAY_ONLY`, `NOT_MAPPED`, `NEXT_STEP_DISPLAY`, plus the exact tutor
sections and highlight context (or the explicit "No highlight is shown for this
field…" note). Statuses are asserted against `studentFeedbackPresentation` in the
frontend tests.

## 11. Cross-links

Six disclosures reuse the same explorer without any request:
five field panels (`engine:goal|primary|working|attention|next`) each with one
"… — open the visual decision flow" button, and `engine:provenance` with five
(one per field) — **10 buttons total**. Clicking activates Overview, selects the
field and scrolls/focuses the selector. Verified in both the fake-DOM tests and
the real browser.

## 12. Read-only guarantees

Verified by three independent layers: response object deep-equal unchanged,
`JSON.stringify(state)` unchanged, `__analysisCalls` and `__writes` counters
unchanged across model building, field/node/item switching, cross-links,
screenshots and the missing-provenance probe; the harness records zero analysis
requests during inspection (boot requests are snapshotted separately).

## 13. Automated tests (pytest)

`tests/test_feedback_decision_flow.py` (3 tests, all passing):

1. `test_feedback_flow_field_records_exist_in_real_responses` — every fixture
   response has all five fields with non-empty `selection_branch` and consistent
   `selected_message_count`.
2. `test_feedback_flow_model_states_nodes_and_read_only` — per case × 5 fields:
   node keys/edges, branch parity, purpose coverage, exact values/messages,
   citation partitions and completeness rules, priority sentences, six-question
   rows, tutor statuses, item-alignment invariants, DOM structure (45 sub-tabs,
   one explorer, 4 connectors, single pressed node, exact output text, item
   selector show/hide, 10 cross-link buttons, state/response/calls unchanged).
3. `test_feedback_flow_branch_contrasts_tutor_honesty_and_missing_records` —
   branch contrasts, WordNet never CITED, §7 conditions table/NEUTRAL_REVIEW/no
   highlight, SKIPPED rows after the selected branch, and probes for deleted
   decisions, deleted provenance, count mismatch, order flip and an empty stage.

Full suite: **512 passed** (509 baseline + 3 new). `node --check static/app.js`
and `node --check tests/transparency_browser_check.cjs` both pass.

## 14. Real-browser verification

`verifyFeedbackDecisionFlow()` added to `tests/transparency_browser_check.cjs`
(called after `verifyRuleDecisionTrees`). Final run: **exit 0,
`javascriptErrors: []`** (49 checks total, verification.json). It asserts, in real
Chrome: 45 sub-tabs, exactly one explorer in `engine:overview`, default field
Primary Feedback, field-option list, five nodes with one pressed, connector/edge
parity with tooltips, per-field branch parity with the response, six questions and
`Source:` per node, exact output text, item alignment with aligned Rule ID +
"not a runtime per-item log", cross-links landing on Overview with the right
field, 10 link buttons, state/calls/writes unchanged, and mobile layout
(single-column, stacked non-overlapping nodes, no overflow).

Missing-provenance probe (real DOM): `unknown=9, cited=1, uncited=0`,
`listAlignment=unavailable` with a written reason — UNKNOWN is shown, NOT_CITED is
never invented, no requests.

Body sample uncited events visible under node A (evidence for §7 below):
`BODY.P1.PARAGRAPH.SEGMENTED`, `BODY.P1.PARAGRAPH.FOCUS_TERMS_OBSERVED`,
`BODY.P1.TOPIC_SENTENCE.CANDIDATE`, `BODY.P1.UNITY.SENTENCE_PAIR_1_2`,
`BODY.P1.REPETITION.*` (2), `BODY.INTRO_CONTINUITY.LEXICAL_COMPARISON`,
`BODY.INTRO_CONTINUITY.WORDNET_CANDIDATES`, `BODY.GOAL.DEVELOP_BODY_IDEAS`,
`BODY.LIMITATION.NO_SEMANTIC_VALIDATION`.

Recorded Primary branches in the run: Introduction
`possible_incomplete_subordinator`, Body
`first_paragraph_without_additional_clause_candidate`, Conclusion
`unobserved_prior_concepts`.

## 15. Finding reported (not fixed — selection weakness)

**§7 `body_generic` has no Paragraph-2 highlight.** Its Needs Attention Primary
message cites only `BODY.LIMITATION.NO_SEMANTIC_VALIDATION`; the second body
paragraph has two clause candidates, so `BODY.P2.SUPPORTING_DETAIL.NOT_OBSERVED`
is never emitted, the tutor mapping stays `NEUTRAL_REVIEW` with no
`excerpt.contexts`, and the Writing Tutor shows no highlight for that field. The
flow displays this honestly (tutor node: status `NEUTRAL_REVIEW`,
"No highlight is shown for this field…"). Fixing it would require backend
selection changes, which are out of scope for Phase 2.

## 16. Files changed and how to run

Changed (frontend/tests/docs only):

- `static/app.js` — Process 07 block (model, purposes, explanations, renderers,
  `renderFeedbackDecisionFlow`, `renderFeedbackFlowEntries`) + mount at :2151
- `static/style.css` — `.feedback-flow-*` styles + 760px media query (:999–1029)
- `tests/test_feedback_decision_flow.py` — new permanent tests (3)
- `tests/transparency_browser_check.cjs` — `verifyFeedbackDecisionFlow()` + call
- `docs/feedback_decision_flow_report.md` — this report

Run:

```
.venv\Scripts\python.exe -m pytest -q --tb=short
.venv\Scripts\python.exe -m pytest tests/test_feedback_decision_flow.py -q
node --check static/app.js
.venv\Scripts\python.exe -B tests/transparency_browser_check.py
```

Screenshots (fresh temp dir per run, printed as `Artifacts:`; kept copy from the
green run: `C:\Users\My Pc\AppData\Local\Temp\opencode\process07-artifacts\`):

| File | Content |
|------|---------|
| `feedback-flow-intro-desktop.png` | Introduction flow, all five nodes |
| `feedback-flow-body-desktop.png` | Body flow |
| `feedback-flow-conclusion-desktop.png` | Conclusion flow |
| `feedback-flow-uncited-event-desktop.png` | Node A with open NOT CITED disclosure (incl. WordNet) |
| `feedback-flow-missing-provenance-desktop.png` | Deleted-probe provenance → UNKNOWN disclosure |
| `feedback-flow-mobile-summary.png` | 390px single-column layout + "Why was this feedback selected?" summary |
