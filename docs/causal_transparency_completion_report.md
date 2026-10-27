# Causal Transparency Overhaul - Completion Report (Part 9)

Date: 2026-10-21. Project: `C:\Users\My Pc\Desktop\EssayScaff-V2` (not a git repository).

## 1. Before/after 45-panel audit

Full matrices, source findings and the unavailable-evidence table are in `docs/causal_transparency_audit.md`.

- Before: A missing on 40 panels; B partial on 44; D and F missing on final:limitations; E missing on 3 panels; G partial on 44; H partial on 42.
- After: A/B/C/D/F/G/H complete on all 45 panels. E complete on 41 panels; 4 residual partial cells (backend:validation, backend:response, backend:flow, nlp:pipeline) each shown in the UI as NOT RECORDED with its origin, matching rows of the unavailable-evidence table. No missing log was replaced with an invented execution claim.
- Every panel now renders causal rows "A - Original essay", "B - Actual component input", "C - Purpose", "D - Processing", "E-F - Why / recorded result", "G - Actual use", "H - Why the conclusion is limited" plus an expandable technical walkthrough.

## 2. Files changed by this overhaul

| File | Change |
|---|---|
| `static/app.js` | Only production file edited. Evidence taxonomy (SOURCE_VERIFIED, NOT_APPLICABLE), causal layer (Section 3), causal block + missing-evidence disclosure for all 45 panels, corrected process-information labels (section 4/10), SOURCE_VERIFIED handoff/consumption wording, one Part 5 correction (topic:wordnet `how`). |
| `tests/causal_transparency_cases.json` | New: 13 real cases (intro presence/incomplete/list/before, body mixed/wordnet/generic, conclusion rewording/new, punctuation-only, missing context, CRLF and LF Unicode). |
| `tests/test_causal_transparency.py` | New: 14 permanent tests (13 parametrized integrity tests + 1 Node scenario rendering all 45 panels). |
| `tests/transparency_browser_check.cjs` | Added `verifyCausalWalkthroughs` (real authenticated API calls, 45 panels, 6 panel-type content checks, read-only inspection, 16 screenshots, empty-text 400 probe) and a narrow exemption so the deliberate 400 probe is the only expected network log entry. |
| `tests/transparency_browser_check.py` | Node timeout 180s -> 300s for the larger check. |
| `docs/causal_transparency_audit.md` | Before matrix, source findings, unavailable-evidence table, new after matrix with residual-partial reasons. |
| `docs/screenshots/` | 16 causal walkthrough screenshots (8 panels x desktop 1440 / mobile 390) + `causal-cases.json` (case branches and emitted events). |
| `docs/causal_transparency_completion_report.md` | This report. |

No other production file was touched: no service, no Python backend, no stylesheet (the causal block reuses the Phase 1 `.transparency-section` / `.student-input-inspector` styles, including the existing 1-column mobile grid; Chrome verified no horizontal overflow at 390px on every screenshot).

## 3. Reusable components (all in `static/app.js`)

| Component | Responsibility |
|---|---|
| `transparencySection`, `transparencyDisclosure`, `transparencyText`, `transparencyExpandable` | Existing two-level scaffold: always-visible summary + native `<details>` disclosure. |
| `causalFacts`, `causalValue`, `causalSpan` | Label/value/source rows; undefined -> NOT RECORDED; verified Unicode code-point span slices. |
| `transparencyEvidenceTypeTag`, `TRANSPARENCY_EVIDENCE_TYPES` | OBSERVED, DERIVED, SOURCE-VERIFIED LOGIC, STATIC EXPLANATION, SKIPPED, NOT APPLICABLE, NOT RECORDED, REPORT ONLY. |
| `causalPanelModel` / `renderCausalPanel` | Per-panel A-H model and renderer; inserts the causal block into every sub-panel and opens the technical disclosure (`causalDetails`). |
| `causalMissingEvidence` | Per-process list of records the source never retains, rendered as NOT RECORDED rows with origin. |
| `causalRuleModel` / `renderCausalRule` | Per Rule Event: measured comparison, event parity, alternatives, provenance links, informational usage for WordNet. |
| `causalSubordinatorConditions` / `renderCausalSubordinators` | All source conditions and safeguards for each SCONJ marker, compared with the recorded candidate. |
| `renderCausalStageObservations`, `renderCausalParagraphs` | Stage finding producer -> criteria -> observed value -> consumer walkthroughs (per stage, per paragraph). |
| `renderCausalLimits` + `CAUSAL_SCOPE_REASONS` | Uncertainty/prohibited-conclusion disclosures with origin and decision-effect. |
| `causalFeedbackPriority` / `renderCausalFeedback` | Priority rows for Primary/Next (selected branch passes, earlier rows false, later rows SKIPPED). |
| `causalIndependentFeedback` | Independent append-condition checks for What's Working / Needs Attention; passing-check count equals actual list size. |
| `renderCausalTutor`, `renderCausalAnnotations`, `renderCausalConcepts`, `renderCausalTopic` | Process-specific technical walkthroughs (tutor highlights, per-token annotations, concept groups, lookup records). |

