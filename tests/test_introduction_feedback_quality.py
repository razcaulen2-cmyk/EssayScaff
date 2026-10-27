"""Real spaCy regressions for sentence-topic review, priority and exact spans."""

from copy import deepcopy
from unittest.mock import Mock

import pytest

from services.essay_analysis_service import EssayAnalysisService
from services.introduction_sentence_evidence import REVIEW_RULE
from tests.test_reason_highlighting import _make_stage_payload, _run_node_scenario

TOPIC = "Should students be allowed to use smartphones during class?"
FOCUS = ["smartphones", "students", "classroom", "learning", "distractions"]
PREFIX = (
    "Smartphones are common in many classrooms, and students often use them to find information. "
    "Teachers can use smartphones for learning activities, such as looking up difficult words and reading educational materials. "
    "However, notifications and games can cause distractions during class. "
)
ALTHOUGH = "Although smartphones can also interrupt lessons."
POINT = "Schools should allow smartphones during teacher-guided activities because clear rules can help students focus on learning."
FINAL = "And have slumber party at my aunt house"
FULL = PREFIX + ALTHOUGH + " " + POINT + " " + FINAL


@pytest.fixture(scope="module")
def service():
    return EssayAnalysisService()


def analyze(service, text, focus=FOCUS):
    return service.analyze(TOPIC, focus, introduction_text=text, include_research_trace=True)


def decisions(result):
    return result["research_trace"]["stages"]["INTRODUCTION"]["feedback_decisions"]["fields"]


def test_a_actual_two_concerns_and_parse(service):
    result = analyze(service, FULL)
    stage = result["stages"]["INTRODUCTION"]
    analysis = stage["analysis"]
    sentences = analysis["linguistic_observations"]["sentences"]
    assert len(sentences) == 6
    assert [(s["start"], s["end"]) for s in sentences] == [(0, 91), (92, 215), (216, 285), (286, 334), (335, 457), (458, 497)]
    final = sentences[-1]
    assert any(t["text"] == "have" and t["pos"] == "VERB" and t["dependency"] == "ROOT" for t in final["tokens"])
    assert not final["subjects"]
    assert not analysis["observable_structure"]["list_or_fragment_candidate"]["fragmentary_text_candidate"]
    # No invented grammar verdict for the subjectless base-form verb.
    assert [m["text"] for m in analysis["observable_structure"]["incomplete_subordinator_candidates"]] == ["Although"]
    rows = analysis["sentence_topic_evidence"]["sentences"]
    assert all(row["matched_focus_terms"] for row in rows[:-1])
    assert rows[-1]["status"] == "POSSIBLE_CONNECTION_GAP"
    assert rows[-1]["matched_focus_terms"] == rows[-1]["shared_neighbor_lemmas"] == rows[-1]["reference_cues"] == []
    assert decisions(result)["Primary Feedback"]["selection_branch"] == "intro_sentence_fluency_complete_sentence"
    assert decisions(result)["Needs Attention"]["rule_ids"] == [REVIEW_RULE]
    assert len(stage["feedback"]["Needs Attention"]) == 1
    event = next(e for e in analysis["rule_evidence"] if e["rule_id"] == REVIEW_RULE)
    assert event["evidence"] == [rows[-1]]
    assert FULL[rows[-1]["start"]:rows[-1]["end"]] == FINAL
    trace = next(r for r in analysis["rule_evaluation_trace"] if r["rule_id"] == REVIEW_RULE)
    assert trace["status"] == "TRIGGERED"
    assert trace["implementation"]["file"].replace("\\", "/") == "services/introduction_sentence_evidence.py"


def test_b_without_although_topic_review_becomes_primary(service):
    result = analyze(service, PREFIX + POINT + " " + FINAL)
    assert decisions(result)["Primary Feedback"]["selection_branch"] == "intro_ideas_review_topic_connection"
    assert decisions(result)["Primary Feedback"]["rule_ids"] == [REVIEW_RULE]
    assert result["stages"]["INTRODUCTION"]["feedback"]["Needs Attention"] == []


@pytest.mark.parametrize("ending,status", [
    ("She helped me understand the lesson better.", "CONTEXT_REVIEW_DEFERRED"),
    ("We had a slumber party at my aunt's house.", "POSSIBLE_CONNECTION_GAP"),
    ("Students can communicate with invisible dragons during class.", "WORDING_MATCH_OBSERVED_NOT_RELEVANCE"),
    ("These activities help me.", "CONTEXT_REVIEW_DEFERRED"),
    ("Teachers explain difficult words.", "CONTEXT_REVIEW_DEFERRED"),
    ("Read the instructions.", "POSSIBLE_CONNECTION_GAP"),
])
def test_c_d_e_missing_words_are_not_irrelevance_or_grammar_verdicts(service, ending, status):
    result = analyze(service, PREFIX + POINT + " " + ending)
    analysis = result["stages"]["INTRODUCTION"]["analysis"]
    row = analysis["sentence_topic_evidence"]["sentences"][-1]
    assert row["status"] == status
    assert "not establish relevance" in row["limitation"]
    assert not analysis["observable_structure"]["incomplete_subordinator_candidates"]
    if status == "POSSIBLE_CONNECTION_GAP":
        assert decisions(result)["Primary Feedback"]["selection_branch"] == "intro_ideas_review_topic_connection"
        assert "may not clearly connect" in result["stages"]["INTRODUCTION"]["feedback"]["Primary Feedback"]
    else:
        assert REVIEW_RULE not in {e["rule_id"] for e in analysis["rule_evidence"]}


