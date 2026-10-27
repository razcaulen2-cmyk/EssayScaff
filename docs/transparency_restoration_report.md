# ESSAYSCAFF V2 — TRANSPARENCY DASHBOARD RESTORATION REPORT

Verified 2026-10-19 in `C:\Users\My Pc\Desktop\EssayScaff-V2`.

## 1. Status

**The analytical coverage recoverable from the retained student dashboard has
been restored alongside Copy Full Analysis.** The interface is titled **How
EssayScaff Analyzed Your Writing**. It has 15 numbered sections, a connected
interactive call/data-flow map, readable evidence tables, and expandable
structured records. Before analysis it explains eligibility; editing invalidates
the evidence, shows a STALE message identifying the previous analyzed text, clears
old tables and disables copying until a successful current analysis arrives.

The production changes are in frontend presentation only. No backend service,
Rule Base, threshold, WordNet algorithm, feedback selection/message, schema,
authorization, storage route or Teacher Research Inspector source was changed.
No package was installed; no Git repository, commit or push was created.

## 2. Verified Source-Code Processing Flow

The pre-UI investigation reference is `docs/transparency_process_map.md`. Its
operation map records input, operation, output, consumer, conditionality,
WHAT/HOW/WHY/WHERE and source functions.

```text
editor input -> state.drafts -> runStageAnalysis
  -> POST /api/analyze-stage, include_transparency_trace=true
  -> Flask account/CSRF checks -> analyze_stage -> analyze_payload
     -> authorized saved-assignment lookup OR practice topic/focus
     -> input validation -> EssayAnalysisService.analyze
        -> TopicService.prepare_teacher_context (shared across sections)
           -> explicit phrases: _unique_focus_terms -> loaded nlp(term)
           -> without phrases: nlp(topic) -> noun concepts -> phrase normalization
        -> TopicService.analyze for EACH supplied full section
           -> NLPService.parse -> loaded spaCy Language -> Doc
           -> NLPService.analyze_doc(Doc)
           -> _extract_concepts(Doc)
           -> _find_matches(Doc, prepared targets)
           -> conditional DIRECT WordNet suggestions (Conclusion only)
        -> each supplied stage's RuleBase.analyze(prepared results)
           -> stage helpers; reuse previous section results
           -> conditional compare_stage_concepts
              -> conditional CROSS-STAGE WordNet inside Body/Conclusion rules
           -> _rule_events -> completed stage analysis
        -> FeedbackService.generate / generate_body / generate_conclusion
        -> AFTER all stage feedback: build_rule_evaluation_trace
           -> rule_inventory + _observed_rule_decisions
     -> requested stage selection, student-response compacting -> jsonify
  -> JS request ID + assignment/input snapshot + stage/view checks
  -> state.analyses + state.analysisSnapshots -> displayFeedback
  -> Writing Feedback, visual dashboard and copy report use that cached result
```

The coordinator also analyzes supplied prior stages; the selected-stage response
does not return their complete analyses. Focus normalization calls spaCy
separately from full-section parsing. Sentence/token/lemma/POS/dependency/noun
chunk displays are educational views of shared observations, not independent
sequential application calls. The trace does not feed FeedbackService: it is
reconstructed afterward for inspection without rerunning rules or NLP.

## 3. Original Transparency Features Recovered

Recovery evidence: `STUDENT_TRANSPARENCY_SUBTABS`,
`STUDENT_TRANSPARENCY_PROCESS_INFO`, legacy renderers and evidence helpers still
existed in `static/app.js`. The template had lost `nlp-transparency-content`, and
`displayFeedback` no longer called its renderer. Existing S3.2 tests explicitly
required that absence and zero rendered dashboard children. Those obsolete
replacement assertions now require the dashboard to coexist with the copy action;
the complete evidence/export assertions were retained.

The retained inventory has **28 technical views** (8 + 7 + 6 + 7):

| Retained area | Recovered analytical views | New location |
|---|---|---|
| Text Processing (8) | Overview, spaCy Pipeline, Tokenization, Lemmatization, POS Tagging, Dependency Parsing, Noun Chunks, Concept Extraction | Sections 02–09 |
| Topic Matching (7) | Overview, Focus Terms, Normalization, Direct Matches, Lemma Matches, WordNet, Cross-stage Comparison | Sections 10–11 |
| Rule Evidence (6) | Overview, Triggered Rules, Not Triggered, Rule Conditions, Evidence & Thresholds, Code & References | Sections 12–13 and complete evidence index |
| Feedback Explanation (7) | Overview, Current Goal, Primary Feedback, What's Working, Needs Attention, Next Step, Provenance | Section 14 |