## 4. Source functions behind each process (read-only references)

- Process 01 Student Text: `static/app.js studentTextInputEvidence`, `performStageAnalysis` (payload built client-side; snapshot checks before caching).
- Process 02 Flask Backend: `app.py require_account`, `require_csrf_token`, `analyze_payload`, `compact_student_transparency_trace`.
- Process 03 Text Processing: `services/nlp_service.py parse`, `analyze_doc`, `_token_data`.
- Process 04 Concepts: `services/topic_service.py _extract_concepts`, `_lemma`.
- Process 05 Topic: `topic_service.py prepare_teacher_context`, `_unique_focus_terms`, `_find_matches`, `_wordnet_status`, `_wordnet_suggestions`; `stage_evidence.py compare_stage_concepts`, `_wordnet_candidates`; `related_topic_concept_service.py match`.
- Process 06 Rule Base: `introduction_rules.py` / `body_rules.py` / `conclusion_rules.py` `analyze` + `_rule_events` + helpers (`_clause_candidates`, `_list_or_fragment_finding`, `_incomplete_subordinator_evidence`, `_development_finding`, `_paragraph_*`, `_synthesis_candidates`, `_closing_candidates`, `_new_material_observations`, `_missing_elements`); `research_inspector.py _observed_rule_decisions`, `build_rule_evaluation_trace`, `rule_inventory`.
- Process 07 Feedback: `feedback_service.py generate`, `generate_body`, `generate_conclusion`, `_emitted_rule_ids`.
- Process 08 Final: `static/app.js selectScaffoldingGuidance`, `selectTutorItems`, `buildTutorItem`, `tutorVerifiedSpan`, `studentFeedbackPresentation`, `buildFullAnalysisReport`.

## 5. Requested walkthrough examples

- INTRO.TEXT.PRESENT (`causalRuleModel`): path `analysis.text_presence.alphabetic_word_count`, observed `6`, required `count > 0`, comparison `satisfied`; paired alternative `INTRO.TEXT.EMPTY_OR_NONALPHABETIC`; summary sentence states the measured comparison, recorded status and event existence; source note states the event is emitted from the alphabetic count and is not a gate that makes later clause rules execute. Asserted in test (value 6, required "count > 0").
- INCOMPLETE_SUBORDINATOR (`causalSubordinatorConditions`): rows for SCONJ + configured marker eligibility, head-in-predicate-sets, the narrow before safeguard (verified sentence length/marker node, verified ADJ/JJ advcl head, separate finite ROOT with consistent heads, ROOT without mark dependent, verified subject for subordinate and main ROOT, conjunction), only-ROOT safeguard, separate finite advcl/ccomp/xcomp alternative, unattached-marker and bad-mark alternatives, prep without pobj/obj, because/prep alternative; then source-derived OR result vs the recorded candidate with an agreement row (a mismatch must be investigated, never used to overwrite the retained result). Asserted for every SCONJ token in every Introduction case: explanation agrees with the real detector.

## 6. Uncertainty and prohibited-conclusion origins

`renderCausalLimits` shows `analysis.uncertainty` and `analysis.prohibited_conclusions` as OBSERVED records produced unconditionally by `<Stage>RuleBase.analyze`'s return object, labelled methodological safeguards rather than detected errors. `CAUSAL_SCOPE_REASONS` maps each exact configured wording to (evidence it qualifies, why the broader reading is unsupported, capability that would be needed). Decision effect row: FeedbackService does not read these arrays; a separate `*.LIMITATION.NO_SEMANTIC_VALIDATION` event is what Body/Conclusion link to their scope caution. Conclusion has no `prohibited_conclusions` array and the UI states "ConclusionRuleBase.analyze does not configure this array; no catalog has been invented." Tests open every wording's disclosure and require "unconditional stage-scope statement" while forbidding the old "origin ... has not been verified" text.

