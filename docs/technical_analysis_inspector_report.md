# Technical Analysis Inspector — Completion Report

**Completed:** 2026-10-26  
**Project:** `C:\Users\My Pc\Desktop\EssayScaff-V2`  
**Scope:** Student Technical Analysis Inspector / Transparency Mode  
**Result:** Implemented and verified against real recorded NLP, rule and feedback output. No fabricated evidence, no new NLP run when opening the inspector, no database or backend-processing change.

---

## Result summary

The inspector is now a single vertical reading experience:

- Six horizontal stage buttons: **Assignment Preparation**, **Linguistic Processing**, **Topic Processing**, **Rule Evaluation**, **Feedback Decisions**, **Output & Technical Trace**.
- Each stage shows only its own process buttons. Choosing a process immediately renders its complete page; there is no "Expand Evidence", "View More" or "Show Technical Details" action.
- Every process page renders the same ordered sections: **A Process Overview**, **B Actual Input**, **C Visual Representation**, **D Actual Recorded Evidence**, **E How the Process Works**, **F Output and Next Destination**, **G Implementation Source**, **H Limitations**. A separate **Developer Evidence** archive follows H.
- All 45 original technical evidence sections are retained exactly once in the Developer Evidence archive. The primary A–H evidence is never hidden behind a toggle.
- All displayed values come from the cached selected-stage response. Switching stage or process performs no request and does not re-run spaCy, rules or FeedbackService.

Verified runs: **73 process views** (23 Introduction, 25 Body, 25 Conclusion), **51 transparency browser checks**, **29 focused tests**, and **709 full-suite tests**, with **zero browser JavaScript errors**.

> **See also:** [How EssayScaff V2 Reads a Student Essay](essay_processing_walkthrough.md) — a start-to-finish, 28-figure walkthrough of one real Introduction → Body → Conclusion run, with every value grounded in the saved response JSON. Evidence and reproduction steps are in [`essay_processing_walkthrough_evidence/`](essay_processing_walkthrough_evidence/README.md).

---

## A. Files changed

| File | Change |
|---|---|
| [`static/nlp_process_explorer.js`](../static/nlp_process_explorer.js) | Rebuilt the explorer as six stage groups with contextual process buttons, lazy A–H process pages, process models bound to cached evidence, rule/feedback/word-relation visualizers, honest status handling, and a per-process Developer Evidence archive. |
| [`static/style.css`](../static/style.css) | Added the explorer layout: stage navigation grid, process pills, A–H section styling, evidence tables, flow lanes, rule tables, mobile horizontal process navigation, and reduced-motion rules. |
| [`tests/test_nlp_process_explorer.py`](../tests/test_nlp_process_explorer.py) | Node-backed model tests for process counts, stage scoping, 45 unique section homes, WordNet execution semantics, missing earlier sections, exact token/concept/match offsets, neutral Body states, and the neutral Introduction trait-mapping regression. |
| [`tests/nlp_process_explorer_browser_check.cjs`](../tests/nlp_process_explorer_browser_check.cjs) | Real-Chrome E2E: all process views, contextual process selection, A–H presence, no toggle control, 45 retained sections, statuses, screenshot capture, export equality, no extra API calls, snapshot and assignment-switch safety. |
| [`tests/test_nlp_transparency.py`](../tests/test_nlp_transparency.py) | Updated retained-evidence and explorer tests for the six-stage inline A–H architecture and actual visual models. |
| [`tests/transparency_browser_check.cjs`](../tests/transparency_browser_check.cjs) | Updated the legacy 51-check transparency E2E for the new section homes, process navigation, keyboard controls, export and no-rerun guarantees. |
| [`docs/technical_analysis_inspector_evidence/`](technical_analysis_inspector_evidence/) | New evidence set: 12 final screenshots, SHA-256 manifest, raw explorer outputs, verification summary, browser log, and the 51-check transparency verification JSON. |
| [`docs/technical_analysis_inspector_report.md`](technical_analysis_inspector_report.md) | This report. |

