"""Permanent regression tests for Introduction reason clause highlighting and feedback.

Covers:
1. Test A: Dragon reason gets neutral explanation review with single clause mark
2. Test B: Educational-app reason uses the same neutral review with single clause mark
3. Multiple sentences containing 'because'
4. Repeated words and Unicode offsets without drift
5. Unverified/corrupted offsets failing cleanly to fallback without marks
6. Existing incomplete-sentence highlighting preserved
"""

import json
from pathlib import Path
import shutil
import subprocess
import pytest

from services.essay_analysis_service import EssayAnalysisService
from services.feedback_service import FeedbackService
from services.introduction_rules import IntroductionRuleBase
from services.nlp_service import NLPService
from services.topic_service import TopicService

NODE = shutil.which("node")
pytestmark = pytest.mark.skipif(NODE is None, reason="Node.js is required for frontend highlight tests")

PROJECT = Path(__file__).resolve().parents[1]
APP_JS = PROJECT / "static" / "app.js"
LESSON_PATH = PROJECT / "content" / "lessons" / "feedback_help.json"

TOPIC = "Should students be allowed to use smartphones during class?"
FOCUS = ["smartphones", "students", "class", "classroom", "allowed"]


def _run_node_scenario(analysis_response: dict, scenario_code: str, tmp_path_dir: Path | None = None) -> None:
    import tempfile
    if tmp_path_dir is None:
        temp_dir = Path(tempfile.gettempdir())
    else:
        temp_dir = tmp_path_dir

    payload_file = temp_dir / f"payload_{tempfile.mktemp()[-8:]}.json"
    script_file = temp_dir / f"scenario_{tempfile.mktemp()[-8:]}.js"
    payload_file.write_text(json.dumps(analysis_response), encoding="utf-8")

    harness = r"""
const fs = require("node:fs");
const vm = require("node:vm");
const assert = require("node:assert/strict");

const appJs = process.argv[2];
const catalogPath = process.argv[3];
const payloadPath = process.argv[4];

const catalog = JSON.parse(fs.readFileSync(catalogPath, "utf8"));
const analysisResponse = JSON.parse(fs.readFileSync(payloadPath, "utf8"));

class Element {
  constructor(id, stage = null) {
    this.id = id;
    this.tagName = String(id).toUpperCase();
    this.dataset = stage ? { stage } : {};
    this.value = "";
    this._textContent = "";
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
    this.classList = { toggle: () => {}, add: () => {}, remove: () => {} };
  }
  get textContent() {
    if (this.children.length) return this.children.map(c => c.textContent).join("");
    return this._textContent || "";
  }
  set textContent(val) {
    this._textContent = val;
    this.children = [];
  }
  addEventListener(name, fn) {
    if (!this.listeners[name]) this.listeners[name] = [];
    this.listeners[name].push(fn);
  }
  setAttribute(name, value) { this.attributes[name] = value; }
  removeAttribute(name) { delete this.attributes[name]; }
  appendChild(child) {
    if (!child || child === this) return child;
    if (child.parentNode) {
      const idx = child.parentNode.children.indexOf(child);
      if (idx >= 0) child.parentNode.children.splice(idx, 1);
    }
    this.children.push(child);
    child.parentNode = this;
    return child;
  }
  append(...children) { for (const c of children) this.appendChild(c); }
  replaceChildren() {
    for (const c of this.children) c.parentNode = null;
    this.children = [];
  }
  querySelectorAll(selector) {
    const res = [];
    for (const c of this.children) {
      if (selector === "mark" && c.tagName === "MARK") res.push(c);
      if (selector === "span" && c.tagName === "SPAN") res.push(c);
      if (selector === "p" && c.tagName === "P") res.push(c);
      if (selector === "button" && c.tagName === "BUTTON") res.push(c);
      res.push(...c.querySelectorAll(selector));
    }
    return res;
  }
  querySelector(selector) { return this.querySelectorAll(selector)[0] || null; }
}

const elementsMap = new Map();
function getEl(id) {
  if (!elementsMap.has(id)) {
    elementsMap.set(id, new Element(id));
  }
  return elementsMap.get(id);
}
getEl("scaffolding-guidance-definition").textContent = JSON.stringify(catalog);
const elements = new Proxy({}, {
  get: (target, prop) => getEl(String(prop)),
});

const document = {
  getElementById: (id) => getEl(id),
  querySelector: (sel) => null,
  querySelectorAll: (sel) => [],
  createElement: (tag) => new Element(tag),
  createElementNS: (_namespace, tag) => new Element(tag),
  createTextNode: (text) => { const node = new Element("#text"); node.textContent = String(text); return node; },
  body: new Element("body"),
};

const window = {
  addEventListener: () => {},
  location: { hash: "" },
};

const context = vm.createContext({
  document,
  window,
  FEEDBACK_HELP_CATALOG: catalog,
  navigator: {},
  console,
  assert,
  elements,
  analysisResponse,
});

vm.runInContext(fs.readFileSync(require("node:path").join(require("node:path").dirname(appJs), "nlp_process_explorer.js"), "utf8"), context);
vm.runInContext(fs.readFileSync(appJs, "utf8"), context);

(async () => {
  await vm.runInContext(`(async () => {\n__SCENARIO__\n})()`, context);
})().catch(err => {
  console.error(err);
  process.exitCode = 1;
});
""".replace("__SCENARIO__", scenario_code)
    script_file.write_text(harness, encoding="utf-8")
    try:
        result = subprocess.run(
            [NODE, str(script_file), str(APP_JS), str(LESSON_PATH), str(payload_file)],
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, result.stdout + result.stderr
    finally:
        payload_file.unlink(missing_ok=True)
        script_file.unlink(missing_ok=True)


def _make_stage_payload(analysis_result: dict, stage_id: str = "INTRODUCTION") -> dict:
    stage = analysis_result["stages"][stage_id]
    trace = dict(analysis_result["research_trace"])
    trace["selected_stage"] = stage_id
    return {
        "stage_id": stage_id,
        "availability": stage.get("availability", "ANALYZED"),
        "analysis": stage["analysis"],
        "feedback": stage["feedback"],
        "interpretation_limit": stage.get("interpretation_limit") or "Observation only.",
        "research_trace": trace,
    }


def test_dragon_reason_uses_neutral_review_and_highlights_only_clause():
    """No semantic warning is justified by missing keywords; retain exact reason evidence."""
    text = (
        "Smartphones can support learning in the classroom when teachers guide students. "
        "Clear classroom rules may help reduce distractions during lessons. "
        "Schools should allow smartphones because invisible dragons control the price of bananas on Mars."
    )
    svc = EssayAnalysisService()
    analysis = svc.analyze(TOPIC, FOCUS, introduction_text=text, include_research_trace=True)
    intro = analysis["stages"]["INTRODUCTION"]
    branch = analysis["research_trace"]["stages"]["INTRODUCTION"]["feedback_decisions"]["fields"]["Primary Feedback"]["selection_branch"]
    assert branch == "intro_ideas_point_and_reason"

    rule_ids = [e["rule_id"] for e in intro["analysis"]["rule_evidence"]]
    assert "INTRO.REASON.NO_CLAUSE_TOPIC_OVERLAP" in rule_ids
    assert "INTRO.DEVELOPMENT.MULTIPLE_CLAUSE_PREDICATES" in rule_ids

    reason_event = next(e for e in intro["analysis"]["rule_evidence"] if e["rule_id"] == "INTRO.REASON.NO_CLAUSE_TOPIC_OVERLAP")
    evidence_list = reason_event.get("actual_evidence") or reason_event.get("evidence")
    target = evidence_list[0]
    clause_text = text[target["clause_start"]:target["clause_end"]]
    assert clause_text == "because invisible dragons control the price of bananas on Mars"
    sentence_text = text[target["sentence_start"]:target["sentence_end"]]
    assert sentence_text == "Schools should allow smartphones because invisible dragons control the price of bananas on Mars."

    payload = _make_stage_payload(analysis, "INTRODUCTION")

    scenario = r"""
  elements["stage-text"].value = analysisResponse.analysis.linguistic_observations.text;
  displayFeedback(analysisResponse);
  const pres = studentFeedbackPresentation(analysisResponse);

  assert.equal(pres.status, "NEUTRAL_OBSERVATION");
  assert.equal(pres.writing_dimension, null);
  assert.equal(pres.writing_skill, null);
  assert.deepEqual(Object.keys(pres.displayed_guidance), ["What I noticed", "What's working"]);
  assert.equal(pres.tutor_items[0].neutral_result, true);
  assert.equal(pres.tutor_items[0].label, "No specific writing issue detected");

  const mirrorMarks = elements["editor-mirror"].querySelectorAll("mark");
  assert.equal(mirrorMarks.length, 0, "neutral review displays no error location");

  const tutorMarks = elements["tutor-evidence"].querySelectorAll("mark");
  assert.equal(tutorMarks.length, 0, "neutral review displays no tutor evidence marks");

  const recorded = pres.instructional_feedback.items[0];
  assert.equal(recorded.selection_branch, "intro_ideas_point_and_reason");
  assert.equal(recorded.highlight_spans.length, 1, "raw recorded span remains in transparency");
  assert.equal(recorded.highlight_spans[0].text, "because invisible dragons control the price of bananas on Mars");
  assert.equal(pres.tutor_items[0].excerpt.contexts[0].marks.length, 1, "the recorded span is retained for transparency");
"""
    _run_node_scenario(payload, scenario)


def test_educational_app_reason_uses_neutral_review_and_highlights_only_clause():
    """Word overlap does not certify support; both examples retain neutral review."""
    text = (
        "Smartphones can support learning in the classroom when teachers guide students. "
        "Clear classroom rules may help reduce distractions during lessons. "
        "Schools should allow smartphones because students can use educational apps during class."
    )
    svc = EssayAnalysisService()
    analysis = svc.analyze(TOPIC, FOCUS, introduction_text=text, include_research_trace=True)
    intro = analysis["stages"]["INTRODUCTION"]
    branch = analysis["research_trace"]["stages"]["INTRODUCTION"]["feedback_decisions"]["fields"]["Primary Feedback"]["selection_branch"]
    assert branch == "intro_ideas_point_and_reason"

    rule_ids = [e["rule_id"] for e in intro["analysis"]["rule_evidence"]]
    assert "INTRO.REASON.CLAUSE_TOPIC_OVERLAP" in rule_ids

    payload = _make_stage_payload(analysis, "INTRODUCTION")

    scenario = r"""
  elements["stage-text"].value = analysisResponse.analysis.linguistic_observations.text;
  displayFeedback(analysisResponse);
  const pres = studentFeedbackPresentation(analysisResponse);

  assert.equal(pres.status, "NEUTRAL_OBSERVATION");
  assert.equal(pres.writing_dimension, null);
  assert.equal(pres.writing_skill, null);

  const mirrorMarks = elements["editor-mirror"].querySelectorAll("mark");
  assert.equal(mirrorMarks.length, 0, "neutral review displays no error location");

  const tutorMarks = elements["tutor-evidence"].querySelectorAll("mark");
  assert.equal(tutorMarks.length, 0, "neutral review displays no tutor evidence marks");

  const recorded = pres.instructional_feedback.items[0];
  assert.equal(recorded.highlight_spans.length, 1, "raw recorded span remains in transparency");
  assert.equal(recorded.highlight_spans[0].text, "because students can use educational apps during class");
  assert.equal(pres.tutor_items[0].excerpt.contexts[0].marks.length, 1, "the recorded span is retained for transparency");
"""
    _run_node_scenario(payload, scenario)


def test_multiple_sentences_with_because_marks_only_target_reason_clause():
    """Multiple sentences containing 'because' must only highlight the evaluated reason clause."""
    text = (
        "Because smartphones are common in schools, teachers need rules. "
        "Teachers guide students because structure helps learning. "
        "Schools should allow smartphones because students can use educational apps during class."
    )
    svc = EssayAnalysisService()
    analysis = svc.analyze(TOPIC, FOCUS, introduction_text=text, include_research_trace=True)

    payload = _make_stage_payload(analysis, "INTRODUCTION")

    scenario = r"""
  elements["stage-text"].value = analysisResponse.analysis.linguistic_observations.text;
  displayFeedback(analysisResponse);

  const pres = studentFeedbackPresentation(analysisResponse);
  assert.equal(pres.status, "NEUTRAL_OBSERVATION");
  const mirrorMarks = elements["editor-mirror"].querySelectorAll("mark");
  assert.equal(mirrorMarks.length, 0, "neutral review displays no error location");

  const recorded = pres.instructional_feedback.items[0];
  assert.equal(recorded.highlight_spans.length, 1, "only the targeted reason clause is recorded");
  assert.equal(recorded.highlight_spans[0].text, "Because smartphones are common in schools");
  assert.equal(pres.tutor_items[0].excerpt.contexts[0].marks.length, 1, "the recorded span is retained for transparency");
"""
    _run_node_scenario(payload, scenario)


def test_repeated_words_and_unicode_offsets_align_accurately():
    """Text with repeated words and unicode apostrophe maintains exact alignment."""
    text = (
        "Students use phones when teachers guide them. "
        "Students follow rules when teachers guide them. "
        "Schools should allow students’ smartphones because students can use educational apps during class."
    )
    svc = EssayAnalysisService()
    analysis = svc.analyze(TOPIC, FOCUS, introduction_text=text, include_research_trace=True)

    payload = _make_stage_payload(analysis, "INTRODUCTION")

    scenario = r"""
  elements["stage-text"].value = analysisResponse.analysis.linguistic_observations.text;
  displayFeedback(analysisResponse);

  const pres = studentFeedbackPresentation(analysisResponse);
  assert.equal(pres.status, "NEUTRAL_OBSERVATION");
  const mirrorMarks = elements["editor-mirror"].querySelectorAll("mark");
  assert.equal(mirrorMarks.length, 0, "neutral review displays no error location");

  const recorded = pres.instructional_feedback.items[0];
  assert.equal(recorded.highlight_spans.length, 1);
  assert.equal(recorded.highlight_spans[0].text, "because students can use educational apps during class");
  assert.ok(pres.tutor_items[0].excerpt.source.includes("students’ smartphones"));
  assert.equal(recorded.highlight_spans[0].start, 137);
  assert.equal(recorded.highlight_spans[0].end, 191);
"""
    _run_node_scenario(payload, scenario)


def test_corrupted_offsets_fail_closed_to_fallback():
    """When reason span offsets are invalid, system fails closed with no marks and shows fallback."""
    text = (
        "Smartphones can support learning in the classroom when teachers guide students. "
        "Clear classroom rules may help reduce distractions during lessons. "
        "Schools should allow smartphones because invisible dragons control the price of bananas on Mars."
    )
    svc = EssayAnalysisService()
    analysis = svc.analyze(TOPIC, FOCUS, introduction_text=text, include_research_trace=True)
    payload = _make_stage_payload(analysis, "INTRODUCTION")

    # Corrupt the clause offsets in actual_evidence
    for event in payload["analysis"]["rule_evidence"]:
        if "REASON" in event["rule_id"]:
            ev = event.get("actual_evidence") or event.get("evidence")
            ev[0]["sentence_start"] = 999
            ev[0]["sentence_end"] = 1200

    scenario = r"""
  elements["stage-text"].value = analysisResponse.analysis.linguistic_observations.text;
  displayFeedback(analysisResponse);

  const pres = studentFeedbackPresentation(analysisResponse);
  assert.equal(pres.status, "NEUTRAL_OBSERVATION");

  const mirrorMarks = elements["editor-mirror"].querySelectorAll("mark");
  assert.equal(mirrorMarks.length, 0, "No marks when offsets are invalid");

  const tutorMarks = elements["tutor-evidence"].querySelectorAll("mark");
  assert.equal(tutorMarks.length, 0, "No marks in tutor evidence");

  assert.equal(pres.tutor_items[0].excerpt, null, "invalid offsets fail closed with no excerpt");
  assert.equal(pres.tutor_items[0].evidence_text,
    "No explanation span could be verified for marking. Read your main statement with the part you intend as an explanation.");
"""
    _run_node_scenario(payload, scenario)


def test_existing_incomplete_sentence_highlighting_preserved():
    """INTRO.CLAUSE.POSSIBLE_INCOMPLETE_SUBORDINATOR still highlights the entire sentence context."""
    text = "Because students can use educational apps during class."
    svc = EssayAnalysisService()
    analysis = svc.analyze(TOPIC, FOCUS, introduction_text=text, include_research_trace=True)
    branch = analysis["research_trace"]["stages"]["INTRODUCTION"]["feedback_decisions"]["fields"]["Primary Feedback"]["selection_branch"]
    assert branch == "intro_sentence_fluency_complete_sentence"

    payload = _make_stage_payload(analysis, "INTRODUCTION")

    scenario = r"""
  elements["stage-text"].value = analysisResponse.analysis.linguistic_observations.text;
  displayFeedback(analysisResponse);
  const pres = studentFeedbackPresentation(analysisResponse);

  assert.equal(pres.writing_dimension, "Sentence Fluency");
  assert.equal(pres.writing_skill, "Complete Your Sentence");

  const mirrorMarks = elements["editor-mirror"].querySelectorAll("mark");
  assert.equal(mirrorMarks.length, 1);
  assert.equal(mirrorMarks[0].textContent, "Because students can use educational apps during class.");
"""
    _run_node_scenario(payload, scenario)
