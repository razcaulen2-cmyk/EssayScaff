"use strict";

const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content || "";
const processNav = document.getElementById("research-process-nav");
const processContent = document.getElementById("research-process-content");
const form = document.getElementById("research-sample-form");
const stageSelect = document.getElementById("research-stage");
const topicInput = document.getElementById("research-topic");
const focusInput = document.getElementById("research-focus-terms");
const introInput = document.getElementById("research-introduction");
const bodyInput = document.getElementById("research-body");
const conclusionInput = document.getElementById("research-conclusion");
const statusLabel = document.getElementById("research-analysis-status");
const requestStatus = document.getElementById("research-request-status");
const errorMessage = document.getElementById("research-error");
const processStatus = document.getElementById("research-process-status");
const detailNumber = document.getElementById("research-detail-number");
const detailTitle = document.getElementById("research-detail-title");
const metricsHost = document.getElementById("research-metrics");
const rawJson = document.getElementById("research-raw-json");
const copyButton = document.getElementById("copy-research-json");
const downloadButton = document.getElementById("download-research-json");

const REGRESSION_SAMPLE = {
  topic: "Should schools allow students to use artificial intelligence tools for learning?",
  focus: "artificial intelligence, education, students, technology, critical thinking",
  introduction: "Artificial intelligence tools are becoming common in schools. Schools should allow students to use them because they help with learning.",
};

const state = {
  metadata: null,
  response: null,
  activeProcess: 0,
  sampleLabel: "Custom sample",
  requestMs: null,
  renderMs: null,
};

function node(tag, text, className) {
  const element = document.createElement(tag);
  if (text !== undefined && text !== null) element.textContent = String(text);
  if (className) element.className = className;
  return element;
}

function appendText(parent, text, className) {
  const paragraph = node("p", text, className);
  parent.appendChild(paragraph);
  return paragraph;
}

function sectionHeading(parent, title) {
  const section = node("section", undefined, "research-explanation");
  section.appendChild(node("h3", title));
  parent.appendChild(section);
  return section;
}

function safeJson(value) {
  const pre = node("pre", JSON.stringify(value, null, 2), "research-raw-json");
  return pre;
}

function valueOr(value, fallback = "Not available") {
  if (value === undefined || value === null || value === "") return fallback;
  return value;
}

function stageName(stage = stageSelect.value) {
  return ({ INTRODUCTION: "Introduction", BODY: "Body", CONCLUSION: "Conclusion" })[stage] || stage;
}

function getAnalysis() {
  return state.response?.analysis || null;
}

function getStageTrace() {
  const trace = state.response?.research_trace;
  return trace?.stages?.[trace.selected_stage] || null;
}

function getLinguistic() {
  const analysis = getAnalysis();
  const stageTrace = getStageTrace();
  return analysis?.linguistic_observations
    || analysis?.linguistic_analysis
    || stageTrace?.linguistic_observations
    || null;
}

function getTopicTraceSteps() {
  return getStageTrace()?.topic_service?.steps || [];
}

function currentInputSummary() {
  const stage = stageSelect.value;
  const sections = {};
  if (introInput.value.trim()) sections.introduction = introInput.value;
  if (bodyInput.value.trim()) sections.body = bodyInput.value;
  if (conclusionInput.value.trim()) sections.conclusion = conclusionInput.value;
  const requiredName = stage.toLowerCase();
  sections[requiredName] = ({
    INTRODUCTION: introInput.value,
    BODY: bodyInput.value,
    CONCLUSION: conclusionInput.value,
  })[stage];
  return {
    stage_id: stage,
    assignment_topic: topicInput.value,
    focus_terms: focusInput.value.split(",").map((term) => term.trim()).filter(Boolean),
    sections,
  };
}

function buildRawTracePayload(result = state.response) {
  if (!result) return null;
  return {
    record_type: "authorized_research_inspector_trace",
    export_note: "Teacher-authorized custom sample analysis. This export contains no session cookies, credentials, saved assignment/session IDs, database rows, or unrelated student writing.",
    sample_label: state.sampleLabel,
    sanitized_request: currentInputSummary(),
    api_response: result,
    inspector_metadata: {
      process_catalog: state.metadata?.processes || [],
      source_locations: state.metadata?.process_source_locations || {},
      references: state.metadata?.references || [],
      evaluation_status: state.metadata?.evaluation || {},
    },
  };
}

function renderNavigation() {
  processNav.replaceChildren();
  for (const [index, item] of (state.metadata?.processes || []).entries()) {
    const button = node("button", undefined, "research-process-button");
    button.type = "button";
    button.dataset.index = String(index);
    button.setAttribute("aria-current", index === state.activeProcess ? "step" : "false");
    button.append(node("span", item.id, "process-number"), node("span", item.title));
    button.addEventListener("click", () => selectProcess(index));
    processNav.appendChild(button);
  }
}

function selectProcess(index) {
  const processes = state.metadata?.processes || [];
  if (!processes.length) return;
  state.activeProcess = Math.max(0, Math.min(index, processes.length - 1));
  const started = performance.now();
  renderNavigation();
  renderProcess();
  state.renderMs = performance.now() - started;
  renderMetrics();
}

function appendStatusChip(parent, status, detail = "") {
  const label = detail ? `${status} — ${detail}` : status;
  const chip = node("span", label, "research-status-chip");
  chip.dataset.status = status;
  parent.appendChild(chip);
}

function processStatusFor(id) {
  const trace = state.response?.research_trace;
  const stageTrace = getStageTrace();
  if (id === "09" || id === "10") {
    return { execution_status: "NOT_APPLICABLE", duration_ms: null };
  }
  if (id === "00" || id === "11") return { execution_status: state.response ? "EXECUTED" : "NOT_INSTRUMENTED" };
  if (id === "01") {
    return {
      execution_status: state.response ? "EXECUTED" : "NOT_INSTRUMENTED",
      duration_ms: trace?.request_validation_and_assignment_resolution_ms,
    };
  }
  if (id === "08") {
    return {
      execution_status: state.response ? "EXECUTED" : "NOT_INSTRUMENTED",
      duration_ms: state.renderMs === null ? null : Number(state.renderMs.toFixed(3)),
      note: "Duration is the most recent Research Inspector process-panel render measured in the browser with performance.now; it is not server NLP time.",
    };
  }
  if (!state.response || !stageTrace) return { execution_status: "NOT_INSTRUMENTED" };
  const traceSteps = getTopicTraceSteps();
  const stepIds = {
    "02": "spacy_document_processing",
    "03": "concept_extraction",
    "04": "topic_matching",
    "05": "wordnet_direct_suggestions",
  };
  if (stepIds[id]) {
    const step = traceSteps.find((item) => item.id === stepIds[id]);
    if (id !== "05") return step || { execution_status: "NOT_INSTRUMENTED" };
    return wordnetExecutionStatus(step);
  }
  const timings = stageTrace.timings_ms || {};
  if (id === "06") return { execution_status: timings.rule_base_ms === undefined ? "NOT_INSTRUMENTED" : "EXECUTED", duration_ms: timings.rule_base_ms };
  if (id === "07") return { execution_status: timings.feedback_ms === undefined ? "NOT_INSTRUMENTED" : "EXECUTED", duration_ms: timings.feedback_ms };
  return { execution_status: "NOT_INSTRUMENTED" };
}

function wordnetExecutionStatus(directStep) {
  const analysis = getAnalysis() || {};
  const stage = stageSelect.value;
  const comparisons = [];
  if (stage === "BODY") comparisons.push(analysis.introduction_to_body_continuity?.wordnet_relationship_candidates);
  if (stage === "CONCLUSION") {
    comparisons.push(analysis.introduction_to_conclusion_continuity?.wordnet_relationship_candidates);
    comparisons.push(analysis.body_to_conclusion_continuity?.wordnet_relationship_candidates);
  }
  const executedComparison = comparisons.find((item) => item && item.status !== "not_evaluated");
  if (directStep?.execution_status === "EXECUTED") {
    return {
      ...directStep,
      direct_path_status: directStep.status,
      cross_stage_status: executedComparison?.status || "NOT_APPLICABLE",
      cross_stage_candidate_count: executedComparison?.suggestions?.length ?? 0,
    };
  }
  if (executedComparison) {
    return {
      execution_status: executedComparison.status === "RESOURCE_MISSING" ? "FAILED" : "EXECUTED",
      direct_path_status: directStep?.status || "SKIPPED",
      cross_stage_status: executedComparison.status,
      suggestion_count: executedComparison.suggestions?.length ?? 0,
      duration_ms: null,
      note: "Cross-stage WordNet work is included in Rule Base timing; its individual duration is not instrumented.",
    };
  }
  return {
    execution_status: directStep?.execution_status || "NOT_APPLICABLE",
    direct_path_status: directStep?.status || "Not available",
    cross_stage_status: "NOT_APPLICABLE",
    duration_ms: directStep?.duration_ms,
  };
}

