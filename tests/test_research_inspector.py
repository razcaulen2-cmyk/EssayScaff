"""Research Inspector authorization and single-pass trace regressions."""

from unittest.mock import Mock

from werkzeug.security import generate_password_hash

from app import create_app
from services.draft_store import DraftStore
from services.essay_analysis_service import EssayAnalysisService
from services.nlp_service import NLPService
from tests.auth_helpers import login_student, register_student


TOPIC = "Should schools allow students to use artificial intelligence tools for learning?"
FOCUS = ["artificial intelligence", "education", "students", "technology", "critical thinking"]
INTRO = (
    "Artificial intelligence tools are becoming common in schools. "
    "Schools should allow students to use them because they help with learning."
)


def make_app(tmp_path, analysis_service=None):
    app = create_app(analysis_service=analysis_service, secret_key="research-inspector-test")
    app.config.update(TESTING=True, DRAFT_DATABASE_PATH=str(tmp_path / "inspector.sqlite3"))
    store = DraftStore(app.config["DRAFT_DATABASE_PATH"])
    return app, store


def create_teacher(store, username="research_teacher"):
    return store.create_teacher_user(username, generate_password_hash("teacher-password-1"))


def login_teacher(client, username="research_teacher"):
    response = login_student(client, username, "teacher-password-1")
    assert response.status_code == 302
    with client.session_transaction() as session:
        return session["_csrf_token"]


def test_student_analysis_requires_available_enrolled_assignment(tmp_path):
    analyzer = Mock()
    app, store = make_app(tmp_path, analysis_service=analyzer)
    teacher = create_teacher(store)
    classroom = store.create_classroom(teacher["user_id"], "Writing", "English", "A")
    assignment = store.create_assignment(
        teacher["user_id"], classroom["classroom_id"],
        "Topic", TOPIC, "Instructions", ",".join(FOCUS),
    )
    client = app.test_client()
    assert register_student(client, "not_enrolled").status_code == 302

    payload = {
        "stage_id": "INTRODUCTION",
        "assignment_id": assignment["assignment_id"],
        "introduction_text": INTRO,
    }
    assert client.post("/api/analyze-stage", json=payload).status_code == 404
    analyzer.analyze.assert_not_called()

    assert client.post(
        "/api/classroom-enrollments", json={"enrollment_code": classroom["enrollment_code"]}
    ).status_code == 200
    store.soft_delete_assignment(teacher["user_id"], assignment["assignment_id"])
    assert client.post("/api/analyze-stage", json=payload).status_code == 404
    analyzer.analyze.assert_not_called()


