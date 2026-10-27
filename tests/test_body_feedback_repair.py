"""Body repair: real observations, contingent guidance and one cached decision."""

from copy import deepcopy
import json
from pathlib import Path
from unittest.mock import Mock

import pytest
from werkzeug.security import generate_password_hash

from app import create_app
from services.draft_store import DraftStore
from services.essay_analysis_service import EssayAnalysisService
from services.feedback_service import FeedbackService
from services.tutoring_lessons import body_instructional_trace
from tests.auth_helpers import login_student, register_student
from tests.test_reason_highlighting import NODE, _make_stage_payload, _run_node_scenario

CORPUS = json.loads(Path(__file__).with_name("body_feedback_repair_cases.json").read_text(encoding="utf-8"))
DEVELOP = ("body_ideas_develop_point", "Ideas", "Develop Your Supporting Details", "HELP-BODY-DEVELOP-POINT")
REPEAT = ("body_sentence_fluency_sentence_beginnings", "Sentence Fluency", "Review Repeated Sentence Openings", "HELP-BODY-SENTENCE-BEGINNINGS")
NEUTRAL = ("body_neutral_observable", None, None, None)
EXPECTED = {
    "B01": NEUTRAL, "B02": DEVELOP, "B03": DEVELOP,
    "B04": ("body_organization_paragraph_shape", "Organization", "Build Your Paragraph", "HELP-BODY-PARAGRAPH-SHAPE"),
    "B05": REPEAT, "B06": NEUTRAL, "B07": NEUTRAL, "B08": NEUTRAL,
    "B09": ("body_organization_paragraph_link", "Organization", "Review Paragraph Connections", "HELP-BODY-PARAGRAPH-LINK"),
    "B10": NEUTRAL, "B11": NEUTRAL, "B12": REPEAT,
}


@pytest.fixture(scope="module")
def analyzer():
    return EssayAnalysisService()


@pytest.fixture(scope="module")
def responses(analyzer):
    return {key: analyzer.analyze(CORPUS["assignment_topic"], CORPUS["focus_terms"], body_text=text,
                                 introduction_text=None if key == "B08" else CORPUS["introduction"],
                                 include_research_trace=True) for key, text in CORPUS["cases"].items()}


def trace(result):
    return result["research_trace"]["stages"]["BODY"]["feedback_decisions"]


@pytest.mark.parametrize("case", EXPECTED)
def test_actual_body_selection_neutral_or_supported_lesson(responses, case):
    result = responses[case]
    selected = trace(result)
    metadata = selected["instructional_feedback"]
    feedback = result["stages"]["BODY"]["feedback"]
    branch, trait, skill, lesson = EXPECTED[case]
    primary = selected["fields"]["Primary Feedback"]
    assert primary["selection_branch"] == metadata["selection_branch"] == branch
    assert primary["trait"] == trait and primary["skill"] == skill
    assert metadata["student_message"] == primary["selected_message"] == feedback["Primary Feedback"]
    assert metadata["selection_condition"] == primary["selection_condition"]
    assert selected["fields"]["Next Step"]["selection_branch"] == branch
    assert len(metadata["strengths"]) <= 2
    events = {e["rule_id"]: e for e in result["stages"]["BODY"]["analysis"]["rule_evidence"]}
    assert "NO_SUPPORTED_CONCERN_SELECTED" not in events
    if lesson is None:
        assert metadata["selection_status"] == "NO_SUPPORTED_CONCERN_SELECTED"
        assert metadata["items"] == []
        assert all(metadata["neutral_result"][key] is None for key in ("trait", "skill", "lesson_id"))
        assert feedback["Next Step"] == "" and feedback["Needs Attention"] == []
        assert "higher-priority" not in feedback["Primary Feedback"]
        assert not any(check["condition_matched"] for check in metadata["selection_checks"])
    else:
        item = metadata["items"][0]
        assert metadata["selection_status"] == "SUPPORTED_CONCERN_SELECTED"
        assert (item["trait"], item["skill"], item["lesson_id"]) == (trait, skill, lesson)
        assert item["rule_ids"] == primary["rule_ids"]
        assert item["selection_condition"] == primary["selection_condition"]
        assert item["catalog_reference"] == {"file": "content/lessons/feedback_help.json", "version": 6, "lesson_id": lesson}
        assert item["feedback_purpose"] in {"DEVELOPMENT_TASK", "STRUCTURAL_REVIEW_TASK", "WORDING_REVIEW_TASK"}
        assert all(events[rule]["triggered"] for rule in item["rule_ids"])
        assert item["prepared_guidance"]["task"]
        assert "{" not in item["prepared_guidance"]["noticed"] + item["prepared_guidance"]["task"]
        if case == "B04":
            assert metadata["strengths"] == [] and item["working_text"] == ""
            assert feedback["What's Working"] == [], "keyword presence in a list must not be rewarded as a strength"
            assert result["stages"]["BODY"]["analysis"]["paragraphs"][0]["focus_term_evidence"], "word matches remain inspectable"
    assert {r["trait"] for r in metadata["coverage"]} == {"Ideas", "Organization", "Voice", "Word Choice", "Sentence Fluency", "Conventions", "Presentation"}
    assert all(r["trait_quality_assessment"] == "NOT_PERFORMED" for r in metadata["coverage"])
    assert {r["trait"] for r in metadata["coverage"] if r["status"] == "NOT_EVALUATED"} == {"Voice", "Conventions", "Presentation"}


