"""Student account and ownership tests use isolated temporary databases."""

import sqlite3
from datetime import timedelta

import pytest
from werkzeug.security import check_password_hash

from app import _persistent_secret_key, create_app
from services.draft_store import DraftStore
from tests.auth_helpers import form_csrf_token, register_student


PASSWORD = "correct-horse-battery"


def make_app_client(tmp_path):
    app = create_app(secret_key="phase6-test-secret")
    app.config.update(TESTING=True, DRAFT_DATABASE_PATH=str(tmp_path / "accounts.sqlite3"))
    return app, app.test_client()


def register_with_token(client, username="learner_one", password=PASSWORD, confirmation=None, **extra):
    page = client.get("/register")
    return client.post(
        "/register",
        data={
            "csrf_token": form_csrf_token(page),
            "username": username,
            "password": password,
            "confirm_password": password if confirmation is None else confirmation,
            **extra,
        },
        follow_redirects=False,
    )


def test_student_registration_hashes_password_and_rejects_admin_role(tmp_path):
    app, client = make_app_client(tmp_path)
    response = register_with_token(client, role="ADMIN")
    assert response.status_code == 400
    assert b"Choose Student or Teacher" in response.data

    response = register_with_token(client, role="STUDENT")
    assert response.status_code == 302
    assert response.location == "/"

    store = DraftStore(app.config["DRAFT_DATABASE_PATH"])
    user = store.get_user_for_login("LEARNER_ONE")
    assert user is not None
    assert user["role"] == "STUDENT"
    assert user["user_id"] > 0
    assert store.get_user(user["user_id"])["created_at"]
    assert user["password_hash"] != PASSWORD
    assert check_password_hash(user["password_hash"], PASSWORD)
    assert client.get("/").status_code == 200
    assert b"Signed in as" in client.get("/").data


def test_public_registration_can_select_teacher_and_routes_to_teacher_page(tmp_path):
    app, client = make_app_client(tmp_path)
    response = register_with_token(client, username="public_teacher", role="TEACHER")
    assert response.status_code == 302
    assert client.get("/").location.endswith("/teacher")
    teacher = DraftStore(app.config["DRAFT_DATABASE_PATH"]).get_user_for_login("public_teacher")
    assert teacher is not None
    assert teacher["role"] == "TEACHER"
    assert check_password_hash(teacher["password_hash"], PASSWORD)


def test_registration_rejects_invalid_details_and_duplicate_case_insensitively(tmp_path):
    app, client = make_app_client(tmp_path)
    mismatch = register_with_token(client, confirmation="not-the-password")
    invalid_username = register_with_token(client, username="bad username")
    assert mismatch.status_code == 400
    assert b"do not match" in mismatch.data
    assert invalid_username.status_code == 400
    assert b"Username must" in invalid_username.data

    assert register_with_token(client).status_code == 302
    duplicate_client = app.test_client()
    duplicate = register_with_token(duplicate_client, username="LEARNER_ONE")
    assert duplicate.status_code == 409
    assert b"already in use" in duplicate.data
    with sqlite3.connect(app.config["DRAFT_DATABASE_PATH"]) as connection:
        assert connection.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 1


def test_login_and_registration_require_csrf_tokens(tmp_path):
    app, client = make_app_client(tmp_path)
    assert client.post(
        "/register",
        data={"username": "csrf_user", "password": PASSWORD, "confirm_password": PASSWORD},
    ).status_code == 400
    page = client.get("/login")
    assert client.post(
        "/login", data={"username": "csrf_user", "password": PASSWORD}
    ).status_code == 400
    assert app.test_client().get("/api/drafts").status_code == 401


def test_login_errors_are_generic_and_successful_session_cookie_is_protected(tmp_path):
    app, registered = make_app_client(tmp_path)
    assert register_student(registered, password=PASSWORD).status_code == 302
    assert registered.get("/logout").status_code == 405
    assert registered.get("/").status_code == 200
    assert "no-store" in registered.get("/").headers["Cache-Control"]
    with registered.session_transaction() as flask_session:
        csrf = flask_session["_csrf_token"]

    client = app.test_client()
    page = client.get("/login")
    token = form_csrf_token(page)
    bad = client.post(
        "/login",
        data={"csrf_token": token, "username": "student_one", "password": "wrong-password"},
    )
    assert bad.status_code == 401
    assert b"Incorrect username or password" in bad.data
    assert b"wrong-password" not in bad.data

    page = client.get("/login")
    valid = client.post(
        "/login",
        data={"csrf_token": form_csrf_token(page), "username": "student_one", "password": PASSWORD},
    )
    assert valid.status_code == 302
    with client.session_transaction() as flask_session:
        assert flask_session["user_id"]
        assert flask_session["_csrf_token"] != csrf
    cookie = valid.headers.get("Set-Cookie", "")
    assert "HttpOnly" in cookie
    assert "SameSite=Lax" in cookie
    assert "Secure" not in cookie  # Local prototype uses HTTP on loopback.


def test_logout_and_csrf_protect_state_changing_routes(tmp_path):
    _app, client = make_app_client(tmp_path)
    assert register_student(client).status_code == 302
    with client.session_transaction() as flask_session:
        csrf = flask_session["_csrf_token"]
    missing_csrf = client.post("/api/drafts", json={}, headers={"X-CSRF-Token": ""})
    assert missing_csrf.status_code == 400
    assert "verified" in missing_csrf.get_json()["error"].lower()

    logout = client.post("/logout", data={"csrf_token": csrf})
    assert logout.status_code == 302
    assert logout.location == "/login"
    assert client.get("/").status_code == 302
    assert client.get("/api/revisions").status_code == 401
    assert client.get("/api/drafts").status_code == 401
    assert client.post("/api/revisions", json={}).status_code == 401
    assert client.post(
        "/api/analyze-introduction",
        json={"assignment_topic": "Reading", "introduction_text": "Students read."},
    ).status_code == 401


