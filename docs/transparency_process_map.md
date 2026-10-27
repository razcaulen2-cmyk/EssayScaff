# Transparency restoration: source-verified implementation reference

Established before interface edits, 2026-10-19. Baseline: **300 tests passed**
(`.venv\Scripts\python.exe -m pytest -q`, 78.68 s). Source locations below
refer to functions, so remain useful when frontend line numbers change.

## Recovered implementation

`static/app.js` retains `STUDENT_TRANSPARENCY_SUBTABS`,
`STUDENT_TRANSPARENCY_PROCESS_INFO`, `createTransparencyTabs`,
`transparencyRenderSubtabEvidence`, and `renderNlpTransparency`. The inventory
contains **28 views**: Text Processing 8, Topic Matching 7, Rule Evidence 6,
Feedback Explanation 7. The current template lacks `nlp-transparency-content`
and `displayFeedback` does not call the renderer. Existing S3.2 tests explicitly
require this removal. These are direct evidence of the replacement; no historical
commit or dated pre-S3.2 dashboard snapshot was found in this project. Exact
historical appearance is unverified. Retained rendering code is the recovery basis.

## Actual call / data flow

```text
editor input -> state.drafts -> runStageAnalysis (manual or existing 6s debounce)
  -> POST /api/analyze-stage (include_transparency_trace=true)
    -> require_account / require_csrf_token -> analyze_stage -> analyze_payload
       -> resolve authorized assignment OR practice topic/focus from payload
       -> validate types, stage, nonblank selected text, limits and prior context
       -> EssayAnalysisService.analyze
          -> TopicService.prepare_teacher_context (once per coordinator request)
             -> _unique_focus_terms -> NLPService.nlp(term) for each phrase
             -> if no focus list: NLPService.nlp(topic) -> _extract_concepts first
          -> for EACH supplied section, TopicService.analyze
             -> NLPService.parse -> self.nlp(text) -> reusable spaCy Doc
             -> NLPService.analyze_doc(Doc): serialize observations
             -> TopicService._extract_concepts(Doc)
             -> reuse prepared teacher context -> _find_matches(Doc, focus)
             -> _wordnet_status -> conditional _wordnet_suggestions
          -> for EACH supplied stage, its RuleBase.analyze(prepared outputs)
             -> validate_prepared_analysis (no reparse)
             -> stage-specific structural/lexical helpers
             -> Body/Conclusion: conditional compare_stage_concepts
                -> _wordnet_candidates (separate from direct suggestions)
             -> _rule_events (emitted events)
             -> FeedbackService.generate / generate_body / generate_conclusion
          -> when trace requested, build_rule_evaluation_trace
             -> rule_inventory + _observed_rule_decisions (no rule/NLP rerun)
          -> stage results + trace
       -> select requested stage -> compact repeated student trace/provenance
       -> jsonify
  -> request ID + assignment/input snapshot + stage/view checks
  -> cache result in state.analyses, snapshot in state.analysisSnapshots
  -> displayFeedback -> five Writing Feedback fields
  -> dashboard and Copy Full Analysis read the SAME cached selected-stage response
```

All supplied earlier stages are prepared and analyzed by the coordinator too;
Flask returns only the selected stage. The diagram must not imply that the
educational order of annotation tables is spaCy's component execution order.

## Operation map and four explanations

Each row records WHAT, HOW, WHY, WHERE (direct consumers), input/output,
conditionality, and source evidence. The UI uses the same distinctions.