def test_original_66_word_body_retains_candidates_and_strength_source_events(responses):
    result = responses["B01"]
    analysis = result["stages"]["BODY"]["analysis"]
    assert analysis["paragraph_count"] == 2
    assert sum(p["counts"]["sentence_count"] for p in analysis["paragraphs"]) == 6
    assert sum(p["counts"]["alphabetic_word_count"] for p in analysis["paragraphs"]) == 66
    metadata = trace(result)["instructional_feedback"]
    assert metadata["strengths"][0]["text"] == "Both paragraphs contain possible opening statements and additional sentence structures."
    assert metadata["strengths"][0]["rule_ids"] == [f"BODY.P{p}.{kind}.CANDIDATE" for p in (1, 2) for kind in ("TOPIC_SENTENCE", "SUPPORTING_DETAIL")]
    for p in analysis["paragraphs"]:
        assert p["topic_sentence_candidates"] and p["supporting_detail_candidates"]["candidates"]
        assert p["example_or_explanation_markers"] == []
    source = CORPUS["cases"]["B01"]
    for strength in metadata["strengths"]:
        for reference in strength["source_positions"]:
            assert reference["rule_id"] in strength["rule_ids"]
            for position in reference["positions"]:
                assert source[position["start"]:position["end"]] == position["text"]
    assert len(result["stages"]["BODY"]["feedback"]["What's Working"]) >= 6


@pytest.mark.parametrize("case", ["B02", "B03", "B04", "B05", "B09", "B12"])
def test_body_highlights_are_source_exact_and_correctly_paragraph_scoped(responses, case):
    result = responses[case]
    source = CORPUS["cases"][case]
    analysis = result["stages"]["BODY"]["analysis"]
    item = trace(result)["instructional_feedback"]["items"][0]
    plans = item["highlight_spans"]
    if case == "B09":
        assert plans == []  # A wording absence is not an invented error location.
    elif case in {"B05", "B12"}:
        assert [p["text"] for p in plans] == ["Students can"] * 3
        assert sum(p["end"] - p["start"] for p in plans) < len(source)
    else:
        assert [p["text"] for p in plans] == [CORPUS["cases"]["B02"] if case == "B03" else source]
    for plan in plans:
        assert source[plan["start"]:plan["end"]] == plan["text"]
        paragraph = analysis["paragraphs"][plan["context"]["paragraph_index"] - 1]
        assert plan["context"]["paragraph_index"] in item["paragraph_indices"]
        assert paragraph["start"] <= plan["start"] < plan["end"] <= paragraph["end"]
        assert source[plan["context"]["start"]:plan["context"]["end"]] == paragraph["text"]
    if case == "B03":
        assert item["paragraph_indices"] == [2]
        assert "Paragraph 2" in item["prepared_guidance"]["noticed"]
        assert plans[0]["start"] == source.rindex(CORPUS["cases"]["B02"])


def test_structural_development_precedes_lexical_connection_review(analyzer):
    text = CORPUS["cases"]["B06"] + "\n\nAn orchestra performs symphonies."
    result = analyzer.analyze(CORPUS["assignment_topic"], CORPUS["focus_terms"], body_text=text, include_research_trace=True)
    selected = trace(result)
    assert selected["fields"]["Primary Feedback"]["selection_branch"] == DEVELOP[0]
    assert selected["instructional_feedback"]["items"][0]["paragraph_indices"] == [2]
    checks = {c["branch"]: c for c in selected["selection_checks"]}
    assert checks[DEVELOP[0]]["status"] == "SELECTED"
    assert checks["body_organization_paragraph_link"]["condition_matched"]
    assert checks["body_organization_paragraph_link"]["status"] == "MATCHED_NOT_SELECTED_HIGHER_PRIORITY"