function renderProcessStatus(item, status) {
  processStatus.replaceChildren();
  appendStatusChip(processStatus, status.execution_status || "NOT_INSTRUMENTED", item.workflow === "separate_workflow" ? "separate workflow" : "");
  if (status.duration_ms !== undefined && status.duration_ms !== null) {
    appendStatusChip(processStatus, "TIMED", `${Number(status.duration_ms).toFixed(3)} ms`);
  } else if (item.workflow !== "separate_workflow") {
    appendStatusChip(processStatus, "NOT_INSTRUMENTED", "duration unavailable");
  }
  if (status.direct_path_status) appendStatusChip(processStatus, status.direct_path_status, "direct WordNet path");
  if (status.cross_stage_status) appendStatusChip(processStatus, status.cross_stage_status, "cross-stage WordNet path");
  if (status.cross_stage_candidate_count !== undefined) appendStatusChip(processStatus, "CANDIDATES", String(status.cross_stage_candidate_count));
  if (status.suggestion_count !== undefined) appendStatusChip(processStatus, "CANDIDATES", String(status.suggestion_count));
  if (status.note) appendText(processStatus, status.note, "field-help");
}

function renderProcess() {
  const processes = state.metadata?.processes || [];
  const item = processes[state.activeProcess];
  if (!item) return;
  document.getElementById("previous-process").disabled = state.activeProcess === 0;
  document.getElementById("next-process").disabled = state.activeProcess === processes.length - 1;
  detailNumber.textContent = `${item.id} — ${item.title.toUpperCase()}`;
  detailTitle.textContent = item.title;
  const status = processStatusFor(item.id);
  renderProcessStatus(item, status);
  processContent.replaceChildren();
  const sections = item.sections || {};
  for (const [label, explanation] of Object.entries(sections)) {
    const section = sectionHeading(processContent, label);
    if (typeof explanation === "string") appendText(section, explanation);
    else if (explanation && typeof explanation === "object") {
      if (explanation.simple) appendText(section, explanation.simple, "research-simple-note");
      if (explanation.technical) appendText(section, explanation.technical, "research-technical-note");
      for (const [key, value] of Object.entries(explanation)) {
        if (key === "simple" || key === "technical") continue;
        if (Array.isArray(value)) value.forEach((entry) => appendText(section, entry));
        else appendText(section, value);
      }
    }
    if (label === "D. Actual input") renderActualInput(section, item.id);
    if (label === "E. Actual output") renderActualOutput(section, item.id);
    if (label === "F. What decision was made?") renderActualDecision(section, item.id);
    if (label === "G. Implementation / source code") renderSourceDetails(section, item.id);
    if (label === "H. Reference / theoretical basis") renderReferences(section, item.id);
    if (label === "J. What happens next?") renderNextStatus(section, item.id);
  }
  if (item.id === "00") renderPipelineDiagram(processContent);
  if (item.id === "10") renderEvaluation(processContent);
  if (item.id === "11") renderGlossary(processContent);
}

function renderActualInput(parent, processId) {
  const payload = currentInputSummary();
  const trace = state.response?.research_trace;
  const stageTrace = getStageTrace();
  let data = payload;
  if (processId === "01") {
    data = {
      http_method: "POST",
      endpoint: "/api/research-inspector/analyze",
      content_type: "application/json",
      csrf_header: "X-CSRF-Token present; token value is intentionally not exposed in the trace.",
      authenticated_role: "TEACHER (required by the route authorization list)",
      accepted_payload_shape: "stage_id, assignment_topic, focus_terms, selected stage text, optional prior Introduction/Body context",
      sanitized_values: payload,
      assignment_id_session_id_user_id: "Rejected by inspector endpoint; not included.",
      input_limits: { topic_characters: 500, introduction_characters: 12000, body_characters: 30000, conclusion_characters: 12000, focus_term_count: 20, focus_term_characters: 120, request_bytes: 262144 },
      rejection_classes: ["400 invalid JSON/type/stage/CSRF/input", "401 not authenticated", "403 wrong role", "413 request body too large", "500 analyzer failure"],
    };
  } else if (processId === "02" || processId === "03" || processId === "04" || processId === "05") {
    data = {
      selected_stage: stageSelect.value,
      assignment_topic: topicInput.value,
      focus_terms: state.response?.research_trace?.teacher_context?.focus_terms || payload.focus_terms,
      stage_texts_supplied: stageTrace?.input_sections || {},
    };
  } else if (processId === "06") {
    data = { stage: stageSelect.value, existing_analysis_fields: Object.keys(getAnalysis() || {}), rule_count: getAnalysis()?.rule_evidence?.length ?? 0 };
  } else if (processId === "07") {
    data = { selected_stage: stageSelect.value, emitted_rule_ids: (getAnalysis()?.rule_evidence || []).map((event) => event.rule_id) };
  } else if (processId === "08") {
    data = state.response ? { response_keys: Object.keys(state.response), stage_id: state.response.stage_id, availability: state.response.availability } : payload;
  } else if (processId === "09") {
    data = { execution_status: "NOT_APPLICABLE_TO_ANALYSIS", note: "No draft/session/submission ID is sent by this custom-sample inspector." };
  } else if (processId === "10") {
    data = state.metadata?.evaluation || { status: "pending" };
  } else if (processId === "11") {
    data = { trace_version: trace?.trace_version || "not available", selected_stage: trace?.selected_stage || "not analyzed" };
  }
  parent.appendChild(safeJson(data));
}

