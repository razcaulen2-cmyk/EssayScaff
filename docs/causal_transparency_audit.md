# Causal transparency audit

Baseline: 492 tests passed in 186.64 seconds, before this overhaul. No AGENTS.md is present.

## Initial audit (before implementation)

The eight columns are: exact essay (A), component input (B), purpose (C), operation/conditions (D), intermediates (E), explained decision (F), actual use (G), limitations **and their cause** (H). C = complete, P = partial, M = missing, N = not applicable. Completeness concerns available evidence, not hypothetical instrumentation. A static consumer description does not count as actual use. A status or object dump does not count as an explained decision.

| Panel | A | B | C | D | E | F | G | H |
|---|---|---|---|---|---|---|---|---|
| student:overview | C | P | C | P | P | P | P | C |
| student:text | C | P | C | P | P | P | P | C |
| student:context | C | P | C | P | P | P | P | C |
| backend:overview | M | P | P | P | M | P | P | P |
| backend:validation | M | P | P | P | M | P | P | P |
| backend:response | M | P | P | P | P | P | P | P |
| backend:flow | M | P | C | P | P | P | P | P |
| nlp:overview | M | P | C | P | P | P | P | P |
| nlp:sentences | M | P | C | P | C | P | P | P |
| nlp:tokens | M | P | C | P | C | P | P | P |
| nlp:lemmas | M | P | C | P | C | P | P | P |
| nlp:pos | M | P | C | P | C | P | P | P |
| nlp:dependencies | M | P | C | P | C | P | P | P |
| nlp:chunks | M | P | C | P | C | P | P | P |
| nlp:pipeline | M | P | C | P | P | P | P | P |
| concept:overview | M | P | C | P | P | P | P | P |
| concept:concepts | M | P | C | P | P | P | P | P |
| concept:occurrences | M | P | C | P | C | P | P | P |
| topic:overview | M | P | C | P | P | P | P | P |
| topic:focus-terms | M | P | C | P | P | P | P | P |
| topic:normalization | M | P | C | P | P | P | P | P |
| topic:direct | M | P | C | P | C | P | P | P |
| topic:lemma | M | P | C | P | C | P | P | P |
| topic:related | M | P | C | P | C | P | C | P |
| topic:wordnet | C | P | C | P | C | P | P | P |
| topic:cross-stage | C | P | C | P | C | P | P | P |
| rules:overview | M | P | C | P | P | P | P | P |
| rules:stage | M | P | C | P | C | P | P | P |
| rules:triggered | M | P | C | P | C | P | P | P |
| rules:not-triggered | M | P | C | P | P | P | P | P |
| rules:evidence | M | P | C | P | C | P | P | P |
| rules:trace | M | P | C | P | C | P | P | P |
| rules:sources | M | P | C | P | P | P | P | P |
| engine:overview | M | P | C | P | P | P | P | P |
| engine:goal | M | P | C | P | P | P | P | P |
| engine:primary | M | P | C | P | C | P | P | P |
| engine:working | M | P | C | P | P | P | P | P |
| engine:attention | M | P | C | P | P | P | P | P |
| engine:next | M | P | C | P | P | P | P | P |
| engine:provenance | M | P | C | P | C | P | P | P |
| final:overview | M | P | C | P | C | P | P | P |
| final:fields | M | P | C | P | P | P | P | P |
| final:response | M | P | C | P | P | P | P | P |
| final:complete | M | C | C | P | C | P | P | P |
| final:limitations | M | P | C | M | P | M | P | P |

### Rendering coverage inspected

