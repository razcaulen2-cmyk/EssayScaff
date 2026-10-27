"""T01–T13: real Introduction observations, neutral Ideas tasks and shared trace."""

from copy import deepcopy
import json
from pathlib import Path
from unittest.mock import Mock

import pytest

from services.essay_analysis_service import EssayAnalysisService
from services.tutoring_lessons import introduction_instructional_trace
from tests.test_reason_highlighting import NODE, _make_stage_payload, _run_node_scenario

CORPUS = json.loads(Path(__file__).with_name("introduction_ideas_cases.json").read_text(encoding="utf-8"))
EXPECTATIONS = {
    "T01": ("intro_ideas_develop_main_point", "Develop Your Main Point", "HELP-INTRO-DEVELOP-POINT", CORPUS["cases"]["T01"]),
    "T02": ("intro_ideas_point_and_reason", "Review Your Explanation", "HELP-INTRO-EXPLAIN-POINT", "because students can research information for their lessons"),
    "T03": ("intro_ideas_review_details", "Review Your Details", "HELP-INTRO-REVIEW-DETAILS", "They can search for difficult words."),
    "T04": ("intro_ideas_point_and_reason", "Review Your Explanation", "HELP-INTRO-EXPLAIN-POINT", "because these devices provide quick access to online dictionaries"),
    "T05": ("intro_ideas_point_and_reason", "Review Your Explanation", "HELP-INTRO-EXPLAIN-POINT", "because smartphones provide quick access to online dictionaries"),
    "T06": ("intro_sentence_fluency_complete_sentence", "Complete Your Sentence", "HELP-INTRO-COMPLETE-SENTENCE", CORPUS["cases"]["T06"]),
    "T07": ("intro_ideas_point_and_reason", "Review Your Explanation", "HELP-INTRO-EXPLAIN-POINT", "Because students can use smartphones for learning"),
    "T08": ("intro_sentence_fluency_complete_sentence", "Complete Your Sentence", "HELP-INTRO-COMPLETE-SENTENCE", CORPUS["cases"]["T08"]),
    "T09": ("intro_ideas_state_position", "State Your Position", "HELP-INTRO-STATE-POSITION", CORPUS["cases"]["T09"]),
    "T10": ("intro_ideas_state_position", "State Your Position", "HELP-INTRO-STATE-POSITION", "Smartphones are useful classroom tools."),
    "T11": ("intro_ideas_review_topic_connection", "Review Topic Connection", "HELP-INTRO-TOPIC-CONNECTION", "We had a slumber party at my aunt's house."),
    "T12": ("intro_ideas_state_position", "State Your Position", "HELP-INTRO-STATE-POSITION", CORPUS["cases"]["T12"]),
    "T13": ("intro_ideas_point_and_reason", "Review Your Explanation", "HELP-INTRO-EXPLAIN-POINT", "because smartphones control invisible dragons on Mars"),
}


@pytest.fixture(scope="module")
def analyzer():
    return EssayAnalysisService()


@pytest.fixture(scope="module")
def responses(analyzer):
    return {key: analyzer.analyze(CORPUS["assignment_topic"], CORPUS["focus_terms"], introduction_text=text,
                                  include_research_trace=True) for key, text in CORPUS["cases"].items()}


def trace(result):
    return result["research_trace"]["stages"]["INTRODUCTION"]["feedback_decisions"]


