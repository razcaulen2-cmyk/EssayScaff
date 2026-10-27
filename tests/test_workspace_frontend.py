"""Exercise workspace persistence and stale-feedback behavior in app.js."""

import shutil
import json
import subprocess
from pathlib import Path

import pytest

from services.essay_analysis_service import EssayAnalysisService


NODE = shutil.which("node")
pytestmark = pytest.mark.skipif(NODE is None, reason="Node.js is required for the JavaScript state test")


def test_draft_state_save_restore_and_dependent_feedback_invalidation(tmp_path) -> None:
    _run_workspace_frontend(tmp_path)


def test_stage_progress_guidance_navigation_freshness_and_draft_safety(tmp_path) -> None:
    from tests.test_reason_highlighting import _make_stage_payload

    service = EssayAnalysisService()
    body_concern = _make_stage_payload(service.analyze(
        "Reading habits",
        ["reading", "students"],
        introduction_text="Students should read every day to build knowledge.",
        body_text="Reading helps students learn. Reading builds vocabulary.\n\nReading improves focus.",
        include_research_trace=True,
    ), "BODY")
    intro_neutral = _make_stage_payload(service.analyze(
        "Reading habits",
        ["reading", "students"],
        introduction_text="Students should read every day to build knowledge because reading strengthens comprehension and vocabulary.",
        include_research_trace=True,
    ), "INTRODUCTION")
    conclusion_concern = _make_stage_payload(service.analyze(
        "Reading habits",
        ["reading", "students"],
        introduction_text="Students should read every day to build knowledge.",
        body_text="Reading helps students learn. Reading builds vocabulary.\n\nReading improves focus. More.",
        conclusion_text="Daily reading helps students learn across subjects.",
        include_research_trace=True,
    ), "CONCLUSION")
    scenario = r'''
(async () => {
  const page = makeWorkspace(fetch, new Map());
  await waitForRestoration(page);
  await click(page.appLinks.find((link) => link.dataset.appLink === "workspace"));
  const e = page.elements;
  assert.equal(e["stage-progress"].hidden, false);
  assert.equal(e["stage-progress-title"].textContent, "Ready to Review Your Writing?");
  assert.equal(e["stage-progress-lead"].textContent, "Click Analyze Now to receive feedback, or continue when you are ready.");
  assert.equal(e["stage-progress-review"].hidden, true);
  assert.equal(e["stage-progress-continue"].textContent, "Continue to Body");
  assert.equal(revisions.length, 0);
  assert.equal(persistenceWrites.length, 0);

  e["assignment-topic"].value = "Reading habits";
  e["focus-terms"].value = "reading, students";
  const unsavedIntroduction = "Students should read every day to build knowledge.";
  e["stage-text"].value = unsavedIntroduction;
  await input(e["stage-text"]);
  const dirtyBefore = value(page, "isDirty()");
  const savedSnapshotBefore = value(page, "state.savedSnapshot");
  assert.equal(dirtyBefore, true);

  await click(e["stage-progress-continue"]);
  assert.equal(value(page, "state.currentStage"), "BODY");
  assert.equal(value(page, "state.currentView"), "BODY");
  assert.equal(value(page, "state.drafts.INTRODUCTION"), unsavedIntroduction);
  assert.equal(value(page, "isDirty()"), dirtyBefore);
  assert.equal(value(page, "state.savedSnapshot"), savedSnapshotBefore);
  assert.equal(e["stage-progress-continue"].textContent, "Continue to Conclusion");
  assert.equal(revisions.length, 0, "navigation must not create a revision");
  assert.equal(persistenceWrites.length, 0, "navigation must not save a draft or revision");
  await click(page.tabs[0]);
  assert.equal(e["stage-text"].value, unsavedIntroduction, "navigation protects unsaved writing");

  await click(page.tabs[1]);
  e["stage-text"].value = actualStageResponses.BODY.research_trace.stages.BODY.linguistic_observations.text;
  await input(e["stage-text"]);
  analysisResponseOverride = actualStageResponses.BODY;
  await click(e["analyze-button"]);
  assert.equal(e["stage-progress"].hidden, false);
  assert.equal(e["stage-progress-title"].textContent, "No Specific Writing Issue Detected");
  assert.equal(e["stage-progress-lead"].textContent, "The available checks did not identify a specific structural concern.");
  assert.equal(e["stage-progress-noticed"].textContent, "Review your ideas before continuing.");
  assert.equal(e["stage-progress-review"].hidden, true, "neutral feedback must not prompt a revision");
  assert.equal(e["stage-progress-continue"].textContent, "Continue to Conclusion");
  assert.equal(revisions.length, 0);

  e["stage-text"].value = "Reading helps students learn. Reading builds vocabulary.\n\nReading improves focus.";
  await input(e["stage-text"]);
  analysisResponseOverride = actualStageResponses.BODY_CONCERN;
  await click(e["analyze-button"]);
  assert.equal(e["stage-progress-title"].textContent, "Review Suggested");
  assert.equal(e["stage-progress-lead"].textContent, "EssayScaff found something you may want to review.");
  assert.match(e["stage-progress-noticed"].textContent, /Paragraph 2 has a possible main statement, but no additional sentence was recorded to develop it/);
  assert.match(e["stage-progress-task"].textContent, /activity, example, or explanation/);
  assert.equal(e["stage-progress-review"].hidden, false);
  assert.equal(e["stage-progress-continue"].textContent, "Continue to Conclusion");
  assert.equal(revisions.length, 0);

  await click(e["stage-progress-review"]);
  assert.equal(e["stage-text"].focused, true, "Review Writing focuses the active editor");
  assert.equal(e["stage-text"].scrollOptions.block, "center");

  e["stage-text"].value += " More.";
  await input(e["stage-text"]);
  assert.equal(e["stage-progress-title"].textContent, "Ready to Review Your Writing?");
  assert.equal(e["stage-progress-lead"].textContent, "Click Analyze Now to receive feedback, or continue when you are ready.");
  assert.equal(e["stage-progress-task"].hidden, false);
  assert.match(e["stage-progress-task"].textContent, /changed since the last analysis/);
  assert.equal(e["stage-progress-review"].hidden, true, "stale feedback cannot be shown as current");

  await click(e["stage-progress-continue"]);
  assert.equal(value(page, "state.currentStage"), "CONCLUSION");
  assert.equal(e["stage-progress-continue"].textContent, "Continue to Essay Review");
  e["stage-text"].value = actualStageResponses.CONCLUSION_CONCERN.analysis.linguistic_observations.text;
  await input(e["stage-text"]);
  analysisResponseOverride = actualStageResponses.CONCLUSION_CONCERN;
  await click(e["analyze-button"]);
  assert.equal(e["stage-progress-title"].textContent, "Review Suggested");
  assert.equal(e["stage-progress-review"].hidden, false);

  await click(e["stage-progress-continue"]);
  assert.equal(value(page, "state.currentView"), "ESSAY_REVIEW");
  assert.equal(e["stage-progress"].hidden, true);
  assert.equal(e["essay-review-panel"].hidden, false);
  assert.equal(revisions.length, 0, "Conclusion navigation must not create a revision");
  assert.equal(persistenceWrites.length, 0, "stage navigation never saves automatically");

  await click(page.tabs[0]);
  e["stage-text"].value = actualStageResponses.INTRO_NEUTRAL.analysis.linguistic_observations.text;
  await input(e["stage-text"]);
  analysisResponseOverride = actualStageResponses.INTRO_NEUTRAL;
  await click(e["analyze-button"]);
  assert.equal(e["stage-progress-title"].textContent, "No Specific Writing Issue Detected");
  assert.equal(e["stage-progress-review"].hidden, true);
  assert.equal(e["stage-progress-continue"].textContent, "Continue to Body");
  assert.equal(revisions.length, 0);
  console.log("Feedback presentation scenarios completed.");
})().catch((error) => { console.error(error); process.exitCode = 1; });
'''
    _run_workspace_frontend(
        tmp_path,
        scenario,
        {"BODY_CONCERN": body_concern, "INTRO_NEUTRAL": intro_neutral, "CONCLUSION_CONCERN": conclusion_concern},
    )