def test_missing_introduction_is_availability_not_a_revision_task(responses):
    left, right = [trace(responses[key])["instructional_feedback"] for key in ("B06", "B08")]
    assert left["neutral_result"] == right["neutral_result"]
    assert right["introduction_context"]["status"] == "NOT_SUPPLIED"
    assert right["introduction_context"]["text"] is None
    assert left["introduction_context"]["text"] == CORPUS["introduction"]
    assert right["items"] == []


@pytest.mark.parametrize("case", ["B07", "B10", "B11"])
def test_nonsense_keywords_and_one_rich_sentence_are_not_quality_verdicts(responses, case):
    metadata = trace(responses[case])["instructional_feedback"]
    assert metadata["selection_status"] == "NO_SUPPORTED_CONCERN_SELECTED"
    assert metadata["items"] == []
    assert "logically correct or sufficient" in metadata["neutral_result"]["limitation"]
    assert all(row["trait_quality_assessment"] == "NOT_PERFORMED" for row in metadata["coverage"])


@pytest.mark.parametrize("damage", ["absent", "triggered_false", "fired_false"])
def test_no_development_lesson_without_its_fired_absence_event(responses, damage):
    analysis = deepcopy(responses["B02"]["stages"]["BODY"]["analysis"])
    rule = "BODY.P1.SUPPORTING_DETAIL.NOT_OBSERVED"
    event = next(e for e in analysis["rule_evidence"] if e["rule_id"] == rule)
    if damage == "absent":
        analysis["rule_evidence"].remove(event)
    else:
        event[damage.removesuffix("_false")] = False
    output = FeedbackService().generate_body(analysis, include_trace=True)
    assert output["_Research Decision Trace"]["selection_status"] == "NO_SUPPORTED_CONCERN_SELECTED"
    assert output["_Research Decision Trace"]["instructional_feedback"]["items"] == []
    assert output["Next Step"] == ""


def test_body_record_builder_never_reparses_or_mutates(analyzer, responses, monkeypatch):
    result = responses["B03"]
    analysis = deepcopy(result["stages"]["BODY"]["analysis"])
    feedback = deepcopy(result["stages"]["BODY"]["feedback"])
    decisions = deepcopy(trace(result))
    original = deepcopy((analysis, feedback, decisions))
    monkeypatch.setattr(analyzer.nlp_service, "parse", Mock(side_effect=AssertionError("Body presentation must reuse observations")))
    assert body_instructional_trace(analysis, feedback, decisions) == decisions["instructional_feedback"]
    assert (analysis, feedback, decisions) == original


@pytest.mark.skipif(NODE is None, reason="Node required for real app.js rendering")
@pytest.mark.parametrize("case", EXPECTED)
def test_body_tutor_trace_export_and_exact_marks_use_one_record(responses, case, tmp_path):
    payload = _make_stage_payload(responses[case], "BODY")
    _run_node_scenario(payload, r'''
      elements["stage-text"].value=analysisResponse.analysis.input_text;
      const original=JSON.stringify(analysisResponse);
      displayFeedback(analysisResponse);
      const model=studentFeedbackPresentation(analysisResponse);
      const backend=analysisResponse.research_trace.stages.BODY.feedback_decisions.instructional_feedback;
      assert.equal(JSON.stringify(model.instructional_feedback),JSON.stringify(backend));
      const marks=elements["editor-mirror"].querySelectorAll("mark").map(m=>m.textContent);
      assert.deepEqual(marks,elements["tutor-evidence"].querySelectorAll("mark").map(m=>m.textContent));
      assert.equal(JSON.stringify(marks),JSON.stringify((backend.items[0]?.highlight_spans||[]).map(s=>s.text)));
      if(backend.selection_status==="NO_SUPPORTED_CONCERN_SELECTED"){
        assert.equal(model.status,"NO_SUPPORTED_CONCERN_SELECTED");
        assert.equal(model.writing_dimension,null);assert.equal(model.writing_skill,null);assert.equal(model.teaching_content_source,null);
        assert.equal(model.tutor_items[0].lesson_id,null);assert.equal(model.tutor_items[0].task_text,"");
        assert.equal("How to improve" in model.displayed_guidance,false);
        assert.equal(elements["tutor-task-section"].hidden,true);assert.equal(elements["tutor-why-section"].hidden,true);
        assert.equal(elements["tutor-evidence-section"].hidden,true);assert.equal(marks.length,0);
        assert.equal(model.displayed_strengths,backend.neutral_result.working);
      }else{
        assert.equal(model.tutor_items[0].lesson_id,backend.items[0].lesson_id);
        assert.equal(model.tutor_items[0].noticed,backend.items[0].prepared_guidance.noticed);
        assert.equal(model.tutor_items[0].why,backend.items[0].prepared_guidance.why);
        assert.equal(model.tutor_items[0].task_text,backend.items[0].prepared_guidance.task);
        assert.equal(elements["tutor-task-section"].hidden,false);
      }
      const exported=[];buildFullAnalysisReport(analysisResponse,exported);
      const recorded=exported.find(r=>r.path.endsWith(".BODY.feedback_decisions.instructional_feedback"));
      assert.ok(recorded);assert.equal(JSON.stringify(recorded.value),JSON.stringify(analysisReportValue(backend)));
      assert.equal(JSON.stringify(analysisResponse),original);
    ''', tmp_path)


