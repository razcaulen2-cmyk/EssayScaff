# S5.1 refinement — direct beginner-friendly scaffolding feedback

## A. Initial inspection

The student workspace already has Your Goal → What to Check → Your Next Step,
with secondary feedback behind Show more feedback. The preceding S5.1 added an
optional Help Me Understand launcher and five-section reading panel. Its content
and eight branch bindings are in `content/lessons/feedback_help.json`, loaded by
`services/tutoring_lessons.py` and embedded by the existing homepage route.

FeedbackService's `generate`, `generate_body` and `generate_conclusion` select
original messages using stage findings and emitted Rule Events. Their recorded
Primary Feedback branch, selected message and Rule IDs are available through the
existing student transparency trace. Flask compacts provenance to field/Rule ID
links but preserves the full events. `runStageAnalysis` checks request IDs,
assignment/input snapshots and active stage/view before caching/rendering results.

The existing Model–Practice–Reflect Introduction lesson, its IES/SRSD metadata,
questions, reflection and progression behavior are separate and preserved.
The technical dashboard has eight main tabs and 45 sub-tabs after the prior
related-concept work; those processing/evidence views remain available.

Baseline: **386 passed**, 0 failures/skips, 72.27 seconds.

## B. Reviewed instructional mapping

Labels are teaching/review focuses, **not NLP quality classifications or scores**.
Each mapping is explicit, checked against the selected branch/message/event
provenance, and has its own prepared rationale. Nothing is categorized from stage
alone. The nine supported branches are retained:

| Recorded branch | Writing dimension / skill | Actual basis and interpretation limit |
|---|---|---|
| INTRODUCTION: possible_incomplete_subordinator | Clarity · Sentence Completion | A listed SCONJ (e.g. "Because") was recorded with a mark dependency whose parser head is the sentence's only finite ROOT clause. This may mean the sentence is a reason clause with no main statement. Parser attachment can be wrong; the heuristic does not prove the sentence is grammatically incomplete. |
| INTRODUCTION: central_clause_without_multiple_clause_candidate | Clarity · Main Point | Root-clause candidate exists; structural elaboration threshold not met. The existing message asks main-point review; a clause does not establish thesis clarity. |
| INTRODUCTION: one_sentence_specific_focus_without_root_candidate | Clarity · Main Point | Specific focus wording matched, no central root candidate and sentence count ≤1. The teaching question follows the selected main-point review, not a finding that a thesis is absent/unclear. |
| INTRODUCTION: no_root_subject_predicate_candidate | Clarity · Main Point | Recorded root-candidate absence after higher-priority checks and outside the concise fallback. Absence under this parser heuristic does not prove a missing or unclear point. |
| INTRODUCTION: central_clause_with_multiple_clause_candidates | Coherence · Point and Reason | Central candidate plus STRUCTURAL_ELABORATION_CANDIDATE. The backend requests point/reason connection review, but does not identify a verified reason or assess logical support. |
| BODY: first_paragraph_without_additional_clause_candidate | Structure · Supporting Details | One sentence-bearing substantive paragraph has no structural detail candidates (fewer than two qualifying clauses). This motivates paragraph-development review, not a judgment of actual support quality. |
| BODY: first_unlinked_adjacent_paragraph_pair | Coherence · Connecting Ideas | A returned adjacent-paragraph pair has no shared content lemma or listed transition. These are lexical signals, not a measure of logical coherence. |
| CONCLUSION: closure_structure_candidate | Structure · Conclusion | Final root-clause candidate or closing expression. This motivates review of an ending's purpose, not a conclusion-quality finding. |
| CONCLUSION: synthesis_structure_candidate | Structure · Conclusion Alignment | A clause-bearing sentence has at least two normalized concept forms observed in supplied earlier sections. This supports a review of return to earlier material, not verified semantic alignment or synthesis. |