@pytest.mark.parametrize("case", EXPECTATIONS)
def test_t01_t13_branches_mapping_provenance_and_exact_span(responses, case):
    result = responses[case]
    analysis = result["stages"]["INTRODUCTION"]["analysis"]
    expected_branch, expected_skill, expected_lesson, expected_mark = EXPECTATIONS[case]
    decision = trace(result)["fields"]["Primary Feedback"]
    metadata = trace(result)["instructional_feedback"]
    item = metadata["items"][0]
    assert decision["selection_branch"] == item["selection_branch"] == expected_branch
    assert decision["trait"] == item["trait"] == ("Sentence Fluency" if case in {"T06", "T08"} else "Ideas")
    assert decision["skill"] == item["skill"] == expected_skill
    assert item["selection_condition"] == decision["selection_condition"]
    assert item["lesson_id"] == expected_lesson
    assert item["catalog_reference"] == {"file": "content/lessons/feedback_help.json", "version": 6, "lesson_id": expected_lesson}
    events = {e["rule_id"]: e for e in analysis["rule_evidence"]}
    assert item["rule_ids"] == item["triggered_rule_ids"] == decision["rule_ids"]
    assert set(item["rule_ids"]) <= set(events)
    assert [p["text"] for p in item["highlight_spans"]] == [expected_mark]
    for plan in item["highlight_spans"]:
        source = CORPUS["cases"][case]
        assert source[plan["start"]:plan["end"]] == plan["text"]
        anchor = events[plan["rule_id"]]["evidence"][plan["evidence_index"]]
        for key in plan["anchor_path"]:
            anchor = anchor[key]
        assert anchor[plan["anchor_start_field"]] == plan["anchor"]["start"]
        assert anchor[plan["anchor_end_field"]] == plan["anchor"]["end"]
        assert source[plan["context"]["start"]:plan["context"]["end"]] == plan["context"]["text"]
        assert "not an error label" in plan["interpretation"]
    observed = item["observed_fields"]
    assert observed["central_candidate_count"] == len(analysis["observable_structure"]["central_direction_candidates"])
    assert observed["supported_predicate_count"] == analysis["development_evidence"]["predicate_count"]
    assert observed["topic_matches"] == analysis["lexical_topic_evidence"]["matches"]
    for bad_claim in ("your reason is wrong", "your answer is correct", "your argument is logical", "no explanation was found"):
        assert bad_claim not in json.dumps(item["prepared_guidance"]).lower()


def test_lexical_rephrasing_does_not_turn_reason_into_warning(responses):
    left, right = [trace(responses[k])["instructional_feedback"]["items"][0] for k in ("T04", "T05")]
    assert left["prepared_guidance"] == right["prepared_guidance"]
    assert left["feedback_purpose"] == right["feedback_purpose"] == "NEUTRAL_REVIEW_TASK"
    assert left["observed_fields"]["reason_topic_status"] == "BECAUSE_CLAUSE_NO_TOPIC_OVERLAP"
    assert right["observed_fields"]["reason_topic_status"] == "BECAUSE_CLAUSE_WITH_TOPIC_OVERLAP"
    assert left["rule_ids"] != right["rule_ids"]  # actual lexical observations remain honest


def test_no_because_and_keyword_rich_nonsense_are_not_semantic_classifications(responses):
    for case in ("T03", "T09", "T10", "T12", "T13"):
        metadata = trace(responses[case])["instructional_feedback"]
        assert all(row["trait_quality_assessment"] == "NOT_PERFORMED" for row in metadata["coverage"])
        assert {r["trait"] for r in metadata["coverage"]} == {"Ideas", "Organization", "Voice", "Word Choice", "Sentence Fluency", "Conventions", "Presentation"}
        assert {r["trait"] for r in metadata["coverage"] if r["status"] == "NOT_EVALUATED"} == {"Voice", "Conventions", "Presentation"}
        assert "Missing 'because' is not proof that an explanation is missing." in metadata["limitations"]
        assert "Missing assignment keywords is not proof that a reason is unrelated." in metadata["limitations"]


def test_passive_statement_uses_existing_linked_subject_and_auxiliary(analyzer):
    text = "Students should be allowed to use smartphones in class."
    result = analyzer.analyze(CORPUS["assignment_topic"], CORPUS["focus_terms"], introduction_text=text, include_research_trace=True)
    statement = result["stages"]["INTRODUCTION"]["analysis"]["observable_structure"]["central_direction_candidates"][0]
    assert statement["predicate_evidence"]["text"] == "allowed"
    assert statement["subject_evidence"][0]["text"] == "Students"
    assert any(t["text"] == "should" and t["tag"] == "MD" for t in statement["finite_auxiliary_evidence"])
    assert trace(result)["fields"]["Primary Feedback"]["selection_branch"] == "intro_ideas_develop_main_point"


def test_mapping_and_render_metadata_do_not_reparse_or_mutate(analyzer, responses, monkeypatch):
    result = responses["T04"]
    analysis = deepcopy(result["stages"]["INTRODUCTION"]["analysis"])
    feedback = deepcopy(result["stages"]["INTRODUCTION"]["feedback"])
    decisions = deepcopy(trace(result))
    original = deepcopy((analysis, feedback, decisions))
    monkeypatch.setattr(analyzer.nlp_service, "parse", Mock(side_effect=AssertionError("metadata must not parse")))
    assert introduction_instructional_trace(analysis, feedback, decisions) == decisions["instructional_feedback"]
    assert (analysis, feedback, decisions) == original