`renderNlpTransparency` builds all 45 panels. Student panels use `renderStudentInputInspector`; backend and several NLP/concept/final panels are inline. NLP/topic detail uses `transparencyRenderSubtabEvidence`; related concepts use `renderRelatedTopicConcepts`; WordNet and continuity use `renderStudentWordNet` and `renderStudentCrossStage`. Rules use `renderTransparencyStageFindings`, `renderTransparencyBodyParagraphs`, `renderTransparencyRules`, and `transparencyRuleInputs`. Feedback uses `renderTransparencyFeedback` and `renderScaffoldingTrace`. Final export uses `buildFullAnalysisReport`. `transparencyProcessExplanation` is unused; its common raw-text input incorrectly suggests a component input. Existing `info.next` and handoff entries mix navigation, possible consumers and observed links.

### Source findings that change the explanation

* Introduction list detection requires absence of **any qualifying subject-linked clause**, not merely absence of a root clause. Some registry descriptions are less precise; preserve the registry while explain the actual `_list_or_fragment_finding` condition separately.
* `INTRO.TEXT.PRESENT` is emitted from `word_count`; it is not a gate that makes later clause rules execute. `FeedbackService.generate` reads findings and only resolves provenance IDs after selecting messages.
* Introduction/Body uncertainty and prohibited conclusions are unconditional arrays in `analyze`; Conclusion has uncertainty but no configured `prohibited_conclusions` array. Do not manufacture one.
* WordNet events document candidates. `FeedbackService` has no WordNet candidate read; lexical continuity list messages use direct/lemma matches. Conclusion retains paraphrase relationships separately from new-material selection.
* Evaluation records are reconstructed by `research_inspector._observed_rule_decisions` after feedback. They are not a live condition log.
* Body detail uses qualifying clauses, not sentence count. Four sentences followed by one sentence can still select generic Primary Feedback when the parser reports multiple qualifying clauses in each paragraph.

## Evidence unavailable without protected instrumentation

| Missing record | Producer / reason | Instrumentation requiring separate approval |
|---|---|---|
| Request payload, individual authorization/validation outcomes, handler duration | `app.py:analyze_payload`, middleware; student response does not serialize them | Record sanitized accepted fields and check outcomes/timings; touches request handler |
| Model internal scores and reasons for a POS/head prediction | `NLPService.parse/analyze_doc`; only final annotations serialized | Model-specific instrumentation; protected NLP code |
| All rejected concept candidates and extraction-local normalization steps | `TopicService._extract_concepts`; returns grouped accepted occurrences | Retain per-candidate decisions; protected extraction |
| Rejected lexical windows | `TopicService._find_matches`; returns accepted matches | Add window-level trace; protected matching |
| Full previous-stage concepts | coordinator trace + `app.py:compact_student_transparency_trace`; selected-stage response removes redundant records | Retain earlier concept inputs; protected response/trace path |
| Subordinator short-circuit Boolean log and narrow safeguard outcome | `IntroductionRuleBase._incomplete_subordinator_evidence/_before_adjective_clause_supported`; returns warnings only | Record each reached predicate and safeguard; protected Rule Base |
| Unselected message texts / independent append-to-item trace | `FeedbackService.generate*`; records chosen branch and field-level provenance | Instrument actual reached branches and list append records; protected feedback |

Source-verifiable comparisons over retained fields may be displayed, explicitly labeled as reconstruction. None of these missing logs may be replaced with invented execution claims.

## After implementation (before/after comparison)

Every panel now renders a causal block (rows A-H with evidence tags) plus an expandable "Technical causal walkthrough" disclosure with actual retained values, source-derived comparisons and a "Evidence the implementation never retains" block. A = exact essay snapshot (row plus expandable preserved-text viewer or jump-to-inspector), B = recorded component input path, C = purpose, D = operation with source function, E = intermediates, F = explained decision, G = actual use with consumer basis, H = limitation and cause.

Enforced permanently by `tests/test_causal_transparency.py`: all 45 panels expose the A, B, "E-F", H rows and a `causalDetails` disclosure containing a NOT RECORDED missing-evidence row; every `rules:trace` row has a measured comparison with event parity; selected feedback branches pass with all earlier conditions false and later rows SKIPPED; independent What's Working / Needs Attention append-check counts equal the actual list sizes; uncertainty/prohibited wording opens a disclosure labelled "unconditional stage-scope statement".

