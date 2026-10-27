"""Revision snapshots and endpoints use temporary SQLite databases."""

import sqlite3
from concurrent.futures import ThreadPoolExecutor

import pytest

from app import create_app
from services.draft_store import DraftStore
from auth_helpers import register_student


def sample_draft(**changes):
    draft = {
        "assignment_topic": "Reading habits",
        "focus_terms": "reading, students",
        "introduction_text": "Introduction café.\r\nSecond line.",
        "body_text": "First paragraph.\r\n\r\n第二段落.",
        "conclusion_text": "Conclusion as written.",
    }
    draft.update(changes)
    return draft


def make_client(path):
    app = create_app(secret_key="test-phase6a-secret")
    app.config.update(TESTING=True, DRAFT_DATABASE_PATH=str(path))
    client = app.test_client()
    assert register_student(client).status_code == 302
    return client


def test_existing_draft_database_migrates_without_changing_draft_rows(tmp_path):
    database_path = tmp_path / "existing.sqlite3"
    store = DraftStore(database_path)
    original = sample_draft()
    session = store.save(original)
    with sqlite3.connect(database_path) as connection:
        connection.execute("DROP TABLE writing_revisions")

    migrated_store = DraftStore(database_path)
    assert migrated_store.get(session["session_id"]) | {} == session | {}
    revisions = migrated_store.list_revisions(session["session_id"])
    assert revisions == []
    with sqlite3.connect(database_path) as connection:
        table_names = {
            row[0]
            for row in connection.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
        }
    assert "writing_sessions" in table_names
    assert "writing_revisions" in table_names


def test_revisions_start_at_one_increment_and_deduplicate_consecutive_snapshots(tmp_path):
    store = DraftStore(tmp_path / "revisions.sqlite3")
    first = sample_draft()
    revision1 = store.save_revision(first)
    duplicate = store.save_revision(first, revision1["session"]["session_id"])
    revision2 = store.save_revision(
        sample_draft(body_text="A changed Body.\n\n第二段."),
        revision1["session"]["session_id"],
    )
    revision3 = store.save_revision(
        sample_draft(
            body_text="A changed Body.\n\n第二段.",
            conclusion_text="A changed Conclusion.",
        ),
        revision1["session"]["session_id"],
    )

    assert revision1["created"] is True
    assert revision1["revision"]["revision_number"] == 1
    assert duplicate["created"] is False
    assert duplicate["revision"]["revision_id"] == revision1["revision"]["revision_id"]
    assert revision2["revision"]["revision_number"] == 2
    assert revision3["revision"]["revision_number"] == 3
    assert [item["revision_number"] for item in store.list_revisions(revision1["session"]["session_id"])] == [3, 2, 1]


def test_revision_snapshot_preserves_unicode_and_all_original_stage_text(tmp_path):
    store = DraftStore(tmp_path / "revisions.sqlite3")
    draft = sample_draft()
    result = store.save_revision(draft)
    revision = store.get_revision(
        result["session"]["session_id"], result["revision"]["revision_id"]
    )
    assert revision is not None
    assert {key: revision[key] for key in draft} == draft
    assert revision["revision_number"] == 1
    assert revision["created_at"]


def test_revision_failure_rolls_back_the_draft_update(tmp_path):
    database_path = tmp_path / "revisions.sqlite3"
    store = DraftStore(database_path)
    original = sample_draft()
    session = store.save(original)
    with sqlite3.connect(database_path) as connection:
        connection.execute(
            """
            CREATE TRIGGER reject_revision BEFORE INSERT ON writing_revisions
            BEGIN SELECT RAISE(ABORT, 'injected revision failure'); END
            """
        )

    with pytest.raises(sqlite3.IntegrityError):
        store.save_revision(
            sample_draft(body_text="This update must roll back."), session["session_id"]
        )
    after = store.get(session["session_id"])
    assert after is not None
    assert {key: after[key] for key in original} == original
    assert store.list_revisions(session["session_id"]) == []