def test_anonymous_draft_migration_preserves_row_unowned_and_inaccessible(tmp_path):
    database_path = tmp_path / "legacy.sqlite3"
    draft = {
        "assignment_topic": "Old assignment",
        "focus_terms": "old, terms",
        "introduction_text": "Old intro.\n\nSecond line.",
        "body_text": "Old body.",
        "conclusion_text": "Old conclusion.",
    }
    legacy_session_id = "a" * 32
    with sqlite3.connect(database_path) as connection:
        connection.execute(
            """
            CREATE TABLE writing_sessions (
                session_id TEXT PRIMARY KEY,
                assignment_topic TEXT NOT NULL,
                focus_terms TEXT NOT NULL,
                introduction_text TEXT NOT NULL,
                body_text TEXT NOT NULL,
                conclusion_text TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        connection.execute(
            "INSERT INTO writing_sessions VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (legacy_session_id, *draft.values(), "2025-01-01T00:00:00Z", "2025-01-01T00:00:00Z"),
        )
    app = create_app(secret_key="phase6-test-secret")
    app.config.update(TESTING=True, DRAFT_DATABASE_PATH=str(database_path))
    client = app.test_client()
    assert register_student(client).status_code == 302
    with sqlite3.connect(database_path) as connection:
        row = connection.execute(
            "SELECT user_id, assignment_id, assignment_topic, focus_terms, introduction_text, body_text, conclusion_text "
            "FROM writing_sessions WHERE session_id = ?",
            (legacy_session_id,),
        ).fetchone()
    assert row == (None, None, *draft.values())
    assert client.get(
        "/api/drafts", query_string={"session_id": legacy_session_id}
    ).status_code == 404
    assert DraftStore(database_path).get(legacy_session_id)["introduction_text"] == draft["introduction_text"]


def test_two_students_cannot_read_or_update_each_others_drafts_or_revisions(tmp_path):
    app, first_client = make_app_client(tmp_path)
    assert register_student(first_client, "student_a").status_code == 302
    second_client = app.test_client()
    assert register_student(second_client, "student_b").status_code == 302

    draft = {
        "assignment_topic": "Reading",
        "focus_terms": "reading",
        "introduction_text": "Student A intro.",
        "body_text": "Student A body.",
        "conclusion_text": "Student A conclusion.",
    }
    saved = first_client.post("/api/drafts", json=draft).get_json()
    session_id = saved["session_id"]
    revision = first_client.post("/api/revisions", json={**draft, "session_id": session_id}).get_json()

    assert first_client.get("/api/drafts", query_string={"session_id": session_id}).status_code == 200
    assert first_client.get(
        "/api/revisions", query_string={"session_id": session_id}
    ).status_code == 200
    assert second_client.get(
        "/api/drafts", query_string={"session_id": session_id}
    ).status_code == 404
    assert second_client.post(
        "/api/drafts", json={**draft, "session_id": session_id}
    ).status_code == 404
    assert second_client.post(
        "/api/revisions", json={**draft, "session_id": session_id}
    ).status_code == 404
    assert second_client.get(
        "/api/revisions", query_string={"session_id": session_id}
    ).status_code == 404
    assert second_client.get(
        f"/api/revisions/{revision['revision_id']}?session_id={session_id}"
    ).status_code == 404


def test_session_for_deleted_account_is_rejected_and_cleared(tmp_path):
    app, client = make_app_client(tmp_path)
    assert register_student(client).status_code == 302
    with client.session_transaction() as flask_session:
        user_id = flask_session["user_id"]
    with sqlite3.connect(app.config["DRAFT_DATABASE_PATH"]) as connection:
        connection.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
    assert client.get("/api/drafts").status_code == 401
    with client.session_transaction() as flask_session:
        assert "user_id" not in flask_session


def test_expired_flask_session_is_rejected(tmp_path):
    app, client = make_app_client(tmp_path)
    assert register_student(client).status_code == 302
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(seconds=-1)
    assert client.get("/api/drafts").status_code == 401


def test_switching_accounts_in_same_browser_does_not_restore_previous_student_draft(tmp_path):
    _app, client = make_app_client(tmp_path)
    assert register_student(client, "browser_student_a").status_code == 302
    saved = client.post(
        "/api/drafts",
        json={
            "assignment_topic": "Private practice",
            "focus_terms": "private",
            "introduction_text": "Student A private text.",
            "body_text": "",
            "conclusion_text": "",
        },
    )
    session_id = saved.get_json()["session_id"]
    with client.session_transaction() as flask_session:
        csrf = flask_session["_csrf_token"]
    assert client.post("/logout", data={"csrf_token": csrf}).status_code == 302
    assert register_student(client, "browser_student_b").status_code == 302
    denied = client.get("/api/drafts", query_string={"session_id": session_id})
    assert denied.status_code == 404
    assert "Student A private text" not in denied.get_data(as_text=True)


def test_persistent_secret_key_is_created_once_and_cookie_flags_are_configured(tmp_path, monkeypatch):
    monkeypatch.delenv("ESSAYSCAFF_SECRET_KEY", raising=False)
    first = _persistent_secret_key(str(tmp_path))
    second = _persistent_secret_key(str(tmp_path))
    assert len(first) == 64
    assert first == second
    app = create_app(secret_key=first)
    assert app.config["SESSION_COOKIE_HTTPONLY"] is True
    assert app.config["SESSION_COOKIE_SAMESITE"] == "Lax"
    assert app.config["SESSION_COOKIE_SECURE"] is False