def _run_workspace_frontend(tmp_path, scenario=None, extra_responses=None) -> None:
    app_js = Path(__file__).resolve().parents[1] / "static" / "app.js"
    lesson_path = Path(__file__).resolve().parents[1] / "content" / "lessons" / "intro_lesson_001.json"
    script = r'''
const fs = require("node:fs");
const vm = require("node:vm");
const assert = require("node:assert/strict");
const appJs = process.argv[2];
const analysisPath = process.argv[3];
const lessonPath = process.argv[4];
const template = fs.readFileSync(require("node:path").join(require("node:path").dirname(appJs), "..", "templates", "index.html"), "utf8");
const lessonDefinition = JSON.parse(fs.readFileSync(lessonPath, "utf8"));
const scaffoldingDefinition = JSON.parse(fs.readFileSync(require("node:path").join(require("node:path").dirname(lessonPath), "feedback_help.json"), "utf8"));
assert.match(template, /<section id="nlp-transparency"[^>]*aria-labelledby="analysis-export-heading"/);
assert.match(template, /id="copy-full-analysis"[^>]*disabled>Copy Full Analysis<\/button>/);
assert.match(template, /id="full-analysis-report"[^>]*readonly/);
assert.match(template, /id="student-history"/);
assert.match(template, /<h2>Student history<\/h2>/);
assert.doesNotMatch(template, /id="introduction-guided-progression"/);
assert.match(template, /id="open-introduction-lesson"/);
assert.match(template, /id="introduction-lesson-definition"/);
assert.match(template, /id="stage-progress"[^>]*aria-labelledby="stage-progress-title"/);
assert.match(template, /id="stage-progress-continue"[^>]*>Continue to Body</);
assert.match(template, /Return to Writing/);
{
  const reviewPanel = template.indexOf('id="essay-review-panel"');
  const summary = template.indexOf('id="review-summary-total-words"');
  const preview = template.indexOf('id="review-introduction"');
  const submissionControls = template.indexOf('id="submission-controls"');
  const inspector = template.indexOf('id="nlp-transparency"');
  assert.ok(reviewPanel !== -1, "Essay Review dashboard exists");
  assert.ok(summary > reviewPanel && summary < preview, "summary precedes the essay preview");
  assert.ok(submissionControls > preview && submissionControls < inspector,
    "submission controls follow the essay preview inside the dashboard");
  assert.ok(inspector > reviewPanel, "technical Inspector follows the dashboard content");
  assert.doesNotMatch(template, /Word counts by section|review-total-count/,
    "the dashboard does not repeat word counts in a second block");
}
assert.doesNotMatch(fs.readFileSync(appJs, "utf8"), /\.innerHTML\s*=/);
const stylesheet = fs.readFileSync(require("node:path").join(require("node:path").dirname(appJs), "style.css"), "utf8");
assert.doesNotMatch(stylesheet, /\.guided-requirements\s*\{/);
assert.match(stylesheet, /@media\s*\(max-width:\s*760px\)[\s\S]*\.introduction-tutoring-launcher\s*\{[^}]*flex-direction:\s*column/s);

class Element {
  constructor(id, stage = null) {
    this.id = id;
    this.tagName = String(id).toUpperCase();
    this.dataset = stage ? { stage } : {};
    this.value = "";
    this.textContent = "";
    this.hidden = false;
    this.disabled = false;
    this.checked = false;
    this.open = false;
    this.maxLength = 0;
    this.placeholder = "";
    this.readOnly = false;
    this.listeners = {};
    this.style = {};
    this.clientWidth = 600;
    this.scrollTop = 0;
    this.scrollLeft = 0;
    this.attributes = {};
    this.children = [];
    this.parentNode = null;
    this.classList = { toggle: () => {} };
  }
  addEventListener(name, fn) {
    if (!this.listeners[name]) this.listeners[name] = [];
    this.listeners[name].push(fn);
  }
  setAttribute(name, value) { this.attributes[name] = value; }
  removeAttribute(name) { delete this.attributes[name]; }
  _attach(child, reference) {
    if (!child || child === this) return child;
    if (child.parentNode) {
      const prior = child.parentNode.children ? child.parentNode.children.indexOf(child) : -1;
      if (prior >= 0) child.parentNode.children.splice(prior, 1);
      child.parentNode = null;
    }
    let index = this.children.length;
    if (reference !== null && reference !== undefined) {
      const refIndex = this.children.indexOf(reference);
      index = refIndex < 0 ? this.children.length : refIndex;
    }
    this.children.splice(index, 0, child);
    child.parentNode = this;
    return child;
  }
  appendChild(child) { return this._attach(child, null); }
  append(...children) { for (const child of children) this._attach(child, null); }
  insertBefore(child, reference) { return this._attach(child, reference); }
  removeChild(child) {
    const index = this.children.indexOf(child);
    if (index < 0) throw new Error("removeChild: node is not a child");
    this.children.splice(index, 1);
    child.parentNode = null;
    return child;
  }
  replaceChildren() {
    for (const child of this.children) child.parentNode = null;
    this.children = [];
  }
  querySelectorAll(selector) {
    const found = [];
    for (const child of this.children) {
      if (selector === "button" && child.tagName === "BUTTON") found.push(child);
      if (selector === "input" && child.tagName === "INPUT") found.push(child);
      if (selector === "label" && child.tagName === "LABEL") found.push(child);
      if (selector === "mark" && child.tagName === "MARK") found.push(child);
      found.push(...child.querySelectorAll(selector));
    }
    return found;
  }
  querySelector(selector) { return this.querySelectorAll(selector)[0] || null; }
  focus() { this.focused = true; }
  select() { this.selected = true; this.selectionStart = 0; this.selectionEnd = this.value.length; }
  scrollIntoView(options) { this.scrollOptions = options; }
}

function makeWorkspace(fetch, storage) {
  const ids = [
    "assignment-topic", "focus-terms", "stage-text", "editor-backdrop", "editor-mirror", "analyze-button", "save-button", "save-revision-button",
    "save-status", "revision-save-status", "revision-empty", "revision-list", "revision-preview",
    "revision-preview-title", "preview-introduction", "preview-body", "preview-conclusion",
    "work-area", "revision-card", "essay-review-panel", "review-assignment-topic", "review-unsaved-note",
    "review-introduction", "review-body", "review-conclusion",
    "review-submission-badge", "review-summary-total-words", "review-summary-sections",
    "review-summary-revisions", "review-revisions-note", "review-summary-active-time",
    "review-active-time-note", "review-summary-remaining-time", "review-remaining-note",
    "review-progress-introduction-words", "review-progress-introduction-status",
    "review-progress-body-words", "review-progress-body-status",
    "review-progress-conclusion-words", "review-progress-conclusion-status",
    "review-edit-introduction", "review-edit-body", "review-edit-conclusion",
    "review-submission-note", "review-toggle-technical",
      "assignment-message", "available-assignment-list", "assignments-empty", "practice-mode-button",
      "dashboard-assignment-list", "dashboard-assignments-empty", "classrooms-page-list", "classrooms-page-empty",
      "show-all-assignments", "practice-setup", "selected-assignment-topic", "selected-assignment-focus-terms",
      "assignment-detail-view", "assignment-detail-title", "assignment-detail-classroom", "assignment-detail-progress",
      "assignment-detail-topic", "assignment-detail-instructions", "assignment-detail-focus", "open-assignment-workspace",
      "introduction-tutoring", "introduction-lesson-suggestion", "open-introduction-lesson",
      "introduction-lesson-panel", "introduction-lesson-title", "introduction-lesson-step-label",
      "introduction-lesson-progress", "introduction-lesson-content", "introduction-lesson-feedback",
      "introduction-lesson-previous", "introduction-lesson-retry", "introduction-lesson-next",
      "introduction-lesson-return", "introduction-lesson-definition",
     "selected-assignment-details", "selected-assignment-title", "selected-assignment-instructions",
     "assignment-submitted-status", "submission-controls", "submit-essay-button", "submission-status", "submission-error",
      "nlp-transparency", "nlp-transparency-content",
      "copy-full-analysis", "analysis-copy-status", "analysis-copy-fallback", "full-analysis-report",
     "student-history", "student-history-list",
    "my-classroom-list", "my-classrooms-empty", "join-classroom-form", "enrollment-code",
    "selected-classroom", "selected-classroom-name", "selected-classroom-subtitle",
     "error-message", "analysis-status", "feedback-content", "feedback-placeholder", "feedback-status", "stage-heading",
    "word-count", "tutor-state-title", "tutor-state-lead", "tutor-state-detail", "tutor-typing-dots",
    "tutor-tabs", "tutor-noticed", "tutor-evidence", "tutor-why", "tutor-task", "tutor-limitation", "tutor-working", "tutor-working-section", "tutor-evidence-section", "tutor-why-section", "tutor-task-section",
    "stage-progress", "stage-progress-title", "stage-progress-badge", "stage-progress-lead",
    "stage-progress-detail", "stage-progress-focus", "stage-progress-noticed", "stage-progress-task",
    "stage-progress-continue", "stage-progress-review",
    "interpretation-limit",
     "whats-working", "needs-attention", "feedback-details",
     "feedback-writing-focus", "scaffolding-guidance-definition",
  ];
    const elements = Object.fromEntries(ids.map((id) => [id, new Element(id)]));
    elements["introduction-lesson-definition"].textContent = JSON.stringify(lessonDefinition);
    elements["scaffolding-guidance-definition"].textContent = JSON.stringify(scaffoldingDefinition);
    elements["full-analysis-report"].readOnly = true;
    const tabs = ["INTRODUCTION", "BODY", "CONCLUSION", "ESSAY_REVIEW"].map((stage) => new Element(`tab-${stage}`, stage));
    const views = ["dashboard", "classrooms", "assignments", "workspace"].map((view) => {
      const element = new Element(`view-${view}`);
      element.dataset.appView = view;
      return element;
    });
    const appLinks = ["dashboard", "classrooms", "assignments", "workspace"].map((view) => {
      const element = new Element(`link-${view}`);
      element.dataset.appLink = view;
      element.classList.toggle = () => {};
      return element;
    });
  const stepLabel = new Element("step-label");
  const writingLabel = new Element("writing-label");
  const windowListeners = {};
  const timers = new Map();
  let nextTimerId = 1;
  const window = {
    addEventListener: (name, fn) => { windowListeners[name] = fn; },
    setTimeout: (callback, delay) => {
      const timerId = nextTimerId++;
      timers.set(timerId, { callback, delay });
      return timerId;
    },
    clearTimeout: (timerId) => timers.delete(timerId),
    confirm: () => true,
    location: { hash: "" },
    history: { pushState: (_state, _title, hash) => { window.location.hash = hash; } },
    localStorage: {
      getItem: (key) => storage.get(key) || null,
      setItem: (key, value) => storage.set(key, value),
      removeItem: (key) => storage.delete(key),
    },
  };
  const document = {
    body: { dataset: { initialView: "dashboard" } },
    getElementById: (id) => elements[id],
    querySelector: (selector) => selector.includes("step-label") ? stepLabel : writingLabel,
    querySelectorAll: (selector) => selector === ".stage-tab" ? tabs : selector === "[data-app-view]" ? views : selector === "[data-app-link]" ? appLinks : [],
    createElement: (tag) => new Element(tag),
    createElementNS: (_namespace, tag) => new Element(tag),
    createTextNode: (text) => { const node = new Element("#text"); node.textContent = String(text); return node; },
  };
  const context = vm.createContext({ document, window, fetch, AbortController, guidedScenarios });
  vm.runInContext(fs.readFileSync(require("node:path").join(require("node:path").dirname(appJs), "nlp_process_explorer.js"), "utf8"), context);
  vm.runInContext(fs.readFileSync(appJs, "utf8"), context);
  return { elements, tabs, views, appLinks, context, windowListeners, timers };
}

const storage = new Map();
const analysisRequests = [];
const persistenceWrites = [];
let holdNextAnalysis = false;
let delayedAnalysisResolve = null;
let delayedAnalysisSignal = null;
let savedDraft = null;
let completeSave;
const revisions = [];
let nextRevisionId = 1;
let recordedActivitySeconds = null;
const assignmentRows = [
  { assignment_id: 101, classroom_id: 10, title: "Assignment One", topic: "Official topic one", instructions: "Use evidence one.", focus_terms: "one, topic" },
  { assignment_id: 102, classroom_id: 10, title: "Assignment Two", topic: "Official topic two", instructions: "Use evidence two.", focus_terms: "two, topic" },
];
const classrooms = [
  { classroom_id: 10, classroom_name: "Class One", subject: "Writing", section: "BSCS 3A" },
  { classroom_id: 20, classroom_name: "Class Two", subject: "Writing", section: "BSCS 3B" },
];
const assignmentWorkspaces = new Map();
let submissionCount = 0;
let analysisResponseOverride = null;
let failNextAnalysis = false;
const actualStageResponses = JSON.parse(fs.readFileSync(analysisPath, "utf8"));
const guidedScenarios = actualStageResponses.GUIDED_SCENARIOS;
const fetch = (url, options = {}) => {
  if (["/api/drafts", "/api/revisions", "/api/submissions"].includes(url) && options.method === "POST") {
    persistenceWrites.push(url);
  }
  if (url === "/api/classrooms") {
    return Promise.resolve({ ok: true, json: async () => ({ classrooms }) });
  }
  if (url === "/api/student-history") {
    return Promise.resolve({ ok: true, json: async () => ({ assignments: [] }) });
  }
  if (url === "/api/assignments") {
    return Promise.resolve({ ok: true, json: async () => ({ assignments: assignmentRows.map((item) => ({ ...item, progress: "Not Started" })) }) });
  }
  if (url.startsWith("/api/classrooms/") && url.endsWith("/assignments")) {
    const classroomId = Number(url.split("/")[3]);
    return Promise.resolve({
      ok: true,
      json: async () => ({ assignments: assignmentRows.filter((item) => item.classroom_id === classroomId) }),
    });
  }
  if (url === "/api/classroom-enrollments" && options.method === "POST") {
    return Promise.resolve({ ok: true, json: async () => ({ classroom: classrooms[0] }) });
  }
  if (url.startsWith("/api/assignments/") && url.endsWith("/workspace")) {
    const assignmentId = Number(url.split("/")[3]);
    const assignment = assignmentRows.find((item) => item.assignment_id === assignmentId);
    if (!assignment) return Promise.resolve({ ok: false, json: async () => ({ error: "missing" }) });
    if (!assignmentWorkspaces.has(assignmentId)) {
      assignmentWorkspaces.set(assignmentId, {
        session_id: assignmentId === 101 ? "10".repeat(16) : "20".repeat(16),
        assignment_topic: assignment.topic,
        focus_terms: assignment.focus_terms,
        assignment_id: assignmentId,
        introduction_text: "",
        body_text: "",
        conclusion_text: "",
      });
    }
    return Promise.resolve({
      ok: true,
      json: async () => ({
        assignment,
        draft: assignmentWorkspaces.get(assignmentId),
        draft_version: "a".repeat(64),
        submission: null,
      }),
    });
  }
  if (url === "/api/drafts" && options.method === "POST") {
    const payload = JSON.parse(options.body);
    if (payload.assignment_id !== null && payload.assignment_id !== undefined) {
      const assigned = assignmentWorkspaces.get(payload.assignment_id);
      Object.assign(assigned, payload);
      return Promise.resolve({ ok: true, json: async () => ({ session_id: assigned.session_id, draft_version: "b".repeat(64) }) });
    }
    savedDraft = payload;
    return new Promise((resolve) => {
      completeSave = () => resolve({
        ok: true,
        json: async () => ({ session_id: "ab".repeat(16), updated_at: "2026-01-01T00:00:00Z" }),
      });
    });
  }
  if (url.startsWith("/api/drafts?")) {
    return Promise.resolve({
      ok: true,
      json: async () => ({
        ...savedDraft,
        session_id: "ab".repeat(16),
        created_at: "2026-01-01T00:00:00Z",
        updated_at: "2026-01-01T00:00:00Z",
      }),
    });
  }
  if (url === "/api/revisions" && options.method === "POST") {
    const payload = JSON.parse(options.body);
    const previous = revisions[0];
    const stageFields = ["assignment_topic", "focus_terms", "introduction_text", "body_text", "conclusion_text"];
    const duplicate = previous && stageFields.every((field) => previous[field] === payload[field]);
    savedDraft = payload;
    let revision = previous;
    if (!duplicate) {
      revision = {
        ...payload,
        revision_id: nextRevisionId++,
        session_id: payload.session_id || "ab".repeat(16),
        revision_number: previous ? previous.revision_number + 1 : 1,
        created_at: `2026-01-01T00:00:0${nextRevisionId}Z`,
      };
      revisions.unshift(revision);
    }
    return Promise.resolve({
      ok: true,
      json: async () => ({
        session_id: revision.session_id,
        revision_id: revision.revision_id,
        revision_number: revision.revision_number,
        created_at: revision.created_at,
        created: !duplicate,
        draft_version: "c".repeat(64),
      }),
    });
  }
  if (url === "/api/submissions" && options.method === "POST") {
    const payload = JSON.parse(options.body);
    const draft = assignmentWorkspaces.get(payload.assignment_id);
    submissionCount += 1;
    return Promise.resolve({
      ok: true,
      json: async () => ({
        submission_id: 700 + submissionCount,
        submitted_at: "2026-10-16T12:00:00Z",
        introduction_snapshot: draft.introduction_text,
        body_snapshot: draft.body_text,
        conclusion_snapshot: draft.conclusion_text,
      }),
    });
  }
  if (url.startsWith("/api/writing-activity?")) {
    return Promise.resolve({
      ok: true,
      json: async () => ({ recorded_seconds: recordedActivitySeconds, tracking_enabled: true }),
    });
  }
  if (url.startsWith("/api/revisions?") ) {
    const requestedSession = decodeURIComponent(url.split("session_id=")[1] || "");
    const scoped = revisions.filter((revision) => revision.session_id === requestedSession);
    return Promise.resolve({
      ok: true,
      json: async () => ({
        revisions: scoped.map(({ revision_id, session_id, revision_number, created_at }) =>
          ({ revision_id, session_id, revision_number, created_at })),
      }),
    });
  }
  if (url.startsWith("/api/revisions/")) {
    const revisionId = Number(url.split("/")[3].split("?")[0]);
    const revision = revisions.find((item) => item.revision_id === revisionId);
    return Promise.resolve({ ok: Boolean(revision), json: async () => revision || { error: "missing" } });
  }
  const payload = JSON.parse(options.body);
  analysisRequests.push(payload);
  if (failNextAnalysis) {
    failNextAnalysis = false;
    return Promise.reject(new TypeError("temporary analysis failure"));
  }
  if (holdNextAnalysis) {
    holdNextAnalysis = false;
    delayedAnalysisSignal = options.signal;
    return new Promise((resolve) => { delayedAnalysisResolve = resolve; });
  }
  return Promise.resolve({
    ok: true,
    json: async () => analysisResponseOverride || ({
      stage_id: payload.stage_id,
      availability: "ANALYZED",
      analysis: { stage: payload.stage_id },
      feedback: {
        "Current Goal": "Goal",
        "Primary Feedback": `${payload.stage_id} feedback`,
        "What's Working": [],
        "Needs Attention": [],
        "Next Step": "Review",
      },
      interpretation_limit: "Observation only.",
    }),
  });
};

const dispatch = async (element, name) => {
  for (const listener of element.listeners[name] || []) await listener({ preventDefault() {} });
};
const click = async (element) => dispatch(element, "click");
const input = async (element) => dispatch(element, "input");
const change = async (element) => dispatch(element, "change");
const lessonOption = (page, questionId, optionValue) => {
  const option = page.elements["introduction-lesson-content"].querySelectorAll("input")
    .find((item) => item.name === `introduction-lesson-${questionId}` && item.value === optionValue);
  assert.ok(option, `Expected lesson option ${questionId}/${optionValue}`);
  return option;
};
const answerLessonQuestion = async (page, questionId, optionValue) => {
  const option = lessonOption(page, questionId, optionValue);
  option.checked = true;
  await change(option);
};
const startAssignment = async (cardButton, workspace) => {
  await click(cardButton);
  assert.equal(workspace.elements["assignment-detail-view"].hidden, false);
  await click(workspace.elements["open-assignment-workspace"]);
  await waitForRestoration(workspace);
};
const value = (workspace, expression) => vm.runInContext(expression, workspace.context);
const textTree = (node) => [node.textContent, ...node.children.map(textTree)].join(" ");
const reportRecord = (report, path) => {
  const marker = `[source: ${path}]\n`;
  const start = report.indexOf(marker);
  assert.notEqual(start, -1, `Expected source record ${path}`);
  let encoded = "";
  for (const line of report.slice(start + marker.length).split("\n")) {
    encoded += line + "\n";
    try { return JSON.parse(encoded); } catch (_error) { /* Read the complete JSON record. */ }
  }
  assert.fail(`No complete JSON record for ${path}`);
};
const waitForRestoration = async (workspace) => {
  for (let attempt = 0; attempt < 20 && value(workspace, "state.restoring"); attempt++) {
    await new Promise((resolve) => setImmediate(resolve));
  }
};
const runTimers = async (workspace, delay) => {
  const due = [...workspace.timers.entries()].filter(([, timer]) => timer.delay <= delay);
  for (const [timerId, timer] of due) {
    workspace.timers.delete(timerId);
    timer.callback();
  }
  for (let attempt = 0; attempt < 6; attempt++) await new Promise((resolve) => setImmediate(resolve));
};
const analyzeGuidedScenario = async ({ topic, focus, text, response }) => {
  const page = makeWorkspace(fetch, new Map());
  await waitForRestoration(page);
  await click(page.appLinks.find((link) => link.dataset.appLink === "workspace"));
  page.elements["assignment-topic"].value = topic;
  page.elements["focus-terms"].value = focus;
  page.elements["stage-text"].value = text;
  await input(page.elements["stage-text"]);
  analysisResponseOverride = response;
  await click(page.elements["analyze-button"]);
  return page;
};

(async () => {
  const page = makeWorkspace(fetch, storage);
  await waitForRestoration(page);
  assert.equal(page.views.filter((view) => !view.hidden).length, 1);
  assert.equal(page.views.find((view) => view.dataset.appView === "dashboard").hidden, false);
  await click(page.appLinks.find((link) => link.dataset.appLink === "workspace"));
  assert.equal(page.views.find((view) => view.dataset.appView === "dashboard").hidden, true);
  assert.equal(page.views.find((view) => view.dataset.appView === "workspace").hidden, false);
  const { elements: e, tabs } = page;
  e["assignment-topic"].value = "Reading habits";
  e["focus-terms"].value = "reading, students";

  e["stage-text"].value = "Intro draft.";
  await input(e["stage-text"]);
   assert.equal(page.timers.size, 2, "typing indicator and debounced analysis are scheduled");
   assert.deepEqual([...page.timers.values()].map((timer) => timer.delay).sort((a,b)=>a-b), [350,1000]);
  await click(e["analyze-button"]);
  assert.equal(page.timers.size, 0, "manual Analyze Now cancels the pending debounce and typing timer");
  assert.ok(value(page, "state.analyses.INTRODUCTION"));

  await click(tabs[1]);
  e["stage-text"].value = "First paragraph.\n\nSecond paragraph.";
  await input(e["stage-text"]);
  await click(e["analyze-button"]);
  assert.equal(analysisRequests[1].body_text, "First paragraph.\n\nSecond paragraph.");
  assert.equal(analysisRequests[1].introduction_text, "Intro draft.");

  await click(tabs[2]);
  e["stage-text"].value = "Conclusion draft.";
  await input(e["stage-text"]);
  await click(e["analyze-button"]);
  assert.ok(value(page, "state.analyses.CONCLUSION"));
  assert.equal(analysisRequests[2].body_text, "First paragraph.\n\nSecond paragraph.");

  e["stage-text"].value = "Edited conclusion.";
  await input(e["stage-text"]);
  assert.ok(value(page, "state.analyses.INTRODUCTION"));
  assert.ok(value(page, "state.analyses.BODY"));
  assert.equal(value(page, "state.analyses.CONCLUSION"), undefined);

  await click(e["analyze-button"]);
  await click(tabs[1]);
  e["stage-text"].value = "Changed body.\n\nAnother paragraph.";
  await input(e["stage-text"]);
  assert.ok(value(page, "state.analyses.INTRODUCTION"));
  assert.equal(value(page, "state.analyses.BODY"), undefined);
  assert.equal(value(page, "state.analyses.CONCLUSION"), undefined);
  assert.equal(e["feedback-content"].hidden, true);

  await click(e["analyze-button"]);
  await click(tabs[2]);
  await click(e["analyze-button"]);
  await click(tabs[1]);
  await click(tabs[0]);
  e["stage-text"].value = "Edited introduction.";
  await input(e["stage-text"]);
  assert.equal(Object.keys(value(page, "state.analyses")).length, 0);

  await click(e["analyze-button"]);
  await click(tabs[1]);
  await click(e["analyze-button"]);
  await click(tabs[2]);
  await click(e["analyze-button"]);
  e["focus-terms"].value = "different focus";
  await input(e["focus-terms"]);
  assert.equal(Object.keys(value(page, "state.analyses")).length, 0);

  e["focus-terms"].value = "reading, students";
  await input(e["focus-terms"]);
  await click(tabs[0]);
  await click(e["analyze-button"]);
  await click(tabs[1]);
  await click(e["analyze-button"]);
  await click(tabs[2]);
  await click(e["analyze-button"]);
  e["assignment-topic"].value = "A changed topic";
  await input(e["assignment-topic"]);
  assert.equal(Object.keys(value(page, "state.analyses")).length, 0);
  e["assignment-topic"].value = "Reading habits";
  await input(e["assignment-topic"]);

  const saving = click(e["save-button"]);
  assert.equal(e["save-status"].textContent, "Saving…");
  assert.notEqual(e["save-status"].textContent, "Draft saved");
  assert.equal(savedDraft.introduction_text, "Edited introduction.");
  assert.equal(savedDraft.body_text, "Changed body.\n\nAnother paragraph.");
  assert.equal(savedDraft.conclusion_text, "Edited conclusion.");
  completeSave();
  await saving;
  assert.equal(e["save-status"].textContent, "Draft saved");
  assert.equal(storage.get("essayScaffSessionId"), "ab".repeat(16));

  const restoredPage = makeWorkspace(fetch, storage);
  await waitForRestoration(restoredPage);
  await click(restoredPage.appLinks.find((link) => link.dataset.appLink === "workspace"));
  assert.equal(restoredPage.elements["assignment-topic"].value, "Reading habits");
  assert.equal(restoredPage.elements["focus-terms"].value, "reading, students");
  assert.equal(restoredPage.elements["stage-text"].value, "Edited introduction.");
  assert.equal(Object.keys(value(restoredPage, "state.analyses")).length, 0);
  assert.equal(restoredPage.elements["feedback-content"].hidden, true);
  await click(restoredPage.tabs[1]);
  assert.equal(restoredPage.elements["stage-text"].value, "Changed body.\n\nAnother paragraph.");
  await click(restoredPage.tabs[2]);
  assert.equal(restoredPage.elements["stage-text"].value, "Edited conclusion.");

  await click(restoredPage.elements["save-revision-button"]);
  assert.equal(restoredPage.elements["revision-save-status"].textContent, "Revision 1 saved.");
  assert.equal(restoredPage.elements["revision-list"].children.length, 1);
  await click(restoredPage.tabs[0]);
  restoredPage.elements["stage-text"].value = "Current unsaved Introduction.";
  await input(restoredPage.elements["stage-text"]);
  await click(restoredPage.elements["save-revision-button"]);
  assert.equal(restoredPage.elements["revision-save-status"].textContent, "Revision 2 saved.");
  assert.equal(restoredPage.elements["revision-list"].children.length, 2);
  restoredPage.elements["stage-text"].value += " Unsaved local work.";
  await input(restoredPage.elements["stage-text"]);
  const liveIntroduction = restoredPage.elements["stage-text"].value;
  const liveSnapshot = value(restoredPage, "state.savedSnapshot");
  const liveBody = value(restoredPage, "state.drafts.BODY");
  const liveConclusion = value(restoredPage, "state.drafts.CONCLUSION");
  const analysisCountBeforePreview = analysisRequests.length;
  await click(restoredPage.elements["revision-list"].children[1].children[0]);
  assert.match(restoredPage.elements["revision-preview-title"].textContent, /Viewing Revision 1/);
  assert.equal(restoredPage.elements["preview-introduction"].textContent, "Edited introduction.");
  assert.equal(restoredPage.elements["stage-text"].value, liveIntroduction);
  assert.equal(restoredPage.elements["assignment-topic"].value, "Reading habits");
  assert.equal(restoredPage.elements["focus-terms"].value, "reading, students");
  assert.equal(analysisRequests.length, analysisCountBeforePreview);
  assert.equal(value(restoredPage, "state.drafts.INTRODUCTION"), liveIntroduction);
  assert.equal(value(restoredPage, "state.drafts.BODY"), liveBody);
  assert.equal(value(restoredPage, "state.drafts.CONCLUSION"), liveConclusion);
  assert.equal(value(restoredPage, "state.savedSnapshot"), liveSnapshot);
  assert.equal(value(restoredPage, "isDirty()"), true);

  restoredPage.elements["stage-text"].value += " More text.";
  await input(restoredPage.elements["stage-text"]);
  const warning = { prevented: false, preventDefault() { this.prevented = true; } };
  restoredPage.windowListeners.beforeunload(warning);
  assert.equal(warning.prevented, true);

  await click(restoredPage.tabs[2]);
  restoredPage.elements["stage-text"].value = "";
  await input(restoredPage.elements["stage-text"]);
  await click(restoredPage.tabs[0]);
  restoredPage.elements["stage-text"].value = "First line.\n\n<script>alert('x')</script> café";
  await input(restoredPage.elements["stage-text"]);
  const analysesBeforeReview = analysisRequests.length;
  const savedDataBeforeReview = JSON.stringify(savedDraft);
  const revisionsBeforeReview = revisions.length;
  const savedSnapshotBeforeReview = value(restoredPage, "state.savedSnapshot");
  await click(restoredPage.tabs[3]);
  assert.equal(value(restoredPage, "state.currentView"), "ESSAY_REVIEW");
  assert.equal(value(restoredPage, "state.currentStage"), "INTRODUCTION");
  assert.equal(restoredPage.elements["work-area"].hidden, true);
  assert.equal(restoredPage.elements["revision-card"].hidden, true);
  assert.equal(restoredPage.elements["essay-review-panel"].hidden, false);
  assert.equal(restoredPage.elements["review-assignment-topic"].textContent, "Reading habits");
  assert.equal(restoredPage.elements["review-introduction"].textContent, "First line.\n\n<script>alert('x')</script> café");
  assert.equal(restoredPage.elements["review-body"].textContent, "Changed body.\n\nAnother paragraph.");
  assert.equal(restoredPage.elements["review-conclusion"].textContent, "Conclusion has not been written yet.");
  assert.equal(restoredPage.elements["review-unsaved-note"].hidden, false);
  assert.deepEqual(
    [
      restoredPage.elements["review-progress-introduction-words"].textContent,
      restoredPage.elements["review-progress-body-words"].textContent,
      restoredPage.elements["review-progress-conclusion-words"].textContent,
      restoredPage.elements["review-summary-total-words"].textContent,
    ],
    ["4", "4", "0", "8"],
  );
  assert.equal(analysisRequests.length, analysesBeforeReview);
  assert.equal(JSON.stringify(savedDraft), savedDataBeforeReview);
  assert.equal(revisions.length, revisionsBeforeReview);
  assert.equal(value(restoredPage, "state.savedSnapshot"), savedSnapshotBeforeReview);

  await click(restoredPage.tabs[1]);
  assert.equal(restoredPage.elements["stage-text"].value, "Changed body.\n\nAnother paragraph.");
  await click(restoredPage.tabs[0]);
  assert.equal(restoredPage.elements["stage-text"].value, "First line.\n\n<script>alert('x')</script> café");
  assert.equal(restoredPage.elements["essay-review-panel"].hidden, true);
  assert.equal(restoredPage.elements["work-area"].hidden, false);

  const practiceText = restoredPage.elements["stage-text"].value;
  await click(restoredPage.elements["my-classroom-list"].children[0].children[0]);
  const assignmentOneButton = restoredPage.elements["available-assignment-list"].children[0].children[0].children[3];
  await startAssignment(assignmentOneButton, restoredPage);
  assert.equal(value(restoredPage, "state.assignmentId"), null);
  assert.equal(restoredPage.elements["stage-text"].value, practiceText);
  assert.match(restoredPage.elements["assignment-message"].textContent, /Save your current draft/);

  const practiceSave = click(restoredPage.elements["save-button"]);
  completeSave();
  await practiceSave;
  assert.equal(value(restoredPage, "isDirty()"), false);
  await startAssignment(assignmentOneButton, restoredPage);
  assert.equal(value(restoredPage, "state.assignmentId"), 101);
  assert.equal(restoredPage.elements["assignment-topic"].value, "Official topic one");
  assert.equal(restoredPage.elements["focus-terms"].value, "one, topic");
  assert.equal(restoredPage.elements["assignment-topic"].readOnly, true);
  assert.equal(restoredPage.elements["focus-terms"].readOnly, true);
  assert.equal(restoredPage.elements["selected-assignment-title"].textContent, "Assignment One");
  assert.equal(restoredPage.elements["selected-assignment-instructions"].textContent, "Use evidence one.");

  restoredPage.elements["stage-text"].value = "Assignment One student writing.";
  await input(restoredPage.elements["stage-text"]);
  const assignmentTwoButton = restoredPage.elements["available-assignment-list"].children[1].children[0].children[3];
  await startAssignment(assignmentTwoButton, restoredPage);
  assert.equal(value(restoredPage, "state.assignmentId"), 101);
  assert.equal(restoredPage.elements["stage-text"].value, "Assignment One student writing.");
  assert.match(restoredPage.elements["assignment-message"].textContent, /Save your current draft/);

  await click(restoredPage.elements["save-button"]);
  assert.equal(assignmentWorkspaces.get(101).assignment_id, 101);
  assert.equal(assignmentWorkspaces.get(101).assignment_topic, "Official topic one");
  assert.equal(assignmentWorkspaces.get(101).focus_terms, "one, topic");
  value(restoredPage, `
    cancelAnalysisWork();
    state.analyses.INTRODUCTION = guidedScenarios.short_complete;
    state.analysisSnapshots.INTRODUCTION = analysisSnapshot("INTRODUCTION");
    state.guidedSelfChecks.position = { confirmedText: currentIntroductionText(), assignmentContext: currentAssignmentDetails() };
    state.guidedSelfChecks.direction = { confirmedText: currentIntroductionText(), assignmentContext: currentAssignmentDetails() };
    updateIntroductionTutoring();
  `);
  assert.equal(restoredPage.elements["guided-state-label"].dataset.state, "CHECKLIST_COMPLETE");
  await startAssignment(assignmentTwoButton, restoredPage);
  assert.equal(value(restoredPage, "state.assignmentId"), 102);
  assert.equal(restoredPage.elements["stage-text"].value, "");
  assert.equal(restoredPage.elements["guided-state-label"].dataset.state, "NOT_STARTED",
    "opening another assignment clears the previous assignment's Introduction readiness");
  assert.equal(restoredPage.elements["guided-position-confirmed"].checked, false);
  await startAssignment(assignmentOneButton, restoredPage);
  assert.equal(value(restoredPage, "state.assignmentId"), 101);
  assert.equal(restoredPage.elements["stage-text"].value, "Assignment One student writing.");

  await click(tabs[1]);
  restoredPage.elements["stage-text"].value = "Assignment One body.";
  await input(restoredPage.elements["stage-text"]);
  await click(tabs[2]);
  restoredPage.elements["stage-text"].value = "Assignment One conclusion.";
  await input(restoredPage.elements["stage-text"]);
  await click(e["save-button"]);
  await click(tabs[3]);
  assert.equal(e["submission-controls"].hidden, false);
  await click(e["submit-essay-button"]);
  assert.equal(submissionCount, 1);
  assert.equal(value(restoredPage, "state.submission.submission_id"), 701);
  assert.equal(e["assignment-submitted-status"].hidden, false);
  assert.equal(e["stage-text"].readOnly, true);
  assert.equal(e["save-button"].disabled, true);
  assert.equal(e["save-revision-button"].disabled, true);
  assert.equal(e["analyze-button"].disabled, true);
  assert.equal(e["submission-controls"].hidden, true);

  await click(restoredPage.elements["practice-mode-button"]);
  assert.equal(value(restoredPage, "state.assignmentId"), null);
  assert.equal(restoredPage.elements["stage-text"].value, practiceText);
  assert.equal(restoredPage.elements["assignment-topic"].readOnly, false);

  await click(tabs[1]);
  const realBody = "Students build knowledge with daily reading. <script>alert('x')</script> Reading also helps learners.";
  restoredPage.elements["stage-text"].value = realBody;
  await input(restoredPage.elements["stage-text"]);
  analysisResponseOverride = actualStageResponses.BODY;
  await click(restoredPage.elements["analyze-button"]);
  assert.equal(restoredPage.elements["copy-full-analysis"].disabled, false);
  const requestsBeforeExport = analysisRequests.length;
  await click(restoredPage.elements["copy-full-analysis"]);
  const transparencyText = restoredPage.elements["full-analysis-report"].value;
  assert.equal(restoredPage.elements["analysis-copy-fallback"].hidden, false);
  assert.deepEqual(reportRecord(transparencyText, "analysis.rule_evidence"), actualStageResponses.BODY.analysis.rule_evidence);
  assert.deepEqual(reportRecord(transparencyText, "analysis.rule_evaluation_trace"), actualStageResponses.BODY.analysis.rule_evaluation_trace);
  assert.deepEqual(reportRecord(transparencyText, "analysis.lexical_topic_evidence"), actualStageResponses.BODY.analysis.lexical_topic_evidence);
  assert.deepEqual(reportRecord(transparencyText, "research_trace.stages.BODY.linguistic_observations"), actualStageResponses.BODY.research_trace.stages.BODY.linguistic_observations);
  assert.equal(analysisRequests.length, requestsBeforeExport, "copying uses the cached analysis");
  assert.match(transparencyText, /Sentences/);
  assert.match(transparencyText, /tokenization|lemmatization|POS/);
  assert.match(transparencyText, /SKIPPED/);
  assert.match(transparencyText, /AVAILABLE|RESOURCE_MISSING/);
  assert.match(transparencyText, /EVALUATED_NOT_TRIGGERED/);
  assert.match(transparencyText, /BODY\.P1\.PARAGRAPH\.FOCUS_TERMS_OBSERVED/);
  assert.match(transparencyText, /daily reading|reading/i);
  assert.match(transparencyText, /<script>alert\('x'\)<\/script>/);
  assert.match(transparencyText, /direct/);
  const recordedMatch = analysisResponseOverride.analysis.lexical_topic_evidence.matches[0];
  assert.ok(reportRecord(transparencyText, "analysis.lexical_topic_evidence").matches.some(match => match.start === recordedMatch.start && match.end === recordedMatch.end));
  assert.match(transparencyText, /5\. Writing Feedback/);
  restoredPage.elements["stage-text"].value = "Edited after analysis.";
  await input(restoredPage.elements["stage-text"]);
  assert.equal(restoredPage.elements["copy-full-analysis"].disabled, true);
  assert.equal(restoredPage.elements["full-analysis-report"].value, "");

  value(restoredPage, "displayFeedback({analysis:{}, feedback:{}, interpretation_limit:'Example limitation.'})");
  assert.equal(restoredPage.elements["copy-full-analysis"].disabled, true);
  assert.match(value(restoredPage, "buildFullAnalysisReport({analysis:{}, feedback:{}, interpretation_limit:'Example limitation.'})"), /Not available in the cached response/);

  await click(tabs[0]);
  const realIntroduction = "Students should read every day to build knowledge.";
  restoredPage.elements["stage-text"].value = realIntroduction;
  await input(restoredPage.elements["stage-text"]);
  analysisResponseOverride = actualStageResponses.INTRODUCTION;
  await click(restoredPage.elements["analyze-button"]);
  await click(restoredPage.elements["copy-full-analysis"]);
  const introductionTransparency = restoredPage.elements["full-analysis-report"].value;
  assert.equal(
    restoredPage.elements["tutor-noticed"].textContent,
    value(restoredPage, "studentFeedbackPresentation(state.analyses.INTRODUCTION).displayed_guidance['What I noticed']"),
  );
  assert.match(introductionTransparency, /INTRO\.TEXT\.PRESENT/);
  assert.match(introductionTransparency, /Students should read every day to build knowledge\./);
  assert.match(introductionTransparency, /INTRO\.TOPIC\.FOCUS_TERMS_OBSERVED/);
  assert.equal(value(restoredPage, "currentAnalysisForExport() === state.analyses.INTRODUCTION"), true);

  await click(tabs[2]);
  restoredPage.elements["stage-text"].value = "Daily reading helps students learn across subjects.";
  await input(restoredPage.elements["stage-text"]);
  analysisResponseOverride = actualStageResponses.CONCLUSION;
  await click(restoredPage.elements["analyze-button"]);
  await click(restoredPage.elements["copy-full-analysis"]);
  const conclusionTransparency = restoredPage.elements["full-analysis-report"].value;
  assert.match(conclusionTransparency, /WordNet/);
  assert.match(conclusionTransparency, /separate, optional candidate relation|not verified semantic equivalence/);

  value(restoredPage, "state.assignmentId=101; state.deletedAssignment=true; state.submission=null; updateSubmissionUI()");
  assert.equal(restoredPage.elements["stage-text"].readOnly, true);
  assert.equal(restoredPage.elements["save-button"].disabled, true);
  assert.equal(restoredPage.elements["save-revision-button"].disabled, true);
  assert.equal(restoredPage.elements["analyze-button"].disabled, true);
  assert.equal(restoredPage.elements["submission-controls"].hidden, true);
  assert.match(restoredPage.elements["assignment-submitted-status"].textContent, /deleted by your teacher/);
   assert.equal(await value(restoredPage, "saveDraft()"), false);
  const preservedText = restoredPage.elements["stage-text"].value;
  await click(restoredPage.appLinks.find((link) => link.dataset.appLink === "dashboard"));
  assert.equal(restoredPage.views.filter((view) => !view.hidden).length, 1);
  assert.equal(restoredPage.views.find((view) => view.dataset.appView === "dashboard").hidden, false);
  assert.equal(restoredPage.windowListeners.hashchange !== undefined, true);
   await click(restoredPage.appLinks.find((link) => link.dataset.appLink === "workspace"));
   assert.equal(restoredPage.elements["stage-text"].value, preservedText);

   const lessonPage = makeWorkspace(fetch, new Map());
   await waitForRestoration(lessonPage);
   await click(lessonPage.appLinks.find((link) => link.dataset.appLink === "workspace"));
   lessonPage.elements["assignment-topic"].value = "Should our school offer one outdoor lunch day each week?";
   lessonPage.elements["focus-terms"].value = "outdoor lunch, school";
   lessonPage.elements["stage-text"].value = "My own Introduction remains in the editor.";
   await input(lessonPage.elements["stage-text"]);
   const lessonRequestsBeforeOpen = analysisRequests.length;
   const lessonWritesBeforeOpen = persistenceWrites.length;
   assert.equal(lessonPage.elements["introduction-lesson-suggestion"].hidden, true,
     "Free Writing focus terms do not create a teacher-assignment suggestion");
   assert.equal(lessonPage.elements["introduction-lesson-panel"].hidden, true,
     "the lesson never opens automatically while the student is typing");
   await click(lessonPage.elements["open-introduction-lesson"]);
   assert.equal(lessonPage.elements["introduction-lesson-panel"].hidden, false);
   assert.match(textTree(lessonPage.elements["introduction-lesson-content"]), /Should our school offer one outdoor lunch day each week/);
   assert.match(textTree(lessonPage.elements["introduction-lesson-content"]), /Our school should offer one outdoor lunch day each week/);
    assert.match(textTree(lessonPage.elements["introduction-lesson-content"]), /Harris, K\. R\., & Graham, S\./);
    assert.equal(lessonPage.elements["stage-text"].value, "My own Introduction remains in the editor.",
      "the lesson does not copy its examples into the writing editor");
    assert.equal(analysisRequests.length, lessonRequestsBeforeOpen, "opening the lesson issues no NLP request");
     assert.equal(lessonPage.elements["introduction-lesson-content"].querySelectorAll("input").length, 0);
    assert.equal(lessonPage.tabs[1].disabled, false, "Body navigation stays available before lesson completion");
    await click(lessonPage.elements["introduction-lesson-return"]);
    assert.equal(lessonPage.elements["introduction-lesson-panel"].hidden, true,
      "the student can leave the lesson before answering any exercise");
    assert.equal(lessonPage.elements["stage-text"].value, "My own Introduction remains in the editor.");
    await click(lessonPage.elements["open-introduction-lesson"]);

    assert.equal(lessonPage.elements["introduction-lesson-content"].querySelectorAll("input").length, 0,
      "the guide contains explanations, not answer-checking activities");
    assert.equal(lessonPage.elements["introduction-lesson-step-label"].textContent, "WRITING GUIDE");
    assert.equal(analysisRequests.length, lessonRequestsBeforeOpen, "reading explanations does not run analysis");
   await click(lessonPage.elements["introduction-lesson-return"]);
   assert.equal(lessonPage.elements["introduction-lesson-panel"].hidden, true);
   assert.equal(lessonPage.elements["stage-text"].value, "My own Introduction remains in the editor.");
   assert.equal(lessonPage.elements["stage-text"].focused, true);
   assert.equal(persistenceWrites.length, lessonWritesBeforeOpen,
     "lesson actions never save, revise, or submit the draft");
   await click(lessonPage.elements["open-introduction-lesson"]);
    assert.equal(lessonPage.elements["introduction-lesson-step-label"].textContent, "WRITING GUIDE");
   await click(lessonPage.tabs[1]);
   assert.equal(lessonPage.elements["introduction-lesson-panel"].hidden, true);
   assert.equal(lessonPage.tabs[1].disabled, false, "the lesson does not lock Body navigation");

   const suggestionPage = makeWorkspace(fetch, new Map());
   await waitForRestoration(suggestionPage);
   await click(suggestionPage.appLinks.find((link) => link.dataset.appLink === "workspace"));
   const suggestionText = guidedScenarios.paraphrase.analysis.input_text;
   suggestionPage.elements["assignment-topic"].value = guidedTopic;
   suggestionPage.elements["focus-terms"].value = guidedFocus;
   suggestionPage.elements["stage-text"].value = suggestionText;
   value(suggestionPage, `state.assignmentId = 101; state.drafts.INTRODUCTION = ${JSON.stringify(suggestionText)}; state.analyses.INTRODUCTION = guidedScenarios.paraphrase; state.analysisSnapshots.INTRODUCTION = analysisSnapshot("INTRODUCTION"); updateIntroductionTutoring();`);
   assert.equal(suggestionPage.elements["introduction-lesson-suggestion"].hidden, false,
     "a current no-match event with configured teacher focus may suggest the lesson");
   assert.match(suggestionPage.elements["introduction-lesson-suggestion"].textContent, /may use different words/);
   assert.equal(suggestionPage.elements["introduction-lesson-panel"].hidden, true,
     "a rule suggestion is not an automatic lesson launch");
   const suggestedAnalysisBeforeOpen = JSON.stringify(value(suggestionPage, "state.analyses.INTRODUCTION"));
   const requestsBeforeSuggestedLesson = analysisRequests.length;
   await click(suggestionPage.elements["open-introduction-lesson"]);
   assert.equal(analysisRequests.length, requestsBeforeSuggestedLesson);
   assert.equal(JSON.stringify(value(suggestionPage, "state.analyses.INTRODUCTION")), suggestedAnalysisBeforeOpen,
     "lesson display preserves the current analysis and its rule events for Transparency and Inspector views");
   suggestionPage.elements["stage-text"].value = `${suggestionText} New wording changes the draft substantially.`;
   await input(suggestionPage.elements["stage-text"]);
   assert.equal(suggestionPage.elements["introduction-lesson-suggestion"].hidden, true,
     "old no-match evidence is not used after the Introduction changes");

   const derivedOnlyPage = makeWorkspace(fetch, new Map());
   await waitForRestoration(derivedOnlyPage);
   await click(derivedOnlyPage.appLinks.find((link) => link.dataset.appLink === "workspace"));
   const lessonDerivedText = guidedScenarios.derived_unavailable.analysis.input_text;
   derivedOnlyPage.elements["assignment-topic"].value = "Effects of urban noise on health";
   derivedOnlyPage.elements["focus-terms"].value = "";
   derivedOnlyPage.elements["stage-text"].value = lessonDerivedText;
   value(derivedOnlyPage, `state.assignmentId = 202; state.drafts.INTRODUCTION = ${JSON.stringify(lessonDerivedText)}; state.analyses.INTRODUCTION = guidedScenarios.derived_unavailable; state.analysisSnapshots.INTRODUCTION = analysisSnapshot("INTRODUCTION"); updateIntroductionTutoring();`);
   assert.equal(derivedOnlyPage.elements["introduction-lesson-suggestion"].hidden, true,
     "topic-derived candidates do not manufacture a teacher-focus lesson trigger");
   await click(derivedOnlyPage.elements["open-introduction-lesson"]);
   assert.equal(derivedOnlyPage.elements["introduction-lesson-panel"].hidden, false,
     "the student can still open the lesson manually when no teacher focus is configured");

   const staleLessonPage = makeWorkspace(fetch, new Map());
   await waitForRestoration(staleLessonPage);
   await click(staleLessonPage.appLinks.find((link) => link.dataset.appLink === "workspace"));
   staleLessonPage.elements["assignment-topic"].value = guidedTopic;
   staleLessonPage.elements["focus-terms"].value = guidedFocus;
   staleLessonPage.elements["stage-text"].value = "Older Introduction text.";
   value(staleLessonPage, 'state.assignmentId = 303; state.drafts.INTRODUCTION = "Older Introduction text."');
   await input(staleLessonPage.elements["stage-text"]);
   holdNextAnalysis = true;
   delayedAnalysisResolve = null;
   delayedAnalysisSignal = null;
   analysisResponseOverride = guidedScenarios.paraphrase;
   const staleLessonAnalysis = staleLessonPage.elements["analyze-button"].listeners.click[0]({});
   for (let attempt = 0; attempt < 5 && delayedAnalysisResolve === null; attempt++) {
     await new Promise((resolve) => setImmediate(resolve));
   }
   staleLessonPage.elements["stage-text"].value = "Current Introduction text.";
   await input(staleLessonPage.elements["stage-text"]);
   assert.equal(delayedAnalysisSignal.aborted, false, "obsolete request is allowed to settle to serialize server execution");
   delayedAnalysisResolve({ ok: true, json: async () => guidedScenarios.paraphrase });
   await staleLessonAnalysis;
   assert.equal(value(staleLessonPage, "state.analyses.INTRODUCTION"), undefined);
   assert.equal(staleLessonPage.elements["introduction-lesson-suggestion"].hidden, true,
     "a late no-match response cannot create a lesson suggestion for newer text");

   analysisResponseOverride = null;
  const livePage = makeWorkspace(fetch, new Map());
  await waitForRestoration(livePage);
  await click(livePage.appLinks.find((link) => link.dataset.appLink === "workspace"));
  livePage.elements["assignment-topic"].value = "Reading habits";
  livePage.elements["focus-terms"].value = "reading, students";
  livePage.elements["stage-text"].value = "Students read books.";
  await input(livePage.elements["stage-text"]);
  const requestCountBeforeLive = analysisRequests.length;
  const persistenceCountBeforeLive = persistenceWrites.length;
   assert.equal(livePage.timers.size, 2, "typing indicator and automatic-analysis debounce");
   await runTimers(livePage, 350);
  assert.equal(analysisRequests.length, requestCountBeforeLive, "analysis waits for the full six-second pause");
   await runTimers(livePage, 1000);
   assert.equal(analysisRequests.length, requestCountBeforeLive + 1);
   await click(livePage.elements["analyze-button"]);
   assert.equal(analysisRequests.length, requestCountBeforeLive + 1, "manual click reuses the current analyzed snapshot");
  assert.equal(analysisRequests.at(-1).introduction_text, "Students read books.");
  assert.ok(value(livePage, "state.analyses.INTRODUCTION"));
  assert.match(livePage.elements["analysis-status"].textContent, /draft was not saved/i);
  assert.equal(persistenceWrites.length, persistenceCountBeforeLive, "live analysis does not save or submit writing");

  const stalePage = makeWorkspace(fetch, new Map());
  await waitForRestoration(stalePage);
  await click(stalePage.appLinks.find((link) => link.dataset.appLink === "workspace"));
  stalePage.elements["assignment-topic"].value = "Reading habits";
  stalePage.elements["focus-terms"].value = "reading, students";
  stalePage.elements["stage-text"].value = "Older writing.";
  await input(stalePage.elements["stage-text"]);
  holdNextAnalysis = true;
  const staleRequestCount = analysisRequests.length;
  const manualHandler = stalePage.elements["analyze-button"].listeners.click[0];
  const pendingAnalysis = manualHandler({});
  for (let attempt = 0; attempt < 5 && delayedAnalysisResolve === null; attempt++) {
    await new Promise((resolve) => setImmediate(resolve));
  }
  assert.equal(analysisRequests.length, staleRequestCount + 1);
  assert.ok(delayedAnalysisSignal);
  stalePage.elements["stage-text"].value = "Newer writing.";
  await input(stalePage.elements["stage-text"]);
   assert.equal(delayedAnalysisSignal.aborted, false);
  const delayedPayload = analysisRequests.at(-1);
  delayedAnalysisResolve({
    ok: true,
    json: async () => ({
      stage_id: delayedPayload.stage_id,
      analysis: { stage: delayedPayload.stage_id },
      feedback: {
        "Current Goal": "Goal", "Primary Feedback": "Old result", "What's Working": [],
        "Needs Attention": [], "Next Step": "Review",
      },
    }),
  });
  await pendingAnalysis;
  assert.equal(value(stalePage, "state.analyses.INTRODUCTION"), undefined);
  assert.equal(stalePage.elements["feedback-content"].hidden, true);
    assert.equal(stalePage.elements["guided-state-label"].dataset.state, "CHECKING");
  assert.equal(stalePage.elements["guided-topic-status"].dataset.state, "NOT_CHECKED");
  await click(stalePage.tabs[1]);

  const guidedTopic = guidedScenarios.topic;
  const guidedFocus = guidedScenarios.focus.join(", ");
  const writesBeforeGuided = persistenceWrites.length;
  const emptyGuidedPage = makeWorkspace(fetch, new Map());
  await waitForRestoration(emptyGuidedPage);
  await click(emptyGuidedPage.appLinks.find((link) => link.dataset.appLink === "workspace"));
  assert.equal(emptyGuidedPage.elements["guided-state-label"].dataset.state, "NOT_STARTED");
  assert.match(emptyGuidedPage.elements["guided-state-message"].textContent, /Start writing your Introduction/);
  assert.equal(emptyGuidedPage.tabs[1].disabled, false, "Body stays accessible without a hard lock");

  const shortText = guidedScenarios.short_complete.analysis.input_text;
  const completeGuidedPage = await analyzeGuidedScenario({
    topic: guidedTopic, focus: guidedFocus, text: shortText,
    response: guidedScenarios.short_complete,
  });
  assert.equal(completeGuidedPage.elements["guided-state-label"].dataset.state, "NEUTRAL");
  assert.equal(completeGuidedPage.elements["guided-topic-status"].dataset.state, "DETECTED");
  assert.equal(completeGuidedPage.elements["guided-thought-status"].dataset.state, "DETECTED");
  assert.equal(completeGuidedPage.elements["guided-position-status"].textContent, "Not Checked");
  const requestsBeforeGuidedChecks = analysisRequests.length;
  completeGuidedPage.elements["guided-position-confirmed"].checked = true;
  await change(completeGuidedPage.elements["guided-position-confirmed"]);
  assert.equal(completeGuidedPage.elements["guided-state-label"].dataset.state, "NEUTRAL");
  assert.equal(analysisRequests.length, requestsBeforeGuidedChecks);
  completeGuidedPage.elements["stage-text"].value = `${shortText}!`;
  await input(completeGuidedPage.elements["stage-text"]);
  assert.equal(completeGuidedPage.elements["guided-position-confirmed"].checked, true,
    "punctuation and ordinary typing do not repeatedly clear a self-check");
  assert.equal(completeGuidedPage.elements["guided-state-label"].dataset.state, "CHECKING");
  completeGuidedPage.elements["stage-text"].value = shortText;
  await input(completeGuidedPage.elements["stage-text"]);
  analysisResponseOverride = guidedScenarios.short_complete;
  await runTimers(completeGuidedPage, 6000);
  assert.equal(completeGuidedPage.elements["guided-position-confirmed"].checked, true);
  assert.equal(completeGuidedPage.elements["guided-state-label"].dataset.state, "NEUTRAL");
  const requestsBeforeCompletingGuidedChecks = analysisRequests.length;
  completeGuidedPage.elements["guided-direction-confirmed"].checked = true;
  await change(completeGuidedPage.elements["guided-direction-confirmed"]);
  assert.equal(completeGuidedPage.elements["guided-position-status"].textContent, "Student Confirmed");
  assert.equal(completeGuidedPage.elements["guided-direction-status"].textContent, "Student Confirmed");
  assert.equal(completeGuidedPage.elements["guided-state-label"].dataset.state, "CHECKLIST_COMPLETE");
  assert.equal(completeGuidedPage.elements["guided-continue-to-body"].hidden, false);
  assert.equal(completeGuidedPage.elements["guided-review-suggestions"].hidden, true);
  assert.equal(analysisRequests.length, requestsBeforeCompletingGuidedChecks,
    "the checklist and self-checks reuse the one Introduction analysis response");
  value(completeGuidedPage, 'state.drafts.BODY = "Existing Body draft."; state.drafts.CONCLUSION = "Existing Conclusion draft."');
  const completeIntro = completeGuidedPage.elements["stage-text"].value;
  await click(completeGuidedPage.elements["guided-continue-to-body"]);
  assert.equal(value(completeGuidedPage, "state.currentStage"), "BODY");
  assert.equal(completeGuidedPage.elements["introduction-guided-progression"].hidden, true);
  assert.equal(completeGuidedPage.elements["stage-text"].value, "Existing Body draft.");
  assert.equal(value(completeGuidedPage, "state.drafts.INTRODUCTION"), completeIntro);
  assert.equal(value(completeGuidedPage, "state.drafts.CONCLUSION"), "Existing Conclusion draft.");
  assert.equal(completeGuidedPage.tabs[1].disabled, false);
  await click(completeGuidedPage.tabs[0]);
  assert.equal(completeGuidedPage.elements["introduction-guided-progression"].hidden, false);
  assert.equal(completeGuidedPage.elements["guided-state-label"].dataset.state, "CHECKLIST_COMPLETE",
    "the completed checklist remains available when returning to Introduction");
  assert.equal(completeGuidedPage.elements["guided-continue-to-body"].hidden, false);
  assert.equal(completeGuidedPage.elements["stage-text"].value, completeIntro,
    "returning to Introduction preserves the student's current writing");
  completeGuidedPage.elements["stage-text"].value = "Artificial intelligence does not help students learn.";
  await input(completeGuidedPage.elements["stage-text"]);
  assert.equal(completeGuidedPage.elements["guided-position-confirmed"].checked, false,
    "a substantial wording change asks the student to confirm again");
  assert.equal(completeGuidedPage.elements["guided-state-label"].dataset.state, "CHECKING");
  assert.equal(completeGuidedPage.elements["guided-topic-status"].dataset.state, "NOT_CHECKED",
    "old automatic evidence is not shown as current after an edit");
  assert.equal(value(completeGuidedPage, "state.analyses.INTRODUCTION"), undefined);
  assert.equal(value(completeGuidedPage, "state.drafts.BODY"), "Existing Body draft.");
  assert.equal(value(completeGuidedPage, "state.drafts.CONCLUSION"), "Existing Conclusion draft.");
  assert.equal(persistenceWrites.length, writesBeforeGuided,
    "checklist changes and navigation do not save, revise, or submit writing");

  const paraphraseText = guidedScenarios.paraphrase.analysis.input_text;
  const reviewGuidedPage = await analyzeGuidedScenario({
    topic: guidedTopic, focus: guidedFocus, text: paraphraseText,
    response: guidedScenarios.paraphrase,
  });
  assert.equal(reviewGuidedPage.elements["guided-state-label"].dataset.state, "REVIEW_SUGGESTED");
  assert.equal(reviewGuidedPage.elements["guided-topic-status"].dataset.state, "REVIEW_SUGGESTED");
  assert.equal(reviewGuidedPage.elements["guided-thought-status"].dataset.state, "DETECTED");
  assert.match(reviewGuidedPage.elements["guided-topic-note"].textContent, /couldn't find your assignment's focus words/i);
  assert.equal(reviewGuidedPage.elements["guided-review-suggestions"].hidden, false);
  assert.equal(reviewGuidedPage.elements["guided-continue-anyway"].hidden, false);
  const requestCountBeforeReview = analysisRequests.length;
  await click(reviewGuidedPage.elements["guided-review-suggestions"]);
  assert.equal(reviewGuidedPage.elements["guided-item-topic"].focused, true);
  assert.deepEqual(reviewGuidedPage.elements["guided-item-topic"].scrollOptions, { behavior: "smooth", block: "center" });
  assert.equal(analysisRequests.length, requestCountBeforeReview,
    "Review Suggestions inspects existing evidence without requesting another NLP analysis");
  const reviewEvidence = value(reviewGuidedPage, "state.analyses.INTRODUCTION");
  value(reviewGuidedPage, 'state.drafts.BODY = "Body text stays here."; state.drafts.CONCLUSION = "Conclusion text stays here."');
  await click(reviewGuidedPage.elements["guided-continue-anyway"]);
  assert.equal(value(reviewGuidedPage, "state.currentStage"), "BODY");
  assert.equal(value(reviewGuidedPage, "state.analyses.INTRODUCTION"), reviewEvidence,
    "Continue Anyway does not alter detection evidence");
  assert.equal(reviewGuidedPage.elements["stage-text"].value, "Body text stays here.");
  assert.equal(value(reviewGuidedPage, "state.drafts.CONCLUSION"), "Conclusion text stays here.");

  const derivedText = guidedScenarios.derived_unavailable.analysis.input_text;
  const unavailableGuidedPage = await analyzeGuidedScenario({
    topic: "Effects of urban noise on health", focus: "", text: derivedText,
    response: guidedScenarios.derived_unavailable,
  });
  assert.equal(unavailableGuidedPage.elements["guided-topic-status"].dataset.state, "UNAVAILABLE");
  assert.match(unavailableGuidedPage.elements["guided-topic-note"].textContent, /No configured focus words/i);
  assert.equal(unavailableGuidedPage.elements["guided-state-label"].dataset.state, "REVIEW_SUGGESTED",
    "an unavailable topic check is not treated as an automatic failure");

  const sinceText = guidedScenarios.since.analysis.input_text;
  const sinceGuidedPage = await analyzeGuidedScenario({
    topic: guidedTopic, focus: "students, technology, artificial intelligence", text: sinceText,
    response: guidedScenarios.since,
  });
  assert.deepEqual(guidedScenarios.since.analysis.observable_structure.incomplete_subordinator_candidates, []);
  assert.equal(sinceGuidedPage.elements["guided-thought-status"].dataset.state, "REVIEW_SUGGESTED",
    "a valid Since sentence with no detected root candidate remains advisory");
  assert.equal(sinceGuidedPage.elements["guided-continue-anyway"].hidden, false);

  const whetherText = guidedScenarios.whether.analysis.input_text;
  const whetherGuidedPage = await analyzeGuidedScenario({
    topic: guidedTopic, focus: guidedFocus, text: whetherText,
    response: guidedScenarios.whether,
  });
  assert.deepEqual(guidedScenarios.whether.analysis.observable_structure.incomplete_subordinator_candidates, []);
  assert.equal(whetherGuidedPage.elements["guided-thought-status"].dataset.state, "DETECTED");
  assert.equal(whetherGuidedPage.elements["guided-topic-status"].dataset.state, "DETECTED");

  const unablePage = makeWorkspace(fetch, new Map());
  await waitForRestoration(unablePage);
  await click(unablePage.appLinks.find((link) => link.dataset.appLink === "workspace"));
  unablePage.elements["assignment-topic"].value = guidedTopic;
  unablePage.elements["focus-terms"].value = guidedFocus;
  unablePage.elements["stage-text"].value = shortText;
  await input(unablePage.elements["stage-text"]);
  failNextAnalysis = true;
  await runTimers(unablePage, 6000);
  assert.equal(unablePage.elements["guided-state-label"].dataset.state, "UNABLE_TO_CHECK");
  assert.equal(unablePage.elements["guided-state-message"].textContent,
    "EssayScaff couldn't check your Introduction right now. You can try again or continue.");
  assert.equal(unablePage.elements["guided-continue-anyway"].hidden, false);

  const changedAssignmentPage = await analyzeGuidedScenario({
    topic: guidedTopic, focus: guidedFocus, text: shortText,
    response: guidedScenarios.short_complete,
  });
  changedAssignmentPage.elements["guided-position-confirmed"].checked = true;
  await change(changedAssignmentPage.elements["guided-position-confirmed"]);
  changedAssignmentPage.elements["guided-direction-confirmed"].checked = true;
  await change(changedAssignmentPage.elements["guided-direction-confirmed"]);
  assert.equal(changedAssignmentPage.elements["guided-state-label"].dataset.state, "CHECKLIST_COMPLETE");
  changedAssignmentPage.elements["assignment-topic"].value = "A different assignment topic";
  await input(changedAssignmentPage.elements["assignment-topic"]);
  assert.equal(changedAssignmentPage.elements["guided-state-label"].dataset.state, "CHECKING");
  assert.equal(changedAssignmentPage.elements["guided-position-confirmed"].checked, false);
  assert.equal(value(changedAssignmentPage, "state.analyses.INTRODUCTION"), undefined);

  const stageStalePage = makeWorkspace(fetch, new Map());
  await waitForRestoration(stageStalePage);
  await click(stageStalePage.appLinks.find((link) => link.dataset.appLink === "workspace"));
  stageStalePage.elements["assignment-topic"].value = guidedTopic;
  stageStalePage.elements["focus-terms"].value = guidedFocus;
  stageStalePage.elements["stage-text"].value = shortText;
  await input(stageStalePage.elements["stage-text"]);
  holdNextAnalysis = true;
  delayedAnalysisResolve = null;
  delayedAnalysisSignal = null;
  analysisResponseOverride = guidedScenarios.short_complete;
  const stageStaleListener = stageStalePage.elements["analyze-button"].listeners.click[0];
  const pendingStageAnalysis = stageStaleListener({});
  for (let attempt = 0; attempt < 5 && delayedAnalysisResolve === null; attempt++) {
    await new Promise((resolve) => setImmediate(resolve));
  }
  assert.ok(delayedAnalysisSignal);
  await click(stageStalePage.tabs[1]);
   assert.equal(delayedAnalysisSignal.aborted, false);
  delayedAnalysisResolve({ ok: true, json: async () => guidedScenarios.short_complete });
  await pendingStageAnalysis;
  assert.equal(value(stageStalePage, "state.analyses.INTRODUCTION"), undefined);
  assert.equal(stageStalePage.elements["introduction-guided-progression"].hidden, true);
  assert.equal(stageStalePage.tabs[1].disabled, false);
})().catch((error) => { console.error(error); process.exitCode = 1; });
'''
    if scenario is not None:
        setup, separator, _ = script.partition("(async () => {")
        assert separator
        script = setup + scenario
    sample_text = "Students build knowledge with daily reading. <script>alert('x')</script> Reading also helps learners."
    actual = EssayAnalysisService().analyze(
        "Reading habits",
        ["reading", "students"],
        introduction_text="Students should read every day to build knowledge.",
        body_text=sample_text,
        conclusion_text="Daily reading helps students learn across subjects.",
        include_research_trace=True,
    )
    guided_service = EssayAnalysisService()

    def guided_response(text, topic, focus_terms):
        combined = guided_service.analyze(
            topic,
            focus_terms,
            introduction_text=text,
            include_research_trace=True,
        )
        stage = combined["stages"]["INTRODUCTION"]
        trace = combined["research_trace"]
        return {
            "stage_id": "INTRODUCTION",
            "availability": stage["availability"],
            "analysis": stage["analysis"],
            "feedback": stage["feedback"],
            "interpretation_limit": combined["interpretation_limit"],
            "research_trace": {
                **trace,
                "selected_stage": "INTRODUCTION",
                "stages": {"INTRODUCTION": trace["stages"]["INTRODUCTION"]},
            },
        }

    guided_scenarios = {
        "topic": "Should schools allow students to use artificial intelligence tools for learning?",
        "focus": ["artificial intelligence", "education", "students", "technology", "critical thinking"],
        "short_complete": guided_response(
            "Artificial intelligence helps students learn.",
            "Should schools allow students to use artificial intelligence tools for learning?",
            ["artificial intelligence", "education", "students", "technology", "critical thinking"],
        ),
        "paraphrase": guided_response(
            "Public buses help commuters travel. Cities can add more routes.",
            "Should schools allow students to use artificial intelligence tools for learning?",
            ["artificial intelligence", "education", "students", "technology", "critical thinking"],
        ),
        "since": guided_response(
            "Since the beginning of time, students have used technology, but AI changes how they can learn and work.",
            "Should schools allow students to use artificial intelligence tools for learning?",
            ["students", "technology", "artificial intelligence"],
        ),
        "whether": guided_response(
            "Whether we use AI to improve education.",
            "Should schools allow students to use artificial intelligence tools for learning?",
            ["artificial intelligence", "education", "students", "technology", "critical thinking"],
        ),
        "derived_unavailable": guided_response(
            "Students build gardens and share vegetables.",
            "Effects of urban noise on health",
            None,
        ),
    }
    analysis_responses = {}
    for stage_id, stage in actual["stages"].items():
        selected_trace = dict(actual["research_trace"]["stages"][stage_id])
        input_sections = dict(selected_trace.get("input_sections", {}))
        input_sections.pop(stage_id.casefold(), None)
        selected_trace["input_sections"] = input_sections
        if stage_id != "BODY":
            selected_trace.pop("linguistic_observations", None)
        selected_trace.pop("rule_evaluation_trace", None)
        selected_trace.pop("cross_stage_comparison_inputs", None)
        topic_trace = dict(selected_trace["topic_service"])
        topic_trace["steps"] = [
            {key: value for key, value in step.items() if not (step["id"] == "topic_matching" and key == "output")}
            for step in topic_trace["steps"]
        ]
        selected_trace["topic_service"] = topic_trace
        response_analysis = dict(stage["analysis"])
        if stage_id == "INTRODUCTION":
            response_analysis.pop("input_text", None)
        response_feedback = dict(stage["feedback"])
        response_feedback["Feedback Provenance"] = [
            {key: item[key] for key in ("feedback_field", "rule_id") if key in item}
            for item in stage["feedback"]["Feedback Provenance"]
        ]
        analysis_responses[stage_id] = {
            "stage_id": stage["stage_id"],
            "availability": stage["availability"],
            "analysis": response_analysis,
            "feedback": response_feedback,
            "interpretation_limit": actual["interpretation_limit"],
            "research_trace": {
                **actual["research_trace"],
                "selected_stage": stage_id,
                "stages": {stage_id: selected_trace},
            },
        }
    analysis_responses["GUIDED_SCENARIOS"] = guided_scenarios
    analysis_responses.update(extra_responses or {})
    analysis_path = tmp_path / "real-analysis-response.json"
    analysis_path.write_text(json.dumps(analysis_responses), encoding="utf-8")
    harness_path = tmp_path / "workspace_frontend_harness.js"
    harness_path.write_text(script, encoding="utf-8")
    completed = subprocess.run(
        [NODE, str(harness_path), str(app_js), str(analysis_path), str(lesson_path)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    if scenario is not None:
        assert "Feedback presentation scenarios completed." in completed.stdout, completed.stdout + completed.stderr


def test_feedback_presentation_preserves_messages_and_disclosure_state(tmp_path) -> None:
    scenario = r'''
const assertRenderedFeedback = (page, response) => {
  const e = page.elements;
  page.context.expectedResponse=response;
  const presentation=value(page,"studentFeedbackPresentation(expectedResponse)");
  assert.equal(e["feedback-content"].hidden, false);
  assert.equal(e["feedback-placeholder"].hidden, true);
  const primary = presentation.tutor_items[0];
  assert.equal(e["tutor-noticed"].textContent, primary.noticed);
  assert.equal(e["tutor-why"].textContent, primary.why);
  assert.equal(e["tutor-task"].textContent, primary.task_text);
  assert.equal(e["feedback-writing-focus"].textContent,primary.role==="NO_SUPPORTED_CONCERN_SELECTED"?primary.label:presentation.displayed_dimension_label||"");
  for (const [id, field, fallback] of [
    ["whats-working", "What's Working", "No positive observation was recorded by these checks."],
    ["needs-attention", "Needs Attention", "No additional issue was flagged by the available checks."],
  ]) {
    const raw = response.feedback[field];
    const items = Array.isArray(raw) ? raw : raw ? [raw] : [];
    assert.deepEqual(e[id].children.map(child => child.textContent), items.length ? items : [fallback]);
  }
  assert.equal(e["interpretation-limit"].textContent, presentation.displayed_limitation);
};

(async () => {
  const networkCalls = [];
  const trackedFetch = (url, options) => { networkCalls.push(url); return fetch(url, options); };
  const page = makeWorkspace(trackedFetch, new Map());
  await waitForRestoration(page);
  await click(page.appLinks.find(link => link.dataset.appLink === "workspace"));
  const e = page.elements;
  assert.equal(e["feedback-details"].open, false);
  assert.equal(e["feedback-content"].hidden, true);
  e["assignment-topic"].value = "Reading habits";
  e["focus-terms"].value = "reading, students";
  const texts = [
    "Students should read every day to build knowledge.",
    "Students build knowledge with daily reading. <script>alert('x')</script> Reading also helps learners.",
    "Daily reading helps students learn across subjects.",
  ];
  for (const [index, stage] of ["INTRODUCTION", "BODY", "CONCLUSION"].entries()) {
    await click(page.tabs[index]);
    assert.equal(e["feedback-content"].hidden, true);
    e["stage-text"].value = texts[index];
    await input(e["stage-text"]);
    analysisResponseOverride = actualStageResponses[stage];
    await click(e["analyze-button"]);
    assertRenderedFeedback(page, actualStageResponses[stage]);
    assert.equal(e["feedback-details"].open, index > 0);
    assert.equal(e["copy-full-analysis"].disabled, false);
    if (index === 0) {
      const stateBefore = value(page, "JSON.stringify(state)");
      const callsBefore = networkCalls.length;
      const timersBefore = page.timers.size;
      for (const open of [true, false, true]) {
        e["feedback-details"].open = open;
        await dispatch(e["feedback-details"], "toggle");
      }
      assert.equal(networkCalls.length, callsBefore, "disclosure toggles issue no network requests");
      assert.equal(page.timers.size, timersBefore, "disclosure toggles schedule no analysis");
      assert.equal(value(page, "JSON.stringify(state)"), stateBefore);
    }
  }
  const callsBeforeCache = networkCalls.length;
  await click(page.tabs[0]);
  assertRenderedFeedback(page, actualStageResponses.INTRODUCTION);
  assert.equal(e["feedback-details"].open, true);
  assert.equal(networkCalls.length, callsBeforeCache, "cached stage feedback needs no new request");

  e["stage-text"].value += " Updated.";
  await input(e["stage-text"]);
  assert.equal(e["feedback-content"].hidden, true);
  assert.equal(e["feedback-placeholder"].hidden, false);
  assert.equal(e["feedback-details"].open, true);
  analysisResponseOverride = actualStageResponses.INTRODUCTION;
  await runTimers(page, 6000);
  assert.equal(e["feedback-content"].hidden, true, "mismatched response source is rejected");
  e["stage-text"].value = texts[0];
  await input(e["stage-text"]);
  await runTimers(page,1000);
  assertRenderedFeedback(page, actualStageResponses.INTRODUCTION);
  assert.equal(e["feedback-details"].open, true, "live updates preserve the open state");
  e["feedback-details"].open = false;
  await click(e["analyze-button"]);
  assert.equal(e["feedback-details"].open, false, "manual analysis preserves the closed state");

  const saving = click(e["save-button"]);
  completeSave();
  await saving;
  await click(e["my-classroom-list"].children[0].children[0]);
  e["feedback-details"].open = true;
  await startAssignment(e["available-assignment-list"].children[0].children[0].children[3], page);
  assert.equal(value(page, "state.assignmentId"), 101);
  assert.equal(e["feedback-content"].hidden, true);
  assert.equal(e["feedback-details"].open, true);
  e["stage-text"].value = texts[0];
  await input(e["stage-text"]);
  await click(e["analyze-button"]);
  assertRenderedFeedback(page, actualStageResponses.INTRODUCTION);
  await click(e["save-button"]);
  await startAssignment(e["available-assignment-list"].children[1].children[0].children[3], page);
  assert.equal(value(page, "state.assignmentId"), 102);
  assert.equal(e["feedback-content"].hidden, true, "a different assignment hides the old feedback");
  assert.equal(e["feedback-details"].open, true);

  e["stage-text"].value = "An older pending Introduction.";
  await input(e["stage-text"]);
  holdNextAnalysis = true;
  delayedAnalysisResolve = null;
  delayedAnalysisSignal = null;
  const pendingAnalysis = e["analyze-button"].listeners.click[0]({});
  for (let attempt = 0; attempt < 5 && delayedAnalysisResolve === null; attempt++) {
    await new Promise(resolve => setImmediate(resolve));
  }
  assert.ok(delayedAnalysisSignal);
  await click(page.tabs[1]);
  assert.equal(delayedAnalysisSignal.aborted, false);
  delayedAnalysisResolve({ok: true, json: async () => actualStageResponses.INTRODUCTION});
  await pendingAnalysis;
  assert.equal(e["feedback-content"].hidden, true, "late results must not expose stale feedback");
  assert.equal(value(page, "state.analyses.INTRODUCTION"), undefined);

  const freshPage = makeWorkspace(trackedFetch, new Map());
  await waitForRestoration(freshPage);
  assert.equal(freshPage.elements["feedback-details"].open, false, "a new page starts closed");
  const longMessage = "Complete observation — café <script>literal text</script>. ".repeat(40);
  const result = {
    analysis: {},
    feedback: {
      "Current Goal": longMessage, "Primary Feedback": longMessage + " Check.", "Next Step": longMessage + " Next.",
      "What's Working": [longMessage + " First.", "Second positive observation."],
      "Needs Attention": ["First issue.", longMessage + " Second."],
    },
    interpretation_limit: "Existing limitation.",
  };
  freshPage.context.presentationResult = result;
  value(freshPage, "displayFeedback(presentationResult)");
  assertRenderedFeedback(freshPage, result);
  freshPage.elements["feedback-details"].open = true;
  value(freshPage, "displayFeedback(presentationResult)");
  assertRenderedFeedback(freshPage, result);
  assert.equal(freshPage.elements["feedback-details"].open, true);
  assert.equal(freshPage.elements["whats-working"].children.length, 2, "repeated updates do not duplicate list items");
  freshPage.context.presentationResult = {analysis:{}, feedback:{}, interpretation_limit:"Existing limitation."};
  value(freshPage, "displayFeedback(presentationResult)");
  assertRenderedFeedback(freshPage, freshPage.context.presentationResult);
  value(freshPage, "displayFeedback(null)");
  assert.equal(freshPage.elements["feedback-content"].hidden, true);
  assert.equal(freshPage.elements["feedback-placeholder"].hidden, false);
  assert.equal(freshPage.elements["copy-full-analysis"].disabled, true);
  console.log("Feedback presentation scenarios completed.");
})().catch(error => { console.error(error); process.exitCode = 1; });
'''
    _run_workspace_frontend(tmp_path, scenario)


def test_full_analysis_clipboard_success_failure_and_manual_fallback(tmp_path) -> None:
    scenario = r'''
(async () => {
  let calls=0;
  const page=makeWorkspace((url,options)=>{calls++;return fetch(url,options);},new Map());
  await waitForRestoration(page);
  await click(page.appLinks.find(link=>link.dataset.appLink==="workspace"));
  const e=page.elements, writes=[];
  let resolveCopy, rejectCopy;
  page.context.navigator={clipboard:{writeText:text=>{
    writes.push(text); return new Promise((resolve,reject)=>{resolveCopy=resolve;rejectCopy=reject;});
  },get readText(){throw new Error("Clipboard reads are forbidden");}}};
  assert.equal(e["copy-full-analysis"].disabled,true);
  await click(e["copy-full-analysis"]);
  assert.equal(writes.length,0);
  e["assignment-topic"].value="Reading habits";
  e["focus-terms"].value="reading, students";
  e["stage-text"].value="Students should read every day to build knowledge.";
  await input(e["stage-text"]);
  analysisResponseOverride=actualStageResponses.INTRODUCTION;
  await click(e["analyze-button"]);
  assert.equal(e["copy-full-analysis"].disabled,false);
  const dirtyBefore=value(page,"isDirty()");
  const stateBefore=value(page,"JSON.stringify(state)");
  const callsBefore=calls, timersBefore=page.timers.size, writesBefore=persistenceWrites.length;
  const pending=click(e["copy-full-analysis"]);
  assert.equal(e["analysis-copy-status"].textContent,"Copying full analysis…");
  assert.equal(e["copy-full-analysis"].disabled,true);
  assert.equal(e["analysis-copy-fallback"].hidden,true);
  assert.equal(writes.length,1);
  assert.notEqual(e["analysis-copy-status"].textContent,"Full analysis copied.");
  await click(e["copy-full-analysis"]);
  assert.equal(writes.length,1,"overlapping copies must not be started");
  resolveCopy(); await pending;
  assert.equal(e["analysis-copy-status"].textContent,"Full analysis copied.");
  assert.equal(e["copy-full-analysis"].disabled,false);
  assert.ok(writes[0].endsWith("END OF FULL ANALYSIS"));

  const denied=click(e["copy-full-analysis"]);
  rejectCopy(new Error("Clipboard permission denied")); await denied;
  assert.notEqual(e["analysis-copy-status"].textContent,"Full analysis copied.");
  assert.match(e["analysis-copy-status"].textContent,/unavailable or blocked/);
  assert.equal(e["analysis-copy-fallback"].hidden,false);
  assert.equal(e["full-analysis-report"].readOnly,true);
  assert.equal(e["full-analysis-report"].value,writes[1]);
  assert.equal(e["full-analysis-report"].selected,true);
  assert.equal(e["full-analysis-report"].selectionEnd,writes[1].length);
  assert.equal(e["full-analysis-report"].focused,true);

  page.context.navigator={clipboard:{writeText:async text=>{writes.push(text);}}};
  await click(e["copy-full-analysis"]);
  assert.equal(e["analysis-copy-status"].textContent,"Full analysis copied.");
  assert.equal(e["analysis-copy-fallback"].hidden,true);
  assert.equal(e["full-analysis-report"].value,"");
  delete page.context.navigator;
  await click(e["copy-full-analysis"]);
  assert.equal(e["analysis-copy-fallback"].hidden,false,"missing Clipboard API exposes manual copy");
  assert.equal(e["full-analysis-report"].value,writes[0]);
  assert.equal(calls,callsBefore,"copy success, failure, retry and fallback perform no requests");
  assert.equal(page.timers.size,timersBefore);
  assert.equal(persistenceWrites.length,writesBefore);
  assert.equal(value(page,"JSON.stringify(state)"),stateBefore);
  assert.equal(value(page,"isDirty()"),dirtyBefore);
  e["stage-text"].value+=" Changed.";
  await input(e["stage-text"]);
  assert.equal(e["copy-full-analysis"].disabled,true);
  assert.equal(e["analysis-copy-fallback"].hidden,true);
  assert.equal(e["full-analysis-report"].value,"");
  const callsBeforeInvalidCopy=calls;
  await click(e["copy-full-analysis"]);
  assert.equal(calls,callsBeforeInvalidCopy);
  console.log("Feedback presentation scenarios completed.");
})().catch(error=>{console.error(error);process.exitCode=1;});
'''
    _run_workspace_frontend(tmp_path, scenario)


def test_full_analysis_stale_async_context_navigation_and_workflow_guards(tmp_path) -> None:
    scenario = r'''
(async () => {
  const page=makeWorkspace(fetch,new Map());
  await waitForRestoration(page);
  await click(page.appLinks.find(link=>link.dataset.appLink==="workspace"));
  const e=page.elements, writes=[];
  e["assignment-topic"].value="Reading habits";
  e["focus-terms"].value="reading, students";
  e["stage-text"].value="Students should read every day to build knowledge.";
  await input(e["stage-text"]);
  failNextAnalysis=true;
  await click(e["analyze-button"]);
  assert.equal(e["copy-full-analysis"].disabled,true,"failed initial analysis does not enable export");
  analysisResponseOverride=actualStageResponses.INTRODUCTION;
  await click(e["analyze-button"]);
  assert.equal(e["copy-full-analysis"].disabled,false);
  let finishCopy, failCopy;
  page.context.navigator={clipboard:{writeText:text=>{writes.push(text);return new Promise((resolve,reject)=>{finishCopy=resolve;failCopy=reject;});}}};
  const copying=click(e["copy-full-analysis"]);
  e["stage-text"].value+=" New draft.";
  await input(e["stage-text"]);
  assert.equal(e["copy-full-analysis"].disabled,true);
  finishCopy(); await copying;
  assert.notEqual(e["analysis-copy-status"].textContent,"Full analysis copied.");
  assert.match(e["analysis-copy-status"].textContent,/earlier analysis/);
  assert.equal(e["analysis-copy-fallback"].hidden,true);
  analysisResponseOverride=actualStageResponses.INTRODUCTION;
  e["stage-text"].value=actualStageResponses.INTRODUCTION.analysis.linguistic_observations.text;
  await input(e["stage-text"]);
  await click(e["analyze-button"]);
  const switchingCopy=click(e["copy-full-analysis"]);
  await click(page.tabs[1]);
  assert.equal(e["copy-full-analysis"].disabled,true);
  e["stage-text"].value=actualStageResponses.BODY.research_trace.stages.BODY.linguistic_observations.text;
  await input(e["stage-text"]);
  analysisResponseOverride=actualStageResponses.BODY;
  await click(e["analyze-button"]);
  assert.equal(e["copy-full-analysis"].disabled,true,"a previous native write must finish before another copy can start");
  failCopy(new Error("Denied after stage switch")); await switchingCopy;
  assert.equal(e["analysis-copy-fallback"].hidden,true,"a late failure must not expose another stage's report");
  assert.equal(e["copy-full-analysis"].disabled,false);
  assert.notEqual(e["analysis-copy-status"].textContent,"Full analysis copied.");
  page.context.navigator={clipboard:{writeText:async text=>{writes.push(text);}}};
  await click(e["copy-full-analysis"]);
  assert.match(writes.at(-1),/Writing stage[^\n]*\nBODY/);
  const requestCount=analysisRequests.length;
  await click(page.tabs[0]);
  assert.equal(e["copy-full-analysis"].disabled,false,"cached current-stage analysis can be copied");
  await click(page.tabs[3]);
  assert.equal(e["copy-full-analysis"].disabled,true,"Essay Review must not export a hidden prior stage as current");
  await click(page.tabs[0]);
  await click(page.appLinks.find(link=>link.dataset.appLink==="dashboard"));
  assert.equal(e["copy-full-analysis"].disabled,true);
  await click(page.appLinks.find(link=>link.dataset.appLink==="workspace"));
  assert.equal(e["copy-full-analysis"].disabled,false);
  assert.equal(analysisRequests.length,requestCount);

  const editor=e["stage-text"].value;
  await click(e["open-introduction-lesson"]);
  assert.equal(e["introduction-lesson-panel"].hidden,false);
  assert.equal(e["stage-text"].value,editor);
  await click(e["introduction-lesson-return"]);
  assert.equal(e["introduction-lesson-panel"].hidden,true);
  assert.equal(analysisRequests.length,requestCount);
  e["focus-terms"].value="changed focus";
  await input(e["focus-terms"]);
  assert.equal(e["copy-full-analysis"].disabled,true,"changed focus invalidates export");
  analysisResponseOverride=actualStageResponses.INTRODUCTION;
  e["stage-text"].value=actualStageResponses.INTRODUCTION.analysis.linguistic_observations.text;
  await click(e["analyze-button"]);
  const good=value(page,"state.analyses.INTRODUCTION");
  e["stage-text"].value+=" Programmatic edit without an input event.";
  const beforeInvalid=writes.length;
  await click(e["copy-full-analysis"]);
  assert.equal(writes.length,beforeInvalid,"the click-time guard also checks the live editor");
  assert.equal(e["copy-full-analysis"].disabled,true);
  await input(e["stage-text"]);
  holdNextAnalysis=true; delayedAnalysisResolve=null;
  const lateAnalysis=e["analyze-button"].listeners.click[0]({});
  for(let i=0;i<5 && delayedAnalysisResolve===null;i++) await new Promise(resolve=>setImmediate(resolve));
  await click(page.tabs[2]);
  delayedAnalysisResolve({ok:true,json:async()=>good}); await lateAnalysis;
  assert.equal(e["copy-full-analysis"].disabled,true,"stale network responses cannot re-enable export");
  await click(page.tabs[0]);
  analysisResponseOverride=null;
  await click(e["analyze-button"]);
  const saving=click(e["save-button"]); completeSave(); await saving;
  assert.equal(e["save-status"].textContent,"Draft saved");
  await click(e["save-revision-button"]);
  assert.match(e["revision-save-status"].textContent,/Revision 1 saved/);
  await click(e["my-classroom-list"].children[0].children[0]);
  await startAssignment(e["available-assignment-list"].children[0].children[0].children[3],page);
  assert.equal(value(page,"state.assignmentId"),101);
  assert.equal(e["copy-full-analysis"].disabled,true,"another assignment must not reuse practice analysis");
  assert.equal(e["full-analysis-report"].value,"");
  console.log("Feedback presentation scenarios completed.");
})().catch(error=>{console.error(error);process.exitCode=1;});
'''
    _run_workspace_frontend(tmp_path, scenario)


def test_writing_tutor_states_tabs_and_highlight_integrity(tmp_path) -> None:
    from tests.test_reason_highlighting import _make_stage_payload

    # Exercise tabs with a REAL Body decision, rather than the old synthetic
    # focus-absence warning (word absence must not force a corrective lesson).
    body_tabs = EssayAnalysisService().analyze(
        "Reading habits", ["reading", "students"],
        introduction_text="Because the library stays open late, students read more.",
        body_text="Public transit reduces traffic. Public transit lowers pollution.\n\nPublic transit reduces delays.",
        include_research_trace=True,
    )
    scenario = r'''
(async () => {
  const page = makeWorkspace(fetch, new Map());
  await waitForRestoration(page);
  await click(page.appLinks.find(link => link.dataset.appLink === "workspace"));
  const e = page.elements;

  assert.equal(e["feedback-placeholder"].hidden, false);
  assert.equal(e["tutor-state-title"].textContent, "Start writing your essay. I'll help you review it as you write.");
  assert.equal(e["tutor-typing-dots"].hidden, true);

  e["assignment-topic"].value = "Reading habits";
  e["focus-terms"].value = "reading, students";
  e["stage-text"].value = "Because the library stays open late.";
  await input(e["stage-text"]);
  assert.equal(e["tutor-state-title"].textContent, "You're writing…");
  assert.equal(e["tutor-typing-dots"].hidden, false);
  await runTimers(page, 350);
  assert.equal(e["tutor-state-title"].textContent, "Checking your latest writing…");
  assert.equal(e["tutor-typing-dots"].hidden, true);

  const introSource = "Because the library stays open late, students read more.";
  const goodOffset = { text: "Because", start: 0, end: 7 };
  const goodResponse = {
    stage_id: "INTRODUCTION",
    availability: "ANALYZED",
    interpretation_limit: "Observation only.",
    analysis: {
      stage: "INTRODUCTION",
      input_text: introSource,
      linguistic_observations: {
        text: introSource,
        tokens: [{ text: "Because", start: 0, end: 7, pos: "SCONJ", dependency: "mark" }],
        sentences: [{ text: introSource, start: 0, end: 56 }],
      },
      observable_structure: {
        incomplete_subordinator_candidates: [
          { text: "Because", start: 0, end: 7, sentence_index: 0, pos: "SCONJ", dependency: "mark" },
        ],
      },
      rule_evidence: [
        {
          rule_id: "INTRO.CLAUSE.POSSIBLE_INCOMPLETE_SUBORDINATOR",
          triggered: true,
          fired: true,
          actual_evidence: [{ ...goodOffset, pos: "SCONJ", sentence_index: 0, dependency: "mark" }],
        },
      ],
    },
    feedback: {
      "Current Goal": "Goal",
      "Primary Feedback": "The parser-based checks recorded a possible incomplete dependent clause.",
      "What's Working": [],
      "Needs Attention": [],
      "Next Step": "Connect the clause.",
      "Feedback Provenance": [
        { feedback_field: "Primary Feedback", rule_id: "INTRO.CLAUSE.POSSIBLE_INCOMPLETE_SUBORDINATOR" },
      ],
    },
    research_trace: {
      selected_stage: "INTRODUCTION",
      stages: {
        INTRODUCTION: {
          feedback_decisions: {
            fields: {
              "Primary Feedback": {
                selection_branch: "intro_sentence_fluency_complete_sentence",
                selected_message: "The parser-based checks recorded a possible incomplete dependent clause.",
                rule_ids: ["INTRO.CLAUSE.POSSIBLE_INCOMPLETE_SUBORDINATOR"],
              },
            },
          },
        },
      },
    },
  };
  analysisResponseOverride = goodResponse;
  e["stage-text"].value = introSource;
  await input(e["stage-text"]);
  await click(e["analyze-button"]);
  assert.equal(e["feedback-content"].hidden, false);
  assert.equal(e["feedback-placeholder"].hidden, true);
  assert.equal(e["tutor-tabs"].children.length, 0, "single item hides the tab strip");
  assert.equal(e["tutor-tabs"].hidden, true);
  assert.equal(e["tutor-noticed"].textContent.includes("Because"), true);

  e["stage-text"].value = "The library stays open late.";
  await input(e["stage-text"]);
  assert.equal(e["feedback-content"].hidden, true);
  assert.equal(e["feedback-placeholder"].hidden, false);
  assert.equal(e["tutor-state-title"].textContent, "You're writing…");
  await runTimers(page, 350);
  assert.equal(e["tutor-state-title"].textContent, "Checking your latest writing…");
  assert.equal(value(page, "state.tutorStaleStages.INTRODUCTION"), true);
  analysisResponseOverride = goodResponse;
  await runTimers(page, 6000);
  assert.equal(e["feedback-content"].hidden, true, "mismatched source cannot update feedback");
  e["stage-text"].value = introSource;
  await input(e["stage-text"]);
  await click(e["analyze-button"]);
  assert.equal(e["feedback-content"].hidden, false);

  const multiResponse = actualStageResponses.BODY_TABS;
  const multiText = multiResponse.analysis.input_text;
  await click(page.tabs[1]);
  e["stage-text"].value = multiText;
  await input(e["stage-text"]);
  analysisResponseOverride = multiResponse;
  await click(e["analyze-button"]);
  assert.equal(e["feedback-content"].hidden, false);
  assert.equal(e["tutor-tabs"].children.length, 2, "primary plus one supported secondary item");
  assert.equal(e["tutor-noticed"].textContent.includes("Paragraph 2"), true);
  assert.equal(e["editor-mirror"].querySelectorAll("mark").length, 1);
  assert.equal(e["editor-mirror"].querySelector("mark").textContent,"Public transit reduces delays.");
  assert.equal(e["editor-mirror"].attributes["data-category"], "Ideas");
  assert.equal(e["tutor-evidence"].querySelector("mark") !== null, true);
  const secondButton = e["tutor-tabs"].children[1];
  assert.equal(secondButton.attributes["aria-selected"], "false");
  await dispatch(secondButton, "click");
  assert.equal(secondButton.attributes["aria-selected"], "true");
  assert.equal(e["editor-mirror"].querySelectorAll("mark").length, 2, "secondary repetition marks only its two source openings");
  assert.deepEqual(e["editor-mirror"].querySelectorAll("mark").map(m=>m.textContent),["Public transit","Public transit"]);
  assert.equal(e["editor-mirror"].attributes["data-category"],"Sentence Fluency");
  const firstButton = e["tutor-tabs"].children[0];
  await dispatch(firstButton, "click");
  assert.equal(firstButton.attributes["aria-selected"], "true");
  assert.equal(e["tutor-evidence"].querySelector("mark").textContent, "Public transit reduces delays.");

  const badSource = "Because the rain stopped the game.";
  const badOffset = { text: "Because", start: 99, end: 106 };
  const badResponse = {
    stage_id: "INTRODUCTION",
    availability: "ANALYZED",
    interpretation_limit: "Observation only.",
    analysis: {
      stage: "INTRODUCTION",
      input_text: badSource,
      linguistic_observations: {
        text: badSource,
        tokens: [{ text: "Because", start: 0, end: 7, pos: "SCONJ", dependency: "mark" }],
        sentences: [{ text: badSource, start: 0, end: 33 }],
      },
      observable_structure: {
        incomplete_subordinator_candidates: [
          { text: "Because", start: 0, end: 7, sentence_index: 0, pos: "SCONJ", dependency: "mark" },
        ],
      },
      rule_evidence: [
        {
          rule_id: "INTRO.CLAUSE.POSSIBLE_INCOMPLETE_SUBORDINATOR",
          triggered: true,
          fired: true,
          actual_evidence: [{ ...badOffset, pos: "SCONJ", sentence_index: 0, dependency: "mark" }],
        },
      ],
    },
    feedback: {
      "Current Goal": "Goal",
      "Primary Feedback": "The parser-based checks recorded a possible incomplete dependent clause.",
      "What's Working": [],
      "Needs Attention": [],
      "Next Step": "Connect the clause.",
      "Feedback Provenance": [
        { feedback_field: "Primary Feedback", rule_id: "INTRO.CLAUSE.POSSIBLE_INCOMPLETE_SUBORDINATOR" },
      ],
    },
    research_trace: {
      selected_stage: "INTRODUCTION",
      stages: {
        INTRODUCTION: {
          feedback_decisions: {
            fields: {
              "Primary Feedback": {
                selection_branch: "intro_sentence_fluency_complete_sentence",
                selected_message: "The parser-based checks recorded a possible incomplete dependent clause.",
                rule_ids: ["INTRO.CLAUSE.POSSIBLE_INCOMPLETE_SUBORDINATOR"],
              },
            },
          },
        },
      },
    },
  };
  await click(page.tabs[0]);
  e["stage-text"].value = badSource;
  await input(e["stage-text"]);
  analysisResponseOverride = badResponse;
  await click(e["analyze-button"]);
  assert.equal(e["feedback-content"].hidden, false);
  assert.equal(e["tutor-noticed"].textContent.includes("Because"), false, "unverified marker is not shown");
  assert.equal(e["tutor-evidence"].children[0].textContent, "No passage could be verified in your current text, so nothing is marked. Find the sentence that starts a thought and complete it.");
  assert.equal(e["tutor-evidence"].querySelector("mark") !== null, false, "invalid offsets fail closed with no highlight");
  assert.equal(e["editor-mirror"].querySelectorAll("mark").length, 0);
  console.log("Feedback presentation scenarios completed.");
})().catch(error=>{console.error(error);process.exitCode=1;});
'''
    _run_workspace_frontend(tmp_path, scenario, {"BODY_TABS": _make_stage_payload(body_tabs, "BODY")})


def test_essay_review_dashboard_summary_preview_editing_and_submission(tmp_path) -> None:
    scenario = r'''
(async () => {
  revisions.length = 0;
  recordedActivitySeconds = null;
  const settle = async () => {
    for (let attempt = 0; attempt < 8; attempt++) await new Promise((resolve) => setImmediate(resolve));
  };

  // Empty practice essay: the dashboard reports no writing without inventing data.
  const page = makeWorkspace(fetch, new Map());
  await waitForRestoration(page);
  await click(page.appLinks.find((link) => link.dataset.appLink === "workspace"));
  const e = page.elements;
  assert.equal(e["essay-review-panel"].hidden, true);
  await click(page.tabs[3]);
  await settle();
  assert.equal(e["essay-review-panel"].hidden, false);
  assert.equal(e["work-area"].hidden, true);
  assert.equal(e["review-summary-total-words"].textContent, "0");
  assert.equal(e["review-summary-sections"].textContent, "0 of 3");
  assert.equal(e["review-summary-revisions"].textContent, "0");
  assert.equal(e["review-summary-active-time"].textContent, "Not recorded");
  assert.equal(e["review-summary-remaining-time"].textContent, "Unavailable");
  assert.match(e["review-remaining-note"].textContent, /No word target/);
  assert.equal(e["review-submission-badge"].textContent, "Not submitted");
  assert.match(e["review-submission-note"].textContent, /classroom assignments/);
  assert.deepEqual(
    ["introduction", "body", "conclusion"].map((stage) => e[`review-progress-${stage}-status`].textContent),
    ["Not started", "Not started", "Not started"],
  );
  assert.deepEqual(
    ["introduction", "body", "conclusion"].map((stage) => e[`review-progress-${stage}-words`].textContent),
    ["0", "0", "0"],
  );
  assert.equal(e["review-introduction"].textContent, "Introduction has not been written yet.");
  assert.equal(e["review-body"].textContent, "Body has not been written yet.");
  assert.equal(e["review-conclusion"].textContent, "Conclusion has not been written yet.");
  assert.equal(e["nlp-transparency"].hidden, true, "the technical Inspector is collapsed during review");
  assert.equal(e["review-toggle-technical"].attributes["aria-expanded"], "false");
  assert.equal(e["submission-controls"].hidden, true, "practice mode offers no submission");

  await click(e["review-toggle-technical"]);
  assert.equal(e["nlp-transparency"].hidden, false, "technical analysis remains accessible");
  assert.equal(e["review-toggle-technical"].attributes["aria-expanded"], "true");
  assert.match(e["review-toggle-technical"].textContent, /Hide technical analysis/);
  await click(e["review-toggle-technical"]);
  assert.equal(e["nlp-transparency"].hidden, true);

  // Introduction only; edits from review stay unsaved and are reflected in the preview.
  await click(e["review-edit-introduction"]);
  assert.equal(value(page, "state.currentView"), "INTRODUCTION");
  assert.equal(e["essay-review-panel"].hidden, true);
  assert.equal(e["stage-text"].focused, true);
  e["stage-text"].value = "One two three.";
  await input(e["stage-text"]);
  await click(page.tabs[3]);
  await settle();
  assert.equal(e["review-summary-total-words"].textContent, "3");
  assert.equal(e["review-summary-sections"].textContent, "1 of 3");
  assert.equal(e["review-introduction"].textContent, "One two three.");
  assert.equal(e["review-progress-introduction-words"].textContent, "3");
  assert.equal(e["review-progress-introduction-status"].textContent, "Drafted");
  assert.equal(e["review-progress-body-status"].textContent, "Not started");
  assert.equal(e["review-unsaved-note"].hidden, false, "unsaved writing is clearly distinguished");
  assert.equal(persistenceWrites.length, 0, "opening review never saves");
  assert.equal(revisions.length, 0, "opening review never creates revisions");
  assert.equal(analysisRequests.length, 0, "opening review never starts analysis");

  // Introduction + Body.
  await click(e["review-edit-body"]);
  assert.equal(value(page, "state.currentView"), "BODY");
  assert.equal(e["stage-text"].value, "");
  e["stage-text"].value = "Four five.\n\nSix seven.";
  await input(e["stage-text"]);
  await click(page.tabs[3]);
  await settle();
  assert.equal(e["review-summary-total-words"].textContent, "7");
  assert.equal(e["review-summary-sections"].textContent, "2 of 3");
  assert.equal(e["review-body"].textContent, "Four five.\n\nSix seven.");
  assert.equal(e["review-progress-body-status"].textContent, "Drafted");

  // All three sections; paragraph breaks and original wording are preserved.
  await click(e["review-edit-conclusion"]);
  assert.equal(value(page, "state.currentView"), "CONCLUSION");
  e["stage-text"].value = "Eight.";
  await input(e["stage-text"]);
  await click(page.tabs[3]);
  await settle();
  assert.equal(e["review-summary-total-words"].textContent, "8");
  assert.equal(e["review-summary-sections"].textContent, "3 of 3");
  assert.deepEqual(
    ["introduction", "body", "conclusion"].map((stage) => e[`review-progress-${stage}-status`].textContent),
    ["Drafted", "Drafted", "Drafted"],
  );
  assert.equal(e["review-introduction"].textContent, "One two three.");
  assert.equal(e["review-body"].textContent, "Four five.\n\nSix seven.");
  assert.equal(e["review-conclusion"].textContent, "Eight.");
  assert.equal(e["review-unsaved-note"].hidden, false);

  // Classroom assignment: persisted revision counts and recorded active time.
  recordedActivitySeconds = 125;
  const assignedPage = makeWorkspace(fetch, new Map());
  await waitForRestoration(assignedPage);
  await click(assignedPage.appLinks.find((link) => link.dataset.appLink === "workspace"));
  const a = assignedPage.elements;
  await click(a["my-classroom-list"].children[0].children[0]);
  const assignmentOneButton = a["available-assignment-list"].children[0].children[0].children[3];
  await startAssignment(assignmentOneButton, assignedPage);
  assert.equal(value(assignedPage, "state.assignmentId"), 101);
  a["stage-text"].value = "Students should read daily.";
  await input(a["stage-text"]);
  await click(assignedPage.tabs[1]);
  a["stage-text"].value = "Reading builds vocabulary.\n\nReading improves focus.";
  await input(a["stage-text"]);
  await click(assignedPage.tabs[2]);
  a["stage-text"].value = "Daily reading helps.";
  await input(a["stage-text"]);
  await click(a["save-revision-button"]);
  assert.equal(a["revision-save-status"].textContent, "Revision 1 saved.");
  assert.equal(revisions.length, 1);
  const writesBeforeReview = persistenceWrites.length;
  await click(assignedPage.tabs[3]);
  await settle();
  assert.equal(a["review-summary-total-words"].textContent, "13");
  assert.equal(a["review-summary-sections"].textContent, "3 of 3");
  assert.equal(a["review-summary-revisions"].textContent, "1");
  assert.match(a["review-revisions-note"].textContent, /Explicit snapshots/);
  assert.equal(a["review-summary-active-time"].textContent, "2 min 5 sec");
  assert.match(a["review-active-time-note"].textContent, /Recorded only while/);
  assert.equal(a["review-summary-remaining-time"].textContent, "Unavailable");
  assert.equal(a["review-submission-badge"].textContent, "Not submitted");
  assert.equal(a["submission-controls"].hidden, false, "submission stays available after the preview");
  assert.equal(a["review-unsaved-note"].hidden, true);
  assert.equal(persistenceWrites.length, writesBeforeReview, "review refreshes are read-only");
  assert.equal(revisions.length, 1);
  assert.equal(a["review-body"].textContent, "Reading builds vocabulary.\n\nReading improves focus.");
  assert.equal(a["review-body"].textContent.includes("\n\n"), true, "paragraph breaks are preserved");
  assert.equal(a["nlp-transparency"].hidden, true);

  // Editing one stage from review updates the total without creating a revision.
  await click(a["review-edit-body"]);
  assert.equal(value(assignedPage, "state.currentView"), "BODY");
  assert.equal(a["stage-text"].value, "Reading builds vocabulary.\n\nReading improves focus.");
  a["stage-text"].value = "Reading builds vocabulary and focus.";
  await input(a["stage-text"]);
  await click(assignedPage.tabs[3]);
  await settle();
  assert.equal(a["review-summary-total-words"].textContent, "12");
  assert.equal(a["review-summary-revisions"].textContent, "1", "editing is not a revision");
  assert.equal(a["review-unsaved-note"].hidden, false);

  // Submission remains validated and locks the essay afterwards.
  const submissionsBefore = submissionCount;
  await click(a["submit-essay-button"]);
  await settle();
  assert.equal(submissionCount, submissionsBefore + 1);
  assert.notEqual(value(assignedPage, "state.submission"), null);
  assert.equal(a["review-submission-badge"].textContent, "Submitted");
  assert.match(a["review-submission-note"].textContent, /read-only/);
  assert.equal(a["submission-controls"].hidden, true);
  assert.equal(a["assignment-submitted-status"].hidden, false);
  assert.equal(a["review-edit-introduction"].disabled, true);
  assert.equal(a["review-edit-body"].disabled, true);
  assert.equal(a["review-edit-conclusion"].disabled, true);
  assert.equal(a["review-summary-total-words"].textContent, "12");

  // A second assignment without activity records reports Not recorded and no revisions.
  recordedActivitySeconds = null;
  const assignmentTwoButton = a["available-assignment-list"].children[1].children[0].children[3];
  await startAssignment(assignmentTwoButton, assignedPage);
  assert.equal(value(assignedPage, "state.assignmentId"), 102);
  await click(assignedPage.tabs[3]);
  await settle();
  assert.equal(a["review-summary-total-words"].textContent, "0");
  assert.equal(a["review-summary-sections"].textContent, "0 of 3");
  assert.equal(a["review-summary-revisions"].textContent, "0");
  assert.equal(a["review-summary-active-time"].textContent, "Not recorded");
  assert.match(a["review-active-time-note"].textContent, /No active writing time/);
  assert.equal(a["review-summary-remaining-time"].textContent, "Unavailable");
  assert.equal(a["review-submission-badge"].textContent, "Not submitted");
  assert.equal(a["submission-controls"].hidden, false);
  assert.equal(a["review-edit-introduction"].disabled, false);
  assert.equal(a["nlp-transparency"].hidden, true);

  console.log("Feedback presentation scenarios completed.");
})().catch((error) => { console.error(error); process.exitCode = 1; });
'''
    _run_workspace_frontend(tmp_path, scenario)
