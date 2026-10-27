/* Cached-evidence presentation only. No requests, NLP, rule or feedback execution. */
"use strict";

globalThis.NlpProcessExplorer = (() => {
  const selections = new Map();
  const GROUPS = [
    ["preparation", "01", "Assignment Preparation"],
    ["linguistic", "02", "Linguistic Processing"],
    ["topic", "03", "Topic Processing"],
    ["rules", "04", "Rule Evaluation"],
    ["feedback", "05", "Feedback Decisions"],
    ["output", "06", "Output & Technical Trace"],
  ];
  const GROUP_TITLES = Object.fromEntries(GROUPS.map(([key, , title]) => [key, title]));
  const PROCESS_ORDER = GROUPS.map(([key]) => key);
  // Each original evidence section has exactly one home. These stable keys also
  // keep source links and the complete export index addressable without UI tabs.
  const SECTION_OWNERS = {
    header: ["student:overview", "student:text", "student:context", "backend:overview", "backend:validation", "backend:response"],
    "focus-preparation": ["topic:focus-terms", "topic:normalization", "backend:flow"],
    tokens: ["nlp:overview", "nlp:pipeline", "nlp:tokens"],
    sentences: ["nlp:sentences"], lemmas: ["nlp:lemmas"], pos: ["nlp:pos"],
    dependencies: ["nlp:dependencies"], "noun-phrases": ["nlp:chunks"],
    concepts: ["concept:overview", "concept:concepts", "concept:occurrences"],
    "topic-matching": ["topic:overview", "topic:direct", "topic:lemma"],
    wordnet: ["topic:wordnet"], "related-concepts": ["topic:related"],
    "cross-stage": ["topic:cross-stage"],
    "rule-events": ["rules:overview", "rules:stage", "rules:triggered", "rules:not-triggered", "rules:evidence", "rules:trace", "rules:sources"],
    "feedback-decision": ["engine:overview", "engine:goal", "engine:primary", "engine:working", "engine:attention", "engine:next", "engine:provenance", "final:overview", "final:fields", "final:response", "final:complete", "final:limitations"],
  };
  const LABELS = { EXECUTED: "Executed", SKIPPED: "Skipped", NOT_APPLICABLE: "Not applicable", UNAVAILABLE: "Unavailable" };
  const titles = { INTRODUCTION: "Introduction", BODY: "Body", CONCLUSION: "Conclusion" };
  const present = value => value !== undefined && value !== null;
  const execution = (status, basis, duration = null) => ({ status, label: LABELS[status] || status, basis, duration_ms: duration });
  const step = (data, id) => data.stageTrace?.topic_service?.steps?.find(item => item.id === id);
  const own = (object, key) => Object.prototype.hasOwnProperty.call(object || {}, key);

  function catalog(stage) {
    const entries = [
      ["focus-preparation", "preparation", "Teacher Focus-Term Preparation", "Prepare the assignment's comparison targets before processing the supplied sections.", "TopicService.prepare_teacher_context normalizes and deduplicates supplied terms, or derives noun candidates from the topic. It calls the loaded model for each focus phrase (and the topic when deriving candidates). This shared preparation precedes section parsing; its calls are separate from the one full-text Doc per section.", "services/topic_service.py: prepare_teacher_context, _unique_focus_terms; services/essay_analysis_service.py: analyze", "Prepared targets go to each supplied section's TopicService.analyze and its lexical matching.", "Prepared focus words are comparison targets, not a complete definition of relevant ideas."],
      ["focus-normalization", "preparation", "Focus-Term Normalization", "Record the original and normalized forms prepared for lexical comparison.", "Read the prepared focus specifications returned by prepare_teacher_context. Each record retains the teacher's original term, its surface words, its lemmatized normalized words and the WordNet parts of speech mapped from the focus tokens.", "services/topic_service.py: prepare_teacher_context, _unique_focus_terms, _lemma, _wordnet_pos", "The prepared surface sequence and lemma sequence are the two comparison targets used by TopicService._find_matches.", "Normalization is word-form handling. It does not decide that two different lemmas mean the same idea."],
      ["tokens", "linguistic", "Tokenization", "Split the analyzed writing into tokens and retain their original positions.", "NLPService.parse creates one spaCy Doc for the section. analyze_doc serializes Token.i, text and offsets. The other linguistic entries inspect annotations of this same completed Doc, not extra model runs.", "services/nlp_service.py: parse, analyze_doc, _token_data", "Original token positions are reused by concept extraction, focus-term matching and stage evidence spans.", "Tokens include punctuation. A token count is not a writing-quality measure; model-internal tokenizer decisions are not logged."],
      ["pos", "linguistic", "Part-of-Speech Tagging", "Record the word-class labels and fine tags predicted for each token.", "Read the existing spaCy Token.pos_ and Token.tag_ annotations serialized from the shared Doc. Enabled model components are recorded in Developer Evidence; no separate POS invocation or timing is claimed.", "services/nlp_service.py: _token_data, analyze_doc", "Noun labels constrain concept extraction; verb/auxiliary labels and fine tags help stage clause checks; eligible POS also constrains lexical resources.", "Predicted POS and tags may be wrong. A label does not prove grammatical or semantic correctness."],
      ["dependencies", "linguistic", "Dependency Parsing", "Record predicted grammatical relationships between words.", "Read the retained dependency label, head text and head_start for each token. The existing dependency tree draws only relationships supported by those records.", "services/nlp_service.py: analyze_doc; services/stage_evidence.py: clause_candidates_from_sentences", "Stage analyzers use subject-to-predicate head links with their POS/tag conditions to form clause candidates.", "Parser attachments can be mistaken. Dependency relationships do not establish a valid argument or the model's internal reasoning."],
      ["lemmas", "linguistic", "Lemmatization", "Record the predicted base form of each token.", "Read Token.lemma_ from the already annotated Doc. TopicService uses casefolded lemma-or-text forms for its recorded normalized comparisons.", "services/nlp_service.py: _token_data; services/topic_service.py: _lemma", "Normalized forms feed focus-term matching, concept grouping, recurrence and earlier-section comparisons.", "A shared lemma is word-form overlap, not semantic equivalence or proof of relevance."],
      ["sentences", "linguistic", "Sentence and Paragraph Detection", "Locate the recorded sentences and applicable paragraph boundaries.", "spaCy Doc.sents supplies sentence predictions. analyze_doc retains first/last nonspace-token bounds. Body and Conclusion additionally split blank-line paragraphs and filter the same recorded sentence/token spans without reparsing.", "services/nlp_service.py: analyze_doc; services/stage_evidence.py: split_paragraph_spans, sentence_segments_in_span", "Sentence bounds constrain clause and sentence-pair checks. Paragraph spans constrain Body and Conclusion observations.", "Blank-line boundaries are not rhetorical judgments. Introduction has no independent paragraph detector; no paragraph count is invented for it."],
      ["noun-phrases", "linguistic", "Noun Phrase Extraction", "Record noun-chunk spans predicted by spaCy.", "Read Doc.noun_chunks retained by analyze_doc. TopicService._extract_concepts reads the same Doc's noun chunks and individual noun/proper-noun tokens.", "services/nlp_service.py: analyze_doc; services/topic_service.py: _extract_concepts", "Qualifying chunks and noun tokens become grouped lexical concept candidates.", "A noun phrase is a syntactic candidate, not a verified important idea or topic sentence."],
      ["concepts", "topic", "Concept Candidate Extraction", "Group noun-based wording and preserve each source occurrence.", "TopicService._extract_concepts retains alphabetic noun-chunk tokens with a NOUN/PROPN, plus individual noun/proper-noun tokens. It groups normalized forms and deduplicates identical occurrence spans.", "services/topic_service.py: _extract_concepts, _lemma", "Body uses paragraph recurrence and earlier-section comparisons; Conclusion uses comparison/synthesis/new-material observations. Introduction's rules do not consume its concept list.", "These lexical candidates do not identify meaning, importance or valid rhetorical roles."],
      ["topic-matching", "topic", "Teacher Focus-Term Matching", "Compare configured targets with the analyzed wording.", "TopicService._find_matches compares consecutive eligible alphabetic-token windows with prepared surfaces first, then lemma sequences. Recorded method and offsets distinguish direct from normalized matches; a direct occurrence is not counted again as normalized.", "services/topic_service.py: _find_matches; services/*_rules.py: lexical topic evidence", "Recorded lexical coverage and spans feed the stage's topic/context observations and applicable Rule Events.", "Missing words may reflect paraphrase. Present words can occur in nonsense. Neither result establishes semantic relevance."],
      ["wordnet", "topic", "WordNet Processing", "Inspect the optional focus-term lexical-resource lookup and any recorded cross-stage comparisons.", "This page reads TopicService's direct suggestion path and the nested cross-stage WordNet paths. The coordinator enables direct suggestions only for Conclusion. Recorded lookup pairs retain both compared forms, their synset IDs, shared IDs and whether a candidate was emitted.", "services/topic_service.py: _wordnet_status, _wordnet_suggestions; services/stage_evidence.py: _wordnet_candidates; services/essay_analysis_service.py: analyze", "Direct suggestions are retained in applicable Conclusion lexical evidence. Cross-stage candidates are retained in continuity observations. Feedback selection does not certify their meaning.", "A shared synset is only a candidate and is not context-sensitive word-sense disambiguation. An absent candidate does not prove unrelated meaning."],
      ["related-concepts", "topic", "Related-Word Resource Evidence", "Inspect the existing informational related-word observations.", "Read related_topic_concept_evidence produced by the existing lexical-resource helper from the prepared observations. This side branch is attached to the response separately and does not change rules or feedback.", "services/topic_service.py: _with_related_concepts; services/related_topic_concept_service.py", "The recorded informational-only result is used by evidence inspection and the full export, not to select a writing concern.", "A related-word lookup does not prove that a sentence is relevant, understandable or correct."],
      ["cross-stage", "topic", stage === "BODY" ? "Introduction–Body Lexical Comparison" : stage === "CONCLUSION" ? "Earlier-Section–Conclusion Comparisons" : "Earlier-Section Comparisons", "Inspect the actual lexical comparisons with supplied earlier writing.", "These comparisons are nested inside the applicable Body/Conclusion Rule Base. compare_stage_concepts compares retained concept occurrences and conditionally records its own WordNet lookup paths. Introduction has no earlier section to compare.", "services/body_rules.py: _introduction_continuity; services/conclusion_rules.py; services/stage_evidence.py: compare_stage_concepts", "Continuity observations and applicable informational events feed the existing stage checks. The retained records identify actual field/provenance links where available.", "Overlap does not prove coherence or logical support; low overlap does not prove disconnection. Missing earlier context is availability, not a student writing defect."],
    ];
    if (stage === "INTRODUCTION") entries.push(
      ["stage-patterns", "rules", "Introduction Sentence and Clause Checks", "Inspect the Introduction's recorded statement, list, development and possible-incomplete patterns.", "IntroductionRuleBase reuses the prepared sentence/token/dependency observations. Its existing finite-predicate, linked-subject, list and subordinator conditions produce structural candidates.", "services/introduction_rules.py: analyze, _clause_candidates, _incomplete_subordinator_evidence, _rule_events", "The stage's emitted Rule Events and recorded observations support FeedbackService.generate.", "These checks can miss constructions or flag complete sentences. They do not establish thesis clarity, correctness or argument quality."],
      ["sentence-connection", "rules", "Sentence Topic-Connection Review", "Inspect the existing cautious local wording-connection review.", "The existing helper reuses recorded focus matches, neighboring content lemmas, reference cues and verified sentence spans. No new relevance detector is run by this view.", "services/introduction_sentence_evidence.py", "Only its emitted review event can support the existing Introduction topic-connection lesson.", "A wording gap is not proof that a sentence is unrelated. Pronouns and demonstratives are not resolved references."]);
    if (stage === "BODY") entries.push(
      ["stage-patterns", "rules", "Paragraph and List Pattern Checks", "Inspect the Body's blank-line paragraph spans and list-like patterns.", "BodyRuleBase._analyze_paragraph filters the single prepared document into paragraph spans. A recorded no-clause pattern plus its existing sentence/noun thresholds supplies the list-like candidate.", "services/body_rules.py: _paragraph_spans, _analyze_paragraph", "Paragraph boundaries and list candidates feed the existing Body events and paragraph-specific feedback selection.", "A planning list can be deliberate. Keyword presence is not a paragraph strength or semantic approval."],
      ["topic-sentences", "rules", "Topic Sentence Checks", "Locate possible topic-sentence structures in each Body paragraph.", "The existing heuristic requires a qualifying clause plus a same-sentence focus match or a concept recurring across paragraph sentences. The retained reasons and spans show which candidates met it.", "services/body_rules.py: _topic_sentence_candidates", "Paragraph-specific TOPIC_SENTENCE events preserve the candidates and can support recorded observations.", "A candidate is not a verified opening statement, rhetorical role or relevant main idea."],
      ["supporting-details", "rules", "Supporting Detail Checks", "Inspect additional structural development candidates for each paragraph.", "BodyRuleBase._supporting_detail_candidates records qualifying clause/statement structures when its existing count condition is met. Example-marker wording alone is not enough, and no marker is required.", "services/body_rules.py: _supporting_detail_candidates", "The paragraph's CANDIDATE or NOT_OBSERVED event supports the existing Body observation or a supported development concern.", "Candidate counts cannot establish relevance, validity or sufficient support. One sentence may contain more than one qualifying structure."],
      ["repetition", "rules", "Repeated Wording and Sentence Openings", "Locate repeated wording and recorded two-word sentence openings.", "The existing repetition_observations helper groups surface words, normalized content terms and identical first two alphabetic words, retaining original occurrences.", "services/stage_evidence.py: repetition_observations; services/body_rules.py: _rule_events", "A fired repeated-opening event can support the existing conditional Sentence Fluency lesson. Word frequency alone does not force a corrective lesson.", "Repetition can be intentional or help continuity. These observations do not determine style quality."]);
    if (stage === "CONCLUSION") entries.push(
      ["stage-patterns", "rules", "Conclusion Structure and Closure Checks", "Inspect the Conclusion's recorded closing-position and sentence patterns.", "The existing analyzer reuses prepared clauses, blank-line paragraphs, final-sentence position and configured closing expressions.", "services/conclusion_rules.py: _text_presence, _paragraphs, _closing_candidates", "Recorded closure and structure observations feed Conclusion events and the existing feedback branches.", "A final sentence or closing phrase does not prove an effective conclusion."],
      ["synthesis", "rules", "Earlier-Idea Combination Checks", "Inspect sentence candidates that combine recorded wording from earlier sections.", "The existing synthesis check requires applicable earlier context, qualifying clause evidence and recorded earlier-concept matches in the sentence.", "services/conclusion_rules.py: _synthesis_candidates", "The candidate observations support the existing synthesis event and prepared ending review.", "Combining earlier words is not verified synthesis or logical integration."],
      ["new-material", "rules", "New-Material Wording Checks", "Inspect wording not observed in the supplied earlier sections.", "The existing check compares retained concept/lemma forms, nested occurrences and known combinations. It retains optional paraphrase candidates separately.", "services/conclusion_rules.py: _new_material_observations, _occurrence_is_nested_in_larger_phrase", "Recorded unobserved-word observations feed the existing Conclusion events and feedback conditions.", "Unseen wording may be rephrasing; it does not prove that a genuinely new argument was introduced."],
      ["repetition", "rules", "Conclusion Repetition Observations", "Inspect recorded repeated wording in the ending.", "Read the existing surface/lemma/opening groups from repetition_observations, with their source positions.", "services/stage_evidence.py: repetition_observations; services/conclusion_rules.py", "These Conclusion repetition observations are retained for inspection; they do not automatically select a feedback branch.", "Repetition is not automatically an error or a measure of conclusion quality."]);
    entries.push(
      ["rule-events", "rules", "Rule Events and Evaluation Evidence", "Inspect this stage's emitted events and recorded rule-condition evidence.", "The stage _rule_events produces events from its observations before feedback selection. The evaluation trace is reconstructed afterwards from returned findings and rule inventory; it is not another Rule Base run or an input to FeedbackService.", "services/*_rules.py: _rule_events; services/research_inspector.py: build_rule_evaluation_trace, rule_inventory; services/essay_analysis_service.py", "Stage observations select feedback; emitted event IDs support field provenance. The later reconstructed trace supports inspection only.", "Only recorded evaluation statuses can be claimed. An absent event is not automatically a tested negative; the trace is not a model-internal execution log."],
      ["feedback-decision", "feedback", "Feedback Branch Selection", "Inspect the exact feedback decision returned for this writing stage.", "FeedbackService uses the existing stage-specific conditions and priority. The cached decision records branch, condition, Rule IDs and five backend fields; Body also records candidate-check outcomes and an explicit neutral status.", "services/feedback_service.py: generate, generate_body, generate_conclusion", "The completed response supplies the Writing Tutor, this explorer and Copy Full Analysis. Selecting a process never calls FeedbackService again.", "A neutral Body result selects no trait, lesson, correction task or error span. Observational feedback is not an essay-quality grade."],
      ["feedback-explanation", "feedback", "Feedback Explanation", "Explain why the recorded branch was selected using the actual conditions and priority order.", "Read the cached branch decisions, their recorded conditions, linked Rule IDs and emitted events. Body retains its ordered selection checks. Unselected alternatives are shown only when the response records them.", "services/feedback_service.py: generate, generate_body, generate_conclusion", "This page explains the same returned decision; it does not rerun or override FeedbackService.", "The explanation cannot recover a hidden ranking that the implementation did not record. A branch condition is not a quality grade."],
      ["feedback-fields", "feedback", "Five Feedback Fields", "Display the five backend fields exactly as returned.", "Read Current Goal, Primary Feedback, What's Working, Needs Attention and Next Step from the cached feedback object. Array fields are shown item by item.", "services/feedback_service.py; static/app.js: displayFeedback", "The student Writing Feedback panel and Copy Full Analysis use the same cached response.", "Display text is not a replacement for the recorded backend fields; empty values remain explicit."],
      ["trait-mapping", "feedback", "6+1 Trait and Lesson Mapping", "Inspect the recorded instructional focus and its prepared lesson, when applicable.", "Use the completed instructional record or the existing verified catalog lookup for this selected branch and its fired event/provenance links. This is presentation after the feedback choice, not another NLP classification.", "services/tutoring_lessons.py; content/lessons/feedback_help.json; static/app.js: studentFeedbackPresentation", "Verified prepared content supplies the actual tutor wording. The neutral no-concern state assigns no instructional trait or lesson.", "Instructional categories are not validated trait assessments, scores or a claim that all seven traits were evaluated."],
      ["highlight-evidence", "feedback", "Highlight Evidence Selection", "Inspect exactly which recorded source passages can be marked.", "Read the existing localization plan and verified tutor excerpt from this cached response. Original Python-character offsets, anchors, paragraph ownership and source text must agree before a mark is shown.", "services/tutoring_lessons.py; static/app.js: tutorInstructionalExcerpt, tutorEvidenceExcerpt, tutorVerifiedSpan", "The same verified evidence supports read-only excerpts and the current Writing Tutor highlight. This view does not edit the student's text or select a new concern.", "A highlight locates evidence, not a guaranteed error. Neutral results and unverified spans receive no invented highlight."],
      ["api-rendering", "output", "API Response and Browser Rendering", "Inspect how the Flask response reaches this inspector without another analysis run.", "The cached stage response contains availability, analysis, feedback, interpretation limits and the selected-stage trace. analyze_payload selects and compacts that stage, jsonify serializes it, and the student app caches it only after snapshot checks. Copy Full Analysis serializes the same cached object.", "app.py: analyze_payload, compact_student_transparency_trace, compact_student_feedback; static/app.js: runStageAnalysis, displayFeedback, renderNlpTransparency, buildFullAnalysisReport", "The browser renders this inspector and the Writing Feedback panel from the same response. This page performs no request and reruns nothing.", "Flask authentication and CSRF handling are not separately timed in this response. Browser rendering time is not a server NER/NLP duration."],
      ["technical-trace", "output", "Complete Technical Trace", "Inspect the retained runtime, timing scope, processing-step and tracing metadata.", "Read the selected-stage research_trace attached to the cached response. It contains runtime metadata, teacher-context preparation, processing-step records, timings, feedback decisions, output counts and trace limitations. Records shown elsewhere in this inspector are cross-referenced rather than duplicated.", "services/essay_analysis_service.py: analyze; services/research_inspector.py: runtime_metadata; app.py: analyze_payload", "The inspector and Copy Full Analysis read this retained trace. It is not a live profiler and contains no model-internal tensor or execution log.", "Timings cover only the marked in-process Python calls. Authentication, network transfer and browser rendering are outside those measurements."]
    );
    return entries.map(([id, group, title, purpose, method, source, next, limitation]) => ({ id, group, title, purpose, method, source, next, limitation }));
  }

  function recordedExecution(record, missing) {
    if (!record) return execution("UNAVAILABLE", missing);
    const status = record.execution_status;
    if (status === "EXECUTED") return execution("EXECUTED", "Recorded execution status from this cached response.", record.duration_ms ?? null);
    if (["SKIPPED", "NOT_EVALUATED", "NOT_EXECUTED"].includes(status)) return execution("SKIPPED", `Recorded status: ${status}.`, record.duration_ms ?? null);
    if (status === "NOT_APPLICABLE") return execution("NOT_APPLICABLE", "The recorded operation does not apply to these inputs.");
    return execution("UNAVAILABLE", `Recorded status: ${status || record.status || "not retained"}. No successful execution is invented.`);
  }

  function ruleRows(data, id) {
    const stage = data.stage;
    const rows = (Array.isArray(data.analysis.rule_evaluation_trace) ? data.analysis.rule_evaluation_trace : [])
      .filter(row => String(row.rule_id).startsWith(`${stage}.`));
    const patterns = {
      "topic-sentences": /\.TOPIC_SENTENCE\./, "supporting-details": /\.SUPPORTING_DETAIL\./,
      repetition: /\.REPETITION\./, synthesis: /\.SYNTHESIS\./, "new-material": /\.NEW_MATERIAL\./,
      "sentence-connection": /^INTRO\.TOPIC\.SENTENCE_CONNECTION_REVIEW$/,
      "stage-patterns": stage === "BODY" ? /^BODY\.P\d+\.PARAGRAPH\./ : stage === "INTRODUCTION" ? /^INTRO\.(TEXT|CLAUSE|DEVELOPMENT|CONTEXT)\./ : /^CONCLUSION\.(TEXT|STRUCTURE|CLOSURE)\./,
    };
    return id === "rule-events" ? rows : rows.filter(row => patterns[id]?.test(row.rule_id));
  }

  function model(spec, result, data, presentation) {
    const a = data.analysis, rows = ruleRows(data, spec.id), source = studentTextInputEvidence(result);
    const lexical = a.lexical_topic_evidence || {};
    const paragraphs = Array.isArray(a.paragraphs) ? a.paragraphs : [];
    const stageTiming = data.stageTrace?.timings_ms || {};
    const m = { ...spec, execution: execution("UNAVAILABLE", "The relevant evidence was not retained."),
      input: null, output: null, rows, presentation, paths: [], input_note: "Retained input context is shown as recorded; it is not a fabricated raw HTTP payload." };
    const observed = (available, basis, duration = null) => available
      ? execution("EXECUTED", basis + " Individual helper timing is not recorded.", duration)
      : execution("UNAVAILABLE", "This response does not retain the required operation records.");
    if (spec.id === "focus-preparation") {
      m.input = { assignment_topic: source.assignment_question, configured_focus_terms: source.configured_focus_terms, focus_source: source.focus_source };
      m.output = data.trace?.teacher_context ?? null;
      m.execution = present(m.output) ? execution("EXECUTED", "The coordinator retained shared teacher-context preparation and its normalized targets.", data.trace?.teacher_context_preparation_ms ?? null) : execution("UNAVAILABLE", "Normalized preparation output was not retained; configured words alone are not a normalization log.");
    } else if (spec.id === "focus-normalization") {
      m.input = { assignment_topic: source.assignment_question, configured_focus_terms: source.configured_focus_terms, focus_source: source.focus_source };
      m.output = data.trace?.teacher_context?.focus_terms ?? null;
      m.execution = Array.isArray(m.output) ? execution("EXECUTED", "Normalized focus-term specifications were retained from shared preparation.", data.trace?.teacher_context_preparation_ms ?? null)
        : execution("UNAVAILABLE", "Normalized focus-term specifications were not retained in this response.");
    } else if (["tokens", "sentences", "lemmas", "pos", "dependencies", "noun-phrases"].includes(spec.id)) {
      m.input = { stage: source.stage, analyzed_text: source.text, text_source: source.text_source };
      m.input_note = "This text created the shared Doc. Internal component tensors and separate annotation-call logs are not retained.";
      const linguistic = data.linguistic;
      m.output = spec.id === "sentences" ? { sentences: linguistic?.sentences, paragraphs: a.paragraphs ?? a.conclusion_paragraphs, boundary_policy: a.paragraph_boundary_policy }
        : spec.id === "noun-phrases" ? linguistic?.noun_phrases
          : spec.id === "dependencies" ? linguistic?.sentences?.map(s => ({ text: s.text, start: s.start, end: s.end, dependencies: s.dependencies })) : linguistic?.tokens;
      m.execution = recordedExecution(step(data, "spacy_document_processing"), "No shared-document execution record was retained.");
      if (m.execution.status === "EXECUTED") m.execution.basis = "Views of the same recorded spaCy document processing. Its duration is shared; no separate time or extra NLP run is claimed for this annotation.";
      if (!present(m.output)) m.execution = execution("UNAVAILABLE", "This annotation output was not retained, even if another processing step has a recorded status.");
    } else if (spec.id === "concepts") {
      m.input = { tokens: data.linguistic?.tokens, noun_phrases: data.linguistic?.noun_phrases };
      m.output = data.concepts;
      m.execution = recordedExecution(step(data, "concept_extraction"), "Concept extraction execution was not retained.");
    } else if (spec.id === "topic-matching") {
      m.input = { configured_targets: data.trace?.teacher_context?.focus_terms, tokens: data.linguistic?.tokens };
      m.output = lexical;
      m.execution = recordedExecution(step(data, "topic_matching"), "Matching execution was not retained.");
    } else if (spec.id === "wordnet") {
      const record = step(data, "wordnet_direct_suggestions");
      m.input = { include_wordnet: data.stageTrace?.topic_service?.input?.include_wordnet, recorded_lookup_pairs: record?.lookup_pairs };
      m.output = record;
      m.crossStageWordNet = Object.fromEntries(["introduction_to_body_continuity", "introduction_to_conclusion_continuity", "body_to_conclusion_continuity"].filter(key => own(a, key)).map(key => [key, a[key].wordnet_relationship_candidates]).filter(([, value]) => present(value)));
      m.execution = recordedExecution(record, "No direct WordNet execution record was retained.");
      if (m.execution.status === "SKIPPED" && Object.values(m.crossStageWordNet).some(value => value?.lookup_pairs?.length)) {
        m.execution = execution("EXECUTED", "Direct focus-term suggestions were skipped as recorded, but nested cross-stage WordNet comparisons are retained below.");
      }
    } else if (spec.id === "related-concepts") {
      m.input = { teacher_context: data.trace?.teacher_context, linguistic_analysis: data.linguistic };
      m.output = result.related_topic_concept_evidence;
      m.execution = recordedExecution(m.output, "Informational related-word evidence was not retained.");
    } else if (spec.id === "cross-stage") {
      m.input = { selected_stage: source.stage, earlier_sections: source.earlier_sections,
        compared_concepts: data.stageTrace?.cross_stage_comparison_inputs ?? "Full earlier concept sets are not retained in this compact response; use the returned comparison pairs." };
      m.output = Object.fromEntries(["introduction_to_body_continuity", "introduction_to_conclusion_continuity", "body_to_conclusion_continuity"].filter(key => own(a, key)).map(key => [key, a[key]]));
      m.paths = Object.entries(m.output).map(([name, value]) => ({ name, status: value.status, wordnet: value.wordnet_relationship_candidates?.status ?? "Not recorded" }));
      m.execution = data.stage === "INTRODUCTION" ? execution("NOT_APPLICABLE", "Introduction has no earlier section. No cross-stage comparison is claimed.")
        : m.paths.some(p => p.status === "LEXICAL_COMPARISON_AVAILABLE") ? execution("EXECUTED", "At least one actual comparison is retained. Each path below has its own availability; this work is nested in the stage Rule Base.")
          : m.paths.length && m.paths.every(p => String(p.status).startsWith("NOT_AVAILABLE_NO_")) ? execution("NOT_APPLICABLE", "Required earlier text was not supplied; the returned path statuses record that absence.") : execution("UNAVAILABLE", "Cross-stage comparison evidence was not retained.");
    } else if (spec.id === "rule-events") {
      m.source = spec.source.replace("services/*_rules.py", `services/${data.stage.toLowerCase()}_rules.py`);
      m.input = { stage_findings: Object.fromEntries(Object.entries(a).filter(([key]) => !["rule_evaluation_trace", "rule_evidence"].includes(key))) };
      m.output = { emitted_events: a.rule_evidence, reconstructed_evaluation_trace: a.rule_evaluation_trace };
      m.execution = observed(Array.isArray(a.rule_evidence), "The stage's emitted-event records are retained. Any displayed duration is the whole stage Rule Base, including its checks and nested comparisons; event emission and later trace reconstruction are not timed separately. Evaluation rows were reconstructed after feedback, not executed again.", stageTiming.rule_base_ms ?? null);
    } else if (spec.id === "feedback-decision" || spec.id === "feedback-explanation" || spec.id === "feedback-fields") {
      m.source = `services/feedback_service.py: ${data.stage === "BODY" ? "generate_body" : data.stage === "CONCLUSION" ? "generate_conclusion" : "generate"}`;
      m.input = { available_stage_observations: Object.fromEntries(Object.entries(a).filter(([key]) => key !== "rule_evaluation_trace")),
        note: "The later reconstructed evaluation trace was not an input to FeedbackService." };
      m.output = { feedback: result.feedback, decision: data.stageTrace?.feedback_decisions };
      if (spec.id === "feedback-fields") m.output = Object.fromEntries(["Current Goal", "Primary Feedback", "What's Working", "Needs Attention", "Next Step"].map(key => [key, result.feedback?.[key]]));
      if (spec.id === "feedback-explanation") m.output = {
        fields: data.stageTrace?.feedback_decisions?.fields,
        priority_order: data.stageTrace?.feedback_decisions?.priority_order,
        unselected_alternatives: data.stageTrace?.feedback_decisions?.unselected_alternatives,
        selection_status: data.stageTrace?.feedback_decisions?.selection_status,
        selection_checks: data.stageTrace?.feedback_decisions?.selection_checks,
        feedback: result.feedback,
      };
      m.execution = observed(present(data.stageTrace?.feedback_decisions?.fields) || present(result.feedback), "The completed stage-specific FeedbackService branch decisions are recorded.", stageTiming.feedback_ms ?? null);
    } else if (spec.id === "trait-mapping") {
      m.input = { decision: data.stageTrace?.feedback_decisions?.fields?.["Primary Feedback"], provenance: result.feedback?.["Feedback Provenance"] };
      m.output = { instructional_feedback: data.stageTrace?.feedback_decisions?.instructional_feedback ?? null,
        actual_presentation: presentation, catalog_source: presentation.teaching_content_source };
      const neutral = presentation.status === "NO_SUPPORTED_CONCERN_SELECTED" || presentation.status === "NEUTRAL_OBSERVATION";
      m.execution = neutral ? execution("NOT_APPLICABLE", presentation.status === "NO_SUPPORTED_CONCERN_SELECTED"
        ? "NO_SUPPORTED_CONCERN_SELECTED: no corrective trait, skill or lesson is assigned to neutral Body feedback."
        : "NEUTRAL_OBSERVATION: the recorded branch is a neutral review. No corrective trait, skill or improvement task is assigned; any prepared explanation item is retained below without becoming a concern.")
        : presentation.teaching_content_source ? execution("EXECUTED", "The existing verified prepared-content lookup supplies this instructional presentation; it is not a separate NLP call.")
          : present(m.input.decision) && !m.input.decision.trait ? execution("NOT_APPLICABLE", "The recorded branch has no instructional trait or lesson assignment.") : execution("UNAVAILABLE", "No verified prepared mapping was retained for this selection.");
    } else if (spec.id === "highlight-evidence") {
      m.input = { source_text: source.text, decision: data.stageTrace?.feedback_decisions, emitted_events: a.rule_evidence };
      m.output = presentation.tutor_items.map(item => ({ lesson_id: item.lesson_id, rule_ids: item.rule_ids,
        highlight_provenance: item.highlight_provenance, verified_excerpt: item.excerpt, fallback_text: item.evidence_text }));
      m.execution = presentation.status === "NO_SUPPORTED_CONCERN_SELECTED" ? execution("NOT_APPLICABLE", "Neutral Body feedback selects no error span or fabricated source highlight.")
        : m.output.some(item => item.verified_excerpt?.contexts?.some(c => c.marks?.length)) ? execution("EXECUTED", "The existing presentation verified the recorded source spans against this cached analyzed text; selecting this process does not change the editor.")
          : execution("UNAVAILABLE", "No precise verified mark is available for this selection. A wording absence or missing evidence is not turned into an error span.");
    } else if (spec.id === "api-rendering") {
      m.input = { stage: result.stage_id, availability: result.availability, trace_timings: {
        request_validation_and_assignment_resolution_ms: data.trace?.request_validation_and_assignment_resolution_ms,
        analysis_service_lookup_ms: data.trace?.analysis_service_lookup_ms,
        analysis_service_total_ms: data.trace?.analysis_service_total_ms,
      } };
      m.output = { response_keys: Object.keys(result).filter(key => key !== "research_trace"), selected_stage_trace: data.stageTrace ? "retained" : "not retained",
        feedback_fields: ["Current Goal", "Primary Feedback", "What's Working", "Needs Attention", "Next Step"] };
      m.execution = execution("EXECUTED", "The browser is displaying this cached stage response; no analysis request is made by the inspector.");
    } else if (spec.id === "technical-trace") {
      m.input = { selected_stage: data.stage, trace_present: Boolean(data.trace) };
      m.output = data.trace ? {
        trace_version: data.trace.trace_version,
        runtime: data.trace.runtime,
        teacher_context_preparation_ms: data.trace.teacher_context_preparation_ms,
        teacher_context_call_frequency: data.trace.teacher_context_call_frequency,
        stage_timings_ms: data.stageTrace?.timings_ms,
        topic_processing_steps: data.stageTrace?.topic_service?.steps,
        feedback_decisions: data.stageTrace?.feedback_decisions,
        output_counts: data.stageTrace?.output_counts,
        limitations: data.trace.limitations,
      } : null;
      m.execution = data.trace ? execution("EXECUTED", "The selected-stage technical trace is retained in this cached response.") : execution("UNAVAILABLE", "No technical trace was retained for this response.");
    } else {
      const fields = spec.id === "stage-patterns" ? (data.stage === "INTRODUCTION" ? ["text_presence", "observable_structure", "development_evidence"] : data.stage === "CONCLUSION" ? ["text_presence", "conclusion_paragraphs", "clause_candidates", "closure_candidates"] : [])
        : spec.id === "sentence-connection" ? ["sentence_topic_evidence"] : spec.id === "synthesis" ? ["synthesis_structure_candidates"] : spec.id === "new-material" ? ["new_material_observations"] : spec.id === "repetition" && data.stage === "CONCLUSION" ? ["repetition_observations"] : [];
      m.input = { sentences: data.linguistic?.sentences, paragraphs: paragraphs.map(p => ({ paragraph_index: p.paragraph_index, sentence_spans: p.sentence_spans, clause_structure_candidates: p.clause_structure_candidates, focus_term_evidence: p.focus_term_evidence })) };
      m.output = fields.length ? Object.fromEntries(fields.filter(key => own(a, key)).map(key => [key, a[key]]))
        : paragraphs.map(p => ({ paragraph_index: p.paragraph_index, start: p.start, end: p.end, text: p.text, counts: p.counts,
          ...(spec.id === "stage-patterns" ? { fragment_or_list_candidate: p.fragment_or_list_candidate } : spec.id === "topic-sentences" ? { topic_sentence_candidates: p.topic_sentence_candidates }
            : spec.id === "supporting-details" ? { supporting_detail_candidates: p.supporting_detail_candidates } : { repetition_observations: p.repetition_observations }) }));
      const available = fields.length ? fields.some(key => own(a, key)) : own(a, "paragraphs");
      m.execution = rows.length && rows.every(row => row.status === "NOT_APPLICABLE") ? execution("NOT_APPLICABLE", "All applicable retained evaluation rows mark this condition not applicable.")
        : rows.length && rows.every(row => row.status === "NOT_EVALUATED") ? execution("SKIPPED", "The retained evaluation rows explicitly mark these conditions not evaluated.")
        : observed(available, "The stage-specific output is retained. Candidate and untriggered statuses below are the recorded rule evidence, not quality judgments.");
    }
    return m;
  }

  function element(tag, text, className) {
    const node = document.createElement(tag);
    if (text !== undefined && text !== null) node.textContent = String(text);
    if (className) node.className = className;
    return node;
  }

  function stageSection(parent, code, title) {
    const section = element("section", null, "explorer-stage-section");
    section.dataset.stageSection = code;
    section.appendChild(element("h4", `${code} · ${title}`, "explorer-stage-section-title"));
    parent.appendChild(section);
    return section;
  }

  function subheading(parent, text) {
    const heading = element("h5", text, "explorer-subheading");
    parent.appendChild(heading);
    return heading;
  }

  function sourceTextBlock(parent, text, label) {
    const host = element("div", typeof text === "string" ? text : "Not recorded.", "explorer-source-text");
    host.tabIndex = 0;
    host.setAttribute("role", "textbox");
    host.setAttribute("aria-readonly", "true");
    host.setAttribute("aria-label", label);
    if (typeof text === "string") {
      host.dataset.sourceStart = "0";
      host.dataset.sourceEnd = String(Array.from(text).length);
      host.dataset.offsetUnit = "Unicode code points; zero-based start, exclusive end";
    }
    parent.appendChild(host);
    return host;
  }

  function chips(parent, items, className = "explorer-chip") {
    const list = element("div", null, "explorer-chip-list");
    for (const item of items) {
      const chip = element("span", null, className);
      if (item && typeof item === "object") {
        chip.appendChild(element("strong", item.label));
        if (item.detail) chip.appendChild(element("span", item.detail, "explorer-chip-detail"));
        if (item.title) chip.title = item.title;
      } else chip.textContent = String(item);
      list.appendChild(chip);
    }
    parent.appendChild(list);
    return list;
  }

  function flowLane(parent, steps, label = "Recorded decision flow") {
    const lane = element("div", null, "explorer-flow-lane");
    lane.setAttribute("role", "list");
    lane.setAttribute("aria-label", label);
    steps.forEach((step, index) => {
      if (index) lane.appendChild(element("span", "→", "explorer-flow-arrow"));
      const box = element("div", null, "explorer-flow-step");
      box.setAttribute("role", "listitem");
      box.appendChild(element("span", step.label, "explorer-flow-label"));
      box.appendChild(element("strong", step.value ?? "Not recorded", "explorer-flow-value"));
      if (step.detail) box.appendChild(element("span", step.detail, "explorer-flow-detail"));
      lane.appendChild(box);
    });
    parent.appendChild(lane);
    return lane;
  }

  function svgNode(tag, attributes = {}) {
    const node = document.createElementNS("http://www.w3.org/2000/svg", tag);
    for (const [key, value] of Object.entries(attributes)) node.setAttribute(key, String(value));
    return node;
  }

  function compactValue(value) {
    if (value === undefined || value === null) return "Not recorded";
    if (Array.isArray(value)) return value.length ? value.map(item => compactValue(item)).join("; ") : "Recorded empty list";
    if (typeof value === "object") return Object.entries(value).map(([key, item]) => `${transparencyLabel(key)}: ${compactValue(item)}`).join("; ");
    return String(value);
  }

  function renderMappingGraph(parent, options) {
    const { kind, title, leftTitle, rightTitle, left, right, edges, note, emptyMessage } = options;
    const wrapper = element("div", null, "explorer-map");
    wrapper.dataset.mappingGraph = kind;
    subheading(wrapper, title);
    if (!left.length && !right.length) {
      transparencyText(wrapper, emptyMessage || "No recorded relationship data is available for this graph.", "explorer-empty-state");
      parent.appendChild(wrapper);
      return wrapper;
    }
    const accepted = edges.filter(edge => edge.accepted !== false).length;
    transparencyText(wrapper, `Source-verified mapping · ${left.length} left record(s) · ${right.length} right record(s) · ${edges.length} recorded relationship edge(s).`, "explorer-evidence-note");
    const scroller = element("div", null, "explorer-map-scroll");
    scroller.tabIndex = 0;
    scroller.setAttribute("role", "region");
    scroller.setAttribute("aria-label", `${title}; scroll horizontally for the complete graph`);
    const figure = element("div", null, "explorer-map-figure");
    const width = 940;
    const rowHeight = 62;
    const top = 64;
    const height = Math.max(190, top * 2 + Math.max(left.length, right.length, 1) * rowHeight);
    figure.style.position = "relative";
    figure.style.width = `${width}px`;
    figure.style.height = `${height}px`;
    figure.dataset.edgeCount = String(edges.length);
    figure.setAttribute("role", "img");
    figure.setAttribute("aria-label", `${title}. ${leftTitle}: ${left.length}. ${rightTitle}: ${right.length}. Recorded edges: ${edges.length}.`);
    const svg = svgNode("svg", { width, height, viewBox: `0 0 ${width} ${height}`, class: "explorer-map-lines", "aria-hidden": "true" });
    figure.appendChild(svg);
    const leftX = 18, rightX = width - 298, nodeWidth = 280;
    const yFor = index => top + index * rowHeight;
    const leftIndex = new Map(left.map((node, index) => [node.key, index]));
    const rightIndex = new Map(right.map((node, index) => [node.key, index]));
    for (const edge of edges) {
      const li = leftIndex.get(edge.from), ri = rightIndex.get(edge.to);
      if (li === undefined || ri === undefined) continue;
      const y1 = yFor(li) + 24, y2 = yFor(ri) + 24;
      const path = svgNode("path", {
        d: `M ${leftX + nodeWidth} ${y1} C ${leftX + nodeWidth + 160} ${y1} ${rightX - 160} ${y2} ${rightX} ${y2}`,
        class: edge.accepted === false ? "explorer-map-edge explorer-map-edge-rejected" : edge.method === "normalized" ? "explorer-map-edge explorer-map-edge-normalized" : "explorer-map-edge",
        "data-from": edge.from, "data-to": edge.to, "data-label": edge.label,
        "data-method": edge.method ?? "recorded",
      });
      svg.appendChild(path);
      const label = svgNode("text", {
        x: Math.round((leftX + nodeWidth + rightX) / 2),
        y: Math.round((y1 + y2) / 2) - 6,
        class: "explorer-map-edge-label",
        "text-anchor": "middle",
      });
      label.textContent = edge.label;
      svg.appendChild(label);
    }
    const addNode = (node, x, index, side) => {
      const box = element("div", null, `explorer-map-node explorer-map-node-${side}${node.unmatched ? " explorer-map-node-unmatched" : ""}${node.accepted === false ? " explorer-map-node-rejected" : ""}`);
      box.style.left = `${x}px`;
      box.style.top = `${yFor(index)}px`;
      box.style.width = `${nodeWidth}px`;
      box.dataset.mapNode = node.key;
      box.dataset.mapSide = side;
      box.appendChild(element("strong", node.label));
      if (node.detail) box.appendChild(element("span", node.detail, "explorer-map-node-detail"));
      figure.appendChild(box);
    };
    left.forEach((node, index) => addNode(node, leftX, index, "left"));
    right.forEach((node, index) => addNode(node, rightX, index, "right"));
    const labels = element("div", null, "explorer-map-column-labels");
    const leftLabel = element("span", leftTitle, "explorer-map-column-label");
    leftLabel.style.width = `${nodeWidth}px`;
    const rightLabel = element("span", rightTitle, "explorer-map-column-label");
    rightLabel.style.width = `${nodeWidth}px`;
    labels.append(leftLabel, element("span", null, "explorer-map-column-spacer"), rightLabel);
    scroller.append(labels, figure);
    wrapper.appendChild(scroller);
    transparencyText(wrapper, `${accepted} recorded relationship edge(s) meet this resource's accepted comparison condition; ${edges.length - accepted} rejected comparison(s) stay visible and are not drawn as accepted matches.`, "explorer-evidence-note");
    if (note) transparencyText(wrapper, note, "explorer-evidence-note");
    parent.appendChild(wrapper);
    return wrapper;
  }

  function renderTokenStrip(parent, tokens) {
    const strip = element("div", null, "explorer-token-strip");
    strip.setAttribute("role", "list");
    strip.setAttribute("aria-label", "Recorded spaCy tokens in order");
    for (const token of tokens) {
      const chip = element("span", null, `explorer-token${token.is_alpha ? "" : " explorer-token-other"}`);
      chip.setAttribute("role", "listitem");
      chip.title = `Token ${token.index} · ${token.pos}/${token.tag} · [${token.start}, ${token.end})`;
      chip.append(element("span", String(token.index), "explorer-token-index"), element("strong", token.text), element("span", `${token.pos}/${token.tag}`, "explorer-token-pos"));
      strip.appendChild(chip);
    }
    parent.appendChild(strip);
  }

  function markExactSpans(parent, text, spans, className) {
    const characters = Array.from(typeof text === "string" ? text : "");
    const marks = (spans || []).filter(span => Number.isInteger(span.start) && Number.isInteger(span.end) && span.start >= 0 && span.end <= characters.length && span.start < span.end)
      .sort((a, b) => a.start - b.start || a.end - b.end);
    const host = element("div", null, "explorer-highlighted-text");
    let cursor = 0;
    for (const span of marks) {
      if (span.start < cursor) continue;
      host.appendChild(document.createTextNode(characters.slice(cursor, span.start).join("")));
      const mark = document.createElement("span");
      mark.className = className;
      mark.textContent = characters.slice(span.start, span.end).join("");
      if (span.title) mark.title = span.title;
      host.appendChild(mark);
      cursor = span.end;
    }
    host.appendChild(document.createTextNode(characters.slice(cursor).join("")));
    parent.appendChild(host);
    return host;
  }

  function renderPosHighlight(parent, tokens, text) {
    const byPos = new Map();
    for (const token of tokens) {
      if (!byPos.has(token.pos)) byPos.set(token.pos, []);
      byPos.get(token.pos).push(token);
    }
    const legend = element("div", null, "explorer-pos-legend");
    for (const [pos, values] of [...byPos.entries()].sort((a, b) => String(a[0]).localeCompare(String(b[0])))) {
      const item = element("span", null, "explorer-pos-legend-item");
      item.dataset.pos = pos;
      item.append(element("span", null, `pos-${String(pos).toLowerCase()}`), element("strong", pos), element("span", transparencyLabelExplanation(pos), "explorer-pos-meaning"), element("span", `${values.length} token(s)`, "explorer-pos-count"));
      legend.appendChild(item);
    }
    parent.appendChild(legend);
    markExactSpans(parent, text, tokens.map(token => ({ start: token.start, end: token.end, title: `${token.text} · ${token.pos}/${token.tag} · ${token.lemma}` })), "explorer-pos-mark");
    transparencyText(parent, "Each highlighted segment is an actual recorded token span with its predicted coarse POS. The exact analyzed text is used, not a reconstructed string.", "explorer-evidence-note");
  }

  function renderTokenEvidence(parent, tokens) {
    const rows = tokens.map(token => [token.index, token.text, token.lemma, token.pos, token.tag, token.start, token.end]);
    transparencyTable(parent, ["Index", "Token", "Lemma", "POS", "Fine tag", "Start", "End"], rows, "No token records were retained.");
  }

  function renderSentenceCards(parent, sentences, paragraphs) {
    const list = element("div", null, "explorer-sentence-list");
    sentences.forEach((sentence, index) => {
      const card = element("article", null, "explorer-sentence-card");
      card.dataset.sentenceIndex = String(index + 1);
      const head = element("div", null, "explorer-sentence-head");
      head.append(element("span", `Sentence ${index + 1}`, "explorer-sentence-number"), element("span", `[${sentence.start}, ${sentence.end})`, "explorer-sentence-span"));
      card.appendChild(head);
      card.appendChild(element("p", sentence.text, "explorer-sentence-text"));
      const paragraph = (paragraphs || []).find(item => sentence.start >= item.start && sentence.end <= item.end);
      if (paragraph) card.appendChild(element("span", `Recorded paragraph ${paragraph.paragraph_index ?? ""}`, "explorer-sentence-paragraph"));
      list.appendChild(card);
    });
    parent.appendChild(list);
    if (!sentences.length) transparencyText(parent, "No sentence records were retained.", "explorer-empty-state");
  }

  function renderParagraphCards(parent, paragraphs) {
    const list = element("div", null, "explorer-paragraph-list");
    paragraphs.forEach((paragraph, index) => {
      const card = element("article", null, "explorer-paragraph-card");
      card.dataset.paragraphIndex = String(paragraph.paragraph_index ?? index + 1);
      const counts = paragraph.counts || {};
      const head = element("div", null, "explorer-paragraph-head");
      head.append(element("strong", `Paragraph ${paragraph.paragraph_index ?? index + 1}`), element("span", `${counts.sentence_count ?? "Not recorded"} sentences · ${counts.alphabetic_word_count ?? counts.word_count ?? "Not recorded"} words`, "explorer-paragraph-meta"));
      card.appendChild(head);
      card.appendChild(element("p", paragraph.text, "explorer-paragraph-text"));
      list.appendChild(card);
    });
    parent.appendChild(list);
    if (!paragraphs.length) transparencyText(parent, "No paragraph records were retained for this stage.", "explorer-empty-state");
  }

  function renderLemmaChanges(parent, tokens) {
    const alphabetic = tokens.filter(token => token.is_alpha);
    const changed = alphabetic.filter(token => token.lemma && token.lemma.toLowerCase() !== token.text.toLowerCase());
    if (!changed.length) {
      transparencyText(parent, "No retained alphabetic token changed form between its surface text and spaCy lemma.", "explorer-empty-state");
      return;
    }
    const list = element("div", null, "explorer-lemma-changes");
    for (const token of changed) {
      const pair = element("span", null, "explorer-lemma-pair");
      pair.append(element("strong", token.text), element("span", "→", "explorer-lemma-arrow"), element("span", token.lemma, "explorer-lemma-result"));
      pair.title = `Token ${token.index} · [${token.start}, ${token.end})`;
      list.appendChild(pair);
    }
    parent.appendChild(list);
    transparencyText(parent, `${changed.length} of ${alphabetic.length} retained alphabetic tokens have a lemma that differs from their surface form. Lemmas are model predictions, not synonym decisions.`, "explorer-evidence-note");
  }

  function renderNounChunkChips(parent, nounPhrases, text) {
    if (!nounPhrases.length) {
      transparencyText(parent, "No noun chunks were retained for this stage.", "explorer-empty-state");
      return;
    }
    chips(parent, nounPhrases.map(item => ({ label: item.text, detail: `[${item.start}, ${item.end})`, title: "Recorded Doc.noun_chunks span" })), "explorer-chip explorer-chunk-chip");
    markExactSpans(parent, text, nounPhrases.map(item => ({ start: item.start, end: item.end, title: item.text })), "explorer-chunk-mark");
    transparencyText(parent, "Highlights mark non-overlapping recorded noun-chunk spans in the exact analyzed text; the list above preserves every returned chunk, including any overlapping span.", "explorer-evidence-note");
  }

  function topicMapModel(data) {
    const lexical = data.analysis.lexical_topic_evidence || {};
    const terms = Array.isArray(lexical.focus_terms) ? lexical.focus_terms.filter(term => typeof term === "string") : [];
    const matches = Array.isArray(lexical.matches) ? lexical.matches : [];
    const matchCounts = new Map();
    for (const match of matches) matchCounts.set(match.focus_term, (matchCounts.get(match.focus_term) || 0) + 1);
    const left = terms.map(term => {
      const count = matchCounts.get(term) || 0;
      return {
        key: `term:${term}`, label: term,
        detail: count ? `${count} recorded match(es)` : "No recorded match",
        unmatched: !count,
      };
    });
    const right = [];
    const seen = new Set();
    for (const match of matches) {
      const text = match.observed_text ?? match.text ?? "";
      const key = `occ:${match.start}:${match.end}:${text}`;
      if (seen.has(key)) continue;
      seen.add(key);
      right.push({ key, label: text, detail: `${match.match_method ?? "method not recorded"} · [${match.start}, ${match.end})` });
    }
    const edges = matches.map(match => {
      const text = match.observed_text ?? match.text ?? "";
      return {
        from: `term:${match.focus_term}`, to: `occ:${match.start}:${match.end}:${text}`,
        label: match.match_method === "direct" ? "direct" : match.match_method === "normalized" ? "normalized (lemma)" : String(match.match_method ?? "method not recorded"),
        method: match.match_method,
        accepted: true,
      };
    });
    return { terms, matches, left, right, edges, unmatched: lexical.unobserved_focus_terms ?? terms.filter(term => !matchCounts.get(term)) };
  }

  function renderTopicMap(parent, data) {
    const model = topicMapModel(data);
    if (!model.terms.length && !model.matches.length) {
      transparencyText(parent, "No configured focus terms or recorded matches were retained; no mapping graph is drawn.", "explorer-empty-state");
      return;
    }
    renderMappingGraph(parent, {
      kind: "topic", title: "Teacher focus terms ↔ recorded student expressions",
      leftTitle: "Configured comparison targets", rightTitle: "Recorded student expressions",
      left: model.left, right: model.right, edges: model.edges,
      note: "Every line is an entry in analysis.lexical_topic_evidence.matches. A target without a line has no recorded direct or lemma-normalized match; no edge is invented for it.",
      emptyMessage: "No focus-term matches were recorded for this stage.",
    });
    if (model.unmatched.length) {
      const section = element("div", null, "explorer-unmatched-terms");
      subheading(section, "Configured targets with no recorded match");
      chips(section, model.unmatched.map(term => ({ label: term, detail: "unmatched" })), "explorer-chip explorer-chip-unmatched");
      transparencyText(section, "These targets are shown without edges. A missing word can reflect paraphrase; it does not establish that the draft is off topic.", "explorer-evidence-note");
      parent.appendChild(section);
    }
  }

  function wordNetPairRows(pair, direct) {
    return {
      source: direct ? (pair.teacher_term ?? "Not recorded") : (pair.source_lemma ?? "Not recorded"),
      target: direct ? (pair.observed_student_term ?? "Not recorded") : (pair.target_lemma ?? "Not recorded"),
      sourcePos: direct ? (Array.isArray(pair.teacher_pos) ? pair.teacher_pos.join("/") : pair.teacher_pos ?? "Not recorded") : pair.source_pos ?? "Not recorded",
      targetPos: direct ? pair.student_pos ?? "Not recorded" : pair.target_pos ?? "Not recorded",
      sourceSynsets: Array.isArray(pair.teacher_synset_ids) ? pair.teacher_synset_ids : Array.isArray(pair.source_synset_ids) ? pair.source_synset_ids : [],
      targetSynsets: Array.isArray(pair.student_synset_ids) ? pair.student_synset_ids : Array.isArray(pair.target_synset_ids) ? pair.target_synset_ids : [],
      shared: Array.isArray(pair.shared_synset_ids) ? pair.shared_synset_ids : [],
      emitted: pair.candidate_emitted === true,
      condition: pair.selection_condition ?? "Not recorded",
      span: Array.isArray(pair.source_span) ? `[${pair.source_span[0]}, ${pair.source_span[1]})` : "Not recorded",
    };
  }

  function renderWordNetGraph(parent, pairs, title, kind, direct) {
    const rows = pairs.map(pair => wordNetPairRows(pair, direct));
    if (!rows.length) return;
    const left = new Map(), right = new Map(), edges = [];
    rows.forEach((row) => {
      if (!left.has(row.source)) left.set(row.source, { key: `${kind}:source:${left.size}`, label: row.source, detail: `${row.sourcePos} · ${row.sourceSynsets.length} synset(s)` });
      if (!right.has(row.target)) right.set(row.target, { key: `${kind}:target:${right.size}`, label: row.target, detail: `${row.targetPos} · ${row.targetSynsets.length} synset(s)` });
      edges.push({
        from: left.get(row.source).key, to: right.get(row.target).key,
        label: row.shared.length ? `${row.shared.join(", ")} · ${row.emitted ? "accepted" : "rejected"}` : "no shared synset · rejected",
        method: row.emitted ? "accepted" : "rejected",
        accepted: row.emitted,
      });
    });
    renderMappingGraph(parent, {
      kind, title, leftTitle: "Source / teacher form", rightTitle: "Observed / target form",
      left: [...left.values()], right: [...right.values()], edges,
      note: "Each line is one recorded WordNet lookup pair. Shared synset IDs come from the returned pair record; an absent shared synset is shown as a rejected comparison, not an inferred relationship.",
    });
  }

  function renderWordNetVisual(parent, m) {
    const direct = Array.isArray(m.output?.lookup_pairs) ? m.output.lookup_pairs : [];
    if (direct.length) renderWordNetGraph(parent, direct, "Direct focus-term WordNet comparisons", "wordnet-direct", true);
    let crossCount = 0;
    for (const [path, value] of Object.entries(m.crossStageWordNet || {})) {
      const pairs = Array.isArray(value?.lookup_pairs) ? value.lookup_pairs : [];
      if (!pairs.length) continue;
      crossCount += pairs.length;
      renderWordNetGraph(parent, pairs, `Cross-stage WordNet — ${transparencyLabel(path)}`, `wordnet-cross-${path}`, false);
    }
    if (!direct.length && !crossCount) {
      const record = m.output;
      const status = record?.execution_status ?? "UNAVAILABLE";
      transparencyText(parent, status === "SKIPPED" ? `No WordNet graph is shown: the direct WordNet path was recorded as ${record?.status ? String(record.status) : "skipped"} and no accepted or rejected lookup pairs were returned.` : "No WordNet lookup pairs were returned, so no WordNet relationship graph can be drawn from this response.", "explorer-empty-state");
    } else if (!direct.length) {
      transparencyText(parent, "The direct focus-term WordNet path returned no lookup pairs; the cross-stage graphs below come from the actual earlier-section comparison records.", "explorer-evidence-note");
    }
  }

  function feedbackRuleUse(result, data, ruleId) {
    const decisions = data.stageTrace?.feedback_decisions?.fields || {};
    const fields = Object.entries(decisions).filter(([, decision]) => Array.isArray(decision?.rule_ids) && decision.rule_ids.includes(ruleId)).map(([field]) => field);
    const provenance = Array.isArray(result.feedback?.["Feedback Provenance"])
      ? result.feedback["Feedback Provenance"].filter(item => item.rule_id === ruleId).map(item => item.feedback_field) : [];
    return [...new Set([...fields, ...provenance])];
  }

  function ruleEvidenceText(event) {
    const items = Array.isArray(event.actual_evidence) ? event.actual_evidence : Array.isArray(event.evidence) ? event.evidence : [];
    if (!items.length) return "No evidence items were returned for this event.";
    return items.map(item => typeof item === "object"
      ? `${item.text ?? item.observed_text ?? transparencyLabel(item.type ?? "record")}${Number.isInteger(item.start) && Number.isInteger(item.end) ? ` [${item.start}, ${item.end})` : ""}`
      : String(item)).join(" · ");
  }

  function renderRuleVisual(parent, m, result, data) {
    const events = Array.isArray(data.analysis.rule_evidence) ? data.analysis.rule_evidence : [];
    const rows = Array.isArray(data.analysis.rule_evaluation_trace) ? data.analysis.rule_evaluation_trace : [];
    if (!events.length) {
      transparencyText(parent, "This stage emitted no Rule Events. No decision flow is drawn; the reconstructed evaluation rows remain in Actual Recorded Evidence.", "explorer-empty-state");
      return;
    }
    for (const event of events) {
      const row = rows.find(item => item.rule_id === event.rule_id);
      const use = feedbackRuleUse(result, data, event.rule_id);
      const flow = element("div", null, "explorer-rule-flow");
      flow.dataset.ruleFlow = event.rule_id;
      flow.appendChild(element("strong", event.rule_id, "explorer-rule-id"));
      flowLane(flow, [
        { label: "Recorded evidence", value: ruleEvidenceText(event), detail: event.evidence_type ?? "Evidence type not recorded" },
        { label: "Programmed condition", value: row?.condition ?? event.triggering_condition ?? "Condition not retained" },
        { label: "Outcome", value: row?.status ?? "TRIGGERED (event emitted)", detail: event.triggering_condition ?? "Triggering condition not recorded" },
        { label: "Feedback use", value: use.length ? use.join(", ") : "Not cited by a returned feedback field", detail: use.length ? "The Rule ID appears in recorded field decisions or provenance." : "No recorded field decision or provenance cites this event." },
      ], `Recorded rule decision flow for ${event.rule_id}`);
      parent.appendChild(flow);
    }
    transparencyText(parent, "Each flow is built from analysis.rule_evidence plus the reconstructed evaluation row. A missing row is shown as not retained, never as an invented outcome.", "explorer-evidence-note");
  }

  function renderRuleEvidence(parent, m, result, data) {
    const events = Array.isArray(data.analysis.rule_evidence) ? data.analysis.rule_evidence : [];
    const rows = Array.isArray(data.analysis.rule_evaluation_trace) ? data.analysis.rule_evaluation_trace : [];
    const emittedIds = new Set(events.map(event => event.rule_id));
    transparencyTable(parent, ["Recorded rule record", "Actual count"], [
      ["Emitted Rule Events (analysis.rule_evidence)", events.length],
      ["Evaluation records (analysis.rule_evaluation_trace)", rows.length],
      ["Evaluation rows marked TRIGGERED", rows.filter(row => row.status === "TRIGGERED").length],
      ["Evaluation rows marked EVALUATED_NOT_TRIGGERED", rows.filter(row => row.status === "EVALUATED_NOT_TRIGGERED").length],
    ]);
    transparencyText(parent, "Emitted events are the Rule Base records that exist in this response. Evaluation rows were reconstructed after feedback selection for inspection; they are not a second Rule Base run. A row with no event is not automatically proof that a negative test executed.", "explorer-evidence-note");
    if (events.length) {
      transparencyTable(parent, ["Emitted Rule Event", "Evidence type", "Triggering condition", "Feedback fields citing it"], events.map(event => [
        event.rule_id, event.evidence_type ?? "Not recorded", event.triggering_condition ?? "Not recorded",
        feedbackRuleUse(result, data, event.rule_id).join(", ") || "Not cited by a returned field",
      ]));
    }
    subheading(parent, "Complete reconstructed evaluation rows");
    transparencyTable(parent, ["Rule ID", "Evaluation status", "Programmed condition", "Implementation", "Event emitted"], rows.map(row => [
      row.rule_id, row.status, row.condition ?? "Not recorded",
      row.implementation ? `${row.implementation.file ?? ""} · ${row.implementation.function ?? ""}` : "Not recorded",
      emittedIds.has(row.rule_id) ? "Yes — event retained" : "No event in this response",
    ]), m.execution.basis);
  }

  function feedbackFields() {
    return ["Current Goal", "Primary Feedback", "What's Working", "Needs Attention", "Next Step"];
  }

  function feedbackValue(value) {
    if (Array.isArray(value)) return value.length ? value.join("\n\n") : "Recorded empty list.";
    if (value === "") return "Recorded empty text.";
    return value === undefined || value === null ? "Not recorded." : String(value);
  }

  function feedbackSummary(value) {
    if (Array.isArray(value)) return value.length ? `${value.length} message(s)` : "Recorded empty list";
    if (value === "") return "Recorded empty text";
    return value === undefined || value === null ? "Not recorded" : "1 message";
  }

  function renderFeedbackTraceVisual(parent, result, data) {
    const decisions = data.stageTrace?.feedback_decisions || {};
    const fields = decisions.fields || {};
    const events = Array.isArray(data.analysis.rule_evidence) ? data.analysis.rule_evidence : [];
    const primary = fields["Primary Feedback"] || {};
    const cited = Array.isArray(primary.rule_ids) ? primary.rule_ids : [];
    const evidenceIds = cited.map(ruleId => `${ruleId}${events.some(event => event.rule_id === ruleId) ? " (emitted)" : " (no matching emitted event)"}`);
    flowLane(parent, [
      { label: "1 · NLP evidence", value: `${events.length} emitted Rule Event(s)`, detail: "From analysis.rule_evidence in this cached response." },
      { label: "2 · Rule decision", value: cited.length ? evidenceIds.join("; ") : "No Rule IDs recorded for this field", detail: "Rule IDs are read from the recorded field decision." },
      { label: "3 · Feedback condition", value: primary.selection_condition ?? "Condition not recorded" },
      { label: "4 · Selected branch", value: primary.selection_branch ?? "No branch recorded", detail: [primary.trait, primary.skill].filter(Boolean).join(" · ") || "No instructional trait or skill recorded." },
      { label: "5 · Displayed feedback", value: `Primary Feedback · ${feedbackSummary(result.feedback?.["Primary Feedback"])}`, detail: "The exact text is listed in the recorded evidence below." },
    ], "Recorded feedback selection trace");
    transparencyText(parent, "This lane follows fields present in the cached response. It does not recover an unrecorded ranking or claim that unselected branches were executed.", "explorer-evidence-note");
  }

  function renderActualFeedbackFields(parent, result) {
    const cards = element("div", null, "explorer-feedback-fields");
    for (const field of feedbackFields()) {
      const card = element("div", null, "explorer-feedback-field");
      card.dataset.feedbackField = field;
      subheading(card, field);
      card.appendChild(element("p", feedbackValue(result.feedback?.[field]), "explorer-feedback-text"));
      cards.appendChild(card);
    }
    parent.appendChild(cards);
  }

  function renderFeedbackFieldSummary(parent, result) {
    const cards = element("div", null, "explorer-feedback-fields explorer-feedback-field-summary");
    for (const field of feedbackFields()) {
      const card = element("div", null, "explorer-feedback-field");
      card.dataset.feedbackField = field;
      subheading(card, field);
      card.appendChild(element("p", feedbackSummary(result.feedback?.[field]), "explorer-feedback-text"));
      cards.appendChild(card);
    }
    parent.appendChild(cards);
    transparencyText(parent, "These five slots mirror the backend field names. Actual returned text is shown in Actual Recorded Evidence without truncation.", "explorer-evidence-note");
  }

  function renderFeedbackDecisionEvidence(parent, result, data) {
    const decisions = data.stageTrace?.feedback_decisions || {};
    const fields = decisions.fields || {};
    const events = Array.isArray(data.analysis.rule_evidence) ? data.analysis.rule_evidence : [];
    transparencyTable(parent, ["Feedback field", "Selected branch", "Recorded condition", "Rule IDs", "Returned value"], feedbackFields().map(field => {
      const decision = fields[field] || {};
      const ruleIds = Array.isArray(decision.rule_ids) ? decision.rule_ids : [];
      return [field, decision.selection_branch ?? "Not recorded", decision.selection_condition ?? "Not recorded",
        ruleIds.length ? ruleIds.map(ruleId => `${ruleId}${events.some(event => event.rule_id === ruleId) ? " ✓" : " (no event)"}`).join(", ") : "No Rule IDs recorded",
        feedbackSummary(result.feedback?.[field])];
    }));
    if (decisions.selection_status) transparencyText(parent, `Recorded section selection status: ${decisions.selection_status}`, "explorer-outcome");
    if (decisions.priority_order) {
      subheading(parent, "Recorded priority order");
      const list = element("ol", null, "explorer-priority-list");
      for (const item of decisions.priority_order) list.appendChild(element("li", item));
      parent.appendChild(list);
    }
    if (Array.isArray(decisions.selection_checks) && decisions.selection_checks.length) {
      subheading(parent, "Recorded Body feedback selection checks");
      transparencyTable(parent, ["Priority", "Branch / check", "Required condition", "Matched", "Recorded status", "Rule IDs"], decisions.selection_checks.map(check => [
        check.priority, check.branch, check.condition, check.condition_matched === true ? "Yes" : check.condition_matched === false ? "No" : "Not recorded",
        check.status ?? "Not recorded", Array.isArray(check.rule_ids) ? check.rule_ids.join(", ") || "None" : "Not recorded",
      ]));
    }
    subheading(parent, "Exact returned feedback fields");
    renderActualFeedbackFields(parent, result);
    if (decisions.selection_source) transparencyText(parent, `Recorded selection source: ${decisions.selection_source}`, "explorer-evidence-note");
  }

  function renderFeedbackExplanationEvidence(parent, result, data) {
    const decisions = data.stageTrace?.feedback_decisions || {};
    const fields = decisions.fields || {};
    transparencyTable(parent, ["Feedback field", "Selected branch", "Recorded selection condition", "Priority position"], feedbackFields().map(field => {
      const decision = fields[field] || {};
      const branch = decision.selection_branch;
      const position = Array.isArray(decisions.priority_order) && branch
        ? decisions.priority_order.findIndex(item => String(item).includes(String(branch).replace(/_/g, " "))) + 1 : 0;
      return [field, branch ?? "Not recorded", decision.selection_condition ?? "Not recorded", position || "Not recorded"];
    }));
    if (decisions.selection_status) transparencyText(parent, `Recorded section selection status: ${decisions.selection_status}`, "explorer-outcome");
    if (Array.isArray(decisions.priority_order)) {
      subheading(parent, "Recorded priority order");
      const list = element("ol", null, "explorer-priority-list");
      for (const item of decisions.priority_order) list.appendChild(element("li", item));
      parent.appendChild(list);
    }
    if (Array.isArray(decisions.selection_checks) && decisions.selection_checks.length) {
      subheading(parent, "Recorded selection checks");
      transparencyTable(parent, ["Priority", "Branch / check", "Required condition", "Matched", "Recorded status", "Rule IDs"], decisions.selection_checks.map(check => [
        check.priority, check.branch, check.condition, check.condition_matched === true ? "Yes" : check.condition_matched === false ? "No" : "Not recorded",
        check.status ?? "Not recorded", Array.isArray(check.rule_ids) ? check.rule_ids.join(", ") || "None" : "Not recorded",
      ]));
    }
    if (decisions.unselected_alternatives) transparencyText(parent, decisions.unselected_alternatives, "explorer-evidence-note");
    if (decisions.selection_source) transparencyText(parent, `Recorded selection source: ${decisions.selection_source}`, "explorer-evidence-note");
    subheading(parent, "Rule IDs cited by each field");
    transparencyTable(parent, ["Feedback field", "Recorded Rule IDs"], feedbackFields().map(field => {
      const decision = fields[field] || {};
      return [field, Array.isArray(decision.rule_ids) && decision.rule_ids.length ? decision.rule_ids.join(", ") : "None recorded"];
    }));
  }

  function renderResponseFlowVisual(parent, result, data) {
    const timings = {
      validation: data.trace?.request_validation_and_assignment_resolution_ms,
      lookup: data.trace?.analysis_service_lookup_ms,
      analysis: data.trace?.analysis_service_total_ms,
    };
    flowLane(parent, [
      { label: "1 · Browser", value: "runStageAnalysis → POST /api/analyze-stage", detail: "The response is cached only after request, text, assignment, stage and view snapshot checks." },
      { label: "2 · Flask", value: `${result.stage_id} · ${result.availability}`, detail: "analyze_payload validates the supplied stage and text, then selects the stage response." },
      { label: "3 · Coordinator", value: `${timings.analysis ?? "Not recorded"} ms recorded service interval`, detail: "analysis_service_total_ms from the retained trace." },
      { label: "4 · Response compaction", value: "Selected stage + compact trace", detail: "compact_student_transparency_trace removes repeated copies; it does not rerun analysis." },
      { label: "5 · Inspector", value: "This page", detail: "Reads the cached response only; no API call, NLP parse, rule run or feedback selection occurs here." },
    ], "Cached analysis response and browser rendering flow");
    transparencyText(parent, "Timings describe only their recorded Python scopes. Authentication, network transfer, JSON serialization and browser rendering are not measured by this response.", "explorer-evidence-note");
  }

  function renderResponseTimingEvidence(parent, data) {
    transparencyTable(parent, ["Recorded timing scope", "Value", "Meaning"], [
      ["Request validation and assignment resolution", data.trace?.request_validation_and_assignment_resolution_ms ?? "Not recorded", "Measured inside the Flask handler before service use."],
      ["Analysis-service lookup", data.trace?.analysis_service_lookup_ms ?? "Not recorded", "Measured when the app retrieves its service; injected prebuilt services are not construction time."],
      ["Analysis-service total", data.trace?.analysis_service_total_ms ?? "Not recorded", "Measured around the coordinator call, including its recorded NLP/rule/feedback work."],
      ["Authentication and CSRF", data.trace?.api_authentication_and_csrf_timing ?? "NOT_INSTRUMENTED", "Not measured by this response."],
      ["JSON response serialization", data.trace?.json_response_serialization_timing ?? "NOT_INSTRUMENTED", "Not measured by this response."],
      ["Browser rendering", "Not recorded", "The browser does not record a render duration for this inspector."],
    ]);
    transparencyTable(parent, ["Response boundary", "Recorded behavior"], [
      ["Validation", "This successful response passed Flask request validation; individual validation booleans are not returned."],
      ["Compaction", "The selected stage is retained with a compact trace; repeated input/linguistic copies are removed."],
      ["Persistence", "Analysis is separate from draft saving, revisions and submission."],
    ]);
  }

  function renderTechnicalTraceVisual(parent, data) {
    const timings = Object.entries(data.stageTrace?.timings_ms || {});
    if (timings.length) {
      flowLane(parent, timings.map(([key, value]) => ({ label: transparencyLabel(key), value: `${value} ms`, detail: "Recorded in this selected-stage trace." })), "Recorded stage timing scopes");
    } else {
      transparencyText(parent, "No selected-stage timing records were retained.", "explorer-empty-state");
    }
    const steps = data.stageTrace?.topic_service?.steps || [];
    if (steps.length) {
      const list = element("div", null, "explorer-step-status-list");
      for (const item of steps) {
        const row = element("div", null, "explorer-step-status");
        row.dataset.topicStep = item.id;
        row.append(element("strong", item.id), element("span", item.execution_status ?? "Not recorded", "explorer-step-execution"), element("span", item.status ?? "Not recorded", "explorer-step-recorded-status"));
        list.appendChild(row);
      }
      parent.appendChild(list);
    }
  }

  function renderTechnicalTraceEvidence(parent, data) {
    const trace = data.trace;
    if (!trace) {
      transparencyText(parent, "No technical trace was retained for this response.", "explorer-empty-state");
      return;
    }
    transparencyTable(parent, ["Trace field", "Actual value"], [
      ["Trace version", trace.trace_version ?? "Not recorded"],
      ["Selected stage", trace.selected_stage ?? data.stage],
      ["Teacher-context preparation", trace.teacher_context_preparation_ms === undefined ? "Not recorded" : `${trace.teacher_context_preparation_ms} ms`],
      ["Teacher-context call frequency", trace.teacher_context_call_frequency ?? "Not recorded"],
      ["Runtime model", trace.runtime?.model_name ?? "Not recorded"],
      ["Runtime version", trace.runtime?.model_version ?? "Not recorded"],
    ]);
    transparencyTable(parent, ["Recorded stage timing", "Milliseconds"], Object.entries(data.stageTrace?.timings_ms || {}).map(([key, value]) => [transparencyLabel(key), value]));
    transparencyTable(parent, ["TopicService step", "Execution", "Recorded status", "Duration", "Output counts"], (data.stageTrace?.topic_service?.steps || []).map(item => [
      item.id, item.execution_status ?? "Not recorded", item.status ?? "Not recorded",
      item.duration_ms === undefined ? "Not recorded" : `${item.duration_ms} ms`,
      item.output_counts ? compactValue(item.output_counts) : "Not recorded",
    ]));
    transparencyTable(parent, ["Recorded output count", "Value"], Object.entries(data.stageTrace?.output_counts || {}).map(([key, value]) => [transparencyLabel(key), compactValue(value)]));
    const limitations = Array.isArray(trace.limitations) ? trace.limitations : trace.limitations ? [trace.limitations] : [];
    if (limitations.length) {
      subheading(parent, "Recorded trace limitations");
      const list = element("ul", null, "explorer-limitations-list");
      for (const item of limitations) list.appendChild(element("li", item));
      parent.appendChild(list);
    }
  }

  function renderRuleRowsTable(parent, m, data) {
    if (!m.rows.length) return;
    subheading(parent, "Stage rule records for this process");
    transparencyTable(parent, ["Rule ID", "Actual evaluation status", "Recorded event condition"], m.rows.map(row => [row.rule_id, row.status,
      (data.analysis.rule_evidence || []).find(event => event.rule_id === row.rule_id)?.triggering_condition ?? "No emitted event condition; inspect the retained evaluation/configuration record."]), m.execution.basis);
  }

  function renderEvidence(parent, m, result, data) {
    const a = data.analysis, p = m.presentation;
    const tokens = data.linguistic?.tokens || [];
    const sentences = data.linguistic?.sentences || [];
    const paragraphs = a.paragraphs ?? a.conclusion_paragraphs ?? [];
    if (["tokens", "lemmas", "pos"].includes(m.id)) {
      renderTokenEvidence(parent, tokens);
    } else if (m.id === "sentences") {
      transparencyTable(parent, ["Sentence", "Recorded text", "Start", "End"], sentences.map((sentence, index) => [index + 1, sentence.text, sentence.start, sentence.end]));
      if (Array.isArray(paragraphs) && paragraphs.length) transparencyTable(parent, ["Paragraph", "Recorded text", "Start", "End"], paragraphs.map((item, index) => [item.paragraph_index ?? index + 1, item.text, item.start, item.end]));
      else transparencyText(parent, "No independent paragraph detector is recorded for this stage.", "field-help");
    } else if (m.id === "dependencies") {
      transparencyTable(parent, ["Token", "Relationship", "Head", "Head start", "Start", "End"], sentences.flatMap(sentence => (sentence.dependencies || []).map(edge => [edge.text, edge.dependency, edge.head, edge.head_start, edge.start, edge.end])));
    } else if (m.id === "noun-phrases") {
      transparencyTable(parent, ["Noun phrase", "Start", "End"], (data.linguistic?.noun_phrases || []).map(item => [item.text, item.start, item.end]));
    } else if (m.id === "focus-preparation") {
      transparencyText(parent, `Recorded focus source: ${data.trace?.teacher_context?.focus_source ?? "Unavailable"}. Shared preparation precedes the section document calls.`);
      transparencyTable(parent, ["Configured term", "Normalized form", "Surface words", "Normalized words", "WordNet POS"], (data.trace?.teacher_context?.focus_terms || []).map(term => [term.term, term.normalized_form, (term.surface_words || []).join(" "), (term.normalized_words || []).join(" "), (term.wordnet_pos || []).join("/")]));
      const derived = data.trace?.teacher_context?.automatically_derived_candidates;
      if (Array.isArray(derived) && derived.length) transparencyTable(parent, ["Derived candidate", "Source"], derived.map(item => [typeof item === "string" ? item : item.term ?? item.text ?? "Recorded candidate", "Automatically derived from the assignment topic"]));
    } else if (m.id === "focus-normalization") {
      transparencyTable(parent, ["Original term", "Normalized form", "Surface words", "Normalized words", "WordNet POS"], (data.trace?.teacher_context?.focus_terms || []).map(term => [term.term, term.normalized_form, (term.surface_words || []).join(" "), (term.normalized_words || []).join(" "), (term.wordnet_pos || []).join("/")]));
    } else if (m.id === "concepts") {
      transparencyTable(parent, ["Concept", "Normalized form", "Occurrences", "Extraction methods"], (data.concepts || []).map(concept => [concept.text, concept.normalized_form, concept.occurrence_count, (concept.extraction_methods || []).join(", ")]));
      transparencyTable(parent, ["Concept", "Occurrence", "Extraction", "Start", "End"], (data.concepts || []).flatMap(concept => (concept.occurrences || []).map(occurrence => [occurrence.text, concept.normalized_form, occurrence.extraction_method, occurrence.start, occurrence.end])));
    } else if (m.id === "topic-matching") {
      const lexical = a.lexical_topic_evidence || {};
      transparencyTable(parent, ["Recorded match measure", "Actual value"], [
        ["Unique matched terms", lexical.observed_unique_focus_terms ?? lexical.observed_focus_terms?.length ?? "Not recorded"],
        ["Total match occurrences", lexical.matches?.length ?? "Not recorded"],
        ["All unique configured targets", lexical.total_unique_focus_terms ?? lexical.focus_terms?.length ?? "Not recorded"],
      ]);
      transparencyTable(parent, ["Target", "Observed wording", "Match method", "Start", "End"], (lexical.matches || []).map(match => [match.focus_term, match.observed_text ?? match.text, match.match_method, match.start, match.end]));
      if (lexical.unobserved_focus_terms?.length) transparencyTable(parent, ["Unmatched focus term", "Recorded meaning"], lexical.unobserved_focus_terms.map(term => [term, "No direct or lemma-normalized match was recorded; this does not establish that the draft is off topic."]));
    } else if (m.id === "wordnet") {
      const record = step(data, "wordnet_direct_suggestions");
      transparencyTable(parent, ["Recorded field", "Actual value"], [
        ["Direct execution", record?.execution_status ?? "Unavailable"], ["Recorded status", record?.status ?? "Not recorded"],
        ["Resource probe", record?.resource_probe ?? "Not recorded"], ["Suggestion count", record?.suggestion_count ?? "Not recorded"],
        ["Lookup pair count", Array.isArray(record?.lookup_pairs) ? record.lookup_pairs.length : "Not recorded"],
      ]);
      if (Array.isArray(record?.lookup_pairs) && record.lookup_pairs.length) {
        transparencyTable(parent, ["Teacher term", "Observed term", "Teacher POS", "Student POS", "Shared synsets", "Candidate emitted", "Source span"], record.lookup_pairs.map(pair => {
          const row = wordNetPairRows(pair, true);
          return [row.source, row.target, row.sourcePos, row.targetPos, row.shared.length ? row.shared.join(", ") : "None", row.emitted ? "Yes" : "No", row.span];
        }));
      }
      const crossEntries = Object.entries(m.crossStageWordNet || {});
      if (crossEntries.length) {
        transparencyTable(parent, ["Cross-stage path", "Recorded status", "Lookup pairs", "Suggestions"], crossEntries.map(([path, value]) => [transparencyLabel(path), value?.status ?? "Not recorded", Array.isArray(value?.lookup_pairs) ? value.lookup_pairs.length : "Not recorded", Array.isArray(value?.suggestions) ? value.suggestions.length : "Not recorded"]));
        for (const [path, value] of crossEntries) {
          const pairs = Array.isArray(value?.lookup_pairs) ? value.lookup_pairs : [];
          if (!pairs.length) continue;
          transparencyTable(parent, [`${transparencyLabel(path)} — source`, "Target", "Source POS", "Target POS", "Source synsets", "Target synsets", "Shared synsets", "Candidate"], pairs.map(pair => {
            const row = wordNetPairRows(pair, false);
            return [row.source, row.target, row.sourcePos, row.targetPos, row.sourceSynsets.join(", ") || "None", row.targetSynsets.join(", ") || "None", row.shared.join(", ") || "None", row.emitted ? "Yes" : "No"];
          }));
        }
      }
    } else if (m.id === "related-concepts") {
      transparencyTable(parent, ["Observed word", "Configured target", "Relationship", "Start", "End"], (result.related_topic_concept_evidence?.evidence || []).map(item => [item.student_word, item.teacher_focus_term, item.relationship_id, item.start, item.end]));
    } else if (m.id === "cross-stage") {
      transparencyTable(parent, ["Actual comparison path", "Recorded status", "Nested WordNet status"], m.paths.map(path => [path.name, path.status, path.wordnet]), m.execution.basis);
      for (const [key, value] of Object.entries(m.output || {})) {
        const section = element("div", null, "explorer-cross-path");
        subheading(section, transparencyLabel(key));
        transparencyText(section, `Recorded direct pairs: ${value.direct_lexical_continuity?.length ?? "Not recorded"}; normalized pairs: ${value.lemma_normalized_continuity?.length ?? "Not recorded"}.`);
        for (const pair of value.direct_lexical_continuity || []) {
          transparencyTable(section, ["Recorded shared form", "Evidence type", "Matching occurrences"], [[pair.normalized_form, pair.evidence_type, (pair.matching_occurrences || []).map(occurrence => Object.entries(occurrence).map(([sectionName, item]) => `${sectionName}: ${item.text} [${item.start}, ${item.end})`).join(" · ")).join("; ")]]);
        }
        for (const pair of value.lemma_normalized_continuity || []) {
          transparencyTable(section, ["Recorded shared lemma form", "Evidence type", "Matching occurrences"], [[pair.normalized_form, pair.evidence_type, (pair.matching_occurrences || []).map(occurrence => Object.entries(occurrence).map(([sectionName, item]) => `${sectionName}: ${item.text} [${item.start}, ${item.end})`).join(" · ")).join("; ")]]);
        }
        if (Array.isArray(value.unobserved_source_concepts) && value.unobserved_source_concepts.length) transparencyText(section, `Recorded earlier concepts without a match: ${value.unobserved_source_concepts.join(", ")}.`, "explorer-evidence-note");
        if (Array.isArray(value.unobserved_introduction_concepts) && value.unobserved_introduction_concepts.length) transparencyText(section, `Recorded Introduction concepts without a Body match: ${value.unobserved_introduction_concepts.join(", ")}.`, "explorer-evidence-note");
        parent.appendChild(section);
      }
    } else if (m.id === "rule-events") {
      renderRuleEvidence(parent, m, result, data);
    } else if (m.id === "feedback-decision") {
      renderFeedbackDecisionEvidence(parent, result, data);
    } else if (m.id === "feedback-explanation") {
      renderFeedbackExplanationEvidence(parent, result, data);
    } else if (m.id === "feedback-fields") {
      subheading(parent, "Exact returned feedback fields");
      renderActualFeedbackFields(parent, result);
      transparencyTable(parent, ["Feedback field", "Returned type", "Recorded branch", "Recorded condition"], feedbackFields().map(field => {
        const decision = data.stageTrace?.feedback_decisions?.fields?.[field] || {};
        const value = result.feedback?.[field];
        return [field, Array.isArray(value) ? `${value.length} item list` : value === undefined || value === null ? "Not recorded" : "text", decision.selection_branch ?? "Not recorded", decision.selection_condition ?? "Not recorded"];
      }));
    } else if (m.id === "trait-mapping") {
      if (p.status === "NO_SUPPORTED_CONCERN_SELECTED") transparencyText(parent, "NO_SUPPORTED_CONCERN_SELECTED — no trait, skill, lesson or improvement task is assigned to this neutral result.", "explorer-outcome");
      else if (p.status === "NEUTRAL_OBSERVATION") transparencyText(parent, "NEUTRAL_OBSERVATION — the recorded branch is a neutral review. No corrective trait, skill, improvement task or error location is assigned; the prepared item below remains an explanation, not a concern.", "explorer-outcome");
      transparencyTable(parent, ["Recorded presentation", "Actual value"], [["Status", p.status], ["Trait", p.writing_dimension ?? "None assigned"], ["Instructional skill", p.writing_skill ?? "None assigned"], ["Assigned corrective lesson", p.teaching_content_source?.content_id ?? "None assigned"], ["Selected branch", p.selection_branch ?? "Not recorded"]]);
      transparencyTable(parent, ["Student tutor section", "Actual wording"], Object.entries(p.displayed_guidance));
      if (p.displayed_strengths) transparencyText(parent, `What's working — recorded observation: ${p.displayed_strengths}`);
      transparencyTable(parent, ["Recorded prepared tutor item", "Lesson ID", "Item role", "Recorded purpose"], (p.tutor_items || []).map(item => [item.label ?? "Not recorded", item.lesson_id ?? "None", item.role ?? "Not recorded", item.feedback_purpose ?? "Not recorded"]), "No prepared tutor item was retained for this selection.");
    } else if (m.id === "highlight-evidence") {
      const marks = p.tutor_items.flatMap(item => (item.highlight_provenance || []).map(mark => [mark.text, mark.start, mark.end, mark.rule_id, mark.selection_reason]));
      transparencyTable(parent, ["Exact marked text", "Start", "End", "Supporting rule", "Why this location"], marks, m.execution.basis);
      for (const item of p.tutor_items.filter(item => item.excerpt?.contexts?.some(context => context.marks?.length))) {
        const excerpt = element("div", null, "tutor-evidence explorer-source-excerpt");
        parent.appendChild(excerpt);
        renderTutorEvidence(excerpt, item);
      }
    } else if (m.id === "api-rendering") {
      renderResponseTimingEvidence(parent, data);
    } else if (m.id === "technical-trace") {
      renderTechnicalTraceEvidence(parent, data);
    } else if (["topic-sentences", "supporting-details", "stage-patterns", "repetition", "synthesis", "new-material", "sentence-connection"].includes(m.id)) {
      renderStageObservationEvidence(parent, m, data);
      renderRuleRowsTable(parent, m, data);
    } else {
      renderRuleRowsTable(parent, m, data);
      if (!m.rows.length) transparencyText(parent, "No process-specific evidence table is retained for this record.", "explorer-empty-state");
    }
    transparencyText(parent, `Execution basis: ${m.execution.basis}`, "explorer-evidence-note");
    if (m.execution.duration_ms !== null && m.execution.duration_ms !== undefined) {
      transparencyText(parent, `Recorded timing: ${m.execution.duration_ms} ms. ${m.group === "linguistic" ? "Shared document duration, not a separate annotation duration." : "Only this recorded scope is claimed."}`, "explorer-evidence-note");
    }
  }

  function renderStageObservationEvidence(parent, m, data) {
    const a = data.analysis;
    if (data.stage === "INTRODUCTION") {
      if (m.id === "sentence-connection") {
        const review = a.sentence_topic_evidence?.review_candidates || [];
        transparencyTable(parent, ["Review candidate", "Recorded status", "Recorded reason", "Start", "End"], review.map(item => [item.text ?? "Candidate", item.status ?? "Not recorded", item.reason ?? item.condition ?? "Recorded review signal", item.start ?? "Not recorded", item.end ?? "Not recorded"]), "No sentence topic-connection review candidate was recorded.");
        return;
      }
      if (a.text_presence) transparencyTable(parent, ["Text-presence observation", "Actual value"], Object.entries(a.text_presence).map(([key, value]) => [transparencyLabel(key), compactValue(value)]));
      const structure = a.observable_structure || {};
      const candidates = structure.central_direction_candidates || structure.central_direction_candidate?.candidates || [];
      const evidenceText = value => Array.isArray(value)
        ? value.map(item => item?.text ?? item).join(", ") || "Not recorded"
        : value?.text ?? (typeof value === "string" ? value : "Not recorded");
      if (Array.isArray(candidates)) transparencyTable(parent, ["Central-direction candidate", "Root clause", "Subject evidence", "Predicate"], candidates.map(candidate => [
        candidate.sentence_text ?? candidate.text ?? candidate.clause_text ?? "Recorded candidate",
        candidate.is_root_clause === true ? "Yes" : candidate.is_root_clause === false ? "No" : "Not recorded",
        evidenceText(candidate.subject_evidence),
        evidenceText(candidate.predicate_evidence),
      ]));
      const incomplete = structure.incomplete_subordinator_candidates || [];
      if (Array.isArray(incomplete)) transparencyTable(parent, ["Possible incomplete subordinator", "Start", "End", "Marker POS"], incomplete.map(item => [item.text, item.start, item.end, item.pos ?? "Not recorded"]));
      if (a.development_evidence) transparencyTable(parent, ["Development observation", "Actual value"], Object.entries(a.development_evidence).map(([key, value]) => [transparencyLabel(key), compactValue(value)]));
      if (a.position_statement_evidence) transparencyTable(parent, ["Position-statement observation", "Actual value"], Object.entries(a.position_statement_evidence).map(([key, value]) => [transparencyLabel(key), compactValue(value)]));
    } else if (data.stage === "BODY") {
      transparencyTable(parent, ["Paragraph", "Sentences", "Words", "Recorded observation"], (a.paragraphs || []).map(paragraph => [paragraph.paragraph_index, paragraph.counts?.sentence_count, paragraph.counts?.alphabetic_word_count ?? paragraph.counts?.word_count,
        m.id === "topic-sentences" ? `${paragraph.topic_sentence_candidates?.length ?? 0} possible topic-sentence structure(s)`
          : m.id === "supporting-details" ? `${paragraph.supporting_detail_candidates?.status ?? "Not recorded"}; ${paragraph.supporting_detail_candidates?.candidates?.length ?? 0} structural candidate(s)`
            : m.id === "repetition" ? `${paragraph.repetition_observations?.repeated_sentence_openings?.length ?? 0} repeated-opening group(s)`
              : paragraph.fragment_or_list_candidate?.keyword_list_candidate ? "Recorded list-like candidate" : "Paragraph span recorded; no list-like candidate flag"]));
      if (m.id === "topic-sentences") {
        for (const paragraph of a.paragraphs || []) {
          const candidates = paragraph.topic_sentence_candidates || [];
          if (candidates.length) transparencyTable(parent, [`Paragraph ${paragraph.paragraph_index} — topic-sentence candidates`, "Recorded candidate", "Recorded reason", "Start", "End"], candidates.map(item => [item.text ?? "Candidate", item.reason ?? "Reason not recorded", item.start ?? "Not recorded", item.end ?? "Not recorded"]));
        }
      }
      if (m.id === "supporting-details") {
        for (const paragraph of a.paragraphs || []) {
          const candidates = paragraph.supporting_detail_candidates?.candidates || [];
          if (candidates.length) transparencyTable(parent, [`Paragraph ${paragraph.paragraph_index} — supporting-detail candidates`, "Recorded candidate", "Start", "End"], candidates.map(item => [item.text ?? "Candidate", item.start ?? "Not recorded", item.end ?? "Not recorded"]));
        }
      }
      if (m.id === "repetition") {
        for (const paragraph of a.paragraphs || []) {
          const groups = paragraph.repetition_observations?.repeated_sentence_openings || [];
          if (groups.length) transparencyTable(parent, [`Paragraph ${paragraph.paragraph_index} — repeated openings`, "Recorded repeated opening", "Occurrences"], groups.map(item => [Array.isArray(item.words) ? item.words.join(" ") : item.text ?? "Recorded group", (item.occurrences || []).length]));
        }
      }
    } else {
      if (a.text_presence) transparencyTable(parent, ["Conclusion text observation", "Actual value"], Object.entries(a.text_presence).map(([key, value]) => [transparencyLabel(key), compactValue(value)]));
      if (Array.isArray(a.conclusion_paragraphs)) transparencyTable(parent, ["Conclusion paragraph", "Sentences", "Words", "Recorded text"], a.conclusion_paragraphs.map((paragraph, index) => [paragraph.paragraph_index ?? index + 1, paragraph.counts?.sentence_count ?? "Not recorded", paragraph.counts?.alphabetic_word_count ?? paragraph.counts?.word_count ?? "Not recorded", paragraph.text]));
      if (m.id === "stage-patterns" && a.closure_candidates) {
        transparencyTable(parent, ["Closure candidate type", "Recorded text", "Evidence type", "Start", "End"], (a.closure_candidates.candidates || []).map(item => [item.candidate_type ?? "Recorded candidate", item.sentence_text ?? item.text ?? "Not recorded", item.evidence_type ?? "Not recorded", item.start ?? item.sentence_span?.[0] ?? "Not recorded", item.end ?? item.sentence_span?.[1] ?? "Not recorded"]));
      }
      if (m.id === "synthesis") {
        const synthesis = a.synthesis_structure_candidates || {};
        transparencyTable(parent, ["Synthesis status", "Candidate count"], [[synthesis.status ?? "Not recorded", Array.isArray(synthesis.candidates) ? synthesis.candidates.length : "Not recorded"]]);
        for (const candidate of synthesis.candidates || []) {
          subheading(parent, "Recorded synthesis candidate");
          transparencyText(parent, candidate.sentence_text ?? "Candidate text not recorded");
          transparencyTable(parent, ["Earlier concept form", "Earlier sections", "Conclusion occurrences"], (candidate.earlier_concept_matches || []).map(item => [item.normalized_form, (item.prior_sections || []).join(", "), (item.conclusion_occurrences || []).map(occurrence => `[${occurrence.start}, ${occurrence.end})`).join(", ")]));
        }
      }
      if (m.id === "new-material") {
        const observations = a.new_material_observations || {};
        transparencyTable(parent, ["New-material status", "Value"], [["Status", observations.status ?? "Not recorded"], ["Prior sections supplied", compactValue(observations.prior_sections_supplied)]], "No new-material observation was retained for this stage.");
        transparencyTable(parent, ["Unobserved concept candidate", "Unobserved content lemmas", "Occurrences"], (observations.unobserved_concept_candidates || []).map(item => [item.normalized_form, (item.unobserved_content_lemmas || []).join(", ") || "Not recorded", (item.conclusion_occurrences || []).map(occurrence => `[${occurrence.start}, ${occurrence.end})`).join(", ")]));
        transparencyTable(parent, ["Phrase of previously observed words", "Occurrences"], (observations.phrase_combinations_of_observed_concepts || []).map(item => [item.normalized_form, (item.conclusion_occurrences || []).length]));
        transparencyTable(parent, ["Surface rewording candidate", "Recorded evidence"], (observations.surface_rewording_candidates || []).map(item => [item.normalized_form ?? item.observed_text ?? "Recorded candidate", compactValue(item.evidence_type ?? item.observation ?? "Recorded rewording observation")]));
      }
      if (m.id === "repetition") {
        for (const paragraph of a.conclusion_paragraphs || []) {
          const groups = paragraph.repetition_observations?.repeated_sentence_openings || (a.repetition_observations?.repeated_sentence_openings || []);
          if (groups.length) transparencyTable(parent, [`Conclusion paragraph ${paragraph.paragraph_index ?? ""} — repeated openings`, "Recorded repeated opening", "Occurrences"], groups.map(item => [Array.isArray(item.words) ? item.words.join(" ") : item.text ?? "Recorded group", (item.occurrences || []).length]));
        }
        if (!Array.isArray(a.conclusion_paragraphs) || !a.conclusion_paragraphs.length) {
          const groups = a.repetition_observations?.repeated_sentence_openings || [];
          if (groups.length) transparencyTable(parent, ["Recorded repeated opening", "Occurrences"], groups.map(item => [Array.isArray(item.words) ? item.words.join(" ") : item.text ?? "Recorded group", (item.occurrences || []).length]));
        }
      }
    }
    transparencyText(parent, "These are recorded structural/lexical observations. They are not writing-quality judgments.", "explorer-evidence-note");
  }

  function renderProcessInput(parent, m, result, data, source) {
    const text = source.text ?? data.linguistic?.text ?? transparencyCurrentText(data);
    const counts = data.linguistic?.counts || {};
    if (["tokens", "pos", "dependencies", "lemmas", "sentences", "noun-phrases"].includes(m.id)) {
      transparencyTable(parent, ["Input", "Actual value"], [
        ["Writing stage", data.stage], ["Recorded text source", source.text_source ?? "Not recorded"],
        ["Unicode code-point characters", source.code_point_characters ?? "Not recorded"], ["Whitespace words", source.whitespace_words ?? "Not recorded"],
        ["Recorded tokens", counts.token_count ?? data.tokens.length], ["Alphabetic words", counts.alphabetic_word_count ?? "Not recorded"],
        ["Recorded sentences", counts.sentence_count ?? data.sentences.length],
      ]);
      sourceTextBlock(parent, text, `Exact analyzed ${titles[data.stage] || data.stage} text`);
      return;
    }
    if (m.id === "focus-preparation" || m.id === "focus-normalization") {
      const context = data.trace?.teacher_context || {};
      transparencyTable(parent, ["Input", "Actual value"], [
        ["Assignment topic", context.assignment_topic ?? source.assignment_question ?? "Not recorded"],
        ["Focus source", context.focus_source ?? source.focus_source ?? "Not recorded"],
        ["Configured focus terms", (context.focus_terms || []).map(term => term.term).join(", ") || "None recorded"],
        ["Preparation duration", data.trace?.teacher_context_preparation_ms === undefined ? "Not recorded" : `${data.trace.teacher_context_preparation_ms} ms`],
      ]);
      return;
    }
    if (m.id === "concepts") {
      transparencyTable(parent, ["Input", "Actual value"], [["Writing stage", data.stage], ["Recorded tokens", counts.token_count ?? data.tokens.length], ["Recorded noun phrases", data.linguistic?.noun_phrases?.length ?? "Not recorded"], ["Concept extraction input", "The same recorded Doc's noun chunks and noun/proper-noun tokens"]]);
      sourceTextBlock(parent, text, "Exact analyzed text used for concept extraction");
      return;
    }
    if (m.id === "topic-matching") {
      const lexical = data.analysis.lexical_topic_evidence || {};
      transparencyTable(parent, ["Input", "Actual value"], [["Configured focus terms", (lexical.focus_terms || []).join(", ") || "No configured terms"], ["Focus source", lexical.focus_source ?? source.focus_source ?? "Not recorded"], ["Input text", "Exact analyzed stage text below"]]);
      sourceTextBlock(parent, text, "Exact analyzed text used for focus-term matching");
      return;
    }
    if (m.id === "wordnet") {
      transparencyTable(parent, ["Input", "Actual value"], [["include_wordnet flag", data.stageTrace?.topic_service?.input?.include_wordnet ?? "Not recorded"], ["Configured focus terms", (data.trace?.teacher_context?.focus_terms || []).map(term => term.term).join(", ") || "None recorded"], ["Direct lookup pairs retained", Array.isArray(m.output?.lookup_pairs) ? m.output.lookup_pairs.length : "Not recorded"]]);
      if (data.stage !== "INTRODUCTION" && source.earlier_sections?.length) {
        for (const prior of source.earlier_sections) {
          if (prior.text === null) transparencyText(parent, `${prior.stage}: not supplied. ${prior.status}`, "explorer-evidence-note");
          else sourceTextBlock(parent, prior.text, `Supplied ${prior.stage} context used in cross-stage comparisons`);
        }
      }
      return;
    }
    if (m.id === "related-concepts") {
      transparencyTable(parent, ["Input", "Actual value"], [["Configured focus terms", (data.trace?.teacher_context?.focus_terms || []).map(term => term.term).join(", ") || "None recorded"], ["Prepared linguistic input", "The recorded tokens and lemmas from the shared Doc"]]);
      sourceTextBlock(parent, text, "Exact analyzed text used for the informational related-word branch");
      return;
    }
    if (m.id === "cross-stage") {
      if (data.stage === "INTRODUCTION") {
        transparencyText(parent, "Not applicable: Introduction has no earlier supplied section to compare.", "explorer-empty-state");
        return;
      }
      for (const prior of source.earlier_sections || []) {
        if (prior.text === null) transparencyText(parent, `${prior.stage}: not supplied. ${prior.status}`, "explorer-evidence-note");
        else sourceTextBlock(parent, prior.text, `Supplied ${prior.stage} text used in the comparison`);
      }
      sourceTextBlock(parent, text, `Exact analyzed ${titles[data.stage] || data.stage} text`);
      return;
    }
    if (m.id === "rule-events") {
      const findings = m.input.stage_findings || {};
      transparencyTable(parent, ["Recorded stage observation group", "Actual value"], Object.entries(findings).map(([key, value]) => [transparencyLabel(key), Array.isArray(value) ? `${value.length} record(s)` : value && typeof value === "object" ? `${Object.keys(value).length} field(s)` : compactValue(value)]));
      transparencyText(parent, "Rule Bases consume these recorded observations. The later reconstructed evaluation trace is not an input to feedback selection.", "explorer-evidence-note");
      return;
    }
    if (m.id === "feedback-decision" || m.id === "feedback-explanation" || m.id === "feedback-fields") {
      const decisions = data.stageTrace?.feedback_decisions || {};
      transparencyTable(parent, ["Feedback input", "Actual value"], [["Available stage observation groups", Object.keys(data.analysis).filter(key => key !== "rule_evaluation_trace").length], ["Recorded decision fields", Object.keys(decisions.fields || {}).length], ["Selection status", decisions.selection_status ?? "Not recorded"], ["Selection source", decisions.selection_source ?? "Not recorded"], ["Reconstructed evaluation trace used as input", "No — it is not an input to FeedbackService."]]);
      return;
    }
    if (m.id === "api-rendering") {
      transparencyTable(parent, ["Request / response fact", "Actual value"], [["Selected stage", result.stage_id], ["Availability", result.availability], ["Returned top-level keys", Object.keys(result).filter(key => key !== "research_trace").join(", ")], ["Selected-stage trace retained", data.trace ? "Yes" : "No"], ["Authentication / CSRF timing", data.trace?.api_authentication_and_csrf_timing ?? "NOT_INSTRUMENTED"]]);
      return;
    }
    if (m.id === "technical-trace") {
      transparencyTable(parent, ["Trace input", "Actual value"], [["Selected stage", data.stage], ["Trace present", data.trace ? "Yes" : "No"], ["Trace version", data.trace?.trace_version ?? "Not recorded"], ["Stage trace keys", data.stageTrace ? Object.keys(data.stageTrace).join(", ") : "No selected-stage trace"]]);
      return;
    }
    if (m.id === "trait-mapping" || m.id === "highlight-evidence") {
      transparencyTable(parent, ["Input", "Actual value"], [["Selected branch", data.stageTrace?.feedback_decisions?.fields?.["Primary Feedback"]?.selection_branch ?? "Not recorded"], ["Primary Feedback rule IDs", (data.stageTrace?.feedback_decisions?.fields?.["Primary Feedback"]?.rule_ids || []).join(", ") || "None recorded"], ["Analyzed text source", source.text_source ?? "Not recorded"]]);
      sourceTextBlock(parent, text, "Exact analyzed text used for presentation and highlight verification");
      return;
    }
    transparencyTable(parent, ["Input", "Actual value"], [["Writing stage", data.stage], ["Recorded sentences", counts.sentence_count ?? data.sentences.length], ["Recorded paragraphs", Array.isArray(data.analysis.paragraphs) ? data.analysis.paragraphs.length : Array.isArray(data.analysis.conclusion_paragraphs) ? data.analysis.conclusion_paragraphs.length : "Not recorded"]]);
    sourceTextBlock(parent, text, "Exact analyzed text used by this stage's observations");
  }

  function renderProcessVisual(parent, m, result, data, source) {
    const text = source.text ?? data.linguistic?.text ?? transparencyCurrentText(data);
    const tokens = data.linguistic?.tokens || [];
    switch (m.id) {
      case "focus-preparation":
      case "focus-normalization": {
        const terms = data.trace?.teacher_context?.focus_terms || [];
        if (!terms.length) { transparencyText(parent, "No normalized focus-term records were retained; no preparation flow is drawn.", "explorer-empty-state"); return; }
        const list = element("div", null, "explorer-normalization-flow");
        for (const term of terms) {
          const row = element("div", null, "explorer-normalization-row");
          row.append(element("strong", term.term, "explorer-term-original"), element("span", "→", "explorer-flow-arrow"), element("span", (term.surface_words || []).join(" "), "explorer-term-surface"), element("span", "→", "explorer-flow-arrow"), element("span", (term.normalized_words || []).join(" "), "explorer-term-normalized"), element("span", (term.wordnet_pos || []).join("/") || "no WordNet POS", "explorer-term-pos"));
          list.appendChild(row);
        }
        parent.appendChild(list);
        transparencyText(parent, "The surface word sequence and normalized lemma sequence are the two targets used by recorded focus-window matching. Normalization does not decide that different lemmas mean the same idea.", "explorer-evidence-note");
        return;
      }
      case "tokens":
        if (!tokens.length) { transparencyText(parent, "No token records were retained; no token strip is drawn.", "explorer-empty-state"); return; }
        renderTokenStrip(parent, tokens);
        transparencyText(parent, `${tokens.length} tokens are shown exactly as returned. Punctuation is retained; whitespace tokens are not part of the serialized list.`, "explorer-evidence-note");
        return;
      case "pos":
        if (!tokens.length || typeof text !== "string") { transparencyText(parent, "No POS/tag records with an exact source text were retained; no highlighted text is drawn.", "explorer-empty-state"); return; }
        renderPosHighlight(parent, tokens, text);
        return;
      case "dependencies":
        renderDependencyTree(parent, data, text);
        return;
      case "lemmas":
        renderLemmaChanges(parent, tokens);
        return;
      case "sentences":
        renderSentenceCards(parent, data.sentences || [], data.analysis.paragraphs || data.analysis.conclusion_paragraphs || []);
        if (Array.isArray(data.analysis.paragraphs || data.analysis.conclusion_paragraphs)) renderParagraphCards(parent, data.analysis.paragraphs || data.analysis.conclusion_paragraphs || []);
        return;
      case "noun-phrases":
        renderNounChunkChips(parent, data.linguistic?.noun_phrases || [], text);
        return;
      case "concepts": {
        const concepts = data.concepts || [];
        if (!concepts.length) { transparencyText(parent, "No concept candidates were retained for this stage.", "explorer-empty-state"); return; }
        const list = element("div", null, "explorer-concept-groups");
        for (const concept of concepts) {
          const card = element("div", null, "explorer-concept-card");
          card.appendChild(element("strong", concept.text));
          card.appendChild(element("span", `${concept.occurrence_count} occurrence(s) · ${(concept.extraction_methods || []).join(", ") || "method not recorded"}`, "explorer-concept-meta"));
          chips(card, (concept.occurrences || []).map(item => ({ label: item.text, detail: `[${item.start}, ${item.end})` })), "explorer-chip explorer-occurrence-chip");
          list.appendChild(card);
        }
        parent.appendChild(list);
        return;
      }
      case "topic-matching":
        renderTopicMap(parent, data);
        return;
      case "wordnet":
        renderWordNetVisual(parent, m);
        return;
      case "related-concepts": {
        const evidence = result.related_topic_concept_evidence?.evidence || [];
        if (!evidence.length) { transparencyText(parent, `No related-word observations were recorded. ${result.related_topic_concept_evidence?.execution_status ? `Recorded status: ${result.related_topic_concept_evidence.execution_status}.` : ""}`, "explorer-empty-state"); return; }
        chips(parent, evidence.map(item => ({ label: item.student_word, detail: `→ ${item.teacher_focus_term} · ${item.relationship_id}` })), "explorer-chip explorer-related-chip");
        transparencyText(parent, "These relationships are informational and are not counted as direct or lemma focus matches.", "explorer-evidence-note");
        return;
      }
      case "cross-stage": {
        if (data.stage === "INTRODUCTION") { transparencyText(parent, "Not applicable: no earlier section exists.", "explorer-empty-state"); return; }
        const rows = Object.entries(m.output || {}).map(([key, value]) => [transparencyLabel(key), value.status ?? "Not recorded", value.direct_lexical_continuity?.length ?? "Not recorded", value.lemma_normalized_continuity?.length ?? "Not recorded", value.wordnet_relationship_candidates?.status ?? "Not recorded"]);
        if (rows.length) transparencyTable(parent, ["Comparison path", "Status", "Direct pairs", "Normalized pairs", "Nested WordNet status"], rows);
        else transparencyText(parent, "No cross-stage comparison records were retained.", "explorer-empty-state");
        return;
      }
      case "stage-patterns": {
        if (data.stage === "BODY") { renderParagraphCards(parent, data.analysis.paragraphs || []); return; }
        if (data.stage === "CONCLUSION") { renderParagraphCards(parent, data.analysis.conclusion_paragraphs || []); return; }
        const structure = data.analysis.observable_structure || {};
        const candidates = structure.central_direction_candidates || structure.central_direction_candidate?.candidates || [];
        const items = candidates.length ? candidates.map((candidate, index) => ({ label: candidate.text ?? candidate.clause_text ?? `Candidate ${index + 1}`, detail: candidate.is_root_clause ? "root clause" : "recorded candidate" })) : [{ label: "No central-direction candidate retained", detail: "recorded empty" }];
        chips(parent, items, "explorer-chip explorer-candidate-chip");
        return;
      }
      case "sentence-connection": {
        const review = data.analysis.sentence_topic_evidence?.review_candidates || [];
        if (!review.length) { transparencyText(parent, "No sentence topic-connection review candidate was recorded.", "explorer-empty-state"); return; }
        chips(parent, review.map(item => ({ label: item.text ?? "Candidate", detail: item.status ?? "recorded review signal" })), "explorer-chip explorer-review-chip");
        return;
      }
      case "topic-sentences":
      case "supporting-details":
      case "repetition":
      case "synthesis":
      case "new-material": {
        const paragraphs = data.stage === "CONCLUSION" ? data.analysis.conclusion_paragraphs || [] : data.analysis.paragraphs || [];
        if (m.id === "synthesis" || m.id === "new-material" || (m.id === "repetition" && data.stage === "CONCLUSION")) {
          const candidates = m.id === "synthesis" ? data.analysis.synthesis_structure_candidates?.candidates || []
            : m.id === "new-material" ? data.analysis.new_material_observations?.unobserved_concept_candidates || []
              : data.analysis.repetition_observations?.repeated_sentence_openings || [];
          if (!candidates.length) { transparencyText(parent, "No candidates of this kind were recorded for the analyzed ending.", "explorer-empty-state"); return; }
          chips(parent, candidates.map(item => ({
            label: m.id === "synthesis" ? item.sentence_text ?? "Recorded candidate" : item.normalized_form ?? (Array.isArray(item.words) ? item.words.join(" ") : "Recorded group"),
            detail: m.id === "synthesis" ? `${(item.earlier_concept_matches || []).length} earlier concept match(es)` : m.id === "new-material" ? "unobserved in supplied earlier sections" : `${(item.occurrences || []).length} occurrence(s)`,
          })), "explorer-chip explorer-candidate-chip");
          return;
        }
        if (!paragraphs.length) { transparencyText(parent, "No paragraph records were retained for this stage.", "explorer-empty-state"); return; }
        const list = element("div", null, "explorer-paragraph-list");
        for (const paragraph of paragraphs) {
          const card = element("article", null, "explorer-paragraph-card");
          card.dataset.paragraphIndex = String(paragraph.paragraph_index);
          card.appendChild(element("strong", `Paragraph ${paragraph.paragraph_index}`));
          const entries = m.id === "topic-sentences" ? paragraph.topic_sentence_candidates || []
            : m.id === "supporting-details" ? paragraph.supporting_detail_candidates?.candidates || []
              : paragraph.repetition_observations?.repeated_sentence_openings || [];
          chips(card, entries.length ? entries.map(item => ({ label: item.text ?? (Array.isArray(item.words) ? item.words.join(" ") : "Recorded candidate"), detail: m.id === "supporting-details" ? "structural candidate" : m.id === "topic-sentences" ? "possible topic sentence" : "repeated opening" })) : [{ label: "No recorded candidate", detail: m.id === "topic-sentences" ? "0 possible topic-sentence structures" : m.id === "supporting-details" ? paragraph.supporting_detail_candidates?.status ?? "Not recorded" : "0 repeated-opening groups" }], "explorer-chip explorer-candidate-chip");
          list.appendChild(card);
        }
        parent.appendChild(list);
        return;
      }
      case "rule-events":
        renderRuleVisual(parent, m, result, data);
        return;
      case "feedback-decision":
      case "feedback-explanation":
        renderFeedbackTraceVisual(parent, result, data);
        return;
      case "feedback-fields":
        renderFeedbackFieldSummary(parent, result);
        return;
      case "trait-mapping": {
        const presentation = m.presentation;
        const lessonIds = [...new Set((presentation.tutor_items || []).map(item => item.lesson_id).filter(Boolean))];
        flowLane(parent, [
          { label: "Selected branch", value: presentation.selection_branch ?? "Not recorded" },
          { label: "Instructional trait", value: presentation.writing_dimension ?? "None assigned" },
          { label: "Instructional skill", value: presentation.writing_skill ?? "None assigned" },
          { label: "Recorded lesson item(s)", value: lessonIds.length ? lessonIds.join(", ") : "None assigned" },
          { label: "Student tutor display", value: presentation.status },
        ], "Recorded instructional presentation flow");
        return;
      }
      case "highlight-evidence": {
        const marks = m.presentation.tutor_items.flatMap(item => item.highlight_provenance || []);
        if (!marks.length) { transparencyText(parent, "No verified highlight was selected for this feedback state; no source span is invented.", "explorer-empty-state"); return; }
        markExactSpans(parent, text, marks.map(mark => ({ start: mark.start, end: mark.end, title: `${mark.rule_id} · ${mark.selection_reason ?? "recorded selection"}` })), "explorer-highlight-mark");
        return;
      }
      case "api-rendering":
        renderResponseFlowVisual(parent, result, data);
        return;
      case "technical-trace":
        renderTechnicalTraceVisual(parent, data);
        return;
      default:
        transparencyText(parent, "The recorded rows for this process are listed in Actual Recorded Evidence; no additional visual model is claimed.", "explorer-empty-state");
    }
  }

  function renderProcessOutput(parent, m, result, data) {
    transparencyText(parent, m.next);
    const rows = [];
    if (m.id === "tokens") rows.push(["Recorded tokens", (data.linguistic?.tokens || []).length]);
    if (m.id === "sentences") rows.push(["Recorded sentences", (data.linguistic?.sentences || []).length]);
    if (m.id === "noun-phrases") rows.push(["Recorded noun phrases", (data.linguistic?.noun_phrases || []).length]);
    if (m.id === "concepts") rows.push(["Recorded concept groups", (data.concepts || []).length]);
    if (m.id === "topic-matching") rows.push(["Recorded matches", data.analysis.lexical_topic_evidence?.matches?.length ?? "Not recorded"]);
    if (m.id === "wordnet") rows.push(["Direct lookup pairs", Array.isArray(m.output?.lookup_pairs) ? m.output.lookup_pairs.length : "Not recorded"], ["Cross-stage lookup pairs", Object.values(m.crossStageWordNet || {}).reduce((count, value) => count + (Array.isArray(value?.lookup_pairs) ? value.lookup_pairs.length : 0), 0)]);
    if (m.id === "rule-events") rows.push(["Emitted Rule Events", (data.analysis.rule_evidence || []).length], ["Reconstructed evaluation rows", (data.analysis.rule_evaluation_trace || []).length]);
    if (m.id === "feedback-decision" || m.id === "feedback-explanation" || m.id === "feedback-fields") rows.push(["Feedback fields returned", feedbackFields().filter(field => field in (result.feedback || {})).length]);
    if (rows.length) transparencyTable(parent, ["Recorded output", "Count / value"], rows);
    transparencyText(parent, "This handoff follows the implementation. Per-record usage is claimed only where the retained comparison or provenance records it.", "explorer-evidence-note");
  }

  function renderProcessPage(host, process, result, data) {
    const source = studentTextInputEvidence(result);
    const overview = stageSection(host, "A", "Process Overview");
    subheading(overview, "What does this process do?");
    transparencyText(overview, process.purpose, "explorer-purpose");
    const status = element("span", process.execution.label, "explorer-status");
    status.dataset.executionStatus = process.execution.status;
    const statusLine = element("div", null, "explorer-status-line");
    statusLine.append(element("span", "Recorded execution", "explorer-status-caption"), status);
    overview.appendChild(statusLine);
    transparencyText(overview, process.execution.basis, "explorer-evidence-note");
    const input = stageSection(host, "B", "Actual Input");
    renderProcessInput(input, process, result, data, source);
    const visual = stageSection(host, "C", "Visual Representation");
    renderProcessVisual(visual, process, result, data, source);
    const evidence = stageSection(host, "D", "Actual Recorded Evidence");
    renderEvidence(evidence, process, result, data);
    const how = stageSection(host, "E", "How the Process Works");
    subheading(how, "How does EssayScaff perform it?");
    transparencyText(how, process.method);
    transparencyText(how, "This is a source-verified explanation of the implementation. It is not a per-request model log or a claim that hidden internal reasoning was inspected.", "explorer-evidence-note");
    const next = stageSection(host, "F", "Output and Next Destination");
    subheading(next, "Where does the output go next?");
    renderProcessOutput(next, process, result, data);
    const sourceSection = stageSection(host, "G", "Implementation Source");
    transparencyText(sourceSection, process.source, "transparency-source");
    const limits = stageSection(host, "H", "Limitations");
    subheading(limits, "Limitations");
    transparencyText(limits, process.limitation);
    transparencyText(limits, process.input_note, "field-help");
  }

  function create(parent, result, data) {
    const presentation = studentFeedbackPresentation(result);
    const processes = catalog(data.stage).map(spec => model(spec, result, data, presentation));
    const source = studentTextInputEvidence(result);
    const preferenceKey = `${state.assignmentId ?? "practice"}:${data.stage}`;
    const root = element("div", null, "nlp-process-explorer");
    root.dataset.processExplorer = "true";
    const metadata = element("div", null, "explorer-snapshot-header");
    const counts = data.linguistic?.counts || {};
    const paragraphCount = data.analysis.paragraph_count ?? data.analysis.text_presence?.paragraph_count
      ?? (Array.isArray(data.analysis.conclusion_paragraphs) ? data.analysis.conclusion_paragraphs.length : null);
    const metrics = [["stage", "Writing stage", data.stage], ["assignment", "Assignment", state.assignmentTitle || source.assignment_question || "Not recorded"],
      ["words", "Words", counts.alphabetic_word_count ?? source.whitespace_words], ["tokens", "Tokens", counts.token_count ?? (Array.isArray(data.linguistic?.tokens) ? data.tokens.length : null)],
      ["sentences", "Sentences", counts.sentence_count ?? (Array.isArray(data.linguistic?.sentences) ? data.sentences.length : null)],
      ...(data.stage !== "INTRODUCTION" ? [["paragraphs", "Paragraphs", paragraphCount]] : []),
      ["fingerprint", "Analyzed-text fingerprint", source.browser_fingerprint || "Not recorded"]];
    for (const [key, label, value] of metrics) {
      const cell = element("div", null, `explorer-metric explorer-metric-${key}`);
      const output = element("strong", present(value) ? value : "Not recorded");
      output.dataset.explorerMetric = key;
      if (key === "words") output.title = present(counts.alphabetic_word_count) ? "Recorded alphabetic-word count from the shared linguistic observations." : "Browser-derived whitespace count from the exact retained analyzed text.";
      if (key === "fingerprint") output.title = "Existing browser-derived analyzed-text fingerprint; not a cryptographic hash or saved revision ID.";
      cell.append(element("span", label), output);
      metadata.appendChild(cell);
    }
    root.appendChild(metadata);
    root.appendChild(element("p", "All pages read the cached selected-stage response. Changing stages or processes never re-runs spaCy, rules or feedback.", "explorer-intro"));
    const stageNavigation = element("div", null, "explorer-stage-navigation");
    stageNavigation.setAttribute("role", "group");
    stageNavigation.setAttribute("aria-label", "Analysis stages");
    const stageButtons = new Map(), groupHosts = new Map(), groupButtonHosts = new Map();
    for (const [group, number, title] of GROUPS) {
      const button = element("button", null, "explorer-stage-button");
      button.type = "button";
      button.dataset.processStage = group;
      button.setAttribute("aria-pressed", "false");
      button.append(element("span", number, "explorer-stage-number"), element("strong", title));
      button.addEventListener("click", () => api.selectStage(group));
      stageNavigation.appendChild(button);
      stageButtons.set(group, button);
    }
    root.appendChild(stageNavigation);
    const stageNote = element("p", null, "explorer-stage-note");
    root.appendChild(stageNote);
    const processNavigation = element("nav", null, "explorer-process-navigation");
    processNavigation.setAttribute("aria-label", "Processes in the selected stage");
    for (const [group, number, title] of GROUPS) {
      const groupHost = element("div", null, "explorer-process-group");
      groupHost.dataset.processGroup = group;
      groupHost.hidden = true;
      groupHost.appendChild(element("span", `${number} · ${title}`, "explorer-process-group-title"));
      const buttonsHost = element("div", null, "explorer-process-buttons");
      groupHost.appendChild(buttonsHost);
      groupHosts.set(group, groupHost);
      groupButtonHosts.set(group, buttonsHost);
      processNavigation.appendChild(groupHost);
    }
    root.appendChild(processNavigation);
    const toolbar = element("div", null, "explorer-toolbar");
    const position = element("span", "", "explorer-process-position");
    const previous = element("button", "Previous Process", "button-secondary");
    previous.type = "button";
    previous.id = "explorer-previous-process";
    const next = element("button", "Next Process", "button-secondary");
    next.type = "button";
    next.id = "explorer-next-process";
    toolbar.append(position, previous, next);
    const detailsHost = element("div", null, "explorer-detail-host");
    detailsHost.appendChild(toolbar);
    root.appendChild(detailsHost);
    const original = element("details", null, "explorer-input-records");
    original.appendChild(element("summary", "Analyzed text, browser input and Flask response records"));
    const originalContent = element("div", null, "explorer-input-records-content");
    original.appendChild(originalContent);
    root.appendChild(original);
    const buttons = new Map(), panels = new Map(), contentHosts = new Map(), evidenceHosts = new Map(), subPanels = {}, sectionDetails = {};
    const api = { processes, subPanels, activeProcessId: null, setOnActivateSubtab(callback) { api.onSection = callback; } };
    const built = new Set();
    const ensureContent = process => {
      if (built.has(process.id)) return;
      built.add(process.id);
      renderProcessPage(contentHosts.get(process.id), process, result, data);
    };
    for (const [group] of GROUPS) {
      const buttonsHost = groupButtonHosts.get(group);
      for (const process of processes.filter(item => item.group === group)) {
        const button = element("button", null, "explorer-process-button");
        button.type = "button";
        button.dataset.processId = process.id;
        button.setAttribute("aria-controls", `explorer-panel-${process.id}`);
        const index = processes.findIndex(item => item.id === process.id) + 1;
        button.append(element("span", String(index).padStart(2, "0"), "explorer-process-number"),
          element("span", process.title, "explorer-process-name"),
          element("span", process.execution.label, "explorer-nav-status"));
        button.setAttribute("data-status", process.execution.status);
        button.addEventListener("click", () => {
          api.selectProcess(process.id);
          if (typeof button.focus === "function") button.focus({ preventScroll: true });
        });
        button.addEventListener("keydown", event => {
          const current = processes.findIndex(item => item.id === api.activeProcessId);
          const target = event.key === "ArrowDown" || event.key === "ArrowRight" ? Math.min(current + 1, processes.length - 1)
            : event.key === "ArrowUp" || event.key === "ArrowLeft" ? Math.max(current - 1, 0)
              : event.key === "Home" ? 0 : event.key === "End" ? processes.length - 1 : null;
          if (target === null) return;
          event.preventDefault();
          api.selectProcess(processes[target].id);
          const targetButton = buttons.get(processes[target].id);
          if (targetButton && typeof targetButton.focus === "function") targetButton.focus();
        });
        buttonsHost.appendChild(button);
        buttons.set(process.id, button);
      }
    }
    for (const process of processes) {
      const panel = element("article", null, "explorer-process-card");
      panel.dataset.explorerProcess = process.id;
      panel.id = `explorer-panel-${process.id}`;
      panel.hidden = true;
      panel.setAttribute("aria-labelledby", `explorer-title-${process.id}`);
      const heading = element("div", null, "explorer-process-heading");
      const headingText = element("div", null, "explorer-process-heading-text");
      headingText.append(element("span", `${String(processes.findIndex(item => item.id === process.id) + 1).padStart(2, "0")} · ${GROUP_TITLES[process.group]}`, "explorer-eyebrow"));
      const title = element("h3", process.title);
      title.id = `explorer-title-${process.id}`;
      headingText.appendChild(title);
      const status = element("span", process.execution.label, "explorer-status");
      status.dataset.executionStatus = process.execution.status;
      heading.append(headingText, status);
      panel.appendChild(heading);
      const content = element("div", null, "explorer-process-content");
      panel.appendChild(content);
      contentHosts.set(process.id, content);
      const developer = element("section", null, "explorer-developer-evidence");
      developer.dataset.explorerDeveloper = process.id;
      const devHeader = element("div", null, "explorer-developer-heading");
      devHeader.appendChild(element("h4", "Developer Evidence"));
      developer.appendChild(devHeader);
      transparencyText(developer, `Implementation: ${process.source}`, "transparency-source");
      transparencyText(developer, process.input_note, "field-help");
      transparencyText(developer, "The technical archive below preserves the original complete evidence sections. The process page above states the actual input, recorded evidence, output handoff and limitations without an expand action.", "explorer-evidence-note");
      const legacy = element("div", null, "explorer-original-evidence");
      developer.appendChild(legacy);
      evidenceHosts.set(process.id, legacy);
      panel.appendChild(developer);
      detailsHost.appendChild(panel);
      panels.set(process.id, panel);
    }
    const legacyTitles = new Map(HORIZONTAL_TRANSPARENCY_TABS.flatMap(([main, group, sections]) => sections.map(([sub, title]) => [`${main}:${sub}`, `${group} — ${title}`])));
    const addEvidenceSections = (home, owner) => {
      for (const key of SECTION_OWNERS[owner] || []) {
        const section = element("details", null, "explorer-evidence-section");
        section.dataset.evidenceSection = key;
        section.appendChild(element("summary", legacyTitles.get(key) || key));
        section.children[0].addEventListener("click", () => api.onSection?.(...key.split(":")));
        const content = element("div", null, "explorer-evidence-content");
        content.dataset.subPanel = key;
        content.id = `nlp-subpanel-${key.replace(":", "-")}`;
        section.appendChild(content);
        section.addEventListener("toggle", () => { if (section.open) api.onSection?.(...key.split(":")); });
        home.appendChild(section);
        subPanels[key] = content;
        sectionDetails[key] = { section, owner };
      }
    };
    addEvidenceSections(originalContent, "header");
    for (const owner of Object.keys(SECTION_OWNERS).filter(owner => owner !== "header")) {
      const home = evidenceHosts.get(owner);
      if (home) addEvidenceSections(home, owner);
    }
    parent.appendChild(root);
    const showStage = group => {
      root.dataset.activeStage = group;
      for (const [key, button] of stageButtons) {
        const active = key === group;
        button.setAttribute("aria-pressed", active ? "true" : "false");
        button.classList.toggle("is-active", active);
      }
      for (const [key, host] of groupHosts) host.hidden = key !== group;
      const members = processes.filter(process => process.group === group);
      const executed = members.filter(process => process.execution.status === "EXECUTED").length;
      const skipped = members.filter(process => process.execution.status === "SKIPPED").length;
      const unavailable = members.filter(process => process.execution.status === "UNAVAILABLE").length;
      stageNote.textContent = `${GROUP_TITLES[group]} · ${members.length} process${members.length === 1 ? "" : "es"} · ${executed} executed${skipped ? ` · ${skipped} skipped` : ""}${unavailable ? ` · ${unavailable} unavailable` : ""}`;
    };
    api.selectStage = group => {
      if (!groupHosts.has(group)) return;
      const active = processes.find(process => process.id === api.activeProcessId);
      if (active && active.group === group) { showStage(group); return; }
      const first = processes.find(process => process.group === group);
      if (first) api.selectProcess(first.id);
      else showStage(group);
    };
    api.selectProcess = id => {
      if (!panels.has(id)) return;
      const process = processes.find(item => item.id === id);
      api.activeProcessId = id;
      selections.set(preferenceKey, id);
      showStage(process.group);
      for (const item of processes) {
        const active = item.id === id;
        const panel = panels.get(item.id);
        panel.hidden = !active;
        const button = buttons.get(item.id);
        button.setAttribute("aria-current", active ? "step" : "false");
        button.tabIndex = active ? 0 : -1;
        button.classList.toggle("is-active", active);
      }
      const index = processes.findIndex(item => item.id === id);
      previous.disabled = index === 0;
      next.disabled = index === processes.length - 1;
      position.textContent = `Process ${index + 1} of ${processes.length} · ${GROUP_TITLES[process.group]}`;
      ensureContent(process);
    };
    api.activate = (main, sub, focus = true) => {
      const key = `${main}:${sub}`, target = sectionDetails[key];
      if (!target) return;
      if (target.owner === "header") original.open = true;
      else api.selectProcess(target.owner);
      target.section.open = true;
      api.onSection?.(main, sub);
      if (focus && target.section.children[0]?.focus) {
        target.section.children[0].focus();
        if (target.section.scrollIntoView) target.section.scrollIntoView({ block: "start" });
      }
    };
    api.finish = () => {
      const initial = selections.get(preferenceKey);
      api.selectProcess(panels.has(initial) ? initial : processes[0].id);
    };
    previous.addEventListener("click", () => {
      const index = processes.findIndex(item => item.id === api.activeProcessId);
      if (index > 0) api.selectProcess(processes[index - 1].id);
    });
    next.addEventListener("click", () => {
      const index = processes.findIndex(item => item.id === api.activeProcessId);
      if (index < processes.length - 1) api.selectProcess(processes[index + 1].id);
    });
    return api;
  }

  return { create, catalog, model, sectionOwners: SECTION_OWNERS };
})();