Other branches remain unlabelled with original feedback, including no-focus/input
cases, unreviewed list/subordinator/repetition branches, general Body feedback,
and Conclusion unobserved-prior-concept feedback. Lexical absence, repetition or
new wording is not automatically converted into a clarity/coherence/structure
finding. Missing trace or inconsistent provenance also retains original feedback.

## C. Implementation

The existing catalog is version 2. Six small `inline_guidance` profiles contain
one goal, one review question, one concept explanation, one action and a brief
limitation. The five pre-existing profiles contain **40–44 instructional words**
and the added sentence-completion profile contains **47 instructional words**
across the three main sections, excluding headings and the short limitation.
Longer preceding lesson definitions/questions remain in the resource as a
content/research reference, but are not rendered as a separate workspace
reading activity.

`selectScaffoldingGuidance` reuses the prior exact stage/field/branch lookup and
message/event/provenance consistency checks. It does not re-evaluate conditions,
reorder feedback or run NLP. `studentFeedbackPresentation` is one read-only model
used by all three consumers:

1. Writing Feedback: one dimension/skill label and the existing three paragraphs.
2. Transparency: original/backend versus exact displayed text, mapping rationale,
   real supporting events/evidence, source and limitations.
3. Copy Full Analysis: the same complete presentation record, explicitly labeled
   as frontend teaching interpretation rather than an API/NLP decision.

The original five backend fields, event lists, evaluation traces and protected
hashes are not mutated. Prepared goal/next-step wording is a presentation for the
one selected Primary Feedback issue; original Goal/Next Step and their independent
backend decision branches remain preserved in the technical record. Secondary
feedback remains behind its existing native disclosure and keeps its open state.

Removed: Help Me Understand markup, open/close state, event handlers, five-section
renderer, old help styles and automatic-focus behavior. The student now needs no
additional interaction. The label and short limitation explicitly identify an
instructional focus, not a score. No modal, editor rewrite, extra request,
new detector, grade, fading/mastery logic or persistence was introduced.

Updated files:

- `content/lessons/feedback_help.json`
- `services/tutoring_lessons.py`
- `templates/index.html`
- `static/app.js`
- `static/style.css`
- `tests/test_feedback_help.py`
- `tests/test_workspace_frontend.py`
- `tests/test_nlp_transparency.py`
- `tests/test_interface_views.py`
- `tests/transparency_browser_check.cjs`
- `docs/s5_1_guided_learning.md` (historical notice)

Created: `docs/s5_1_direct_feedback.md` (this reference/report).
No analysis endpoint, FeedbackService, Rule Base, model, topic/WordNet algorithm,
database schema, assignment/storage/authentication code or Teacher Inspector
source was changed in this refinement.

## D. Actual end-to-end traces

### D1. Point and reason (pre-existing mapping)

Environmental Protection Introduction:

> Single-use plastics are everywhere in our communities. Communities should
> reduce their use of these plastics because they can pollute rivers and harm animals.

The real installed spaCy pipeline returns 27 tokens, 24 alphabetic tokens and
2 sentences. Qualifying root predicates include `are` [20,23), AUX/VBP/ROOT and
`reduce` [74,80), VERB/VB/ROOT, with linked subjects. Three supported clause
predicates are recorded: `are`, `reduce`, `pollute` [126,133), VERB/VB/advcl.

These observations appear in the emitted events:

- `INTRO.CLAUSE.SUBJECT_PREDICATE_CANDIDATE`
- `INTRO.DEVELOPMENT.MULTIPLE_CLAUSE_PREDICATES`

The actual Primary Feedback branch is
`central_clause_with_multiple_clause_candidates`; its recorded condition is a
central candidate plus STRUCTURAL_ELABORATION_CANDIDATE. The original message is:

> The checks found sentence patterns that may state a point and give a reason.
> Check that the reason explains the point.

The approved catalog binding selects the instructional focus **Coherence · Point
and Reason**, not an NLP coherence score. Exact displayed guidance (44 words):