function renderActualOutput(parent, processId) {
  const analysis = getAnalysis();
  if (!analysis) {
    appendText(parent, "No analysis output yet. Run Analyze Sample to populate this process from the actual implementation.", "empty-state");
    return;
  }
  if (processId === "00") {
    appendText(parent, "The selected-stage response and recorded stage trace are available below and in Raw Analysis Trace.");
  } else if (processId === "01") {
    const trace = state.response.research_trace || {};
    const data = {
      stage_id: state.response.stage_id,
      topic: topicInput.value,
      focus_terms: trace.teacher_context?.focus_terms || [],
      focus_source: trace.teacher_context?.focus_source,
      prior_context_supplied: Object.keys(getStageTrace()?.input_sections || {}).filter((key) => key !== stageSelect.value.toLowerCase()),
      request_validation_and_assignment_resolution_ms: trace.request_validation_and_assignment_resolution_ms,
      analysis_service_lookup_ms: trace.analysis_service_lookup_ms,
      analysis_service_initialization: trace.runtime?.analysis_service_initialization,
      teacher_context_preparation_ms: trace.teacher_context_preparation_ms,
      teacher_context_call_frequency: trace.teacher_context_call_frequency,
      authentication_and_csrf_timing: trace.api_authentication_and_csrf_timing,
    };
    parent.appendChild(safeJson(data));
  } else if (processId === "02") {
    renderNlpOutput(parent);
  } else if (processId === "03") {
    renderConceptTable(parent);
  } else if (processId === "04") {
    renderTopicTable(parent);
  } else if (processId === "05") {
    renderWordnetOutput(parent);
  } else if (processId === "06") {
    renderRuleTable(parent);
  } else if (processId === "07") {
    renderFeedbackOutput(parent);
  } else if (processId === "08") {
    const responseInfo = {
      stage_id: state.response.stage_id,
      availability: state.response.availability,
      response_keys: Object.keys(state.response),
      interpretation_limit: state.response.interpretation_limit,
      client_fetch_round_trip_ms: state.requestMs === null ? "not measured" : Number(state.requestMs.toFixed(3)),
      client_render_ms: state.renderMs === null ? "not measured" : Number(state.renderMs.toFixed(3)),
    };
    parent.appendChild(safeJson(responseInfo));
  } else if (processId === "09") {
    appendText(parent, "Source-defined persistence schema. The analysis itself does not read student writing or assignment rows; Flask authentication performs a lookup of the currently signed-in user record.");
    const table = makeTable(parent, ["Table", "Purpose / ownership", "NLP request relationship"], "Schema description unavailable.");
    for (const row of [
      ["users", "Account role and credential hash", "Authentication middleware reads the current account; no credential/hash is returned."],
      ["classrooms", "Teacher-owned class context", "Not read by the custom-sample analysis endpoint."],
      ["assignments", "Teacher-owned topic/focus/instructions; optional classroom; soft-delete timestamp", "Normal student analysis resolves only an enrolled active assignment. Inspector custom samples reject assignment IDs."],
      ["classroom_enrollments", "Student/classroom membership", "Used by assignment access and workspace routes, not by custom inspector analysis."],
      ["writing_sessions", "Owner/assignment link and current three-section draft", "Analyze does not save; custom inspector does not reference a session."],
      ["writing_revisions", "Immutable numbered draft snapshots", "Separate Save Revision route."],
      ["submissions", "Final snapshots, unique per student/assignment", "Separate Submit route; submission checks saved version and non-empty sections, not analysis quality."],
    ]) addTableRow(table, row);
    appendText(parent, "Observed test result: custom Inspector request leaves writing_sessions, writing_revisions, and submissions unchanged. Authentication reads only the signed-in account record. Teacher Progress Tracking is a separate query workflow.");
  } else if (processId === "10") {
    appendText(parent, state.metadata?.evaluation?.message || "Evaluation pending — No verified human-labeled dataset available.");
  } else if (processId === "11") {
    appendText(parent, "The raw current response is available in the expandable Raw Analysis Trace section below. Export is generated in browser memory and is not uploaded or persisted.");
  }
}

function renderNlpOutput(parent) {
  const linguistic = getLinguistic();
  if (!linguistic) {
    appendText(parent, "Linguistic observations were not returned for this stage.");
    return;
  }
  appendText(parent, "spaCy's tokenizer creates Doc/Token objects. EssayScaff reports non-space tokens, sentence spans, and zero-based end-exclusive offsets. Fine/coarse tags and dependencies are parser/model annotations.");
  const counts = linguistic.counts || {};
  parent.appendChild(safeJson({ counts, sentence_count: linguistic.sentences?.length ?? 0, noun_phrase_count: linguistic.noun_phrases?.length ?? 0 }));
  const tokens = linguistic.tokens || (linguistic.sentences || []).flatMap((sentence) => sentence.tokens || []);
  const table = makeTable(parent, ["Token index", "Original token", "Lemma", "POS", "Tag", "Dependency", "Head", "Start", "End", "Alphabetic"], "No tokens were returned.");
  for (const token of tokens) {
    addTableRow(table, [
      token.index,
      token.text,
      token.lemma,
      glossaryCell(token.pos),
      glossaryCell(token.tag),
      glossaryCell(token.dependency),
      token.head,
      token.start,
      token.end,
      token.is_alpha,
    ]);
  }
  const sentences = linguistic.sentences || [];
  const sentenceTable = makeTable(parent, ["Sentence", "Start", "End", "Subjects", "Objects/complements"], "No sentence records were returned.");
  for (const sentence of sentences) {
    addTableRow(sentenceTable, [
      sentence.text,
      sentence.start,
      sentence.end,
      (sentence.subjects || []).map((item) => `${item.text} (${item.dependency})`).join(", "),
      (sentence.objects_or_complements || []).map((item) => `${item.text} (${item.dependency})`).join(", "),
    ]);
  }
  const nounTable = makeTable(parent, ["Noun phrase", "Start", "End", "Source slice verified"], "No noun phrases were returned.");
  for (const phrase of linguistic.noun_phrases || []) {
    const sourceText = getStageTrace()?.input_sections?.[stageSelect.value.toLowerCase()] || "";
    addTableRow(nounTable, [phrase.text, phrase.start, phrase.end, sourceText.slice(phrase.start, phrase.end) === phrase.text]);
  }
  const dependencyTable = makeTable(parent, ["Dependent token", "Relation", "Head", "Character span"], "No dependency records were returned.");
  for (const sentence of sentences) {
    for (const dep of sentence.dependencies || []) {
      addTableRow(dependencyTable, [dep.text, glossaryCell(dep.dependency), dep.head, `${dep.start}–${dep.end}`]);
    }
  }
  renderDependencyView(parent, linguistic.sentences || []);
  appendText(parent, "spaCy pipeline components that executed: " + ((state.metadata?.runtime?.pipeline?.enabled_components || getStageTrace()?.topic_service?.steps?.[0]?.pipeline_components || []).join(" → ") || "runtime metadata unavailable") + ". Tokenizer runs before the named components and is not listed in nlp.pipe_names. EssayScaff consumes POS/tag, lemma, parser dependency/head, sentence boundaries, and noun chunks. NER runs but its entities are not consumed by the active Rule Bases.");
}

function renderDependencyView(parent, sentences) {
  const section = sectionHeading(parent, "Dependency relationship view");
  appendText(section, "Each row is a parser edge from the dependent token to its predicted head. Head offsets use the parser's actual head_start value, avoiding ambiguity when the same token text appears more than once.");
  const view = node("div", undefined, "research-dependency-view");
  for (const sentence of sentences) {
    const sentenceTokens = sentence.tokens || [];
    for (const dependency of sentence.dependencies || []) {
      const dependent = sentenceTokens.find((token) => token.start === dependency.start);
      const head = sentenceTokens.find((token) => token.start === dependency.head_start);
      const row = node("div", undefined, "dependency-edge");
      row.append(node("span", `${dependency.text} [${dependency.start},${dependency.end})`, "dependency-node"));
      row.append(node("span", `— ${dependency.dependency || "?"} →`, "dependency-relation"));
      row.append(node("span", head ? `${head.text} [${head.start},${head.end})` : `${valueOr(dependency.head)} [offset ${valueOr(dependency.head_start)}]`, "dependency-node"));
      row.title = dependent?.index === undefined ? "Parser dependency edge." : `Dependent token index ${dependent.index}.`;
      view.appendChild(row);
    }
  }
  section.appendChild(view);
}

function renderConceptTable(parent) {
  const concepts = getStageTrace()?.topic_service?.steps?.find((step) => step.id === "concept_extraction")?.output || [];
  const table = makeTable(parent, ["Original phrase", "Normalized concept", "Extraction method", "POS", "Occurrence span", "Source token indices", "Occurrences", "Observed downstream use"], "No candidate concepts were returned by TopicService.");
  for (const concept of concepts) {
    for (const occurrence of concept.occurrences || []) {
      addTableRow(table, [
        occurrence.text,
        concept.normalized_form,
        occurrence.extraction_method,
        (occurrence.pos || []).join(", "),
        `${occurrence.start}–${occurrence.end}`,
        (occurrence.source_token_indices || []).join(", "),
        concept.occurrence_count,
        conceptDownstreamUsage(concept.normalized_form) || "No downstream use was observed in the selected stage's returned fields; concept remains a candidate.",
      ]);
    }
  }
  appendText(parent, "Every concept row is a returned candidate. EssayScaff does not compute a concept relevance score or rank concepts by importance. Stage rules consume candidates only where their existing conditions use them.");
}