@pytest.mark.skipif(NODE is None, reason="Node required for exact-evidence rejection")
@pytest.mark.parametrize("damage", ["mark", "anchor", "paragraph", "subject", "event", "provenance", "catalog"])
def test_corrupt_body_evidence_does_not_fall_back_to_a_paragraph_highlight(responses, damage, tmp_path):
    payload = deepcopy(_make_stage_payload(responses["B03"], "BODY"))
    item = payload["research_trace"]["stages"]["BODY"]["feedback_decisions"]["instructional_feedback"]["items"][0]
    rule = "BODY.P2.SUPPORTING_DETAIL.NOT_OBSERVED"
    if damage == "mark":
        item["highlight_spans"][0]["text"] = "not the original writing"
    elif damage == "anchor":
        item["highlight_spans"][0]["anchor"]["end"] = 99999
    elif damage == "paragraph":
        item["highlight_spans"][0]["context"]["paragraph_index"] = 1
    elif damage == "subject":
        payload["analysis"]["paragraphs"][1]["clause_structure_candidates"][0]["subject_evidence"][0]["start"] = -1
    elif damage == "event":
        payload["analysis"]["rule_evidence"] = [e for e in payload["analysis"]["rule_evidence"] if e["rule_id"] != rule]
    elif damage == "provenance":
        payload["feedback"]["Feedback Provenance"] = []
    else:
        item["catalog_reference"]["version"] = -1
    _run_node_scenario(payload, r'''
      elements["stage-text"].value=analysisResponse.analysis.input_text;
      displayFeedback(analysisResponse);
      assert.equal(elements["editor-mirror"].querySelectorAll("mark").length,0);
      assert.equal(elements["tutor-evidence"].querySelectorAll("mark").length,0);
    ''', tmp_path)


@pytest.fixture(scope="module")
def api_clients(tmp_path_factory, analyzer):
    app = create_app(analyzer, secret_key="body-repair-disposable")
    app.config.update(TESTING=True, DRAFT_DATABASE_PATH=str(tmp_path_factory.mktemp("body-repair") / "isolated.sqlite3"))
    student = app.test_client()
    assert register_student(student, "body_repair_student").status_code == 302
    store = DraftStore(app.config["DRAFT_DATABASE_PATH"])
    store.create_teacher_user("body_repair_teacher", generate_password_hash("body-repair-password"))
    teacher = app.test_client()
    assert login_student(teacher, "body_repair_teacher", "body-repair-password").status_code == 302
    return student, teacher


@pytest.mark.parametrize("case", EXPECTED)
def test_student_and_professor_apis_record_identical_body_decision(api_clients, case):
    student, teacher = api_clients
    payload = {"stage_id": "BODY", "assignment_topic": CORPUS["assignment_topic"], "focus_terms": CORPUS["focus_terms"],
               "body_text": CORPUS["cases"][case], "introduction_text": "" if case == "B08" else CORPUS["introduction"],
               "include_transparency_trace": True}
    student_result = student.post("/api/analyze-stage", json=payload)
    payload.pop("include_transparency_trace")
    teacher_result = teacher.post("/api/research-inspector/analyze", json=payload)
    assert student_result.status_code == teacher_result.status_code == 200
    left, right = student_result.get_json(), teacher_result.get_json()
    assert trace(left)["instructional_feedback"] == trace(right)["instructional_feedback"]
    assert left["analysis"]["input_text"] == right["analysis"]["input_text"] == CORPUS["cases"][case]