| Operation / WHAT | HOW (actual input → processing → output) | WHY | WHERE output goes | Condition / source |
|---|---|---|---|---|
| Text reception: receive the exact draft and assignment | `runStageAnalysis` sends selected text, topic/focus, optional assignment ID and prior sections; `analyze_payload` resolves authorized assignment data and validates values → coordinator arguments | Checks need a known stage, text and assignment targets | `EssayAnalysisService.analyze` | Nonblank selected text/topic, valid types/lengths; `static/app.js:runStageAnalysis`, `app.py:analyze_stage, analyze_payload` |
| Focus preparation: build lexical targets | Explicit phrases, or noun concepts from a separately parsed topic, go through `_unique_focus_terms`; alphabetic tokens → casefolded lemmas; deduplicate normalized forms | Reuse consistent targets across supplied sections | `_find_matches`, direct WordNet suggestion inputs | Topic parse only without explicit terms; `topic_service.py:prepare_teacher_context, _unique_focus_terms` |
| spaCy document processing: annotate one section | `TopicService.analyze` → `NLPService.parse` → loaded `en_core_web_sm` Language → Doc; enabled pipeline order comes from runtime metadata | Share one parsed section across observations and rules | `analyze_doc`, `_extract_concepts`, `_find_matches` | Once per supplied full section, plus separate focus/topic calls; `nlp_service.py:__init__, parse`; coordinator lines 74–88 |
| Sentence segmentation: identify sentence boundaries | Parser-backed `Doc.sents`; first/last nonspace token offsets → exact sentence text, spans, tokens, dependencies | Clause and paragraph checks need sentence-local evidence | Introduction `_clause_candidates`, subordinator checks; shared clause/paragraph helpers for Body/Conclusion | Empty input returns no sentences; `nlp_service.py:analyze_doc` |
| Tokenization: split words and punctuation | spaCy tokenizer creates Doc tokens; serializer omits space tokens and records index/text/start/end/is_alpha | Map matches and annotations to original text | Topic token windows, concept extraction, sentence/rule evidence | All actual nonspace tokens retained; `nlp_service.py:_token_data, analyze_doc` |
| Lemmatization: supply base forms | Installed pipeline assigns `lemma_`; serializer keeps it; TopicService `_lemma` uses lemma or surface fallback, then casefolds | Match inflected forms and group lexical candidates | Focus normalization/matching; concept recurrence and comparisons | Alphabetic filtering for lexical operations; `topic_service.py:_lemma, _unique_focus_terms, _find_matches, _extract_concepts` |
| POS/tag prediction: label word types | Installed tagger/attribute pipeline assigns `pos_`, `tag_`; serializer records both | Filter noun concepts, content words and finite predicate candidates | Stage rules and `_extract_concepts`; WordNet POS mapping | No new prediction in UI; `nlp_service.py:_token_data`, stage FINITE_TAGS / CONTENT_POS |
| Dependency parsing: connect tokens to heads | Parser supplies `dep_`, head text; sentence dependencies additionally record `head_start`; subject/object lists filter selected relations | Verify parser-labeled subject attachment to candidate predicates | Introduction `_clause_candidates`; `stage_evidence.clause_candidates_from_sentences` | Missing head position must remain missing; `nlp_service.py:analyze_doc` |
| Noun chunks: collect parser phrase spans | `Doc.noun_chunks` → text/start/end; TopicService separately reads the same Doc chunks | Supply noun-phrase lexical candidates | `_extract_concepts` directly from Doc (not from serialized noun_phrases) | `nlp_service.py:analyze_doc`, `topic_service.py:_extract_concepts` |
| Concept extraction: group noun-like wording | Alphabetic noun-chunk tokens containing NOUN/PROPN plus individual NOUN/PROPN tokens → lemma groups, unique spans, token indices, methods, POS | Record recurrence and compare sections | Body paragraph concepts, Introduction–Body and Conclusion comparisons; direct WordNet suggestions | Introduction rules do not consume concepts; concept output still retained in trace; `_extract_concepts` |
| Focus matching: compare targets with draft | Consecutive alphabetic-token windows compare casefolded surface first, then lemmas; allow whitespace/apostrophe/hyphen separators but reject blank-line boundaries → one direct OR normalized record per eligible window/target | Show lexical coverage with exact positions | Stage `_all_matches`/`_all_focus_matches`/`_topic_matches`, then rule findings | Unique term count differs from occurrence count; `topic_service.py:_find_matches` |
| Direct WordNet: optional lexical candidates | Probe corpus with `synsets('essay')`; unmatched single-word targets vs single-word noun concepts; exactly one shared synset → separate suggestions | Surface limited lexical relations beyond exact/lemma coverage | Conclusion lexical candidate output, inspector/copy/dashboard; not confirmed focus coverage | Coordinator enables only Conclusion; disabled Introduction/Body do not probe corpus; `_wordnet_status, _wordnet_suggestions` |
| Paragraph segmentation: blank-line groups | `split_paragraph_spans` trims outer whitespace; `sentence_segments_in_span` clips existing token/dependency records without parsing → paragraph observations | Scope Body/Conclusion evidence correctly | Body per-paragraph findings, continuity; Conclusion paragraph distribution | Body/Conclusion only; `stage_evidence.py`, `BodyRuleBase._analyze_paragraph`, `ConclusionRuleBase._paragraphs` |
| Clause candidates: subject/predicate checks | VERB/AUX + tag in VB/VBD/VBP/VBZ + accepted dependency + subject whose head_start equals predicate start → recorded candidates | Supply structural signals without claiming valid meaning | Introduction central/context/development; Body topic/detail; Conclusion synthesis/closure | Introduction central candidates restrict to ROOT; shared helper accepts configured clause dependencies; `introduction_rules.py:_clause_candidates`, `stage_evidence.py:clause_candidates_from_sentences` |
| Introduction findings | Root candidates + focus spans → context candidates; clause absence and noun/sentence thresholds → list/fragment flags; SCONJ attachment checks; remove incomplete-marker sentence clauses before development count | Explain observable introduction structure | Introduction `_rule_events` and FeedbackService.generate | See exact helpers `_list_or_fragment_finding`, `_incomplete_subordinator_evidence`, `_context_candidates`, `_development_finding`; at least two supported clauses for development |
| Body findings | Per-paragraph clause + focus/recurrence → topic candidates; >=2 clauses → detail candidates; adjacent content surface/lemma intersections, repeated words/lemmas/two-word openings, regex example/transition scans | Explain paragraph development and lexical links | Body `_rule_events`, `generate_body` | No scores of semantic unity; `body_rules.py:_analyze_paragraph`, `_topic_sentence_candidates`, `_supporting_detail_candidates`, `_sentence_unity`, `_cross_paragraph_continuity`; shared repetition helper |
| Cross-stage lexical comparison | Prepared concepts with same normalized form and identical POS lists: equal casefolded surface → direct, other surface → lemma pairs; preserve source-specific spans | Show observed continuity | Body/Conclusion findings, events, feedback | Earlier text required; `stage_evidence.py:compare_stage_concepts`; Body filters concepts to paragraph spans |
| Cross-stage WordNet | Corpus probe; different single-word concepts with equal mapped POS; skip pair if both words already common forms; cache synsets per word/POS; exactly one shared synset → candidate | Expose limited relationship candidates | Optional WordNet events; Conclusion new-material paraphrase candidate record | Inside Body/Conclusion comparisons, missing context skips; resource-missing status preserved; `stage_evidence.py:_wordnet_candidates` |
| Conclusion findings | Sentence clause with >=2 prior normalized concepts → synthesis candidate; final ROOT clause or listed expression → closure; final cue words recorded separately; compare content lemmas and exclude closing-expression/nested component spans → new-material candidates | Explain lexical return and ending signals | Conclusion `_rule_events`, `generate_conclusion` | Missing earlier text yields unavailable/partial states; `conclusion_rules.py:_synthesis_candidates, _closing_candidates, _new_material_observations, _occurrence_is_nested_in_larger_phrase` |
| Rule Event emission | Stage `_rule_events` appends ID, condition, evidence, flag, evidence type and limit at existing branches | Preserve why an observation fired | FeedbackService and trace reconstruction | Actual emitted list is `analysis.rule_evidence`; not the inventory |
| Evaluation trace construction | `build_rule_evaluation_trace` joins static/dynamic inventory, emitted IDs and `_observed_rule_decisions` from returned findings → status/basis/configuration/source metadata | Inspect alternatives without pretending missing events are negatives | Dashboard/copy/inspector only; FeedbackService has already run | Trace mode only; no second rule run; `research_inspector.py:rule_inventory, _observed_rule_decisions` |
| Feedback selection | Stage analysis + emitted events → ordered primary/next branches; independent positive/caution checks; retain links only to emitted events → five fields, provenance and optional decision trace | Turn observations into predefined revision advice | Coordinator stage feedback → Flask → Writing Feedback and transparency | First matching priority branch wins; lists may have several checks; `feedback_service.py:generate, generate_body, generate_conclusion` |
| Response packaging/display | Select requested stage, compact repeated records and provenance to field/rule links, jsonify; JS checks request ID, input/assignment snapshot, stage/view before caching | Prevent old responses appearing as current writing | `state.analyses`, feedback DOM, transparency dashboard and copy | `app.py:compact_student_transparency_trace, compact_student_feedback, analyze_payload`; JS `runStageAnalysis, displayFeedback, analysisSnapshot` |
| Copy report | `buildFullAnalysisReport` serializes complete available selected-stage technical evidence from cache, with source paths and missing-data labels | Preserve the inspectable record | Clipboard or existing manual-copy fallback | Current successful snapshot required; no fetch/NLP/storage; `currentAnalysisForExport`, copy listener |