function conceptDownstreamUsage(normalizedForm) {
  const analysis = getAnalysis() || {};
  const usages = [];
  if (stageSelect.value === "INTRODUCTION") {
    return "Returned for transparency; Introduction Rule Base does not consume concept candidates, and direct WordNet suggestions are disabled for this stage.";
  }
  if (stageSelect.value === "BODY") {
    for (const paragraph of analysis.paragraphs || []) {
      if ((paragraph.paragraph_focus_candidates || []).some((concept) => concept.normalized_form === normalizedForm)) usages.push(`Paragraph ${paragraph.paragraph_index} paragraph_focus_candidates`);
      if ((paragraph.prominent_concept_candidates || []).some((concept) => concept.normalized_form === normalizedForm)) usages.push(`Paragraph ${paragraph.paragraph_index} prominent_concept_candidates`);
    }
    const continuity = analysis.introduction_to_body_continuity || {};
    if (hasNormalizedConcept(continuity, normalizedForm)) usages.push("Introduction–Body lexical comparison");
  } else {
    if (hasNormalizedConcept(analysis.synthesis_structure_candidates || {}, normalizedForm)) usages.push("Conclusion synthesis candidate evidence");
    if (hasNormalizedConcept(analysis.new_material_observations || {}, normalizedForm)) usages.push("Conclusion new-material lexical comparison");
    if (hasNormalizedConcept(analysis.introduction_to_conclusion_continuity || {}, normalizedForm)
      || hasNormalizedConcept(analysis.body_to_conclusion_continuity || {}, normalizedForm)) usages.push("Cross-stage continuity comparison");
  }
  return [...new Set(usages)].join("; ");
}

function hasNormalizedConcept(value, expected) {
  if (Array.isArray(value)) return value.some((item) => hasNormalizedConcept(item, expected));
  if (!value || typeof value !== "object") return false;
  if (value.normalized_form === expected) return true;
  return Object.values(value).some((item) => hasNormalizedConcept(item, expected));
}

function renderTopicTable(parent) {
  const lexical = getAnalysis()?.lexical_topic_evidence || {};
  const focusTerms = lexical.focus_terms || state.response?.research_trace?.teacher_context?.focus_terms?.map((item) => item.term) || [];
  const matches = lexical.matches || [];
  const table = makeTable(parent, ["Configured term", "Normalized form", "Observed?", "Match method", "Matched text", "Span", "POS", "Related evidence"], "No configured terms are available.");
  for (const term of focusTerms) {
    const termMatches = matches.filter((match) => match.focus_term === term);
    const traceSpec = state.response?.research_trace?.teacher_context?.focus_terms?.find((item) => item.term === term);
    if (!termMatches.length) {
      const noMatchRules = (getAnalysis()?.rule_evidence || []).filter((event) => event.rule_id.includes("NO_FOCUS_MATCH")).map((event) => event.rule_id);
      addTableRow(table, [term, traceSpec?.normalized_form || "Not available", "No lexical match observed", "—", "—", "—", "—", noMatchRules.join(", ") || "No individual no-match Rule Event was emitted for this one unmatched term."]);
      continue;
    }
    for (const match of termMatches) {
      addTableRow(table, [term, match.normalized_form, "Yes", match.match_method, match.observed_text, `[${match.start}, ${match.end})`, (match.pos || []).join(", "), relatedTopicRuleIds(term, match).join(", ") || "No matching Rule Event reference was emitted"]);
    }
  }
  const focusSource = lexical.focus_source || state.response?.research_trace?.teacher_context?.focus_source;
  appendText(parent, `Focus source: ${valueOr(focusSource)}. Direct matching compares case-folded surfaces; normalized matching compares lemma sequences. Both remain lexical evidence, not semantic relevance.`);
}

function relatedTopicRuleIds(term, match) {
  const rules = [];
  const containsMatch = (value) => {
    if (Array.isArray(value)) return value.some(containsMatch);
    if (!value || typeof value !== "object") return false;
    if (value.focus_term === term && value.start === match.start && value.end === match.end) return true;
    return Object.values(value).some(containsMatch);
  };
  for (const event of getAnalysis()?.rule_evidence || []) {
    const evidence = event.actual_evidence ?? event.evidence;
    if (containsMatch(evidence)) rules.push(event.rule_id);
  }
  return [...new Set(rules)];
}

function renderWordnetOutput(parent) {
  const topicTrace = getStageTrace()?.topic_service?.steps?.find((step) => step.id === "wordnet_direct_suggestions");
  const crossStageInputs = getStageTrace()?.cross_stage_comparison_inputs || {};
  const analysis = getAnalysis() || {};
  const stage = stageSelect.value;
  const records = [];
  if (topicTrace) records.push({ path: "TopicService direct focus suggestions", ...topicTrace });
  if (stage === "BODY") {
    const comparison = analysis.introduction_to_body_continuity?.wordnet_relationship_candidates;
    if (comparison) records.push({ path: "Introduction–Body cross-stage", execution_status: comparison.status === "RESOURCE_MISSING" ? "FAILED" : "EXECUTED", ...comparison });
  }
  if (stage === "CONCLUSION") {
    const introComparison = analysis.introduction_to_conclusion_continuity?.wordnet_relationship_candidates;
    const bodyComparison = analysis.body_to_conclusion_continuity?.wordnet_relationship_candidates;
    if (introComparison) records.push({ path: "Introduction–Conclusion cross-stage", execution_status: introComparison.status === "RESOURCE_MISSING" ? "FAILED" : "EXECUTED", ...introComparison });
    if (bodyComparison) records.push({ path: "Body–Conclusion cross-stage", execution_status: bodyComparison.status === "RESOURCE_MISSING" ? "FAILED" : "EXECUTED", ...bodyComparison });
  }
  if (!records.length) {
    appendText(parent, stage === "INTRODUCTION" ? "Not executed — direct WordNet suggestions are disabled for this Introduction analysis. No prior-stage comparison is part of the Introduction Rule Base." : "WordNet execution status was not included in the returned trace.");
    return;
  }
  if (topicTrace) {
    const directInputs = node("details");
    directInputs.appendChild(node("summary", "Direct WordNet path inputs and focus configuration"));
    directInputs.appendChild(safeJson({ input: getStageTrace()?.topic_service?.input, candidate_concepts: getStageTrace()?.topic_service?.steps?.find((step) => step.id === "concept_extraction")?.output || [] }));
    parent.appendChild(directInputs);
  }
  if (Object.keys(crossStageInputs).length) {
    const crossInputs = node("details");
    crossInputs.appendChild(node("summary", "Actual extracted concepts passed to cross-stage comparison"));
    crossInputs.appendChild(safeJson(crossStageInputs));
    parent.appendChild(crossInputs);
  }
  const table = makeTable(parent, ["Path", "Execution/status", "WordNet version", "Candidate count", "Measured duration", "Evidence/output"], "No WordNet path details were returned.");
  for (const record of records) {
    const candidateList = record.output || record.suggestions || [];
    addTableRow(table, [record.path, record.execution_status || record.status, record.wordnet_version || "Not available / not executed", candidateList.length ?? record.suggestion_count ?? 0, record.duration_ms === undefined ? "Not individually instrumented" : `${record.duration_ms} ms`, JSON.stringify(candidateList)]);
    if (record.lookup_pairs?.length) {
      const lookupDetails = node("details");
      lookupDetails.appendChild(node("summary", `${record.path}: ${record.lookup_pairs.length} actual WordNet lookup-pair record(s)`));
      lookupDetails.appendChild(safeJson({ resource_probe: record.resource_probe, lookup_pairs: record.lookup_pairs }));
      parent.appendChild(lookupDetails);
    } else if (record.lookup_pairs && record.execution_status === "FAILED") {
      appendText(parent, `${record.path}: WordNet resource lookup failed; no candidate-pair lookups were made. Resource probe: ${valueOr(record.resource_probe, "not recorded")}.`, "field-help");
    } else if (record.lookup_pairs && record.execution_status === "SKIPPED") {
      appendText(parent, `${record.path}: WordNet candidate lookup was skipped by stage configuration; this is distinct from an executed lookup with zero candidates.`, "field-help");
    } else if (record.lookup_pairs) {
      appendText(parent, `${record.path}: no eligible WordNet word-pair lookup records were made; resource probe: ${valueOr(record.resource_probe, "not recorded")}.`, "field-help");
    }
  }
  appendText(parent, "The direct Introduction path can be skipped while a Body/Conclusion comparison independently calls the shared-synset helper. The inspector keeps those paths separate. A WordNet candidate is not contextual sense disambiguation.");
}

