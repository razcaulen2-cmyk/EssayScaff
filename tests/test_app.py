"""Route-level checks for the three-stage Flask interface."""

import json
import re

import pytest

from app import create_app
from services.essay_analysis_service import EssayAnalysisService
from auth_helpers import register_student


class FakeAnalysisService:
    def __init__(self):
        self.calls = []

    def analyze(self, **kwargs):
        self.calls.append(kwargs)
        stage_id = (
            "CONCLUSION" if "conclusion_text" in kwargs
            else "BODY" if "body_text" in kwargs
            else "INTRODUCTION"
        )
        return {
            "interpretation_limit": "Observation only; no readiness decision is made.",
            "stages": {
                stage_id: {
                    "stage_id": stage_id,
                    "availability": "ANALYZED",
                    "analysis": {"stage": stage_id, "rule_evidence": []},
                    "feedback": {
                        "Current Goal": "Introduce the subject.",
                        "Primary Feedback": "A clause candidate was observed.",
                        "What's Working": ["A focus term matched."],
                        "Needs Attention": ["Meaning was not assessed."],
                        "Next Step": "Review the sentence in context.",
                        "Feedback Provenance": [],
                    },
                }
            },
        }


@pytest.fixture
def client(tmp_path):
    app = create_app(FakeAnalysisService(), secret_key="test-phase6a-secret")
    app.config["DRAFT_DATABASE_PATH"] = str(tmp_path / "app-tests.sqlite3")
    app.config["TESTING"] = True
    test_client = app.test_client()
    assert register_student(test_client).status_code == 302
    return test_client