- **Your Goal:** Help readers understand your point and reason.
- **What to Check:** Check whether your reason explains your point. A point states
  what you believe; a reason explains why you believe it.
- **Your Next Step:** Read them together and explain their connection in your own
  words if a reader might miss it.

Exact displayed limitation:

> Writing focus, not a score. Sentence patterns do not prove that a reason supports a point.

Feedback Engine → Primary Feedback exposes all nine requested trace elements,
including exact original/displayed text, `supporting_rule_events` with actual
evidence/spans, binding rationale and catalog file/version/content ID. Final
Feedback also distinguishes displayed text from the five original backend fields.
Copy uses `frontend.studentFeedbackPresentation (prepared catalog + selected-stage
response)` as an explicitly frontend-derived source path. No semantic judgments
or evidence spans are invented.

### D2. Incomplete subordinator (added mapping)

Original student Introduction:

> Throwing away plastic waste on communities is very harmful in the environment.
> Because it can effect rivers, animals, plants ect.

The second sentence parses as: `Because` [79,86) SCONJ/IN/`mark` whose parser head
is `effect` [94,100) VERB/VB/`ROOT`; `it` is its `nsubj`; `can` is `aux`. The
sentence's only finite ROOT clause predicate is `effect`, so the recorded
`head_is_only_root_clause` condition is met and the rule fires with evidence
`Because` (SCONJ, `mark`, `predicate_starts_in_sentence` [94, 125]).

Emitted event: `INTRO.CLAUSE.POSSIBLE_INCOMPLETE_SUBORDINATOR` (triggered).
Recorded Primary Feedback branch: `possible_incomplete_subordinator`; original
message: "The sentence may be unfinished after 'Because'. Add the rest of the
thought so readers can follow it."

The approved catalog binding selects **Clarity · Sentence Completion**. Exact
displayed guidance (47 instructional words) **as first implemented**:

- **Your Goal:** Introduce the assignment topic, then tell readers the main point
  you plan to explain.
- **What to Check:** Your sentence beginning with 'Because' may be incomplete.
  'Because' introduces a reason that usually needs a complete main statement.
- **Your Next Step:** Check whether your reason can connect to the previous
  sentence or needs a complete main statement.

> **Superseded (2026-10-19):** the Because-specific What to Check / Next Step
> wording above assumed every trigger was "Because" and asserted a causal
> relationship that the rule does not establish (any of the thirteen listed
> subordinators can fire the branch). It was replaced by marker-verified,
> relationship-neutral wording; see §H.

Exact displayed limitation:

> Writing focus, not a score. A parser attachment cannot prove that a sentence is
> incomplete; check the sentence yourself.

The original five backend fields, the emitted event and its evidence spans are
unchanged; only the student-facing presentation and its transparency/export
record carry the new instructional text.

## E. Verification

- Baseline full suite (prior session): **386 passed**, 72.27 s.
- Prior final full regression: **392 passed**, 0 failures/skips, 71.87 s.
- This refinement focused S5.1 checks: **27 passed**, 6.23 s.
- This refinement full regression: **395 passed**, 0 failures/skips, **69.91 s**.
- `node --check` passed for application and browser-test JavaScript.
- Existing protected Introduction analysis/feedback hash remains unchanged
  (`78811fc8…`); the subordinator input is a different Introduction text and is
  not covered by that fixture.