function renderRuleTable(parent) {
  const analysis = getAnalysis() || {};
  const decisions = analysis.rule_evaluation_trace || [];
  const emittedEvents = new Map((analysis.rule_evidence || []).map((event) => [event.rule_id, event]));
  if (!decisions.length) {
    appendText(parent, "No rule evaluation trace was returned.");
    return;
  }
  const stageDetails = stageSelect.value === "INTRODUCTION"
    ? {
        text_presence: analysis.text_presence,
        observable_structure: analysis.observable_structure,
        central_direction_candidate: analysis.central_direction_candidate,
        development_evidence: analysis.development_evidence,
        missing_observable_elements: analysis.missing_observable_elements,
      }
    : stageSelect.value === "BODY"
      ? {
          paragraph_boundary_policy: analysis.paragraph_boundary_policy,
          paragraph_observations_without_separate_events: (analysis.paragraphs || []).map((paragraph) => ({
            paragraph_index: paragraph.paragraph_index,
            counts: paragraph.counts,
            fragment_or_list_candidate: paragraph.fragment_or_list_candidate,
            prominent_concept_candidates: paragraph.prominent_concept_candidates,
            paragraph_missing_observable_elements: paragraph.missing_observable_elements,
          })),
          cross_paragraph_continuity: analysis.cross_paragraph_continuity,
          introduction_to_body_continuity: analysis.introduction_to_body_continuity,
          missing_observable_elements: analysis.missing_observable_elements,
        }
      : {
          text_presence: analysis.text_presence,
          keyword_list_candidate: analysis.keyword_list_candidate,
          clause_candidates: analysis.clause_candidates,
          introduction_to_conclusion_continuity: analysis.introduction_to_conclusion_continuity,
          body_to_conclusion_continuity: analysis.body_to_conclusion_continuity,
          synthesis_structure_candidates: analysis.synthesis_structure_candidates,
          closure_candidates: analysis.closure_candidates,
          new_material_observations: analysis.new_material_observations,
          repetition_observations: analysis.repetition_observations,
          missing_observable_elements: analysis.missing_observable_elements,
        };
  const detailRecord = node("details");
  detailRecord.appendChild(node("summary", "Returned stage evidence not represented by a separate Rule Event"));
  detailRecord.appendChild(safeJson(stageDetails));
  parent.appendChild(detailRecord);
  const controls = node("div", undefined, "research-rule-controls");
  const filter = node("select");
  for (const status of ["ALL", "TRIGGERED", "EVALUATED_NOT_TRIGGERED", "NOT_APPLICABLE", "NOT_RECORDED", "FAILED"]) {
    const option = node("option", status);
    option.value = status;
    filter.appendChild(option);
  }
  const search = node("input");
  search.type = "search";
  search.placeholder = "Filter by Rule ID or name";
  search.setAttribute("aria-label", "Filter rules by ID or name");
  controls.append(filter, search);
  parent.appendChild(controls);
  const cards = node("div", undefined, "research-rule-list");
  parent.appendChild(cards);
  const render = () => {
    cards.replaceChildren();
    const selectedStatus = filter.value;
    const query = search.value.trim().toLowerCase();
    const visible = decisions.filter((decision) =>
      (selectedStatus === "ALL" || decision.status === selectedStatus)
      && (!query || `${decision.rule_id} ${decision.name}`.toLowerCase().includes(query))
    );
    if (!visible.length) appendText(cards, "No rule records match this filter.");
    for (const decision of visible) renderRuleCard(cards, decision, emittedEvents.get(decision.rule_id));
  };
  filter.addEventListener("change", render);
  search.addEventListener("input", render);
  render();
}

function renderRuleCard(parent, decision, emittedEvent) {
  const card = node("article", undefined, "research-rule-card");
  card.dataset.status = decision.status;
  const title = node("h4", `${decision.rule_id} — ${decision.name}`);
  card.appendChild(title);
  appendText(card, `Stage: ${decision.stage} | Status: ${decision.status}`);
  appendText(card, `Exact condition: ${decision.condition}`);
  appendText(card, `What it checks: ${decision.purpose}`);
  appendText(card, `Decision basis: ${decision.decision_basis}`);
  appendText(card, `Educational rationale: ${decision.educational_rationale}`);
  appendText(card, `Evidence requirement: ${decision.required_evidence}`);
  appendText(card, `Configuration: ${decision.configuration}`);
  appendText(card, `Limitation: ${decision.interpretation_limit}`);
  const source = decision.implementation || {};
  appendText(card, `Source: ${source.file || "not resolved"}${source.class ? ` · ${source.class}` : ""}.${source.function || ""}${source.start_line ? `, lines ${source.start_line}–${source.end_line}` : ""}`, "research-source-ref");
  const relatedReferences = (state.metadata?.references || []).filter((reference) => (decision.reference_ids || []).includes(reference.id));
  if (!relatedReferences.length) appendText(card, "Reference status: no direct external validation source is mapped to this exact condition; see References for general technical/educational context.", "field-help");
  for (const reference of relatedReferences) {
    const refDetails = node("details");
    refDetails.appendChild(node("summary", `Reference: ${reference.author} (${reference.year}) — ${reference.title}`));
    appendText(refDetails, `Supports: ${reference.supports}`);
    appendText(refDetails, `Does not prove: ${reference.does_not_prove}`);
    const href = reference.url;
    if (href) {
      const link = node("a", href);
      link.href = href;
      link.target = "_blank";
      link.rel = "noopener noreferrer";
      refDetails.appendChild(link);
    }
    card.appendChild(refDetails);
  }
  const event = emittedEvent;
  if (event) {
    const detail = node("details");
    detail.appendChild(node("summary", "Actual emitted event and evidence"));
    detail.appendChild(safeJson(event));
    card.appendChild(detail);
  } else {
    appendText(card, "No event is attached. The status above is only set to an evaluated result when an existing analysis output exposes that condition; otherwise it remains NOT_RECORDED.", "field-help");
  }
  parent.appendChild(card);
}