## 7. Direct vs informational consumption examples

- Direct/lemma continuity is consumed: `generate_body` reads `introduction_to_body_continuity` availability and direct/lemma lists; `causalFeedbackPriority` shows status + match counts as the condition.
- WordNet is informational: every `*WORDNET*` rule row's usage starts "Informational Rule Event: the Rule Base retains the candidate; FeedbackService does not read WordNet candidates..."; the rules handoff row and panel G use SOURCE_VERIFIED wording stating the same. Case `conclusion_rewording` emits `CONCLUSION.CONTINUITY.BODY_WORDNET_CANDIDATE` while the selected branch is `synthesis_structure_candidate` driven by direct/lemma evidence; case `conclusion_new` selects `unobserved_prior_concepts` from unobserved concepts, not from paraphrase candidates. WordNet events are never treated as provenance for feedback messages.

## 8. Unrecorded evidence shown in the UI

Every panel's technical disclosure ends with "Evidence the implementation never retains" rows (NOT RECORDED + origin): exact HTTP payload; save/readiness state; per-field validation/authorization outcomes and handler timing; model-internal POS/lemma/head scores and component timings; rejected concept candidates; rejected lexical windows and word-sense disambiguation; full earlier-stage concept sets beyond compact findings; per-request short-circuit/evaluation log and subordinator safeguard flags; unselected candidate messages, item-by-item append log and hidden scores; highlight-omission reasons and item-level provenance mapping. The same items are tabulated with their producers in `docs/causal_transparency_audit.md`.

## 9. Part 5 static-vs-actual audit

All 29 `STUDENT_TRANSPARENCY_PROCESS_INFO` entries were checked against the Python source. Verified: Introduction does not consume concepts; `_find_matches` classifies windows direct/else-normalized (so lemma matches are never direct matches); `_unique_focus_terms` dedups by normalized lemma form; `essay_analysis_service.py` passes `include_wordnet=(stage == "CONCLUSION")`. One correction applied: `topic:wordnet.how` now states that the coordinator enables direct suggestions only for CONCLUSION and the Conclusion Rule Base passes `include_wordnet=True` for the Conclusion text while prior-section and Body analyses pass False. Section labels were corrected to "4. Retained essay context (not necessarily this component's direct input)" and "10. Navigation / source-defined next consumer (not observed usage)". `transparencyProcessExplanation` is confirmed dead code (rendering uses `transparencyExplanation`); it was corrected in place and no test references it.

## 10. Exact verification results

- Baseline before overhaul: `pytest -q` = 492 passed in 186.64s.
- Final: `pytest -q` = **506 passed in 67.98s** (492 pre-existing intact + 14 new causal tests; nothing weakened).
- `node --check static/app.js` and `node --check tests/transparency_browser_check.cjs`: OK.
- Chrome regression (`tests/transparency_browser_check.py`, Chrome/155 headless, isolated DB): pass, `javascriptErrors: []`. Preserved constraints: 8 main tabs, 45 sub-tabs, 27 token rows, 7 emitted events, 14 evaluation records, WHAT/HOW/WHY/WHERE labels on every panel, no analysis request when opening Transparency, tutor highlight checks, persistence counts all 0.
- New causal check in the same run: 13 real API cases, 45 causal panels with SOURCE-VERIFIED LOGIC + NOT RECORDED content, source-condition agreement for every SCONJ token, state/response/analysis-call immutability, empty Introduction returns HTTP 400 (never a fabricated analyzed response), 16 desktop/mobile screenshots (no horizontal overflow at 390px).
- Correlation artifact: `docs/screenshots/causal-cases.json` (case name, stage, selected Primary branch, emitted Rule IDs).

## 11. Protected logic and no-commit confirmation

- Production files edited by this overhaul: `static/app.js` only. No changes to NLPService, spaCy config, TopicService, WordNet matching, concept extraction, `stage_evidence`, any Rule Base, FeedbackService priorities, Research Inspector calculations, fingerprints/pins, drafts/auth/submission, or tutoring lessons.
- `tests/test_causal_transparency.py` hashes `app.py`, all `services/*.py` and `content/**/*.json` before and after running every real analysis through the Flask test client and asserts they are unchanged.
- All row-count and interface constraints from the existing suite remain green in the 506-test run.
- `C:\Users\My Pc\Desktop\EssayScaff-V2` is not a git repository: nothing was committed, and no push was attempted.