def test_f_complete_complex_sentence_and_valid_coordination(service):
    for text in ["Although smartphones can distract students, teachers can use them for learning.",
                 "Use smartphones carefully and follow the rules.", "Students read and discuss their ideas."]:
        analysis = analyze(service, text)["stages"]["INTRODUCTION"]["analysis"]
        assert analysis["observable_structure"]["incomplete_subordinator_candidates"] == []
        assert analysis["sentence_topic_evidence"]["review_candidates"] == []


def test_derived_focus_and_single_sentence_gaps_defer_to_teacher(service):
    for text, focus in [(FULL, None), (FINAL, FOCUS), ("Smartphones. Slumber parties.", FOCUS)]:
        analysis = analyze(service, text, focus)["stages"]["INTRODUCTION"]["analysis"]
        assert analysis["sentence_topic_evidence"]["review_candidates"] == []
        assert REVIEW_RULE not in {e["rule_id"] for e in analysis["rule_evidence"]}


def test_no_extra_student_parse_and_exact_unicode_spans(service, monkeypatch):
    parse = Mock(wraps=service.nlp_service.parse)
    monkeypatch.setattr(service.nlp_service, "parse", parse)
    text = "🌍 " + FULL + ". " + FINAL
    result = analyze(service, text)
    assert parse.call_count == 1
    for row in result["stages"]["INTRODUCTION"]["analysis"]["sentence_topic_evidence"]["sentences"]:
        assert row["span_verified"]
        assert text[row["start"]:row["end"]] == row["text"]


def test_main_and_also_check_highlight_exact_distinct_sentences(service, tmp_path):
    payload = _make_stage_payload(analyze(service, FULL))
    scenario = r'''
      elements["stage-text"].value=analysisResponse.analysis.linguistic_observations.text;
      displayFeedback(analysisResponse);
      const model=studentFeedbackPresentation(analysisResponse);
      assert.equal(model.tutor_items.length,2);
      assert.equal(model.tutor_items[0].feedback_heading,"Main Feedback");
      assert.equal(model.tutor_items[1].feedback_heading,"Also Check");
      assert.equal(model.tutor_items[1].label,"Ideas · Review Topic Connection");
      assert.equal(elements["editor-mirror"].querySelector("mark").textContent,"Although smartphones can also interrupt lessons.");
      assert.equal(elements["tutor-evidence"].querySelector("mark").textContent,"Although smartphones can also interrupt lessons.");
      renderTutorItem(model.tutor_items[1]);
      assert.equal(JSON.stringify(elements["editor-mirror"].querySelectorAll("mark").map(m=>m.textContent)),JSON.stringify(["And have slumber party at my aunt house"]));
      assert.equal(JSON.stringify(elements["tutor-evidence"].querySelectorAll("mark").map(m=>m.textContent)),JSON.stringify(["And have slumber party at my aunt house"]));
      const flow=buildFeedbackDecisionFlow("Needs Attention",analysisResponse);
      assert.equal(flow.tutor.status,"SECONDARY_LESSONS");
      assert.ok(flow.cited.some(r=>r.rule_id==="INTRO.TOPIC.SENTENCE_CONNECTION_REVIEW"));
    '''
    _run_node_scenario(payload, scenario, tmp_path)


@pytest.mark.parametrize("damage", ["missing_event", "false_event", "bad_offset", "bad_text", "missing_finding", "stale_editor"])
def test_missing_or_contradictory_evidence_never_creates_secondary_highlight(service, tmp_path, damage):
    payload = deepcopy(_make_stage_payload(analyze(service, FULL)))
    analysis = payload["analysis"]
    event = next(e for e in analysis["rule_evidence"] if e["rule_id"] == REVIEW_RULE)
    if damage == "missing_event":
        analysis["rule_evidence"].remove(event)
    elif damage == "false_event":
        event["triggered"] = False
    elif damage == "bad_offset":
        event["evidence"][0]["end"] = 99999
    elif damage == "bad_text":
        event["evidence"][0]["text"] = "Different received text"
    elif damage == "missing_finding":
        analysis.pop("sentence_topic_evidence")
    extra = " + ' edit'" if damage == "stale_editor" else ""
    _run_node_scenario(payload, f'''
      elements["stage-text"].value=analysisResponse.analysis.linguistic_observations.text{extra};
      const model=studentFeedbackPresentation(analysisResponse);
      assert.equal(model.tutor_items.length,1,"no unsupported Also Check");
    ''', tmp_path)