function renderFeedbackOutput(parent) {
  const feedback = state.response?.feedback;
  if (!feedback) {
    appendText(parent, "Feedback is not available until analysis completes.");
    return;
  }
  const fields = ["Current Goal", "Primary Feedback", "What's Working", "Needs Attention", "Next Step"];
  const provenance = feedback["Feedback Provenance"] || [];
  const chain = node("div", undefined, "research-feedback-chain");
  for (const field of fields) {
    const box = node("article", undefined, "research-chain-step");
    box.appendChild(node("h4", field));
    const value = feedback[field];
    if (Array.isArray(value)) {
      if (!value.length) appendText(box, "No item recorded by this feedback field.");
      for (const item of value) appendText(box, item);
    } else appendText(box, valueOr(value));
    const evidence = provenance.filter((item) => item.feedback_field === field);
    if (!evidence.length) appendText(box, "No rule provenance item is recorded for this field.", "field-help");
    for (const item of evidence) {
      const detail = node("details");
      detail.appendChild(node("summary", `${item.rule_id} — triggering condition and source evidence`));
      detail.appendChild(safeJson(item));
      box.appendChild(detail);
    }
    chain.appendChild(box);
    if (field !== "Next Step") chain.appendChild(node("div", "↓", "research-chain-arrow"));
  }
  parent.appendChild(chain);
  const decisionTrace = getStageTrace()?.feedback_decisions;
  const instructional = decisionTrace?.instructional_feedback;
  if (instructional) {
    const section = sectionHeading(parent, "6+1 instructional feedback — actual selected mapping");
    section.dataset.sixTraitTrace = "true";
    appendText(section, `Framework: ${instructional.framework}. Limited observations and instructional categories are not seven completed trait assessments; highlights are evidence locations, not automatically errors.`);
    if (instructional.stage === "BODY") {
      appendText(section, `Actual Body selection status: ${instructional.selection_status}. ${instructional.neutral_result ? "No trait, skill, lesson, correction task or error highlight is assigned. This is not a passing grade." : "A supported recorded concern selects the prepared instructional focus below."}`);
      appendText(section, `Recorded backend Primary Feedback: ${instructional.student_message}`);
      const prepared = instructional.neutral_result || instructional.items?.[0]?.prepared_guidance;
      if (prepared) {
        const tutor = makeTable(section, ["Student tutor section", "Actual recorded tutor wording"]);
        addTableRow(tutor, ["What I noticed", prepared.noticed]);
        if (prepared.working) addTableRow(tutor, ["What's working", prepared.working]);
        if (!instructional.neutral_result) {
          addTableRow(tutor, ["Why it matters", prepared.why]);
          addTableRow(tutor, ["How to improve", prepared.task]);
        }
      }
      for (const strength of instructional.strengths || []) appendText(section, `What's working — recorded observation: ${strength.text}`);
      const recorded = node("details");
      recorded.appendChild(node("summary", "Actual Body selection checks, strength evidence, paragraph/sentence observations and compared Introduction"));
      recorded.appendChild(safeJson({ selection_checks: instructional.selection_checks, strengths: instructional.strengths,
        observed_paragraphs: instructional.observed_paragraphs, introduction_context: instructional.introduction_context,
        neutral_result: instructional.neutral_result }));
      section.appendChild(recorded);
    }
    if (instructional.stage === "BODY" && instructional.neutral_result) appendText(section, "No trait, skill or lesson is assigned — NO_SUPPORTED_CONCERN_SELECTED.");
    const table = makeTable(section, ["Feedback item", "Trait / skill", "Lesson / actual catalog", "FeedbackService branch", "Purpose"]);
    for (const item of instructional.items) {
      addTableRow(table, [item.feedback_field, `${item.trait || "No trait"} · ${item.skill || "No skill"}`,
        item.catalog_reference ? `${item.catalog_reference.file} · v${item.catalog_reference.version} · ${item.lesson_id}` : "No prepared mapping",
        item.selection_branch, item.feedback_purpose]);
      const detail = node("details");
      detail.appendChild(node("summary", `${item.feedback_field} — actual condition, evidence, strengths and highlight provenance`));
      appendText(detail, `Selection condition: ${item.selection_condition || "Not recorded"}`);
      appendText(detail, `Triggered Rule IDs: ${item.triggered_rule_ids.join(", ")}. Mapping basis: ${item.mapping_basis}`);
      const spans = makeTable(detail, ["Start", "End", "Original highlighted text", "Supporting rule", "Why this passage"]);
      for (const span of item.highlight_spans) addTableRow(spans, [span.start, span.end, span.text, span.rule_id, span.selection_reason]);
      detail.appendChild(safeJson({ observed_fields: item.observed_fields, rule_conditions: item.rule_conditions,
        prepared_guidance: item.prepared_guidance, highlight_provenance: item.highlight_spans,
        supporting_events: (getAnalysis()?.rule_evidence || []).filter(e => item.rule_ids.includes(e.rule_id)) }));
      section.appendChild(detail);
    }
    const coverage = makeTable(section, ["Framework trait", "Scope", "Status", "Selected instructional category", "Trait-quality assessment"]);
    for (const row of instructional.coverage) addTableRow(coverage, [row.trait, row.scope, row.status, row.instructional_category_selected, row.trait_quality_assessment]);
    for (const limitation of instructional.limitations) appendText(section, limitation, "field-help");
  }
  if (decisionTrace) {
    const decisionSection = sectionHeading(parent, "Recorded FeedbackService branch decisions");
    const decisions = makeTable(decisionSection, ["Feedback field", "Selected branch", "Selection condition", "Supporting rule IDs", "Selected output"], "No feedback decisions were recorded.");
    for (const [field, choice] of Object.entries(decisionTrace.fields || {})) {
      addTableRow(decisions, [field, choice.selection_branch, choice.selection_condition || "Not recorded for this field", (choice.rule_ids || []).join(", "), choice.selected_message || `${choice.selected_message_count ?? 0} item(s)`]);
    }
    if (decisionTrace.priority_order) appendText(decisionSection, `Implemented Primary Feedback priority: ${decisionTrace.priority_order.join(" → ")}`);
    if (decisionTrace.unselected_alternatives) appendText(decisionSection, decisionTrace.unselected_alternatives);
  } else {
    appendText(parent, "FeedbackService branch timing/selection labels were not recorded for this response.");
  }
  appendText(parent, `Feedback limitation: ${valueOr(feedback.interpretation_limit)}`);
}

function renderActualDecision(parent, processId) {
  const analysis = getAnalysis();
  if (!analysis) {
    appendText(parent, "No decision can be reported before an actual analysis is returned.");
    return;
  }
  if (processId === "02") {
    appendText(parent, "spaCy produced the displayed labels. The application consumes only the attributes listed in the process explanation; no semantic-validity decision is made.");
  } else if (processId === "03") {
    appendText(parent, "Concept grouping is by normalized lemma form. The trace reports extraction method and spans; no confidence or relevance decision exists.");
  } else if (processId === "04") {
    appendText(parent, `Observed focus terms: ${(analysis.lexical_topic_evidence?.observed_focus_terms || []).join(", ") || "none"}. This is lexical coverage only.`);
  } else if (processId === "05") {
    renderWordnetOutput(parent);
  } else if (processId === "06") {
    appendText(parent, "Rule statuses come from emitted events or explicit fields returned by the existing stage analysis. Other absent branches remain NOT_RECORDED rather than being treated as negative.");
  } else if (processId === "07") {
    appendText(parent, `The displayed Primary Feedback is: ${state.response.feedback["Primary Feedback"]}`);
  } else if (processId === "09") {
    appendText(parent, "No draft, revision, or submission decision was made by Analyze Sample. This inspector endpoint rejects assignment/session/user IDs and performs no DraftStore writes.");
  } else if (processId === "10") {
    appendText(parent, state.metadata?.evaluation?.message || "Evaluation pending — No verified human-labeled dataset available.");
  }
}

function renderSourceDetails(parent, processId) {
  const locations = state.metadata?.process_source_locations?.[processId] || [];
  if (locations.length) {
    const table = makeTable(parent, ["File", "Symbol", "Source line"], "No source locations resolved.");
    for (const location of locations) {
      addTableRow(table, [location.file, location.symbol, location.start_line || location.line_status || "Not resolved"]);
    }
  }
  if (processId === "06") {
    const trace = getAnalysis()?.rule_evaluation_trace || [];
    const files = [...new Set(trace.map((item) => item.implementation?.file).filter(Boolean))];
    appendText(parent, `Current stage source files: ${files.join(", ") || "not resolved"}. Each rule card includes the resolved class/function and line range when available.`);
  } else if (processId === "07") {
    appendText(parent, "services/feedback_service.py — FeedbackService.generate, generate_body, generate_conclusion. The coordinator calls only the selected stage's existing feedback generator for each supplied section.");
  } else if (processId === "02") {
    appendText(parent, "services/nlp_service.py — NLPService.__init__, parse, analyze_doc, _token_data. services/topic_service.py — TopicService.analyze and _extract_concepts. Runtime metadata comes from the already-loaded NLPService.");
  }
}

function renderReferences(parent, processId) {
  const references = state.metadata?.references || [];
  const ruleRefs = processId === "06"
    ? [...new Set((getAnalysis()?.rule_evaluation_trace || []).flatMap((item) => item.reference_ids || []))]
    : [];
  const list = node("div", undefined, "research-source-list");
  const relevant = ruleRefs.length ? references.filter((item) => ruleRefs.includes(item.id)) : references;
  for (const reference of relevant) {
    const entry = node("article", undefined, "research-rule-card");
    entry.appendChild(node("h4", `${reference.author} (${reference.year}) — ${reference.title}`));
    appendText(entry, reference.publication);
    appendText(entry, `Supports: ${reference.supports}`);
    appendText(entry, `Does not prove: ${reference.does_not_prove}`);
    const href = reference.url || (reference.doi ? `https://doi.org/${reference.doi}` : "");
    if (href) {
      const link = node("a", href);
      link.href = href;
      link.target = "_blank";
      link.rel = "noopener noreferrer";
      entry.appendChild(link);
    }
    list.appendChild(entry);
  }
  if (!relevant.length) appendText(parent, "No specific external source is recorded for this project-specific condition. See the full reference list in process 11.");
  else parent.appendChild(list);
}