| Panel | A | B | C | D | E | F | G | H |
|---|---|---|---|---|---|---|---|---|
| student:overview | C | C | C | C | C | C | C | C |
| student:text | C | C | C | C | C | C | C | C |
| student:context | C | C | C | C | C | C | C | C |
| backend:overview | C | C | C | C | C | C | C | C |
| backend:validation | C | C | C | C | P | C | C | C |
| backend:response | C | C | C | C | P | C | C | C |
| backend:flow | C | C | C | C | P | C | C | C |
| nlp:overview | C | C | C | C | C | C | C | C |
| nlp:sentences | C | C | C | C | C | C | C | C |
| nlp:tokens | C | C | C | C | C | C | C | C |
| nlp:lemmas | C | C | C | C | C | C | C | C |
| nlp:pos | C | C | C | C | C | C | C | C |
| nlp:dependencies | C | C | C | C | C | C | C | C |
| nlp:chunks | C | C | C | C | C | C | C | C |
| nlp:pipeline | C | C | C | C | P | C | C | C |
| concept:overview | C | C | C | C | C | C | C | C |
| concept:concepts | C | C | C | C | C | C | C | C |
| concept:occurrences | C | C | C | C | C | C | C | C |
| topic:overview | C | C | C | C | C | C | C | C |
| topic:focus-terms | C | C | C | C | C | C | C | C |
| topic:normalization | C | C | C | C | C | C | C | C |
| topic:direct | C | C | C | C | C | C | C | C |
| topic:lemma | C | C | C | C | C | C | C | C |
| topic:related | C | C | C | C | C | C | C | C |
| topic:wordnet | C | C | C | C | C | C | C | C |
| topic:cross-stage | C | C | C | C | C | C | C | C |
| rules:overview | C | C | C | C | C | C | C | C |
| rules:stage | C | C | C | C | C | C | C | C |
| rules:triggered | C | C | C | C | C | C | C | C |
| rules:not-triggered | C | C | C | C | C | C | C | C |
| rules:evidence | C | C | C | C | C | C | C | C |
| rules:trace | C | C | C | C | C | C | C | C |
| rules:sources | C | C | C | C | C | C | C | C |
| engine:overview | C | C | C | C | C | C | C | C |
| engine:goal | C | C | C | C | C | C | C | C |
| engine:primary | C | C | C | C | C | C | C | C |
| engine:working | C | C | C | C | C | C | C | C |
| engine:attention | C | C | C | C | C | C | C | C |
| engine:next | C | C | C | C | C | C | C | C |
| engine:provenance | C | C | C | C | C | C | C | C |
| final:overview | C | C | C | C | C | C | C | C |
| final:fields | C | C | C | C | C | C | C | C |
| final:response | C | C | C | C | C | C | C | C |
| final:complete | C | C | C | C | C | C | C | C |
| final:limitations | C | C | C | C | C | C | C | C |

Before totals: A had 40 missing; B had 44 partial; D and F were missing on final:limitations; E was missing on 3 panels; G was partial on 44 panels; H was partial on 42 panels. After: A/B/C/D/F/G/H are complete on all 45 panels.

### Residual partials (E column), each labelled NOT RECORDED in the UI

* `backend:validation` - individual per-field validation and authorization outcomes are not serialized; only acceptance (or a 400 error response) is observable.
* `backend:response` - compaction, serialization and handler-timing intermediates are not retained; the full response fields are shown instead.
* `backend:flow` - step rows are a STATIC EXPLANATION of the source control flow; per-request step outcomes and durations are not recorded.
* `nlp:pipeline` - enabled/disabled components are recorded but per-component timings and model-internal decision scores are not measured.

These four cells are exactly rows 1, 6, 7 and 2 of the unavailable-evidence table above; none was replaced with an invented execution claim.