Detector inspection (no NLP change made): the rule fired via the documented
`head_is_only_root_clause` condition, not a defect. Correcting the spelling to
"affect … etc." still fires, confirming spelling did not cause the trigger. A
complete mid-sentence reason ("Communities should reduce plastic waste because it
can affect rivers and animals.") and an initial reason with a following main
clause ("Because communities reduce plastic waste, rivers stay cleaner.") do not
fire. One clean initial-reason sentence ("Because plastic waste harms rivers,
communities should reduce their use of it.") does fire, because the parser
attaches `Because` to the ROOT `reduce` instead of the advcl `harms`; the rule's
own limitation already covers parser-attachment error.

Tests additionally exercise all nine bindings using real isolated API outputs,
the exact student-facing subordinator wording, unmapped/clean branches, missing
or corrupt provenance, catalog failures, safe literal HTML-shaped strings,
assignment/stage changes, exact copied presentation records, unchanged
draft/state/timer counts and preserved original Model–Practice–Reflect behavior.

Limitations: only the nine reviewed branches have concise prepared text; labels
are instructional associations, not measurements. Missing trace leaves original
feedback. Resource edits require restarting the cached loader. The incomplete-
subordinator rule can misfire when the parser attaches a initial subordinator to
the main-clause verb; this is a known parser limitation, not changed here. Mobile
checks use emulation, not a physical device or screen-reader audit. No S5.2
highlighting, new quizzes, automatic fading, scores, analytics or AI models were
added. Software tests establish functioning and traceability, not improved
learning. Student learning outcomes still require educational review and
empirical study.

## F. Controlled Transparency documentation correction (2026-10-19)

Authorized, documentation-only correction of the Transparency Mode rule
description for `INTRO.CLAUSE.POSSIBLE_INCOMPLETE_SUBORDINATOR`. No NLP rule,
threshold, parser behavior, Rule Event, feedback selection, stage gate or
student-facing S5.1 content was changed.

### Why the protected hash required an authorized re-pin

The human-readable description is not display-only metadata: `RULE_SPECS`
condition and `_rule_configuration` strings flow through `_rule_spec` →
`rule_inventory` → `build_rule_evaluation_trace` into
`analysis.rule_evaluation_trace`, which is part of the protected analysis/
feedback/decision-trace payload hashed by
`tests/test_nlp_transparency.py::test_exact_plastics_introduction_preserves_prechange_observations_and_feedback`.
Correcting either string therefore changes the payload hash by design.

### Authorized field changes (services/research_inspector.py only)

1. `RULE_SPECS["INTRO.CLAUSE.POSSIBLE_INCOMPLETE_SUBORDINATOR"].condition`
   (was: "An SCONJ lacks expected mark dependency or its head is not a
   parser-labeled clause predicate.") now documents all five OR conditions:
   unattached ROOT marker; mark with non-clause-predicate head; mark whose head
   is the sentence's only finite ROOT clause predicate
   (`head_is_only_root_clause`); prep with no pobj/obj complement; and "because"
   as prep with only a nominal pobj and no later predicate.
2. `_rule_configuration("INTRO.CLAUSE.POSSIBLE_INCOMPLETE_SUBORDINATOR")`
   (was: "POS must be SCONJ; flag when dependency != mark OR head_start is not a
   clause-predicate start.") now records the exact SCONJ/CLAUSE_SUBORDINATORS
   gate, the five OR conditions with their constants, and the observation-not-
   proof caveat.

### Protected-output comparison

The protected payload for the pinned Environmental Protection Introduction
fixture was captured before and after the edit via the exact hash-test
construction (`protected = {analysis, feedback, feedback_decisions}`, sorted
compact JSON). Field-by-field diff result: **exactly 2 changed paths**,
`$.analysis.rule_evaluation_trace[1].condition` and
`$.analysis.rule_evaluation_trace[1].configuration` — the two authorized
fields on the `INTRO.CLAUSE.POSSIBLE_INCOMPLETE_SUBORDINATOR` trace row. The
`feedback` and `feedback_decisions` objects were byte-identical. No other
protected value differed.

### Hash values

- Original (preserved for the record, asserted through 2026-10-19):
  `78811fc86728b7643ee155eeb260921d136635b4602373af5e57abe853b7f6de`
- Second (pinned after the §F documentation correction):
  `c73bd8844acd37c69007f0fc54741f84de33ee7c3619882d0156845f229aba6b`
- Current (pinned after the §I subordinator safeguard, approved 2026-10-19):
  `448e642716afa25286b9202d9265aebe60b6438301ec0f0008ccf4bf05727967`

The pinned assertion was updated only after the comparison confirmed the two
intended field changes; no test was weakened, skipped or disabled.

### Display and feedback verification

A temporary DOM check (removed after running) fed the real subordinator input
("…Because it can effect rivers, animals, plants ect.") through the app.js
workspace harness and confirmed: the corrected condition and configuration text
render in Transparency Mode (Rule Evaluation Trace table and per-rule
detail); the Copy Full Analysis report contains the corrected text; the old
incomplete condition string no longer appears; the student Writing Feedback
panel shows the unchanged S5.1 wording and contains no internal identifiers;
and the response object is not mutated. The existing Node copy-action
regression additionally deep-equals `analysis.rule_evaluation_trace` into the
copied report record.

### Known parser false positive (superseded by §I safeguard)

The complete sentence "Because plastic waste harms rivers, communities should
reduce their use of it." formerly fired the rule because spaCy attaches `Because`
as `mark` of the ROOT `reduce` instead of the advcl `harms`, satisfying
`head_is_only_root_clause`. This was the parser-attachment limitation recorded
above (§E and Limitations). The detector has since been corrected with an
evidence-based safeguard; see §I.

### Verification

- Focused: `tests/test_nlp_transparency.py`, `tests/test_feedback_help.py`,
  `tests/test_research_inspector.py` — **41 passed**.
- Full regression after re-pin: **395 passed**, matching the verified starting
  baseline, 0 failures/skips.
- No S5.2 work, new dependencies, commits or pushes were made.

## G. NLP model limitation — misspelled abbreviation "ect" (2026-10-19)

Investigation of the original student input ("…Because it can effect rivers,
animals, plants ect.") with the installed `en_core_web_sm` model confirmed:

- spaCy predicts `ect` [125,128) as **VERB / VBP / conj** (head `rivers`) and
  `plants` [118,124) as **NOUN / compound** (head `ect`). Linguistically the
  student intended "etc."; with the corrected spelling ("…plants, etc.") spaCy
  correctly predicts `etc` as **X / FW / conj**. The mis-tagging is a model
  error on the misspelled abbreviation, not an EssayScaff transformation.
- EssayScaff preserves spaCy's annotations byte-identically: every reported
  token (text, POS, tag, dependency, character offsets) matched raw spaCy
  output for the original input and four controlled comparison cases
  (original spelling; corrected spelling; complete mid-sentence reason;
  known parser false positive).
- `ect` is **not** counted as a clause candidate: `_clause_candidates`
  requires VERB/AUX + finite tag + clause dependency + a dependency-linked
  subject; nothing attaches a subject to `ect`. Clause counts, central
  direction candidates, development status (`predicate_count`), emitted Rule
  Events and FeedbackService branch selection are therefore unaffected by the
  `ect` mis-tag. The incomplete-subordinator rule on this input fires solely
  via `head_is_only_root_clause` on the ROOT verb `effect` [94,100).
- Nuance recorded honestly: the rule's internal `predicate_starts` set
  (VERB/AUX + clause-dependency label, no subject required) does include a
  conj-linked verb, so `ect` appears in the informational evidence field
  `predicate_starts_in_sentence: [94, 125]`. For the observed inputs this did
  not change any condition outcome (the `head_is_only_root_clause` condition
  keys on the sole finite ROOT at 94; `root_predicate_starts` is `[94]`).
- Uncertainty is already communicated: the rule limitation states "This may be
  a parser error or an unusual construction; inspect the actual wording", the
  evidence limitation states "Parser attachment can be wrong", and the stage
  limitation states that parser observations do not establish meaning.

**Decision:** documented as a model limitation. No POS guard, hardcoded tag or
annotation replacement was added: the unreliable prediction does not cause an
inappropriate rule decision, so any "fix" would be speculative NLP logic
change rather than the smallest defensible correction. spaCy's original
predictions remain faithfully reported in Transparency Mode.

## H. Marker-verified subordinator guidance repair (2026-10-19)

### Root cause

The prepared `HELP-SENTENCE-COMPLETION` lesson hard-coded "Because" and a
causal ("reason") explanation for every `possible_incomplete_subordinator`
trigger. The branch fires for any of the thirteen `CLAUSE_SUBORDINATORS`
(although, as, because, before, if, once, since, though, unless, until, when,
whereas, while), so "Although communities reduce single-use plastics." was
incorrectly explained as a "Because … reason" sentence. The catalog's
`mapping_basis` also asserted a single condition (`mark` head = sole finite
ROOT) although the rule has five alternative conditions.

### Repair

- Catalog: neutral dependent-clause wording; `marker_question` template with a
  single `{marker}` slot; relationship-neutral explanation and next step; the
  binding's `mapping_basis`/`noticed` now describe all five alternative
  conditions without asserting which fired.
- Frontend (`studentFeedbackPresentation` → `verifiedScaffoldingSubordinator`):
  a marker is named only when **one** emitted rule-evidence item is
  cross-verified against the analyzed input (`linguistic_observations.text`,
  Python code-point offsets converted with `Array.from`, token POS/dependency,
  sentence span, and the stage finding). Zero, multiple, contradictory, or
  out-of-range markers take the generic question with no conjunction named.
  Existing optional `matched_conditions` evidence is passed through verbatim
  in the presentation record and Transparency disclosure; it is never
  inferred. No new NLP call, no backend change, no protected payload change.
- Student-facing result: "The clause with 'Although' may be incomplete. A
  dependent clause needs a complete main statement to finish the thought." /
  "Check whether this idea connects to a complete main statement. Make the
  connection in your own words." The backend message keeps its own recorded
  marker ("The sentence may be unfinished after 'Although'. …").

### Cleanup

The already-removed Help Me Understand interface left one obsolete runtime
dependency: `load_feedback_help` still validated the old panel's long-form
`definitions` / `why` / `questions` / `revision_task` fields. Validation was
trimmed to the fields the current concise interface actually consumes
(`lesson_id`, `title`, `limitation`, `inline_guidance` + the new marker-slot
check); the long-form fields remain in the catalog as retained reference
content. No files were deleted: the old panel's markup, handlers and CSS were
already absent (verified by project-wide search); `content/lessons/feedback_help.json`,
the historical `docs/s5_1_guided_learning.md`, the Model–Practice–Reflect
activity, Transparency Mode, research inspector and all protected-hash
history are active or provenance records and were preserved.

### Verification

- Focused: `tests/test_feedback_help.py` **28 passed** (all thirteen
  conjunctions exercised through the real API, Unicode offset case, multiple
  markers → neutral fallback, thirteen corruption/ambiguity fallbacks, Cases
  A–H, full trace/Copy-report agreement, no extra requests, no stale feedback).
- `tests/transparency_browser_check.cjs` updated for the new wording and an
  additional Although real-Chrome case.
- Protected payload: captured before/after via the exact hash-test
  construction; the pinned Environmental Protection hash is unchanged
  (`c73bd884…`) because the repair touches only the frontend presentation
  model and prepared catalog, not analysis, feedback or decision fields.

## I. Incomplete-subordinator false-positive safeguard (2026-10-19)

### Root cause

`INTRO.CLAUSE.POSSIBLE_INCOMPLETE_SUBORDINATOR`'s `head_is_only_root_clause`
condition (services/introduction_rules.py) fires when a `CLAUSE_SUBORDINATORS`
token has `mark` dependency and its head is the sentence's sole finite ROOT
predicate. For "Because plastic waste harms rivers, communities should reduce
their use of it." spaCy attaches `Because` as `mark` of the ROOT `reduce`
instead of the advcl `harms`. The parse already contains both clause
structures — `harms` (advcl, subject `waste`) and `reduce` (ROOT, subject
`communities`) — but the rule treated the marker's ROOT attachment alone as
evidence of an incomplete subordinate clause. The issue is an interaction: a
faithful spaCy prediction (the misattachment) consumed by an insufficient
custom heuristic.

### Safeguard

A 20-line deterministic check was added inside
`_incomplete_subordinator_evidence`. When `head_is_only_root_clause` would
fire, the rule now also verifies whether the same sentence contains a separate
finite subordinate-clause predicate (dependency in `advcl`/`ccomp`/`xcomp`,
tag in `FINITE_TAGS`) carrying its own parser-labeled subject. If such a
predicate exists, the two-clause structure is already observed in the parse
and the marker's ROOT attachment is treated as a likely parser misattachment —
the warning is suppressed. `conj` and `relcl` are deliberately excluded so
coordination or relativization inside a dependent clause (controlled cases A4
and C2) still triggers the warning.

### Research inspector

The rule's `condition` string and `_rule_configuration` description were
updated to document the safeguard (research_inspector.py:412, 565).

### Protected hash re-pin (authorized)

Old `c73bd8844acd37c69007f0fc54741f84de33ee7c3619882d0156845f229aba6b`
→ New `448e642716afa25286b9202d9265aebe60b6438301ec0f0008ccf4bf05727967`.
Diff: 17 paths, exclusively `rule_evaluation_trace[*].condition`,
`.configuration`, and `.implementation.start_line`/`.end_line`. After stripping
those four metadata fields the analysis results are byte-identical — the
PLASTICS fixture does not trigger the subordinator rule, so its analysis,
feedback and decisions are unchanged. Approved 2026-10-19; the previous hash
is preserved in the assertion comment and in §F above.

### Downstream correction

For the confirmed false-positive sentence, `_development_finding` no longer
filters its clause candidates: `predicate_count` restored 0 → 2 and the status
changed from `NO_ADDITIONAL_CLAUSE_ELABORATION_OBSERVED` to
`STRUCTURAL_ELABORATION_CANDIDATE` through the existing logic unchanged. No
Rule Event (`INTRO.CLAUSE.POSSIBLE_INCOMPLETE_SUBORDINATOR`) is emitted for
suppressed sentences; the feedback decision naturally falls through to
`central_clause_with_multiple_clause_candidates`.

### Pre-existing limitation (documented, not expanded)

"When people reduce plastic waste." does not trigger the rule: spaCy attaches
`When` as `advmod` (tag `WRB`) rather than `mark`, and the rule only inspects
`mark` for the ROOT-attachment conditions. This gap predates the safeguard and
is recorded in tests/test_subordinator_safeguard.py; fixing it would expand
the detector beyond this phase's approved scope.

### Rule Event enrichment status

The previously proposed `matched_conditions` / `head_*` /
`root_predicate_starts_in_sentence` evidence-enrichment has **not** been
implemented in the running backend. The rule evidence dict still carries only
`sentence_index`, `text`, `start`, `end`, `pos`, `dependency`,
`predicate_starts_in_sentence`, `evidence_type` and `limitation`.
`tests/test_feedback_help.py` injects `matched_conditions` as a fixture to
verify the frontend passes it through verbatim; the backend never emits it.
Reported as-is; no expansion in this phase.

### Verification

- Focused: `tests/test_subordinator_safeguard.py` **39 passed** (all
  Section 7 controlled cases, the "ect" artifact, 12/13 conjunctions,
  Unicode offsets, unit-level parse-pattern checks).
- Full regression without exclusions: **435 passed**, 0 failed (after the
  authorized re-pin).
- No spaCy annotation was modified; no unrelated detector was changed; no
  S5.2 work, new algorithms, commits or pushes.