Source locations/references are displayed as metadata, not raw source listings.
No reliable dated pre-S3.2 snapshot or Git history was found in the selected
project. Exact historical appearance remains unverified; this restores the
retained code's analytical coverage in a redesigned layout.

## 4. New Dashboard Structure

The header identifies assignment question, selected stage, successful availability
and a browser-derived analyzed-text fingerprint (stage, character count, hash).
The fingerprint is explicitly not a saved revision ID. Copy stays alongside it.

The diagram uses labeled arrows and nested coordinator/TopicService/Rule Base
groups. Each node scrolls and focuses its corresponding evidence section.
Conditional direct WordNet status comes from the response. Cross-stage paths
have their own status table. A separate later inspection branch shows evaluation
trace reconstruction after feedback.

Sections: **01 Input; 02 Shared spaCy/pipeline; 03 Sentences; 04 Tokens;
05 Lemmas; 06 POS/tags; 07 Dependencies; 08 Noun chunks; 09 Concepts;
10 Focus normalization/matching; 11 WordNet/cross-stage; 12 Stage observations;
13 Evaluation trace/events; 14 FeedbackService; 15 Response and complete evidence.**

Tables scroll inside bounded containers. Main explanations use two desktop
columns and one mobile column. Evidence records use text nodes and lazy
disclosures, with no JSON/source-code blocks. A small mobile header wrapping fix
prevents existing account controls from expanding the layout viewport.

## 5. WHAT / HOW / WHY / WHERE Explanations

All 15 main sections contain the four explanations. Focus preparation,
normalization, direct matching and lemma matching have individual explanations.
Each rule's metadata and each feedback field has its own four-part detail.
Supported operations include:

- Request reception, assignment resolution, validation and eligibility.
- Shared teacher context, separate focus/topic parsing and deduplication.
- Loaded spaCy processing, tokenization, sentence boundaries, lemmatization,
  POS/fine tags, dependencies/heads and noun chunks.
- Noun concept grouping, extraction methods, positions and downstream consumers.
- Direct/lemma focus-window matching, multiword separators, unmatched targets,
  unique counts versus occurrence counts.
- Direct WordNet and separate cross-stage lexical/WordNet paths.
- Paragraph segmentation and span filtering without reparsing.
- Subject-linked finite clause candidates.
- Introduction central/context, fragment/list, subordinator and supported
  development observations.
- Body paragraph concepts, prominent candidates, focus evidence, topic-sentence
  candidates, detail candidates, adjacent-sentence lexical comparison, repeated
  surfaces/lemmas/openings and example-expression scans. Each has a separate
  four-part explanation in paragraph detail.
- Body adjacent-paragraph continuity/transition observations.
- Conclusion paragraph/clause/list, synthesis, closure/cue, new-material,
  nested-concept exclusion, known-combination, rewording and repetition checks.
- Event emission versus inventory-based evaluation trace reconstruction.
- Predefined feedback selection, branch priority, provenance, response packaging,
  stale-response protection, rendering and separate persistence workflows.

Explanations distinguish direct consumers. In particular, direct/lemma focus
matching consumes Doc token windows independently of extracted noun concepts;
Introduction rules do not consume the concept list.

## 6. Technical Tables

| Table / inspection | Actual response source |
|---|---|
| Context/input | `stage_id`, `availability`, `analysis.assignment_topic`, `research_trace.teacher_context`, retained linguistic text, selected trace `input_sections` |
| Pipeline/model | `research_trace.runtime.pipeline`, `.model`, runtime versions |
| Counts/sentences | retained `linguistic_observations.counts`, `.sentences` |
| Complete token/lemma/POS/tag records | retained `linguistic_observations.tokens`; no row truncation |
| Dependency/head/POS/positions | sentence `.dependencies`, including `head_start`; token POS joined by actual start position |
| Noun chunks | `.noun_phrases`; source slice verification uses Python-compatible Unicode code-point offsets |
| Concepts/occurrences | selected trace `topic_service.steps[id=concept_extraction].output` |
| Prepared targets/normalization | `research_trace.teacher_context.focus_terms` |
| Matched/unmatched targets and methods | `analysis.lexical_topic_evidence`; list lengths explicitly identified as derived counts |
| Direct WordNet status/lookup pairs/candidates | selected trace `topic_service.steps[id=wordnet_direct_suggestions]` |
| Cross-stage WordNet/lexical comparison | `analysis.introduction_to_body_continuity`, `.introduction_to_conclusion_continuity`, `.body_to_conclusion_continuity` |
| Stage observations | Introduction `observable_structure`, `development_evidence`, `text_presence`; Body `paragraphs`, `cross_paragraph_continuity`; Conclusion paragraph/clause/synthesis/closure/new-material/repetition fields |
| Rule decisions/configuration/source metadata | `analysis.rule_evaluation_trace` |
| Emitted Rule Event evidence/spans/limits | `analysis.rule_evidence` |
| Five messages, branches and supporting events | `feedback`, selected trace `feedback_decisions.fields`, compact `Feedback Provenance` resolved against returned events |
| Complete evidence index | the same sanitized technical records collected by `buildFullAnalysisReport(result, records)` |