Reused without modification:

- [`tests/nlp_process_explorer_browser_check.py`](../tests/nlp_process_explorer_browser_check.py) — isolated Flask/SQLite/Chrome runner with protected-file hashing.
- [`tests/nlp_process_explorer_cases.json`](../tests/nlp_process_explorer_cases.json) — real analysis corpus and teacher focus terms.

Not changed: Flask routes, `services/*.py`, NLP algorithms, stage Rule Bases, thresholds, FeedbackService selection, the lesson catalog, database schema or migrations, authentication, classroom, draft, submission, and real student data. The explorer consumes the existing host functions in [`static/app.js`](../static/app.js) (`transparencyData`, `studentFeedbackPresentation`, `renderDependencyTree`) read-only.

---

## B. Six-stage navigation

The six stage buttons are defined at [`static/nlp_process_explorer.js:6`](../static/nlp_process_explorer.js#L6). Each stage has its own process row; selecting a process marks it `aria-current="step"` and shows exactly one process card. Previous/Next move through the full stage order, and Arrow/Home/End keys move between process buttons.

| Stage | Introduction | Body | Conclusion |
|---|---:|---:|---:|
| 01 Assignment Preparation | 2 | 2 | 2 |
| 02 Linguistic Processing | 6 | 6 | 6 |
| 03 Topic Processing | 5 | 5 | 5 |
| 04 Rule Evaluation | 3 | 5 | 5 |
| 05 Feedback Decisions | 5 | 5 | 5 |
| 06 Output & Technical Trace | 2 | 2 | 2 |
| **Total** | **23** | **25** | **25** |

Rules differ per stage: Introduction has sentence/clause checks and the sentence topic-connection review; Body has paragraph/list checks, topic sentences, supporting details and repetition; Conclusion has structure/closure, synthesis, new-material and repetition checks. Every rule process shows only `INTRODUCTION.*`, `BODY.*` or `CONCLUSION.*` Rule IDs for the selected stage.

Navigation behavior verified in Chrome:

- A stage change selects that stage's first process and updates the inspector; a process change shows only that process card.
- Selected processes are remembered per `assignment:stage`.
- Switching stages does not call `/api/analyze`; the measured `__explorerCalls` count and the cached analysis JSON stay unchanged.
- Editing the text marks the inspector stale and disables **Copy Full Analysis** until the draft is analyzed again.
- Mobile uses horizontal stage/process rows with no page overflow and no nested scroll panel.
- There is no obsolete horizontal/vertical tab strip, no Simple/Technical mode, and no `[data-explorer-toggle]` control.
- Every process page contains the A–H labels plus **Developer Evidence**; all 45 original technical sections remain reachable exactly once.

**Developer Evidence note:** the 45 original legacy evidence sections are preserved as native `<details>` entries inside the always-visible Developer Evidence archive. They are supplementary technical records, not the primary explanation; the A–H process evidence is always rendered in full above them.

---

## C. Real NLP verification per process

### Method

Three real analyses were run through the actual `EssayAnalysisService` with the shared assignment and teacher focus terms:

- **Assignment:** "Should schools have a vegetable garden?"
- **Focus terms:** `school`, `vegetable garden`, `students`, `science`, `responsibility`, `vegetables`
- **Introduction:** "Schools should have vegetable gardens because students can learn science and responsibility through practical activities."
- **Body:** two blank-line paragraphs about observing seeds, measuring growth, responsibility, watering and teamwork.
- **Conclusion:** "Overall, schools should use vegetable gardens to give students practical ways to learn science and responsibility."

The Node tests recompute the explorer model from the recorded response and compare it with `data.linguistic.tokens`, `data.concepts`, `data.analysis.lexical_topic_evidence`, the rule trace and the feedback decision. The Chrome test performs the same checks through the real Flask response and visible DOM. Values below are from the final recorded run, not samples.

### Per-stage recorded totals

| Recorded item | Introduction | Body | Conclusion |
|---|---:|---:|---:|
| Tokens | 16 | 74 | 18 |
| Alphabetic words | 15 | 66 | 16 |
| Sentences | 1 | 6 | 1 |
| Paragraphs | 0 (no independent Introduction paragraph detector) | 2 | 1 |
| Noun phrases | 6 | 26 | 6 |
| Concept groups | 9 | 28 | 9 |
| Focus-term matches | 6 | 9 | 6 |
| Emitted Rule Events | 9 | 19 | 11 |
| Reconstructed evaluation rows | 19 | 35 | 26 |
| Triggered evaluation rows | 9 | 19 | 11 |
| Primary Feedback branch | `intro_ideas_point_and_reason` | `body_neutral_observable` | `conclusion_ideas_new_words` |
| Recorded selection status | no corrective concern (neutral review) | `NO_SUPPORTED_CONCERN_SELECTED` | corrective wording request |

### Per-process matrix

`E` = Executed, `S` = Skipped, `N/A` = Not applicable, `U` = Unavailable. Every status is the recorded status of the selected run; no status is inferred from candidate counts alone.

| Process (stable ID) | Intro | Body | Conclusion | Actual verification |
|---|---|---|---|---|
| Teacher Focus-Term Preparation (`focus-preparation`) | E | E | E | Output equals `research_trace.teacher_context`; 6 teacher terms; `teacher_provided`. |
| Focus-Term Normalization (`focus-normalization`) | E | E | E | Actual forms include `students → student` and `vegetables → vegetable`; other terms retain their forms. |
| Tokenization (`tokens`) | E | E | E | Model output equals the recorded token array; every `start:end` slice reconstructs the recorded token text; 16/74/18 records. |
| Part-of-Speech Tagging (`pos`) | E | E | E | Displays each token's recorded `pos` and fine tag from the same Doc; duration is the shared spaCy document duration, explicitly labelled. |
| Dependency Parsing (`dependencies`) | E | E | E | Tree nodes and edges use recorded `head_start` links; the Introduction sentence renders 16 actual dependency relationships. |
| Lemmatization (`lemmas`) | E | E | E | Displays recorded token lemmas; the same lemmas support normalized matching and concept grouping. |
| Sentence and Paragraph Detection (`sentences`) | E | E | E | Sentence spans come from the shared Doc; Body uses 2 blank-line paragraphs; Introduction invents no paragraph count. |
| Noun Phrase Extraction (`noun-phrases`) | E | E | E | 6/26/6 noun chunks from the same Doc, each with exact source offsets. |
| Concept Candidate Extraction (`concepts`) | E | E | E | Model output equals `data.concepts`; 9/28/9 groups with occurrence spans. |
| Teacher Focus-Term Matching (`topic-matching`) | E | E | E | Model output equals `lexical_topic_evidence`; 6/9/6 matches with direct vs normalized method and exact spans. |
| WordNet Processing (`wordnet`) | S | E | E | Introduction: recorded direct step `SKIPPED` (`include_wordnet=false`). Body: direct step skipped, nested cross-stage WordNet comparisons executed (98 lookup pairs). Conclusion: direct step executed with 0 pairs, plus 13 Introduction→Conclusion and 111 Body→Conclusion nested pairs. |
| Related-Word Resource Evidence (`related-concepts`) | N/A | N/A | N/A | Recorded `NOT_APPLICABLE`: `NO_APPROVED_FOCUS_CONCEPT`; resource is available, but no complete active teacher focus matched a configured key. Zero observations, informational only. |
| Earlier-Section Comparisons (`cross-stage`) | N/A | E | E | Introduction has no earlier section. Body: Introduction→Body status `LEXICAL_COMPARISON_AVAILABLE` (4 direct, 3 lemma-normalized, 2 unobserved Introduction concepts). Conclusion: 7 direct/0 lemma-normalized from Introduction and 3 direct/3 lemma-normalized from Body. |
| Stage patterns (`stage-patterns`) | E | E | E | Stage-specific rule tables with recorded conditions and outcomes; Introduction 9 events, Body 19, Conclusion 11. |
| Sentence Topic-Connection Review (`sentence-connection`) | E | — | — | Emitted `INTRO.TOPIC.SENTENCE_CONNECTION_REVIEW`; no separate analysis is run by opening the page. |
| Topic Sentence Checks (`topic-sentences`) | — | E | — | `BODY.P1.*`/`BODY.P2.*` candidate evidence from recorded clauses and focus concepts. |
| Supporting Detail Checks (`supporting-details`) | — | E | — | Recorded paragraph-level candidate/not-observed events, not a quality judgment. |
| Repeated Wording and Sentence Openings (`repetition`) | — | E | E | Recorded surface/lemma/opening groups with source positions; Conclusion repetition does not auto-select a branch. |
| Synthesis checks (`synthesis`) | — | — | E | Candidate sentences that combine recorded earlier-section concepts; no semantic synthesis claim. |
| New-Material Wording Checks (`new-material`) | — | — | E | 22 Body concepts unmatched by the Conclusion wording; the actual `practical way` observation drives the selected concern. |
| Rule Events and Evaluation Evidence (`rule-events`) | E | E | E | Emitted events and the later reconstructed 19/35/26-row evaluation trace; the trace is explicitly not a second Rule Base run. |
| Feedback Branch Selection (`feedback-decision`) | E | E | E | Exact recorded branch, condition, Rule IDs and five fields; Introduction 82 and Body 148 and Conclusion 82 unselected alternatives remain labelled as recorded. |
| Feedback Explanation (`feedback-explanation`) | E | E | E | Priority order, recorded fields, conditions and Body's five explicit selection checks; no invented hidden ranking. |
| Five Feedback Fields (`feedback-fields`) | E | E | E | Renders the returned Current Goal, Primary Feedback, What's Working, Needs Attention and Next Step verbatim. |
| 6+1 Trait and Lesson Mapping (`trait-mapping`) | N/A | N/A | E | Introduction `NEUTRAL_OBSERVATION`: no corrective trait/skill/lesson/task, but the retained prepared explanation item `HELP-INTRO-EXPLAIN-POINT` is shown. Body `NO_SUPPORTED_CONCERN_SELECTED`: no trait, lesson or task. Conclusion: verified prepared presentation is shown. |
| Highlight Evidence Selection (`highlight-evidence`) | E | N/A | U | Introduction: verified span 38–120, "because students can learn science and responsibility through practical activities", rule `INTRO.REASON.CLAUSE_TOPIC_OVERLAP`. Body: neutral result selects no error span. Conclusion: no precise verified mark was retained, so the page says unavailable and invents nothing. |
| API Response and Browser Rendering (`api-rendering`) | E | E | E | The page describes the cached Flask response and browser rendering; opening it makes no request and reruns nothing. |
| Complete Technical Trace (`technical-trace`) | E | E | E | Runtime metadata, trace version, stage timings and limitations are read from the retained `research_trace`. |

### Feedback verification against actual returned fields

**Introduction — neutral review**

- Primary Feedback: "The checks recorded a possible main statement and a 'because' part. Read them together and decide whether a reader needs more explanation."
- What's Working: 2 recorded observations; Needs Attention: 0; Next Step: a neutral reading suggestion.
- Recorded branch `intro_ideas_point_and_reason`; rules `INTRO.CLAUSE.SUBJECT_PREDICATE_CANDIDATE` and `INTRO.REASON.CLAUSE_TOPIC_OVERLAP`; 82 unselected alternatives.
- Student tutor status `NEUTRAL_OBSERVATION`; no corrective trait, lesson, improvement task or error location. The raw prepared item `HELP-INTRO-EXPLAIN-POINT` remains visible only as recorded explanation evidence.

**Body — no supported concern**

- Primary Feedback: "The available checks did not identify a specific structural concern in this Body section."
- Next Step is empty; no trait, lesson, task or highlight is assigned.
- All five selection checks are recorded `NOT_MATCHED`:
  1. `body_neutral_empty` — no substantive paragraph.
  2. `body_organization_paragraph_shape` — no supported list-like paragraph.
  3. `body_ideas_develop_point` — no supported development concern.
  4. `body_sentence_fluency_sentence_beginnings` — no repeated-opening concern.
  5. `body_organization_paragraph_link` — no adjacent-paragraph wording concern.
- Recorded neutral branch `body_neutral_observable` with `BODY.P1.PARAGRAPH.SEGMENTED` and `BODY.P2.PARAGRAPH.SEGMENTED`; 148 alternatives.

**Conclusion — actual wording concern**

- Primary Feedback: "These idea words (practical way) do not appear in the earlier sections you provided. Decide whether readers need that idea explained earlier; the checks may miss reworded ideas."
- Needs Attention: 2 items (unobserved idea words and the structural/wording limitation); What's Working: 5 items.
- Recorded branch `conclusion_ideas_new_words` from `CONCLUSION.NEW_MATERIAL.UNOBSERVED_CONCEPTS`; 22 Body concepts unmatched; 82 alternatives; the student tutor receives the verified prepared presentation.

### Timing scopes

Only recorded in-process timings are shown:

| Stage | Teacher context prep | TopicService | Rule Base | FeedbackService |
|---|---:|---:|---:|---:|
| Introduction | 19.234 ms (shared) | 7.673 ms | 0.514 ms | 2.339 ms |
| Body | shared | 20.473 ms | 2065.912 ms | 0.265 ms |
| Conclusion | shared | 7.340 ms | 1.794 ms | 0.029 ms |

Token, POS, lemma, dependency, sentence and noun-phrase views share the single spaCy document time; they do not claim separate model runs. The Body Rule Base duration includes its nested cross-stage comparisons. Authentication, network transfer and browser rendering are outside these measurements and are labelled as not separately instrumented.

### No-extra-run verification

For each stage, the Chrome run compared the cached analysis object and the fetch counter before and after visiting all 23/25/25 processes. Both were unchanged. The full export record was also identical (after normalizing measured runtime fields), and Copy Full Analysis matched the clipboard text exactly.

---

## D. Visualization verification

All graphs are derived only from retained records. An empty or unavailable input produces an explicit message instead of a decorative graph.

1. **Dependency tree** (`05`): built from the recorded `head_start`, dependency label, token text and offset for the actual Introduction sentence. The test verifies the node/edge set against the recorded relationships; the screenshot shows `Schools → nsubj`, `should → aux`, `gardens → dobj`, `have → ROOT`, `learn → advcl`, etc. The same real tree is rendered twice by design: once on the Dependencies process page and once in the retained operation section; the E2E asserts exactly two `[data-dependency-tree-section="true"]` trees and confirms the retained section still contains its own.
2. **Token and POS table** (`02`): the screenshot shows a different recorded sample ("Single-use plastics…") with 27 tokens, 24 alphabetic words, 2 sentences and 158 code points. This demonstrates that the table is driven by the input, not a fixed template; the explorer corpus itself produced 16/74/18 tokens.
3. **Topic map**: Introduction 6, Body 9 and Conclusion 6 recorded focus-term matches. Edges carry the recorded `direct`/`normalized` method and exact offsets; unmatched configured terms appear as targets without an edge and are not described as errors.
4. **WordNet / cross-stage table** (`04`, `08`): Introduction shows the real skipped state with `include_wordnet=false`, 0 pairs and no graph. Conclusion's comparison table shows the actual 7 direct/0 normalized Introduction→Conclusion path and 3 direct/3 normalized Body→Conclusion path, with nested WordNet status `AVAILABLE`. The retained lookup counts are 98 (Body nested), 13 (Introduction→Conclusion) and 111 (Body→Conclusion). An executed but empty direct lookup shows 0, not a fabricated suggestion.
5. **Rule evaluation table** (`09`): actual Rule IDs, evidence descriptions, conditions and decisions, including `EVALUATED_NOT_TRIGGERED` rows only where the returned trace records them. Emitted events are separately listed. No unrecorded negative evaluation is invented.
6. **Feedback decision flow** (`10`, `11`): the retained flow shows recorded events → conditions → selected branch → actual field output → tutor display. `10` shows the real `intro_sentence_fluency_complete_sentence` example with 10 emitted events, 13 priority rows and 2 cited events. `11` shows the neutral Introduction mapping: branch `intro_ideas_point_and_reason`, no corrective trait/skill, recorded prepared item `HELP-INTRO-EXPLAIN-POINT`, tutor display `NEUTRAL_OBSERVATION`.
7. **Highlight offsets** (`06`): the marked text is reconstructed from the original offsets 38–120, and the table shows start, end, supporting rule and the recorded reason. The editor is not modified.
8. **Mobile process navigation** (`03`): contextual process pills with an active outline, Previous/Next controls and A–H content at 390 px, with no horizontal page overflow.

---

## E. Test results

### Commands and counts

```text
PYTHONPATH=tests .venv/Scripts/python.exe -m pytest -q tests/test_nlp_process_explorer.py -p no:cacheprovider
15 passed in 5.05s

PYTHONPATH=tests .venv/Scripts/python.exe -m pytest -q tests/test_nlp_process_explorer.py tests/test_nlp_transparency.py tests/test_feedback_decision_flow.py --no-header -p no:cacheprovider
29 passed in 23.52s

PYTHONPATH=tests .venv/Scripts/python.exe -m pytest -q --no-header -p no:cacheprovider
709 passed in 125.87s
```

The full suite includes the focused inspector tests, the real-analysis service tests, feedback/rule tests, workspace tests and the existing regression suite.

### Browser E2E

```text
PYTHONPATH=. .venv/Scripts/python.exe tests/nlp_process_explorer_browser_check.py
```

- Exit code 0.
- 73 process views checked in real headless Chrome: 23 Introduction, 25 Body, 25 Conclusion.
- Every process: one visible process card, A–H labels present, Developer Evidence is a `SECTION`, no evidence-revealing toggle, correct stage scoping.
- 45 original evidence sections present exactly once.
- Introduction/Body/Conclusion statuses match the recorded response; WordNet skipped/executed states verified; neutral Introduction and Body mapping states verified.
- Previous/Next and keyboard navigation verified.
- Clipboard equals the complete export; no analysis request during inspection.
- Assignment A/B switch and snapshot-safety checks passed (`snapshotAndAssignmentSwitches: PASS`).
- `javascriptErrors: []`.
- Isolated SQLite: `{"writing_sessions": 3, "writing_revisions": 0, "submissions": 0}`, `integrity: ok`, 0 foreign-key violations.
- Protected real databases and research files retained their pre-run SHA-256 values; backend/source/content hashes were unchanged.

```text
PYTHONPATH=. .venv/Scripts/python.exe tests/transparency_browser_check.py
```

- 51 checks passed; `javascriptErrors: []`.
- Verified the retained explorer, in-place stage/process switching that leaves the page scroll position unchanged, 45 original sections, keyboard operation, teacher research inspector, process navigation, copy/export agreement, no extra analysis calls, and isolated persistence `{"writing_sessions": 0, "writing_revisions": 0, "submissions": 0}`.

### Follow-up UI correction (2026-10-26)

- **No layout change while scrolling.** Wheel and touch scrolling no longer auto-enter or auto-exit full-screen. The page keeps its normal width while scrolling; full-screen is entered and exited only through the visible toggle.
- **Full-screen keeps the actual size.** The focus layout now uses the normal `1440px` layout width and `1240px` content cap instead of expanding to `1920px`. `scrollbar-gutter: stable` reserves the page scrollbar gutter so hiding the page scrollbar does not shift the content by 15px.
- **Six stage accent colors.** Assignment Preparation is amber, Linguistic Processing blue, Topic Processing teal, Rule Evaluation purple, Feedback Decisions rose, and Output & Technical Trace slate. The color follows the active stage through its process group, selected process pill, process heading and A–H section accents; non-active stage buttons keep their own colored number badge.
- **Selection switches in place.** Clicking a stage button or a process pill changes the active stage/process and swaps the displayed panel only. It no longer scrolls the page to the detail area, so the viewport stays where the reader left it. Keyboard arrow navigation, the Previous/Next controls and explicit evidence deep-links (flow nodes and rule links) are unchanged.
- **Verification after the correction:** `tests/test_nlp_process_explorer.py` — 15 passed in 4.73s; full suite — 709 passed in 130.67s; `tests/transparency_browser_check.py` — 51 checks passed, `javascriptErrors: []`, isolated persistence all zero. The focus test asserts that wheel scrolling leaves the layout unfocused and at the same width, that the toggle opens full-screen at the same content width, and that all six stage badges expose distinct colors. Additional checks assert that stage and process clicks leave `window.scrollY` unchanged on desktop and mobile, and that process selection in full-screen leaves the transparency pane's `scrollTop` unchanged.
- [Screenshot 12](technical_analysis_inspector_evidence/12-stage-colors-and-normal-width.png) captures the corrected Feedback Decisions full-screen state at 1440×1000.

### Unresolved problems / honest states

No test failed. The following are deliberate, recorded states rather than implementation failures:

1. **Conclusion highlight unavailable** — no precise verified source mark was retained for the selected Conclusion branch. The page states `UNAVAILABLE` and produces no mark; inventing one would violate the evidence rule. This is the only process status of type `UNAVAILABLE` in the final runs aside from absent legacy records.
2. **Body WordNet pill is `EXECUTED` while the direct suggestion step is `SKIPPED`** — the process covers both the direct path and the nested cross-stage WordNet paths. The basis text and the evidence tables distinguish them; 98 nested pairs were actually recorded.
3. **Conclusion direct WordNet executed with 0 pairs** — a real executed-but-empty result. The page shows zero suggestions and zero pairs instead of hiding the path or inventing semantic matches.
4. **Introduction neutral review retains a recorded because-clause span** — the student tutor assigns no error location, but the Highlight Evidence page can show the recorded span as *explanation evidence* with its rule and offsets. This is a transparency record, not a corrective highlight.
5. **Related-word evidence is `NOT_APPLICABLE`** — the recorded reason is `NO_APPROVED_FOCUS_CONCEPT`; the curated resource was available, but no complete active teacher focus matched a configured key.
6. **The inspector is a snapshot** — after editing, it becomes stale until the text is analyzed again. It does not silently refresh or re-run the pipeline.

---

## F. Limitations

- spaCy tokenization, POS, lemmas, dependency heads, sentences and noun chunks are model predictions, not ground truth. The inspector shows final annotations but cannot show why the model chose them.
- Lexical focus-term matching, normalized matching and WordNet relationships establish wording overlap at most. They do not establish meaning, relevance, argument quality or correctness. The pages state this limitation directly.
- WordNet lookup pairs are candidate relationships; they are not context-sensitive word-sense disambiguation. Absence of a candidate does not prove unrelated meaning.
- Rule Events and the reconstructed evaluation trace are inspection records. The trace is rebuilt after feedback and is not a second Rule Base execution; only recorded statuses are displayed.
- Neutral Introduction/Body states assign no corrective trait, lesson, improvement task or error location. The recorded raw mapping remains in transparency, including the prepared Introduction explanation item.
- Timing values cover only the marked in-process Python calls. Model component timing, authentication, CSRF, network transfer and browser rendering are not separately measured.
- The inspector reads the cached selected-stage response. It does not call the API, re-run NLP, select feedback, modify the draft, or save anything. It becomes stale when the edited text no longer matches the analyzed snapshot.
- The 45 original technical sections remain in the Developer Evidence archive as native collapsible details. The primary A–H explanation and all required process evidence are always visible; the archive exists to preserve the original complete records without dropping them.
- Mobile screenshots cover the Introduction stage; responsive layout was checks at 390×844 for all three stages, but the curated evidence includes one mobile process view.

---

## G. Screenshots

All images are from the final isolated Chrome runs and are listed with SHA-256 hashes in [`screenshots.json`](technical_analysis_inspector_evidence/screenshots.json).

1. [Six-stage navigation, Introduction desktop](technical_analysis_inspector_evidence/01-six-stage-navigation-desktop.png) — six stage buttons, contextual Linguistic Processing pills, Tokenization A–H page, 15 words / 16 tokens / 1 sentence, fingerprint `ad0faf0`.
2. [Tokenization process, desktop](technical_analysis_inspector_evidence/02-tokenization-process-desktop.png) — actual recorded tokens and POS for the transparency-run sample (27 tokens, 2 sentences, 158 code points).
3. [Process navigation, mobile](technical_analysis_inspector_evidence/03-process-navigation-mobile.png) — 390×844, contextual pills, active POS process, no overflow.
4. [WordNet skipped state, desktop](technical_analysis_inspector_evidence/04-wordnet-skipped-desktop.png) — `include_wordnet=false`, 0 direct lookup pairs, explicit no-graph message.
5. [Dependency tree and Developer Evidence](technical_analysis_inspector_evidence/05-dependency-tree-developer-evidence.png) — real dependency tree and the 16 retained relationships for the Introduction sentence.
6. [Highlight evidence offsets](technical_analysis_inspector_evidence/06-highlight-evidence-offsets.png) — exact span 38–120, rule `INTRO.REASON.CLAUSE_TOPIC_OVERLAP`, recorded reason.
7. [Body neutral mapping](technical_analysis_inspector_evidence/07-body-neutral-mapping.png) — `NO_SUPPORTED_CONCERN_SELECTED`, no trait/skill/lesson/task, neutral tutor display.
8. [Conclusion comparisons](technical_analysis_inspector_evidence/08-conclusion-comparisons.png) — actual 7/0 and 3/3 direct/normalized comparison paths with nested WordNet `AVAILABLE`.
9. [Rule evaluation trace](technical_analysis_inspector_evidence/09-rule-evaluation-trace.png) — actual Rule IDs, evidence, conditions and `TRIGGERED` / `EVALUATED_NOT_TRIGGERED` decisions.
10. [Feedback decision flow](technical_analysis_inspector_evidence/10-feedback-decision-flow.png) — recorded events → conditions → selected branch → output → tutor display.
11. [Introduction neutral trait mapping](technical_analysis_inspector_evidence/11-introduction-neutral-mapping.png) — corrected final state: `NOT_APPLICABLE`, basis states the neutral review, and the retained prepared explanation item `HELP-INTRO-EXPLAIN-POINT` is shown without becoming a concern.
12. [Stage colors and normal full-screen width](technical_analysis_inspector_evidence/12-stage-colors-and-normal-width.png) — Feedback Decisions active: rose stage accent, all six stage badges color-coded, full-screen content width matching the normal workspace.

---

## Evidence index

- [Screenshot manifest](technical_analysis_inspector_evidence/screenshots.json) — 12 files with byte counts and SHA-256.
- [Raw explorer Chrome outputs](technical_analysis_inspector_evidence/explorer-browser-outputs.json) — stable analysis/feedback/export records, per-stage process statuses and section mapping.
- [Explorer verification summary](technical_analysis_inspector_evidence/explorer-verification-summary.json) — browser exit code, protected-data and backend hashes, isolated counts, integrity and foreign-key results.
- [Explorer browser log](technical_analysis_inspector_evidence/explorer-browser.log).
- [Transparency verification](technical_analysis_inspector_evidence/transparency-browser-verification.json) — all 51 checks and `javascriptErrors: []`.

## Safety statement

No migration was run. No production writing-time tracking was enabled. No test data was written to the real database. No real student record was changed. Nothing was committed, pushed or deployed.