def test_homepage_renders_editor_and_feedback_sections(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"EssayScaff" in response.data
    assert b"Assignment topic" in response.data
    assert b"Analyze Now" in response.data
    assert b"Feedback updates after a short pause. Analyze Now checks immediately" in response.data
    assert b"Before you continue to Body" in response.data
    assert b"Continue Anyway" in response.data
    assert b"This is a progression checklist, not a writing-quality grade" in response.data
    assert b"Writing Tutor" in response.data
    assert b"Needs Attention" in response.data
    assert b'data-stage="INTRODUCTION"' in response.data
    assert b'data-stage="BODY"' in response.data
    assert b'<button class="stage-tab" type="button" data-stage="BODY" aria-pressed="false">Body</button>' in response.data
    assert b'data-stage="CONCLUSION"' in response.data
    assert b'data-stage="ESSAY_REVIEW"' in response.data
    assert response.data.index(b'data-stage="INTRODUCTION"') < response.data.index(b'data-stage="BODY"')
    assert response.data.index(b'data-stage="BODY"') < response.data.index(b'data-stage="CONCLUSION"')
    assert response.data.index(b'data-stage="CONCLUSION"') < response.data.index(b'data-stage="ESSAY_REVIEW"')
    assert b"Save Draft" in response.data
    assert b"Save Revision" in response.data
    assert b"Revision History" in response.data
    assert b"Unsaved changes are protected when you navigate within the app" in response.data
    assert b"Learn how to write your Introduction" in response.data
    assert b'id="introduction-lesson-panel"' in response.data
    lesson_json = re.search(
        rb'<script id="introduction-lesson-definition" type="application/json">(.*?)</script>',
        response.data,
        re.DOTALL,
    )
    assert lesson_json is not None
    assert json.loads(lesson_json.group(1))["lesson_id"] == "INTRO-LESSON-001"


def test_existing_brand_logo_is_served_without_authentication():
    app = create_app(FakeAnalysisService(), secret_key="logo-route-test")
    response = app.test_client().get("/assets/essayscaff-logo.png")
    assert response.status_code == 200
    assert response.mimetype == "image/png"
    assert response.data.startswith(b"\x89PNG\r\n\x1a\n")


def test_static_interface_assets_are_available(client):
    assert client.get("/static/style.css").status_code == 200
    assert client.get("/static/app.js").status_code == 200


def test_endpoint_uses_existing_coordinator_and_preserves_writing(client):
    coordinator = client.application.config["ANALYSIS_SERVICE"]
    writing = "  Students read more when books are easy to reach.  "
    response = client.post(
        "/api/analyze-introduction",
        json={
            "assignment_topic": " Reading habits ",
            "focus_terms": "reading habits, students",
            "introduction_text": writing,
        },
    )

    assert response.status_code == 200
    assert coordinator.calls == [
        {
            "assignment_topic": "Reading habits",
            "focus_terms": ["reading habits", "students"],
            "introduction_text": writing,
        }
    ]
    payload = response.get_json()
    assert payload["stage_id"] == "INTRODUCTION"
    assert payload["analysis"]["stage"] == "INTRODUCTION"
    assert payload["feedback"]["Primary Feedback"] == "A clause candidate was observed."


def test_body_endpoint_sends_body_and_optional_introduction_context(client):
    coordinator = client.application.config["ANALYSIS_SERVICE"]
    body = "First body paragraph.\n\nSecond body paragraph."
    response = client.post(
        "/api/analyze-stage",
        json={
            "stage_id": "BODY",
            "assignment_topic": "Reading habits",
            "focus_terms": ["reading", "students"],
            "introduction_text": "Reading can help students.",
            "body_text": body,
        },
    )
    assert response.status_code == 200
    assert response.get_json()["stage_id"] == "BODY"
    assert coordinator.calls[-1] == {
        "assignment_topic": "Reading habits",
        "focus_terms": ["reading", "students"],
        "introduction_text": "Reading can help students.",
        "body_text": body,
    }


def test_conclusion_endpoint_sends_available_prior_stages(client):
    coordinator = client.application.config["ANALYSIS_SERVICE"]
    response = client.post(
        "/api/analyze-stage",
        json={
            "stage_id": "CONCLUSION",
            "assignment_topic": "Reading habits",
            "conclusion_text": "Overall, reading can help students.",
            "introduction_text": "Reading can help students learn.",
            "body_text": "Students can learn through regular reading.\n\nBooks provide examples.",
        },
    )
    assert response.status_code == 200
    assert response.get_json()["stage_id"] == "CONCLUSION"
    assert coordinator.calls[-1]["conclusion_text"] == "Overall, reading can help students."
    assert coordinator.calls[-1]["introduction_text"] == "Reading can help students learn."
    assert coordinator.calls[-1]["body_text"].count("\n\n") == 1


def test_conclusion_endpoint_keeps_missing_prior_stages_unavailable(client):
    coordinator = client.application.config["ANALYSIS_SERVICE"]
    response = client.post(
        "/api/analyze-stage",
        json={
            "stage_id": "CONCLUSION",
            "assignment_topic": "Reading habits",
            "conclusion_text": "Overall, reading helps students.",
        },
    )
    assert response.status_code == 200
    assert coordinator.calls[-1] == {
        "assignment_topic": "Reading habits",
        "focus_terms": None,
        "conclusion_text": "Overall, reading helps students.",
    }


def test_body_endpoint_does_not_invent_missing_introduction_context(client):
    coordinator = client.application.config["ANALYSIS_SERVICE"]
    response = client.post(
        "/api/analyze-stage",
        json={
            "stage_id": "BODY",
            "assignment_topic": "Reading habits",
            "body_text": "Students read books.",
        },
    )
    assert response.status_code == 200
    assert "introduction_text" not in coordinator.calls[-1]
    assert response.get_json()["stage_id"] == "BODY"


def test_stage_endpoint_rejects_unknown_stage_and_invalid_context(client):
    unknown = client.post(
        "/api/analyze-stage",
        json={"stage_id": "ESSAY", "assignment_topic": "Reading", "body_text": "Some text."},
    )
    invalid_context = client.post(
        "/api/analyze-stage",
        json={
            "stage_id": "CONCLUSION",
            "assignment_topic": "Reading",
            "conclusion_text": "Some text.",
            "body_text": 42,
        },
    )
    invalid_stage_type = client.post(
        "/api/analyze-stage",
        json={"stage_id": [], "assignment_topic": "Reading", "body_text": "Some text."},
    )
    assert unknown.status_code == 400
    assert invalid_context.status_code == 400
    assert invalid_stage_type.status_code == 400


@pytest.mark.parametrize(
    ("payload", "message"),
    [
        ({"assignment_topic": "", "introduction_text": "Some writing."}, "assignment topic"),
        ({"assignment_topic": "Reading", "introduction_text": "  "}, "Introduction"),
    ],
)
def test_empty_required_fields_return_clear_client_errors(client, payload, message):
    response = client.post("/api/analyze-introduction", json=payload)
    assert response.status_code == 400
    assert message in response.get_json()["error"]
    assert not client.application.config["ANALYSIS_SERVICE"].calls


@pytest.mark.parametrize(
    ("payload", "status"),
    [
        (None, 400),
        ({"assignment_topic": [], "introduction_text": "Text."}, 400),
        ({"assignment_topic": "Reading", "introduction_text": "Text.", "focus_terms": [1]}, 400),
        ({"assignment_topic": "x" * 501, "introduction_text": "Text."}, 400),
        ({"assignment_topic": "Reading", "introduction_text": "x" * 12001}, 400),
    ],
)
def test_invalid_inputs_return_json_errors(client, payload, status):
    if payload is None:
        response = client.post("/api/analyze-introduction", data="not json", content_type="text/plain")
    else:
        response = client.post("/api/analyze-introduction", json=payload)
    assert response.status_code == status
    assert isinstance(response.get_json()["error"], str)


def test_coordinator_exception_returns_understandable_server_error(tmp_path):
    class BrokenCoordinator:
        def analyze(self, **_kwargs):
            raise RuntimeError("internal detail must not be sent to the student")

    app = create_app(BrokenCoordinator(), secret_key="test-phase6a-secret")
    app.config["DRAFT_DATABASE_PATH"] = str(tmp_path / "broken-app.sqlite3")
    app.config["TESTING"] = True
    client = app.test_client()
    assert register_student(client).status_code == 302
    response = client.post(
        "/api/analyze-introduction",
        json={"assignment_topic": "Reading", "introduction_text": "Students read books."},
    )
    assert response.status_code == 500
    assert response.get_json()["error"] == "Introduction analysis could not be completed. Please try again."
    assert "internal detail" not in response.get_data(as_text=True)


def test_real_coordinator_returns_introduction_feedback_without_readiness(tmp_path):
    app = create_app(EssayAnalysisService(), secret_key="test-phase6a-secret")
    app.config["DRAFT_DATABASE_PATH"] = str(tmp_path / "real-intro.sqlite3")
    app.config["TESTING"] = True
    client = app.test_client()
    assert register_student(client).status_code == 302
    response = client.post(
        "/api/analyze-introduction",
        json={
            "assignment_topic": "Effects of reading habits on students",
            "focus_terms": ["reading habits", "students"],
            "introduction_text": "Reading habits can help students learn new ideas.",
        },
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["stage_id"] == "INTRODUCTION"
    assert payload["availability"] == "ANALYZED"
    assert set(payload["feedback"]) >= {
        "Current Goal",
        "Primary Feedback",
        "What's Working",
        "Needs Attention",
        "Next Step",
        "Feedback Provenance",
    }
    assert "ready" not in payload
    assert "pass" not in payload
    assert "semantic understanding" in payload["interpretation_limit"].lower()


def test_real_coordinator_analyzes_body_and_conclusion_with_prior_context(tmp_path):
    app = create_app(EssayAnalysisService(), secret_key="test-phase6a-secret")
    app.config["DRAFT_DATABASE_PATH"] = str(tmp_path / "real-essay.sqlite3")
    app.config["TESTING"] = True
    client = app.test_client()
    assert register_student(client).status_code == 302
    introduction = "Reading habits can help students learn new ideas."
    body = "Students can read regularly at home.\n\nBooks provide examples for learning."

    body_response = client.post(
        "/api/analyze-stage",
        json={
            "stage_id": "BODY",
            "assignment_topic": "Effects of reading habits on students",
            "focus_terms": ["reading", "students", "books", "learning"],
            "introduction_text": introduction,
            "body_text": body,
        },
    )
    conclusion_response = client.post(
        "/api/analyze-stage",
        json={
            "stage_id": "CONCLUSION",
            "assignment_topic": "Effects of reading habits on students",
            "focus_terms": ["reading", "students", "books", "learning"],
            "introduction_text": introduction,
            "body_text": body,
            "conclusion_text": "Overall, regular reading can help students learn.",
        },
    )

    body_result = body_response.get_json()
    conclusion_result = conclusion_response.get_json()
    assert body_response.status_code == conclusion_response.status_code == 200
    assert body_result["analysis"]["stage"] == "BODY"
    assert conclusion_result["analysis"]["stage"] == "CONCLUSION"
    assert body_result["feedback"]["Feedback Provenance"]
    assert conclusion_result["feedback"]["Feedback Provenance"]
    assert "BODY" not in conclusion_result["analysis"]
    assert "BODY_READY" not in conclusion_result