@pytest.mark.skipif(NODE is None, reason="Node required for actual frontend functions")
@pytest.mark.parametrize("case", EXPECTATIONS)
def test_actual_tutor_transparency_and_export_share_cached_backend_item(responses, tmp_path, case):
    expected_mark = EXPECTATIONS[case][3]
    scenario = r'''
      elements["stage-text"].value=analysisResponse.analysis.linguistic_observations.text;
      const snapshot=JSON.stringify(analysisResponse);
      displayFeedback(analysisResponse);
      const model=studentFeedbackPresentation(analysisResponse);
      const backend=analysisResponse.research_trace.stages.INTRODUCTION.feedback_decisions.instructional_feedback;
      assert.equal(JSON.stringify(model.instructional_feedback),JSON.stringify(backend));
      assert.equal(model.tutor_items[0].lesson_id,backend.items[0].lesson_id);
      assert.equal(model.tutor_items[0].noticed,backend.items[0].prepared_guidance.noticed);
      assert.equal(model.tutor_items[0].why,backend.items[0].prepared_guidance.why);
      assert.equal(model.tutor_items[0].task_text,backend.items[0].prepared_guidance.task);
      if(model.status==="NEUTRAL_OBSERVATION"){
        assert.equal(model.writing_dimension,null);
        assert.equal(model.writing_skill,null);
        assert.equal(model.tutor_items[0].neutral_result,true);
        assert.equal(backend.items[0].highlight_spans[0].text,__EXPECTED__,"recorded span remains in transparency");
        assert.equal(elements["editor-mirror"].querySelectorAll("mark").length,0,"neutral review displays no error location");
        assert.equal(elements["tutor-evidence"].querySelectorAll("mark").length,0,"neutral review displays no tutor marks");
        assert.equal(elements["tutor-evidence"].children.length,0);
        assert.equal(elements["tutor-evidence-section"].hidden,true);
        assert.equal(elements["tutor-why-section"].hidden,true);
        assert.equal(elements["tutor-task-section"].hidden,true);
      } else {
        assert.equal(elements["editor-mirror"].querySelectorAll("mark").length,1);
        assert.equal(elements["editor-mirror"].querySelector("mark").textContent,__EXPECTED__);
        assert.equal(elements["tutor-evidence"].querySelector("mark").textContent,__EXPECTED__);
      }
      if(backend.items[0].working_text){assert.equal(elements["tutor-working"].textContent,backend.items[0].working_text);assert.equal(elements["tutor-working-section"].hidden,false);}
      const records=[];buildFullAnalysisReport(analysisResponse,records);
      const record=records.find(r=>r.path.endsWith('.feedback_decisions.instructional_feedback'));
      assert.equal(JSON.stringify(record.value),JSON.stringify(analysisReportValue(backend)));
      assert.equal(JSON.stringify(analysisResponse),snapshot);
    '''.replace("__EXPECTED__", json.dumps(expected_mark))
    _run_node_scenario(_make_stage_payload(responses[case]), scenario, tmp_path)


@pytest.mark.skipif(NODE is None, reason="Node required for exact-span fallback")
@pytest.mark.parametrize("damage", ["anchor", "text", "context", "event", "provenance"])
def test_invalid_evidence_never_falls_back_to_whole_reason_sentence(responses, tmp_path, damage):
    payload = deepcopy(_make_stage_payload(responses["T04"]))
    item = payload["research_trace"]["stages"]["INTRODUCTION"]["feedback_decisions"]["instructional_feedback"]["items"][0]
    if damage == "anchor":
        next(e for e in payload["analysis"]["rule_evidence"] if e["rule_id"].startswith("INTRO.REASON."))["evidence"][0]["clause_start"] = -1
    elif damage == "text":
        item["highlight_spans"][0]["text"] = "Not the source text"
    elif damage == "context":
        item["highlight_spans"][0]["context"]["end"] = 99999
    elif damage == "event":
        payload["analysis"]["rule_evidence"] = [e for e in payload["analysis"]["rule_evidence"] if not e["rule_id"].startswith("INTRO.REASON.")]
    else:
        payload["feedback"]["Feedback Provenance"] = []
    _run_node_scenario(payload, '''
      elements["stage-text"].value=analysisResponse.analysis.linguistic_observations.text;
      displayFeedback(analysisResponse);
      const model=studentFeedbackPresentation(analysisResponse);
      if(model.status==="NEUTRAL_OBSERVATION") assert.equal(model.tutor_items[0].neutral_result,true);
      else assert.equal(model.status,"ORIGINAL_FEEDBACK","damaged selection data must fail closed");
      assert.equal(elements["editor-mirror"].querySelectorAll("mark").length,0);
      assert.equal(elements["tutor-evidence"].querySelectorAll("mark").length,0);
    ''', tmp_path)
