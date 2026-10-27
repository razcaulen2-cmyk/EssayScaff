"""SQLite persistence tests use a temporary database for every case."""

import sqlite3
import time

import pytest

from app import create_app
from services.draft_store import DraftStore
from auth_helpers import register_student


def sample_draft(**changes):
    draft = {
        "assignment_topic": "Reading habits",
        "focus_terms": "reading, students",
        "introduction_text": "Introduction as written.\nSecond line.",
        "body_text": "First paragraph.\n\nSecond paragraph.",
        "conclusion_text": "Conclusion as written.",
    }
    draft.update(changes)
    return draft


def make_client(database_path):
    app = create_app(secret_key="test-phase6a-secret")
    app.config.update(TESTING=True, DRAFT_DATABASE_PATH=str(database_path))
    client = app.test_client()
    assert register_student(client).status_code == 302
    return client


def test_database_initialization_creates_the_expected_table(tmp_path):
    database_path = tmp_path / "drafts.sqlite3"
    DraftStore(database_path)
    with sqlite3.connect(database_path) as connection:
        columns = {row[1] for row in connection.execute("PRAGMA table_info(writing_sessions)")}
    assert columns == {
        "session_id",
        "user_id",
        "assignment_id",
        "assignment_topic",
        "focus_terms",
        "introduction_text",
        "body_text",
        "conclusion_text",
        "created_at",
        "updated_at",
    }


def test_save_creates_and_restore_returns_all_exact_draft_text(tmp_path):
    client = make_client(tmp_path / "drafts.sqlite3")
    draft = sample_draft()
    saved = client.post("/api/drafts", json=draft)
    assert saved.status_code == 200
    session_id = saved.get_json()["session_id"]
    assert len(session_id) == 32
    assert saved.get_json()["updated_at"]

    restored = client.get("/api/drafts", query_string={"session_id": session_id})
    assert restored.status_code == 200
    restored_draft = restored.get_json()
    assert {key: restored_draft[key] for key in draft} == draft
    assert restored_draft["session_id"] == session_id
    assert restored_draft["created_at"]
    assert restored_draft["updated_at"]


def test_saving_existing_session_updates_all_fields_and_keeps_creation_time(tmp_path):
    client = make_client(tmp_path / "drafts.sqlite3")
    created = client.post("/api/drafts", json=sample_draft()).get_json()
    before = client.get("/api/drafts", query_string={"session_id": created["session_id"]}).get_json()
    time.sleep(0.02)
    edited = sample_draft(
        assignment_topic="Updated topic",
        focus_terms="changed focus",
        introduction_text="Edited introduction.",
        body_text="Updated first.\n\nUpdated second.",
        conclusion_text="Edited conclusion.",
    )
    saved = client.post(
        "/api/drafts", json={**edited, "session_id": created["session_id"]}
    )
    after = client.get("/api/drafts", query_string={"session_id": created["session_id"]}).get_json()

    assert saved.status_code == 200
    assert {key: after[key] for key in edited} == edited
    assert after["created_at"] == before["created_at"]
    assert after["updated_at"] >= before["updated_at"]


def test_empty_drafts_can_be_saved_and_restored(tmp_path):
    client = make_client(tmp_path / "drafts.sqlite3")
    empty = sample_draft(
        assignment_topic="",
        focus_terms="",
        introduction_text="",
        body_text="",
        conclusion_text="",
    )
    saved = client.post("/api/drafts", json=empty)
    assert saved.status_code == 200
    restored = client.get("/api/drafts", query_string={"session_id": saved.get_json()["session_id"]})
    assert restored.status_code == 200
    assert {key: restored.get_json()[key] for key in empty} == empty


@pytest.mark.parametrize(
    "payload",
    [
        {"session_id": "bad-id"},
        {"session_id": 123},
        {"session_id": "f" * 32},
    ],
)
def test_invalid_or_unknown_save_session_ids_are_rejected(tmp_path, payload):
    client = make_client(tmp_path / "drafts.sqlite3")
    response = client.post("/api/drafts", json={**sample_draft(), **payload})
    expected = 404 if payload["session_id"] == "f" * 32 else 400
    assert response.status_code == expected


def test_restore_requires_valid_existing_session_id(tmp_path):
    client = make_client(tmp_path / "drafts.sqlite3")
    assert client.get("/api/drafts").status_code == 400
    assert client.get("/api/drafts?session_id=bad-id").status_code == 400
    assert client.get(f"/api/drafts?session_id={'a' * 32}").status_code == 404


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("assignment_topic", 10),
        ("focus_terms", ["reading"]),
        ("focus_terms", ", ".join(f"term{i}" for i in range(21))),
        ("introduction_text", None),
        ("body_text", "x" * 30001),
        ("conclusion_text", "x" * 12001),
    ],
)
def test_save_validates_field_types_and_size_limits(tmp_path, field, value):
    client = make_client(tmp_path / "drafts.sqlite3")
    response = client.post("/api/drafts", json=sample_draft(**{field: value}))
    assert response.status_code == 400
    assert response.get_json()["error"]


def test_database_errors_return_clear_save_and_restore_failures(tmp_path):
    client = make_client(tmp_path / "valid.sqlite3")
    session_id = client.post("/api/drafts", json=sample_draft()).get_json()["session_id"]
    with sqlite3.connect(tmp_path / "valid.sqlite3") as connection:
        connection.execute(
            """
            CREATE TRIGGER reject_draft_update BEFORE UPDATE ON writing_sessions
            BEGIN SELECT RAISE(ABORT, 'injected draft failure'); END
            """
        )
    save_response = client.post(
        "/api/drafts", json={**sample_draft(introduction_text="changed"), "session_id": session_id}
    )
    assert save_response.status_code == 500
    assert "could not be saved" in save_response.get_json()["error"].lower()