def test_research_inspector_is_teacher_only_and_does_not_persist_samples(tmp_path):
    app, store = make_app(tmp_path, analysis_service=EssayAnalysisService())
    create_teacher(store)
    teacher_client = app.test_client()
    csrf = login_teacher(teacher_client)

    dashboard = teacher_client.get("/teacher")
    assert dashboard.status_code == 200
    assert b"NLP Research Inspector" in dashboard.data
    page = teacher_client.get("/teacher/research-inspector")
    assert page.status_code == 200
    assert b"NLP Research Inspector" in page.data
    assert b"research-process-nav" in page.data
    assert b"Load Technology in Education sample" in page.data

    metadata = teacher_client.get("/api/research-inspector/metadata")
    assert metadata.status_code == 200
    metadata_json = metadata.get_json()
    assert [item["id"] for item in metadata_json["processes"]] == [f"{i:02}" for i in range(12)]
    assert all(len(item["sections"]) == 10 for item in metadata_json["processes"])
    assert metadata_json["evaluation"]["status"] == "pending"
    assert metadata_json["evaluation"]["human_reference_count"] == 0
    assert metadata_json["evaluation"]["diagnostic_sample_count"] == 31

    payload = {
        "stage_id": "INTRODUCTION",
        "assignment_topic": TOPIC,
        "focus_terms": ",".join(FOCUS),
        "introduction_text": INTRO,
    }
    csrf_failure = teacher_client.post(
        "/api/research-inspector/analyze", json=payload, headers={"X-CSRF-Token": ""}
    )
    assert csrf_failure.status_code == 400
    response = teacher_client.post(
        "/api/research-inspector/analyze",
        json=payload,
        headers={"X-CSRF-Token": csrf},
    )
    assert response.status_code == 200
    result = response.get_json()
    assert result["stage_id"] == "INTRODUCTION"
    assert result["analysis"]["linguistic_observations"]["counts"] == {
        "alphabetic_word_count": 20,
        "sentence_count": 2,
        "token_count": 22,
    }
    assert [
        (item["focus_term"], item["observed_text"], item["start"], item["end"], item["match_method"])
        for item in result["analysis"]["lexical_topic_evidence"]["matches"]
    ] == [
        ("artificial intelligence", "Artificial intelligence", 0, 23, "direct"),
        ("students", "students", 83, 91, "direct"),
    ]
    assert len(result["analysis"]["rule_evidence"]) == 9
    assert [item["text"] for item in result["analysis"]["development_evidence"]["evidence"]] == ["becoming", "allow", "use", "help"]
    assert result["research_trace"]["runtime"]["model"]["package_name"] == "core_web_sm"
    assert result["analysis"]["linguistic_observations"]["tokens"][0]["index"] == 0
    assert "rule_evaluation_trace" in result["analysis"]
    assert any(item["status"] == "TRIGGERED" for item in result["analysis"]["rule_evaluation_trace"])
    assert result["research_trace"]["stages"]["INTRODUCTION"]["topic_service"]["steps"][0]["execution_status"] == "EXECUTED"
    assert "assignment_id" not in result
    assert result["research_trace"]["request_validation_and_assignment_resolution_ms"] >= 0
    assert result["research_trace"]["stages"]["INTRODUCTION"]["topic_service"]["steps"][1]["output"]
    feedback_trace = result["research_trace"]["stages"]["INTRODUCTION"]["feedback_decisions"]
    # The recorded "should" sentence contains only the broad term "students";
    # the specific assignment term appears in a different sentence, so the
    # topic-linked position check remains unresolved (conservative by design).
    assert feedback_trace["fields"]["Primary Feedback"]["selection_branch"] == "intro_ideas_state_position"
    assert feedback_trace["fields"]["Next Step"]["rule_ids"] == [
        "INTRO.POSITION.NO_RELEVANT_POSITION_OBSERVED",
        "INTRO.CLAUSE.SUBJECT_PREDICATE_CANDIDATE",
    ]
    forbidden_reference = teacher_client.post(
        "/api/research-inspector/analyze",
        json={**payload, "assignment_id": 1},
        headers={"X-CSRF-Token": csrf},
    )
    assert forbidden_reference.status_code == 400
    for ownership_field in ("session_id", "user_id"):
        rejected = teacher_client.post(
            "/api/research-inspector/analyze",
            json={**payload, ownership_field: "untrusted-reference"},
            headers={"X-CSRF-Token": csrf},
        )
        assert rejected.status_code == 400

    with teacher_client.session_transaction() as session:
        assert session["_csrf_token"] == csrf
    with store._connection() as connection:
        assert connection.execute("SELECT COUNT(*) FROM writing_sessions").fetchone()[0] == 0
        assert connection.execute("SELECT COUNT(*) FROM writing_revisions").fetchone()[0] == 0
        assert connection.execute("SELECT COUNT(*) FROM submissions").fetchone()[0] == 0

    student = app.test_client()
    assert register_student(student, "student_research_denied").status_code == 302
    assert student.get("/teacher/research-inspector").status_code == 403
    assert student.get("/api/research-inspector/metadata").status_code == 403
    assert student.post(
        "/api/research-inspector/analyze", json=payload
    ).status_code == 403
    ordinary_analysis = student.post(
        "/api/analyze-stage",
        json={key: value for key, value in payload.items() if key != "stage_id"} | {"stage_id": "INTRODUCTION"},
    )
    assert ordinary_analysis.status_code == 200
    assert "research_trace" not in ordinary_analysis.get_json()