def test_concurrent_revision_requests_get_unique_sequential_numbers(tmp_path):
    database_path = tmp_path / "revisions.sqlite3"
    first_store = DraftStore(database_path)
    session = first_store.save(sample_draft())
    session_id = session["session_id"]
    snapshots = [
        sample_draft(body_text="Body version one."),
        sample_draft(body_text="Body version two."),
    ]

    def save_one(draft):
        return DraftStore(database_path).save_revision(draft, session_id)

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(save_one, snapshots))
    numbers = sorted(item["revision"]["revision_number"] for item in results)
    assert numbers == [1, 2]
    assert [item["revision_number"] for item in first_store.list_revisions(session_id)] == [2, 1]


def test_concurrent_identical_revisions_create_only_one_snapshot(tmp_path):
    database_path = tmp_path / "revisions.sqlite3"
    store = DraftStore(database_path)
    session_id = store.save(sample_draft())["session_id"]
    draft = sample_draft()

    def save_one(_index):
        return DraftStore(database_path).save_revision(draft, session_id)

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(save_one, range(2)))
    assert sum(item["created"] for item in results) == 1
    assert [item["revision_number"] for item in store.list_revisions(session_id)] == [1]


def test_revision_api_creates_lists_and_reads_without_changing_current_draft(tmp_path):
    client = make_client(tmp_path / "api.sqlite3")
    original = sample_draft()
    created = client.post("/api/revisions", json=original)
    assert created.status_code == 200
    result = created.get_json()
    session_id = result["session_id"]
    assert result["created"] is True
    assert result["revision_number"] == 1

    current = sample_draft(introduction_text="Live unsaved Introduction.")
    saved = client.post("/api/drafts", json={**current, "session_id": session_id})
    history = client.get("/api/revisions", query_string={"session_id": session_id})
    view = client.get(
        f"/api/revisions/{result['revision_id']}", query_string={"session_id": session_id}
    )
    current_read = client.get("/api/drafts", query_string={"session_id": session_id})

    assert saved.status_code == 200
    assert history.status_code == 200
    assert [item["revision_number"] for item in history.get_json()["revisions"]] == [1]
    assert view.status_code == 200
    assert {key: view.get_json()[key] for key in original} == original
    assert current_read.get_json()["introduction_text"] == "Live unsaved Introduction."


def test_revision_api_duplicate_and_invalid_or_missing_ids(tmp_path):
    client = make_client(tmp_path / "api.sqlite3")
    draft = sample_draft()
    first = client.post("/api/revisions", json=draft).get_json()
    duplicate = client.post("/api/revisions", json={**draft, "session_id": first["session_id"]})
    assert duplicate.status_code == 200
    assert duplicate.get_json()["created"] is False
    assert duplicate.get_json()["revision_number"] == 1

    assert client.get("/api/revisions").status_code == 400
    assert client.get("/api/revisions?session_id=bad-id").status_code == 400
    assert client.get("/api/revisions?session_id=" + "f" * 32).status_code == 404
    assert client.get("/api/revisions/not-an-id?session_id=" + first["session_id"]).status_code == 400
    assert client.get("/api/revisions/²?session_id=" + first["session_id"]).status_code == 400
    assert client.get(
        f"/api/revisions/{first['revision_id']}?session_id={'f' * 32}"
    ).status_code == 404
    assert client.post("/api/revisions", json={**draft, "session_id": "bad-id"}).status_code == 400


def test_revision_api_rejects_missing_or_invalid_draft_fields(tmp_path):
    client = make_client(tmp_path / "api.sqlite3")
    assert client.post("/api/revisions", json={"assignment_topic": "Reading"}).status_code == 400
    assert client.post("/api/revisions", data="invalid", content_type="text/plain").status_code == 400


def test_revision_api_returns_a_clear_database_error(tmp_path):
    client = make_client(tmp_path / "valid.sqlite3")
    session_id = client.post("/api/drafts", json=sample_draft()).get_json()["session_id"]
    with sqlite3.connect(tmp_path / "valid.sqlite3") as connection:
        connection.execute(
            """
            CREATE TRIGGER reject_revision BEFORE INSERT ON writing_revisions
            BEGIN SELECT RAISE(ABORT, 'injected revision failure'); END
            """
        )
    response = client.post(
        "/api/revisions", json={**sample_draft(body_text="changed"), "session_id": session_id}
    )
    assert response.status_code == 500
    assert "could not be saved" in response.get_json()["error"].lower()