function renderNextStatus(parent, processId) {
  if (!state.response) return;
  const next = ({
    "02": "Concept Extraction and Topic Matching consume the same parsed Doc.",
    "03": "Stage-specific rules use concepts for configured lexical comparisons and recurrence candidates.",
    "04": "The stage Rule Base uses matches and coverage; they do not establish semantic relevance.",
    "05": "WordNet suggestions remain candidates and may be attached to cross-stage Rule Evidence.",
    "06": "FeedbackService consumes stage findings and emitted rule events.",
    "07": "Flask returns JSON; the browser renders feedback and provenance.",
  })[processId];
  if (next) appendText(parent, next);
}

function renderPipelineDiagram(parent) {
  const section = sectionHeading(parent, "Interactive production dataflow");
  appendText(section, "The diagram reflects source execution. The tokenizer is part of spaCy's nlp(text) call, even though it is not listed in nlp.pipe_names. Storage and research evaluation are separate workflows.");
  const sequence = [
    ["Student or inspector sample input", "01"],
    ["Flask validation and access checks", "01"],
    ["Assignment/topic/focus context", "01"],
    ["spaCy Doc and linguistic observations", "02"],
    ["Concept extraction", "03"],
    ["Focus-term matching", "04"],
    ["Optional TopicService WordNet path (direct focus suggestions)", "05"],
    ["Stage Rule Base (Body/Conclusion may call cross-stage WordNet here)", "06"],
    ["FeedbackService", "07"],
    ["API JSON and browser rendering", "08"],
  ];
  const diagram = node("div", undefined, "research-pipeline-diagram");
  for (const [index, [label, processId]] of sequence.entries()) {
    const button = node("button", undefined, "research-pipeline-node");
    button.type = "button";
    button.append(node("span", `${String(index + 1).padStart(2, "0")} · ${label}`));
    button.addEventListener("click", () => selectProcess((state.metadata.processes || []).findIndex((item) => item.id === processId)));
    diagram.appendChild(button);
    if (index < sequence.length - 1) diagram.appendChild(node("span", "↓", "research-pipeline-arrow"));
  }
  section.appendChild(diagram);
  const separate = node("div", undefined, "research-separate-workflows");
  for (const processId of ["09", "10"]) {
    const item = state.metadata.processes.find((entry) => entry.id === processId);
    const button = node("button", `${item.id} · ${item.title}`, "button-secondary");
    button.type = "button";
    button.addEventListener("click", () => selectProcess(state.metadata.processes.indexOf(item)));
    separate.appendChild(button);
  }
  section.appendChild(node("h4", "Separate workflows — not executed as NLP steps"));
  section.appendChild(separate);
  const trace = state.response?.research_trace;
  if (trace) {
    const table = makeTable(section, ["Process", "Execution status", "Duration / evidence"], "No execution records.");
    for (const item of state.metadata.processes) {
      const stateRecord = processStatusFor(item.id);
      addTableRow(table, [`${item.id} ${item.title}`, stateRecord.execution_status, stateRecord.duration_ms === undefined || stateRecord.duration_ms === null ? "Not individually measured" : `${Number(stateRecord.duration_ms).toFixed(3)} ms`]);
    }
  }
}

function renderEvaluation(parent) {
  const evaluation = state.metadata?.evaluation || {};
  const section = sectionHeading(parent, "Research evaluation status");
  appendText(section, evaluation.message || "Evaluation pending — No verified human-labeled dataset available.", "research-simple-note");
  appendText(section, `Developer-authored samples: ${valueOr(evaluation.diagnostic_sample_count, 0)}. Provisional AI labels: ${valueOr(evaluation.provisional_ai_label_count, 0)}. Human reference labels: ${valueOr(evaluation.human_reference_count, 0)}. Aligned prediction file: ${evaluation.aligned_prediction_file_found ? "found" : "not found"}.`);
  appendText(section, "The isolated annotation guide's potential primary target is intelligibility (CLEAR, UNCLEAR, NONSENSICAL, UNCERTAIN); topic relevance and figurative language are separate optional fields. The active production Rule Bases do not emit these classification labels or a model prediction.");
  appendText(section, "A future evaluation requires a defined target, human reference labels, model predictions for matching sample IDs, and provenance. No confusion matrix or effectiveness metric is fabricated here.");
  const table = makeTable(section, ["Measure", "Definition", "Current status"], "No measures.");
  for (const [measure, definition] of [
    ["TP", "Predicted positive and human reference positive"],
    ["FP", "Predicted positive while reference is negative"],
    ["TN", "Predicted negative and reference negative"],
    ["FN", "Predicted negative while reference is positive"],
    ["Precision", "TP / (TP + FP) for a specified positive class"],
    ["Recall", "TP / (TP + FN) for a specified positive class"],
    ["F1", "2 × precision × recall / (precision + recall)"],
    ["Accuracy", "(TP + TN) / (TP + FP + TN + FN)"],
    ["Support", "Number of human reference samples for a class; report per class and evaluation split"],
  ]) addTableRow(table, [measure, definition, "Not calculated — no valid aligned labeled evaluation"]);
}

function renderGlossary(parent) {
  const section = sectionHeading(parent, "Technical glossary");
  const search = node("input");
  search.type = "search";
  search.placeholder = "Find a term";
  search.setAttribute("aria-label", "Find a glossary term");
  section.appendChild(search);
  const host = node("div", undefined, "research-glossary");
  section.appendChild(host);
  const entries = state.metadata?.glossary || [];
  const render = () => {
    host.replaceChildren();
    const query = search.value.trim().toLowerCase();
    for (const item of entries.filter((entry) => `${entry.term} ${entry.definition} ${entry.example}`.toLowerCase().includes(query))) {
      const details = node("details");
      details.appendChild(node("summary", item.term));
      appendText(details, `Definition: ${item.definition}`);
      appendText(details, `Example: ${item.example}`);
      appendText(details, `Why EssayScaff uses it: ${item.why_used}`);
      appendText(details, `Related process: ${item.related_process}`);
      host.appendChild(details);
    }
  };
  search.addEventListener("input", render);
  render();
}

function makeTable(parent, headings, emptyMessage) {
  const wrapper = node("div", undefined, "research-table-wrap");
  const table = node("table", undefined, "research-table");
  const head = node("thead");
  const row = node("tr");
  for (const heading of headings) {
    const cell = node("th", heading);
    cell.scope = "col";
    row.appendChild(cell);
  }
  head.appendChild(row);
  table.appendChild(head);
  const body = node("tbody");
  body.dataset.emptyMessage = emptyMessage;
  const emptyRow = node("tr");
  emptyRow.dataset.empty = "true";
  const emptyCell = node("td", emptyMessage);
  emptyCell.colSpan = headings.length;
  emptyRow.appendChild(emptyCell);
  body.appendChild(emptyRow);
  table.appendChild(body);
  wrapper.appendChild(table);
  parent.appendChild(wrapper);
  return body;
}

function addTableRow(tbody, values) {
  if (tbody.firstElementChild?.dataset.empty === "true") tbody.replaceChildren();
  const row = node("tr");
  for (const value of values) {
    const cell = node("td");
    if (value instanceof HTMLElement) cell.appendChild(value);
    else cell.textContent = value === undefined || value === null ? "—" : String(value);
    row.appendChild(cell);
  }
  tbody.appendChild(row);
}

function glossaryCell(value) {
  const button = node("button", valueOr(value, "—"), "research-inline-glossary");
  button.type = "button";
  button.addEventListener("click", () => {
    const found = (state.metadata?.glossary || []).find((item) => item.term.toLowerCase() === String(value).toLowerCase());
    if (!found) {
      showRequestStatus(`No glossary entry is registered for “${value}”; see the relevant process explanation.`);
      return;
    }
    const index = state.metadata.processes.findIndex((item) => item.id === "11");
    selectProcess(index);
    window.setTimeout(() => {
      const details = [...document.querySelectorAll(".research-glossary details")].find((item) => item.querySelector("summary")?.textContent === found.term);
      if (details) {
        details.open = true;
        details.scrollIntoView({ behavior: "smooth", block: "center" });
      }
    }, 0);
  });
  return button;
}