def test_rule_trace_covers_body_and_conclusion_and_does_not_change_feedback():
    service = EssayAnalysisService()
    body = (
        "Artificial intelligence can help students learn new vocabulary. For example, students can use context to understand unfamiliar words.\n\n"
        "Reading also helps students follow longer arguments."
    )
    conclusion = "In conclusion, regular reading helps students understand new ideas and continue learning."
    ordinary = service.analyze(TOPIC, FOCUS, INTRO, body, conclusion)
    traced = service.analyze(
        TOPIC, FOCUS, INTRO, body, conclusion, include_research_trace=True
    )
    for stage in ("INTRODUCTION", "BODY", "CONCLUSION"):
        ordinary_stage = ordinary["stages"][stage]
        traced_stage = traced["stages"][stage]
        assert traced["research_trace"]["stages"][stage]["execution_status"] == "EXECUTED"
        assert traced_stage["feedback"] == ordinary_stage["feedback"]
        assert traced_stage["supplied_text"] == ordinary_stage["supplied_text"]
        assert traced_stage["analysis"]["rule_evidence"] == ordinary_stage["analysis"]["rule_evidence"]
        assert all(item["rule_id"] for item in traced_stage["analysis"]["rule_evaluation_trace"])

    body_trace = traced["research_trace"]["stages"]["BODY"]
    body_wordnet = body_trace["topic_service"]["steps"][-1]
    assert body_wordnet["execution_status"] == "SKIPPED"
    assert body_trace["feedback_decisions"]["fields"]["Primary Feedback"]["selection_branch"]
    body_comparison_wordnet = traced["stages"]["BODY"]["analysis"]["introduction_to_body_continuity"]["wordnet_relationship_candidates"]
    assert body_comparison_wordnet["status"] in {
        "AVAILABLE", "RESOURCE_MISSING"
    }
    if body_comparison_wordnet["status"] == "AVAILABLE":
        assert "lookup_pairs" in body_comparison_wordnet
    conclusion_analysis = traced["stages"]["CONCLUSION"]["analysis"]
    assert conclusion_analysis["synthesis_structure_candidates"]["status"]
    assert conclusion_analysis["closure_candidates"]["status"]
    assert set(traced["research_trace"]["stages"]["CONCLUSION"]["cross_stage_comparison_inputs"]) == {
        "introduction_concepts", "body_concepts", "conclusion_concepts"
    }
    assert traced["research_trace"]["stages"]["CONCLUSION"]["feedback_decisions"]["fields"]["Primary Feedback"]["selection_condition"]
    conclusion_wordnet = traced["research_trace"]["stages"]["CONCLUSION"]["topic_service"]["steps"][-1]
    assert conclusion_wordnet["execution_status"] in {"EXECUTED", "FAILED"}
    assert "lookup_pairs" in conclusion_wordnet


def test_trace_collection_does_not_reparse_supplied_sections():
    nlp_service = NLPService()
    original_pipeline = nlp_service.nlp
    counting_pipeline = Mock(wraps=original_pipeline)
    counting_pipeline.meta = original_pipeline.meta
    counting_pipeline.pipe_names = original_pipeline.pipe_names
    counting_pipeline.disabled = original_pipeline.disabled
    nlp_service.nlp = counting_pipeline
    try:
        service = EssayAnalysisService(nlp_service)
        service.analyze(
            TOPIC,
            ["reading", "students", "learning"],
            "Regular reading helps students learn.",
            "Regular reading helps students practice.",
            "In conclusion, reading helps students learn.",
            include_research_trace=True,
        )
        # Three supplied focus phrases and three section documents: rule execution
        # and trace packaging reuse those Docs rather than parsing them again.
        assert counting_pipeline.call_count == 6
    finally:
        nlp_service.nlp = original_pipeline


def test_research_inspector_frontend_uses_safe_text_rendering_and_exposes_raw_actions():
    from pathlib import Path

    script = (Path(__file__).resolve().parents[1] / "static" / "research_inspector.js").read_text(encoding="utf-8")
    template = (Path(__file__).resolve().parents[1] / "templates" / "research_inspector.html").read_text(encoding="utf-8")
    assert ".innerHTML" not in script
    assert "textContent" in script
    assert "copy-research-json" in template
    assert "download-research-json" in template
    assert "research-process-nav" in template