Introduction/Conclusion full linguistic observations are in analysis; Body full
observations are in the selected trace. Missing, empty, disabled, failed and
not-applicable states remain distinct. Browser-derived editor counts and draft
identification are labeled. No example tokens or fabricated model output appear.

## 7. Rule Evaluation and Rule Events

The Environmental Protection Introduction returns **7 emitted events**, plus
**14 reconstructed evaluation records: 7 TRIGGERED and 7
EVALUATED_NOT_TRIGGERED**. They have separate counts, tables and details.

The evaluation trace joins the rule inventory with returned observations and
emitted events using `research_inspector.rule_inventory` and
`_observed_rule_decisions`. It does not rerun conditions. The interface preserves
decision basis and unknown/not-applicable/failure statuses, and never calls an
untriggered row an emitted event. Detailed rules expose related returned input
observations and exact event evidence where present. Feedback effects are
identified only by recorded field-level provenance.

## 8. Feedback Provenance

The verified Introduction Primary Feedback branch is
`central_clause_with_multiple_clause_candidates`. Its recorded condition is a
central candidate plus `STRUCTURAL_ELABORATION_CANDIDATE` development status.
The response has **2 root subject–predicate candidates** and **3 supported clause
predicates**. The branch links:

- `INTRO.CLAUSE.SUBJECT_PREDICATE_CANDIDATE`
- `INTRO.DEVELOPMENT.MULTIPLE_CLAUSE_PREDICATES`

The selected unchanged message is:

> The checks found sentence patterns that may state a point and give a reason.
> Check that the reason explains the point.

The UI shows all five exact backend fields, recorded branch labels/conditions,
supporting Rule IDs, event evidence and available priority metadata. It explicitly
separates empty backend lists from the Writing Feedback panel's fallback text.
Unselected message candidates/hidden ranking are not recorded and are not invented.

## 9. Copy Full Analysis

Preserved: one button, current-snapshot eligibility, real Clipboard API copying,
manual-copy fallback, complete untruncated technical report and stale-copy guards.
Both views use the cached authoritative selected-stage response. The visual
complete-evidence index is populated by the report generator's record collector;
automated tests compare every index path/count with that collector for real stage
responses. No second analysis pipeline or extra fetch is used.

Actual Chrome clipboard content matched the generated report after normalizing
Windows-native CRLF line endings to LF. The copied Introduction report in the
verified run had 104,440 clipboard characters; runtime timing values can change
between analyses. Export remains deterministic for the same cached response.

## 10. Introduction, Body, and Conclusion Coverage

| Stage | Real Chrome verification | Automated coverage |
|---|---|---|
| Introduction | Environmental Protection exact input; all 27 token rows, current/stale transition, clipboard equality, 7 events/14 trace rows | Exact result hash, counts, spans, feedback, empty/no-match/missing-trace fixtures |
| Body | Two paragraphs with Introduction context; 18 emitted events; paragraph observations accessible | One/multiple/repeated/no-overlap/empty cases, with/without earlier context |
| Conclusion | Introduction+Body context; 9 emitted events; synthesis/closure/new-material and comparisons accessible | With/without earlier context, no overlap, new material and empty cases |

Environmental Protection comparison: **27 nonspace tokens; 24 alphabetic tokens;
2 sentences; 23 whitespace editor words; 3 unique focus targets matched;
4 occurrences; 2 root candidates; 3 clause predicates; 7 emitted events;
14 evaluation records; `harm` = NOUN/NN/compound; direct WordNet = SKIPPED/disabled**.
All supplied expected values matched the current model, `core_web_sm` 3.7.1.

The exact protected analysis/feedback/decision-trace SHA-256 assertion remains
unchanged and passes: `78811fc86728b7643ee155eeb260921d136635b4602373af5e57abe853b7f6de`.

## 11. Files Modified

All paths below are under `C:\Users\My Pc\Desktop\EssayScaff-V2`:

1. `static\app.js` — restored rendering integration, diagram, explanations,
   structured evidence, stage/rule/feedback detail, report record collector.
2. `static\style.css` — student dashboard responsive styles and mobile header wrap.
3. `templates\index.html` — restored content host and dashboard heading alongside copy.
4. `tests\test_nlp_transparency.py` — restored-dashboard assertions and real-response
   evidence/navigation/staleness/report agreement regression.