function renderMetrics() {
  metricsHost.replaceChildren();
  const analysis = getAnalysis();
  if (!analysis) return;
  const linguistic = getLinguistic() || {};
  const bodyParagraphs = analysis.paragraph_count ?? analysis.text_presence?.paragraph_count ?? analysis.conclusion_paragraphs?.length ?? "Not returned";
  const concepts = getStageTrace()?.topic_service?.steps?.find((item) => item.id === "concept_extraction")?.candidate_count;
  const values = [
    ["Alphabetic words", linguistic.counts?.alphabetic_word_count],
    ["Tokens", linguistic.counts?.token_count],
    ["Sentences", linguistic.counts?.sentence_count],
    ["Paragraphs", bodyParagraphs],
    ["Rule events", analysis.rule_evidence?.length],
    ["Concept candidates", concepts],
    ["Feedback provenance", state.response?.feedback?.["Feedback Provenance"]?.length],
  ];
  for (const [label, value] of values) {
    const card = node("div", undefined, "research-metric");
    card.append(node("span", label), node("strong", valueOr(value, "Not returned")));
    metricsHost.appendChild(card);
  }
  document.getElementById("summary-stage").textContent = stageName(state.response.stage_id);
  document.getElementById("summary-status").textContent = state.response.availability;
  document.getElementById("summary-topic").textContent = topicInput.value;
  document.getElementById("summary-sample").textContent = state.sampleLabel;
  const runtime = state.response.research_trace?.runtime;
  document.getElementById("summary-runtime").textContent = runtime
    ? `Py ${runtime.python_version} · spaCy ${runtime.spacy_version} · NLTK ${runtime.nltk_version} · model ${runtime.model?.version}`
    : "Runtime metadata unavailable";
}

function clearStaleAnalysis() {
  state.response = null;
  state.requestMs = null;
  state.renderMs = null;
  statusLabel.textContent = "Inputs changed — reanalyze";
  requestStatus.textContent = "Previous trace cleared because inputs changed.";
  metricsHost.replaceChildren();
  rawJson.textContent = "No trace available.";
  copyButton.disabled = true;
  downloadButton.disabled = true;
  if (state.metadata) renderProcess();
}

function showRequestStatus(message) {
  requestStatus.textContent = message;
}

function loadRegressionSample() {
  stageSelect.value = "INTRODUCTION";
  topicInput.value = REGRESSION_SAMPLE.topic;
  focusInput.value = REGRESSION_SAMPLE.focus;
  introInput.value = REGRESSION_SAMPLE.introduction;
  bodyInput.value = "";
  conclusionInput.value = "";
  state.sampleLabel = "Technology in Education regression sample";
  clearStaleAnalysis();
  document.getElementById("summary-sample").textContent = state.sampleLabel;
  document.getElementById("summary-topic").textContent = topicInput.value;
}

function buildRequest() {
  const stage = stageSelect.value;
  const texts = { INTRODUCTION: introInput.value, BODY: bodyInput.value, CONCLUSION: conclusionInput.value };
  const payload = {
    stage_id: stage,
    assignment_topic: topicInput.value,
    focus_terms: focusInput.value,
    [stage === "INTRODUCTION" ? "introduction_text" : stage === "BODY" ? "body_text" : "conclusion_text"]: texts[stage],
  };
  if (stage !== "INTRODUCTION" && introInput.value.trim()) payload.introduction_text = introInput.value;
  if (stage === "CONCLUSION" && bodyInput.value.trim()) payload.body_text = bodyInput.value;
  return payload;
}

async function analyzeSample(event) {
  event.preventDefault();
  errorMessage.hidden = true;
  errorMessage.textContent = "";
  const payload = buildRequest();
  const requestSnapshot = JSON.stringify(payload);
  const selectedText = payload[stageSelect.value === "INTRODUCTION" ? "introduction_text" : stageSelect.value === "BODY" ? "body_text" : "conclusion_text"];
  if (!payload.assignment_topic.trim()) return showError("Enter an assignment topic.");
  if (!selectedText?.trim()) return showError(`Write the ${stageName().toLowerCase()} sample before analyzing it.`);
  const button = document.getElementById("run-research-analysis");
  button.disabled = true;
  button.textContent = "Analyzing…";
  statusLabel.textContent = "Analysis in progress";
  requestStatus.textContent = "Sending one analysis request; process navigation will not rerun NLP.";
  const started = performance.now();
  try {
    const response = await fetch("/api/research-inspector/analyze", {
      method: "POST",
      credentials: "same-origin",
      headers: { "Content-Type": "application/json", "X-CSRF-Token": csrfToken },
      body: JSON.stringify(payload),
    });
    const result = await response.json().catch(() => ({}));
    if (requestSnapshot !== JSON.stringify(buildRequest())) {
      clearStaleAnalysis();
      return;
    }
    state.requestMs = performance.now() - started;
    if (!response.ok) throw new Error(result.error || `Analysis failed (HTTP ${response.status}).`);
    if (!result.analysis || !result.feedback || result.stage_id !== stageSelect.value || !result.research_trace) {
      throw new Error("The server returned an incomplete research trace.");
    }
    state.response = result;
    state.sampleLabel = state.sampleLabel || "Custom sample";
    statusLabel.textContent = `${result.availability} · ${stageName(result.stage_id)}`;
    requestStatus.textContent = `Analysis returned in ${state.requestMs.toFixed(2)} ms round trip; this includes browser/network time and is not server-only NLP latency.`;
    rawJson.textContent = JSON.stringify(buildRawTracePayload(result), null, 2);
    copyButton.disabled = false;
    downloadButton.disabled = false;
    renderMetrics();
    selectProcess(state.activeProcess);
  } catch (error) {
    if (requestSnapshot !== JSON.stringify(buildRequest())) {
      clearStaleAnalysis();
      return;
    }
    state.response = null;
    statusLabel.textContent = "Analysis failed";
    showError(error instanceof TypeError ? "The server could not be reached. Check that EssayScaff V2 is running." : error.message);
  } finally {
    button.disabled = false;
    button.textContent = "Analyze Sample";
  }
}

function showError(message) {
  errorMessage.textContent = message;
  errorMessage.hidden = false;
}

async function copyTrace() {
  if (!state.response) return;
  try {
    await navigator.clipboard.writeText(rawJson.textContent);
    showRequestStatus("Current authorized trace copied to clipboard.");
  } catch (_error) {
    const temporary = node("textarea");
    temporary.value = rawJson.textContent;
    document.body.appendChild(temporary);
    temporary.select();
    let copied = false;
    try { copied = document.execCommand("copy"); } catch (_copyError) { copied = false; }
    temporary.remove();
    showRequestStatus(copied ? "Current authorized trace copied to clipboard." : "Clipboard access is unavailable in this browser.");
  }
}

function downloadTrace() {
  if (!state.response) return;
  const blob = new Blob([rawJson.textContent], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const anchor = node("a");
  anchor.href = url;
  anchor.download = "essayscaff-v2-research-trace.json";
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  window.setTimeout(() => URL.revokeObjectURL(url), 1000);
  showRequestStatus("Trace exported locally. It was not uploaded or stored by the application.");
}

function selectAdjacent(offset) {
  selectProcess(state.activeProcess + offset);
}

async function initialize() {
  for (const input of [stageSelect, topicInput, focusInput, introInput, bodyInput, conclusionInput]) {
    input.addEventListener("input", clearStaleAnalysis);
    input.addEventListener("change", clearStaleAnalysis);
  }
  document.getElementById("load-regression-sample").addEventListener("click", loadRegressionSample);
  document.getElementById("previous-process").addEventListener("click", () => selectAdjacent(-1));
  document.getElementById("next-process").addEventListener("click", () => selectAdjacent(1));
  form.addEventListener("submit", analyzeSample);
  copyButton.addEventListener("click", copyTrace);
  downloadButton.addEventListener("click", downloadTrace);
  try {
    const response = await fetch("/api/research-inspector/metadata", { credentials: "same-origin" });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(data.error || "Inspector metadata could not be loaded.");
    state.metadata = data;
    const analyzeButton = document.getElementById("run-research-analysis");
    analyzeButton.disabled = false;
    analyzeButton.textContent = "Analyze Sample";
    if (data.processes?.length) state.activeProcess = 0;
    renderNavigation();
    renderProcess();
    loadRegressionSample();
  } catch (error) {
    document.getElementById("run-research-analysis").disabled = true;
    showError(error.message || "Inspector metadata could not be loaded.");
  }
}

initialize();