## Retained versus backend-only data

Student trace retains runtime/pipeline metadata, prepared focus terms, selected
stage concept output, direct WordNet execution/lookup evidence, previous input
sections, feedback branches and priority, timings, and output counts. Full
linguistic observations are in Introduction/Conclusion analysis and Body trace.
Rule trace is in analysis; emitted events stay separate. Compact feedback links
are resolved against these events in the browser. Duplicate topic-matching output,
selected-stage input copy, cross-stage concept input copies, and duplicate rule
trace are removed by Flask, but equivalent evidence remains elsewhere.

The live spaCy Doc, vectors, model probabilities, NER entities, complete per-token
component internals, hidden message alternatives, and per-component timings are
not returned. No such data may be reconstructed or fabricated. Earlier-stage full
analyses computed by the coordinator are not returned in the selected response.
Analysis does not save a draft, revision, or submission; separate routes do that.

## Source-audit caution

Some existing research-inspector registry summaries are less exact than the
algorithm: the Introduction subordinator configuration text abbreviates the
actual branching logic, and list descriptions sometimes say root clause although
the implementation checks all qualifying clauses. Preserve backend metadata,
identify it as a registry summary, and use the verified helper explanations when
describing the algorithm. Do not change the Rule Bases or Inspector to resolve
this presentation task.