5. `tests\test_interface_views.py` — dashboard/copy coexistence expectations.
6. `tests\transparency_browser_check.py` — isolated temporary Flask/browser runner.
7. `tests\transparency_browser_check.cjs` — real Chrome CDP workflow/layout/clipboard checks.
8. `docs\transparency_process_map.md` — pre-UI source investigation reference.
9. `docs\transparency_restoration_report.md` — this completion report.

## 12. Automated Test Results

Command: `.venv\Scripts\python.exe -m pytest -q`

- Baseline before edits: **300 passed**, 0 failed, 0 skipped, 78.68 seconds.
- Focused implementation checks: **15 passed**, 17.93 seconds.
- Final complete suite: **301 passed**, 0 failed, 0 skipped, **66.34 seconds**.
- JavaScript syntax: `node --check static/app.js` passed during implementation.

The suite covers authentication/authorization, assignments, drafts, revisions,
submissions, stage navigation, tutoring lessons, simplified feedback, Inspector,
single-pass parsing, provenance, export integrity and stale asynchronous responses.
No existing evidence/hash test was weakened. Only assertions demanding the
unwanted dashboard removal were replaced with restoration/coexistence assertions.

## 13. Chrome Verification

Actual **Chrome 155.0.8059.80**, headless, via Chrome DevTools Protocol using
Node's built-in WebSocket (no browser automation package installation).

Command: `.venv\Scripts\python.exe tests/transparency_browser_check.py`

Verified real student login, practice workspace, pre-analysis explanation, manual
analysis in all three stages, exact cached/API response agreement, full token rows,
diagram focus/scroll navigation, evidence disclosures, complete report index,
real clipboard copying without reanalysis, stale invalidation and reanalysis,
unchanged Primary Feedback display, logout/unsaved guard, teacher login and
Research Inspector metadata/analysis/process navigation.

All stages checked at **1440×1000 desktop** and **390×844 mobile**. Mobile
document width was 390, diagram width 324, explanation grid one column. Desktop
document width was 1425 (scrollbar) within the 1440 viewport. No page-wide
horizontal overflow was detected. Generated desktop/mobile and token-table
screenshots were reviewed. No JavaScript or application console errors were
recorded; the existing unrelated `/favicon.ico` 404 is excluded from that check.

Isolated persistence after browser analysis/inspection: **0 writing sessions,
0 writing revisions, 0 submissions**; zero persistence POSTs observed. The runner
creates only synthetic users in its own temporary SQLite database.

Successful-run artifacts, including `verification.json` and seven screenshots:
`C:\Users\My Pc\AppData\Local\Temp\opencode\essayscaff-transparency-mdbdh4yk`.

## 14. Remaining Limitations

- Exact pre-S3.2 historical styling cannot be authenticated from an archived
  snapshot; recovery is based on retained dashboard source and existing tests.
- The evaluation trace is reconstructed metadata. Some existing registry
  condition/configuration summaries abbreviate actual helper logic, particularly
  Introduction subordinator/list conditions. These summaries remain preserved and
  labeled; stage explanations follow the verified source. Backend metadata was
  not silently changed.
- Non-triggered rows only expose their recorded decision basis and related
  observations. Missing internal execution detail is not inferred.
- Feedback provenance is field-level, not a complete mapping from each list
  sentence to an individual event. Hidden alternatives are not available.
- Live Doc internals, probabilities, NER entities, contextual WordNet sense
  disambiguation and per-component timings are not returned. Missing optional
  trace data remains explicitly unavailable.
- Full earlier-stage analyses are not returned in a selected-stage response.
  Supplied earlier text and returned cross-stage comparison evidence are shown.
- Large nested evidence remains expandable for completeness; the numbered main
  sections and purpose-built linguistic tables are the primary explanation.
- Browser verification used headless Chrome desktop/mobile emulation, not a
  physical mobile device or an independent screen-reader audit. Browser tests
  analyzed practice inputs; assigned-work saving/submission preservation is covered
  by the existing automated suite rather than being recreated in this browser run.
- A recorded grammatical/lexical observation is not evidence of semantic
  understanding, truth, coherent reasoning, rhetorical success or essay quality.

## 15. Final Assessment

**Yes, within the evidence the current application actually records.** A professor
can follow the analyzed words through shared spaCy annotations, focus matching,
conditional WordNet paths, stage-specific findings, emitted events and
reconstructed rule decisions to the exact selected feedback. Sources, input/output
relationships, statuses, spans and recorded provenance are inspectable. Unsupported
internal details and semantic conclusions are explicitly identified rather than
fabricated. Copy Full Analysis remains available alongside the restored visual
dashboard and uses the same authoritative cached response.
