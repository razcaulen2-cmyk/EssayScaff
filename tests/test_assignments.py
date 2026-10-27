"""Teacher assignments use the same temporary SQLite store and user roles."""

import sqlite3

from werkzeug.security import check_password_hash, generate_password_hash

import create_teacher as teacher_cli
from app import create_app
from services.essay_analysis_service import EssayAnalysisService
from services.draft_store import DraftStore
from tests.auth_helpers import login_student, register_student


def assignment_payload(**changes):
    values = {
        "title": "The Effects of Social Media",
        "topic": "Should students limit their social media use?",
        "instructions": "Write an essay with an Introduction, Body, and Conclusion.",
        "focus_terms": "social media, students, learning, distraction",
    }
    values.update(changes)
    return values


def new_test_app(database_path, analysis_service=None):
    app = create_app(analysis_service, secret_key="phase6b-test-secret")
    app.config.update(TESTING=True, DRAFT_DATABASE_PATH=str(database_path))
    return app


def create_teacher(store, username="teacher_one", password="teacher-password-1"):
    return store.create_teacher_user(username, generate_password_hash(password))


def test_teacher_cli_uses_hidden_password_and_creates_hashed_teacher_account(tmp_path, monkeypatch):
    database_path = tmp_path / "teacher-cli.sqlite3"
    monkeypatch.setattr(teacher_cli, "DATABASE_PATH", database_path)
    entered = iter(["local_teacher"])
    passwords = iter(["cli-teacher-password", "cli-teacher-password"])
    monkeypatch.setattr("builtins.input", lambda _prompt: next(entered))
    monkeypatch.setattr(teacher_cli, "getpass", lambda _prompt: next(passwords))

    assert teacher_cli.main() == 0
    user = DraftStore(database_path).get_user_for_login("LOCAL_TEACHER")
    assert user is not None
    assert user["role"] == "TEACHER"
    assert user["password_hash"] != "cli-teacher-password"
    assert check_password_hash(user["password_hash"], "cli-teacher-password")


def test_teacher_login_routes_to_teacher_page_and_assignments_are_private(tmp_path):
    app = new_test_app(tmp_path / "assignments.sqlite3")
    store = DraftStore(app.config["DRAFT_DATABASE_PATH"])
    teacher_a = create_teacher(store, "teacher_a")
    teacher_b = create_teacher(store, "teacher_b")
    classroom_a = store.create_classroom(teacher_a["user_id"], "English 101", "Academic Writing", "BSCS 3A")
    classroom_b = store.create_classroom(teacher_b["user_id"], "English 102", "Academic Writing", "BSCS 3B")
    client_a = app.test_client()
    client_b = app.test_client()
    assert login_student(client_a, "teacher_a", "teacher-password-1").status_code == 302
    assert login_student(client_b, "teacher_b", "teacher-password-1").status_code == 302

    missing_csrf = client_a.post(
        "/teacher/assignments",
        data=assignment_payload(),
        headers={"X-CSRF-Token": ""},
    )
    assert missing_csrf.status_code == 400
    assignment_a = client_a.post(
        "/teacher/assignments",
        data={
            **assignment_payload(),
            "classroom_id": classroom_a["classroom_id"],
            "teacher_user_id": teacher_b["user_id"],
        },
    )
    assignment_b = client_b.post(
        "/teacher/assignments",
        data={
            **assignment_payload(title="Teacher B assignment"),
            "classroom_id": classroom_b["classroom_id"],
        },
    )
    assert assignment_a.status_code == assignment_b.status_code == 302
    foreign_class_assignment = client_a.post(
        "/teacher/assignments",
        data={
            **assignment_payload(title="Must not enter teacher B class"),
            "classroom_id": classroom_b["classroom_id"],
        },
    )
    assert foreign_class_assignment.status_code == 404
    assert client_a.get("/").location.endswith("/teacher")
    page_a = client_a.get("/teacher")
    page_b = client_b.get("/teacher")
    assert b"The Effects of Social Media" in page_a.data
    assert b"Teacher B assignment" not in page_a.data
    assert b"Teacher B assignment" in page_b.data

    student = app.test_client()
    assert register_student(student, "student_reader").status_code == 302
    assert student.post(
        "/api/classroom-enrollments", json={"enrollment_code": classroom_a["enrollment_code"]}
    ).status_code == 200
    assert student.post(
        "/api/classroom-enrollments", json={"enrollment_code": classroom_b["enrollment_code"]}
    ).status_code == 200
    assert student.post(
        "/api/classroom-enrollments", json={"enrollment_code": classroom_a["enrollment_code"]}
    ).status_code == 409
    assert student.post(
        "/api/classroom-enrollments", json={"enrollment_code": "INVALID1234"}
    ).status_code == 404
    assert len(student.get("/api/classrooms").get_json()["classrooms"]) == 2
    available = student.get("/api/assignments").get_json()["assignments"]
    assert {item["title"] for item in available} == {
        "The Effects of Social Media",
        "Teacher B assignment",
    }
    page_a = client_a.get("/teacher")
    assert b"English 101" in page_a.data
    assert classroom_a["enrollment_code"].encode() in page_a.data
    assert b"student_reader" in page_a.data
    assert b"Not Started" in page_a.data

    with sqlite3.connect(app.config["DRAFT_DATABASE_PATH"]) as connection:
        owners = {
            title: (teacher_id, classroom_id)
            for title, teacher_id, classroom_id in connection.execute(
                "SELECT title, teacher_user_id, classroom_id FROM assignments"
            )
        }
    assert owners["The Effects of Social Media"] == (
        teacher_a["user_id"], classroom_a["classroom_id"]
    )
    assert owners["Teacher B assignment"] == (
        teacher_b["user_id"], classroom_b["classroom_id"]
    )


def test_teacher_classroom_creation_generates_secure_unique_enrollment_codes(tmp_path):
    app = new_test_app(tmp_path / "classrooms.sqlite3")
    store = DraftStore(app.config["DRAFT_DATABASE_PATH"])
    teacher = create_teacher(store)
    teacher_client = app.test_client()
    assert login_student(teacher_client, "teacher_one", "teacher-password-1").status_code == 302
    created = teacher_client.post(
        "/teacher/classrooms",
        data={"classroom_name": "English 101", "subject": "Writing", "section": "BSCS 3A"},
    )
    assert created.status_code == 302
    first, = store.list_teacher_classrooms(teacher["user_id"])
    assert first["classroom_name"] == "English 101"
    assert len(first["enrollment_code"]) == 10
    assert all(character in "ABCDEFGHIJKLMNOPQRSTUVWXYZ23456789" for character in first["enrollment_code"])

    teacher_client.post(
        "/teacher/classrooms",
        data={"classroom_name": "English 102", "subject": "Writing", "section": "BSCS 3B"},
    )
    classrooms = store.list_teacher_classrooms(teacher["user_id"])
    assert len(classrooms) == 2
    assert len({item["enrollment_code"] for item in classrooms}) == 2

    student = app.test_client()
    assert register_student(student, "not_a_teacher").status_code == 302
    denied = student.post(
        "/teacher/classrooms",
        data={"classroom_name": "No", "subject": "No", "section": "No"},
    )
    assert denied.status_code == 403


def test_students_can_read_available_assignments_but_not_create_or_manage_them(tmp_path):
    app = new_test_app(tmp_path / "assignments.sqlite3")
    store = DraftStore(app.config["DRAFT_DATABASE_PATH"])
    teacher = create_teacher(store)
    classroom = store.create_classroom(teacher["user_id"], "English 101", "Writing", "BSCS 3A")
    assignment = store.create_assignment(
        teacher["user_id"], classroom["classroom_id"], **assignment_payload()
    )
    student = app.test_client()
    assert register_student(student, "student_one").status_code == 302
    assert student.post(
        "/api/classroom-enrollments", json={"enrollment_code": classroom["enrollment_code"]}
    ).status_code == 200

    listing = student.get("/api/assignments")
    assert listing.status_code == 200
    listed = listing.get_json()["assignments"]
    assert len(listed) == 1
    assert listed[0]["assignment_id"] == assignment["assignment_id"]
    assert listed[0]["instructions"] == assignment["instructions"]
    assert listed[0]["classroom_name"] == classroom["classroom_name"]

    not_enrolled = app.test_client()
    assert register_student(not_enrolled, "student_outside").status_code == 302
    assert not_enrolled.get("/api/assignments").get_json()["assignments"] == []
    assert not_enrolled.get(
        f"/api/classrooms/{classroom['classroom_id']}/assignments"
    ).status_code == 404

    denied_page = student.get("/teacher")
    denied_create = student.post("/teacher/assignments", data=assignment_payload())
    assert denied_page.status_code == 403
    assert denied_create.status_code == 403
    assert len(store.list_teacher_assignments(teacher["user_id"])) == 1

    teacher_client = app.test_client()
    login_student(teacher_client, "teacher_one", "teacher-password-1")
    assert teacher_client.get("/api/assignments").status_code == 403
    assert teacher_client.get("/api/drafts").status_code == 403
    assert teacher_client.post("/api/classroom-enrollments", json={"enrollment_code": "ABC1234567"}).status_code == 403
    assert teacher_client.get(
        f"/api/assignments/{assignment['assignment_id']}/workspace"
    ).status_code == 403


def test_teacher_can_safely_reassign_only_own_legacy_assignment(tmp_path):
    app = new_test_app(tmp_path / "legacy-assignment.sqlite3")
    store = DraftStore(app.config["DRAFT_DATABASE_PATH"])
    owner = create_teacher(store, "legacy_owner")
    other = create_teacher(store, "other_teacher")
    classroom = store.create_classroom(owner["user_id"], "English 101", "Writing", "BSCS 3A")
    with sqlite3.connect(app.config["DRAFT_DATABASE_PATH"]) as connection:
        cursor = connection.execute(
            """
            INSERT INTO assignments (teacher_user_id, title, topic, instructions, focus_terms)
            VALUES (?, ?, ?, ?, ?)
            """,
            (owner["user_id"], "Legacy", "Old topic", "Old instructions", "old terms"),
        )
        assignment_id = cursor.lastrowid

    owner_client = app.test_client()
    login_student(owner_client, "legacy_owner", "teacher-password-1")
    response = owner_client.post(
        f"/teacher/assignments/{assignment_id}/classroom",
        data={"classroom_id": classroom["classroom_id"]},
    )
    assert response.status_code == 302
    assert store.get_assignment(assignment_id)["classroom_id"] == classroom["classroom_id"]

    other_client = app.test_client()
    login_student(other_client, "other_teacher", "teacher-password-1")
    denied = other_client.post(
        f"/teacher/assignments/{assignment_id}/classroom",
        data={"classroom_id": classroom["classroom_id"]},
    )
    assert denied.status_code == 404
    assert store.get_assignment(assignment_id)["teacher_user_id"] == owner["user_id"]


class RecordingAnalysisService:
    def __init__(self):
        self.calls = []

    def analyze(self, **kwargs):
        self.calls.append(kwargs)
        stage = next(
            key.removesuffix("_text").upper()
            for key in ("introduction_text", "body_text", "conclusion_text")
            if key in kwargs
        )
        return {
            "interpretation_limit": "Existing coordinator output.",
            "stages": {
                stage: {
                    "stage_id": stage,
                    "availability": "ANALYZED",
                    "analysis": {"stage": stage},
                    "feedback": {"Primary Feedback": "Existing feedback."},
                }
            },
        }


def test_assignment_drafts_are_per_student_and_analysis_uses_official_topic(tmp_path):
    analyzer = RecordingAnalysisService()
    app = new_test_app(tmp_path / "assigned-writing.sqlite3", analyzer)
    store = DraftStore(app.config["DRAFT_DATABASE_PATH"])
    teacher = create_teacher(store)
    classroom = store.create_classroom(teacher["user_id"], "English 101", "Writing", "BSCS 3A")
    assignment = store.create_assignment(teacher["user_id"], classroom["classroom_id"], **assignment_payload())
    student_a = app.test_client()
    student_b = app.test_client()
    assert register_student(student_a, "student_a").status_code == 302
    assert register_student(student_b, "student_b").status_code == 302
    assert student_a.post(
        "/api/classroom-enrollments", json={"enrollment_code": classroom["enrollment_code"]}
    ).status_code == 200
    assert student_b.post(
        "/api/classroom-enrollments", json={"enrollment_code": classroom["enrollment_code"]}
    ).status_code == 200

    workspace_a = student_a.get(f"/api/assignments/{assignment['assignment_id']}/workspace").get_json()
    workspace_a_again = student_a.get(f"/api/assignments/{assignment['assignment_id']}/workspace").get_json()
    workspace_b = student_b.get(f"/api/assignments/{assignment['assignment_id']}/workspace").get_json()
    session_a = workspace_a["draft"]["session_id"]
    assert workspace_a_again["draft"]["session_id"] == session_a
    assert workspace_b["draft"]["session_id"] != session_a
    assert workspace_b["draft"]["introduction_text"] == ""
    assert workspace_a["assignment"]["topic"] == assignment["topic"]
    assert workspace_a["assignment"]["focus_terms"] == assignment["focus_terms"]

    saved = student_a.post(
        "/api/drafts",
        json={
            "session_id": session_a,
            "assignment_id": assignment["assignment_id"],
            "assignment_topic": "Forged client topic",
            "focus_terms": "forged terms",
            "introduction_text": "My assigned introduction.",
            "body_text": "First body paragraph.\n\nSecond body paragraph.",
            "conclusion_text": "My conclusion.",
        },
    )
    assert saved.status_code == 200
    restored = student_a.get(
        f"/api/assignments/{assignment['assignment_id']}/workspace"
    ).get_json()
    assert restored["draft"]["introduction_text"] == "My assigned introduction."
    assert restored["draft"]["assignment_topic"] == assignment["topic"]
    assert restored["draft"]["focus_terms"] == assignment["focus_terms"]

    teacher_client = app.test_client()
    assert login_student(teacher_client, "teacher_one", "teacher-password-1").status_code == 302
    progress_page = teacher_client.get("/teacher")
    assert b"student_a" in progress_page.data
    assert b"student_b" in progress_page.data
    assert b"In Progress" in progress_page.data
    assert b"Not Started" in progress_page.data

    analyzed = student_a.post(
        "/api/analyze-stage",
        json={
            "stage_id": "INTRODUCTION",
            "assignment_id": assignment["assignment_id"],
            "assignment_topic": "Forged topic",
            "focus_terms": "forged terms",
            "introduction_text": "My assigned introduction.",
        },
    )
    assert analyzed.status_code == 200
    assert analyzer.calls[-1]["assignment_topic"] == assignment["topic"]
    assert analyzer.calls[-1]["focus_terms"] == ["social media", "students", "learning", "distraction"]

    revision = student_a.post(
        "/api/revisions",
        json={
            "session_id": session_a,
            "assignment_id": assignment["assignment_id"],
            "assignment_topic": "Forged topic",
            "focus_terms": "forged terms",
            "introduction_text": "My assigned introduction.",
            "body_text": "First body paragraph.\n\nSecond body paragraph.",
            "conclusion_text": "My conclusion.",
        },
    )
    assert revision.status_code == 200
    history = student_a.get(f"/api/revisions?session_id={session_a}").get_json()["revisions"]
    assert history[0]["revision_number"] == 1
    historical = student_a.get(
        f"/api/revisions/{history[0]['revision_id']}?session_id={session_a}"
    ).get_json()
    assert historical["assignment_topic"] == assignment["topic"]
    with sqlite3.connect(app.config["DRAFT_DATABASE_PATH"]) as connection:
        row = connection.execute(
            "SELECT user_id, assignment_id FROM writing_sessions WHERE session_id = ?",
            (session_a,),
        ).fetchone()
    owner_id = store.get_user_for_login("student_a")["user_id"]
    assert row == (owner_id, assignment["assignment_id"])

    practice = student_a.post(
        "/api/drafts",
        json={
            "assignment_topic": "Practice topic",
            "focus_terms": "practice",
            "introduction_text": "Practice intro.",
            "body_text": "",
            "conclusion_text": "",
        },
    ).get_json()
    with sqlite3.connect(app.config["DRAFT_DATABASE_PATH"]) as connection:
        practice_assignment_id = connection.execute(
            "SELECT assignment_id FROM writing_sessions WHERE session_id = ?",
            (practice["session_id"],),
        ).fetchone()[0]
    assert practice_assignment_id is None
    assert practice["session_id"] != session_a


def test_assignment_analysis_uses_the_existing_real_coordinator(tmp_path):
    app = new_test_app(
        tmp_path / "real-analysis.sqlite3", EssayAnalysisService()
    )
    store = DraftStore(app.config["DRAFT_DATABASE_PATH"])
    teacher = create_teacher(store)
    classroom = store.create_classroom(teacher["user_id"], "English 101", "Writing", "BSCS 3A")
    assignment = store.create_assignment(teacher["user_id"], classroom["classroom_id"], **assignment_payload())
    student = app.test_client()
    assert register_student(student, "analysis_student").status_code == 302
    assert student.post(
        "/api/classroom-enrollments", json={"enrollment_code": classroom["enrollment_code"]}
    ).status_code == 200

    response = student.post(
        "/api/analyze-stage",
        json={
            "stage_id": "INTRODUCTION",
            "assignment_id": assignment["assignment_id"],
            "assignment_topic": "Untrusted browser topic",
            "focus_terms": "untrusted terms",
            "introduction_text": "Social media can distract students from learning.",
        },
    )
    result = response.get_json()
    assert response.status_code == 200
    assert result["analysis"]["assignment_topic"] == assignment["topic"]
    assert result["analysis"]["lexical_topic_evidence"]["focus_terms"] == [
        "social media", "students", "learning", "distraction"
    ]
    assert result["feedback"]["Feedback Provenance"]


def test_assignment_migration_preserves_existing_sessions_and_revisions(tmp_path):
    database_path = tmp_path / "phase6a.sqlite3"
    draft = {
        "assignment_topic": "Existing practice topic",
        "focus_terms": "practice",
        "introduction_text": "Existing Introduction.",
        "body_text": "Existing Body.",
        "conclusion_text": "Existing Conclusion.",
    }
    session_id = "c" * 32
    with sqlite3.connect(database_path) as connection:
        connection.executescript(
            """
            CREATE TABLE users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'STUDENT',
                created_at TEXT NOT NULL
            );
            CREATE TABLE writing_sessions (
                session_id TEXT PRIMARY KEY,
                user_id INTEGER REFERENCES users(user_id),
                assignment_topic TEXT NOT NULL,
                focus_terms TEXT NOT NULL,
                introduction_text TEXT NOT NULL,
                body_text TEXT NOT NULL,
                conclusion_text TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            CREATE TABLE writing_revisions (
                revision_id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                revision_number INTEGER NOT NULL,
                assignment_topic TEXT NOT NULL,
                focus_terms TEXT NOT NULL,
                introduction_text TEXT NOT NULL,
                body_text TEXT NOT NULL,
                conclusion_text TEXT NOT NULL,
                created_at TEXT NOT NULL,
                UNIQUE(session_id, revision_number),
                FOREIGN KEY(session_id) REFERENCES writing_sessions(session_id)
            );
            CREATE TABLE assignments (
                assignment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                teacher_user_id INTEGER NOT NULL REFERENCES users(user_id),
                title TEXT NOT NULL,
                topic TEXT NOT NULL,
                instructions TEXT NOT NULL,
                focus_terms TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            INSERT INTO users(username, password_hash, role, created_at)
                VALUES ('existing_student', 'not-a-real-hash', 'STUDENT', '2025-01-01T00:00:00Z');
            INSERT INTO users(username, password_hash, role, created_at)
                VALUES ('legacy_teacher', 'not-a-real-hash', 'TEACHER', '2025-01-01T00:00:00Z');
            """
        )
        connection.execute(
            """
            INSERT INTO writing_sessions (
                session_id, user_id, assignment_topic, focus_terms, introduction_text,
                body_text, conclusion_text, created_at, updated_at
            ) VALUES (?, 1, ?, ?, ?, ?, ?, ?, ?)
            """,
            (session_id, *draft.values(), "2025-01-01T00:00:00Z", "2025-01-01T00:00:00Z"),
        )
        connection.execute(
            """
            INSERT INTO writing_revisions (
                session_id, revision_number, assignment_topic, focus_terms,
                introduction_text, body_text, conclusion_text, created_at
            ) VALUES (?, 1, ?, ?, ?, ?, ?, ?)
            """,
            (session_id, *draft.values(), "2025-01-01T00:00:00Z"),
        )
        connection.execute(
            """
            INSERT INTO assignments (
                assignment_id, teacher_user_id, title, topic, instructions, focus_terms, created_at
            ) VALUES (77, 2, 'Legacy assignment', 'Legacy topic', 'Legacy instructions', 'legacy', '2025-01-01T00:00:00Z')
            """
        )

    migrated = DraftStore(database_path)
    restored = migrated.get(session_id, 1)
    revisions = migrated.list_revisions(session_id, 1)
    assert restored is not None
    assert {key: restored[key] for key in draft} == draft
    assert restored["assignment_id"] is None
    assert [item["revision_number"] for item in revisions] == [1]
    historical = migrated.get_revision(
        session_id, revisions[0]["revision_id"], 1
    )
    assert historical is not None
    assert historical["introduction_text"] == draft["introduction_text"]
    legacy_assignments = migrated.list_unassigned_teacher_assignments(2)
    assert len(legacy_assignments) == 1
    assert legacy_assignments[0]["assignment_id"] == 77
    assert legacy_assignments[0]["classroom_id"] is None
    assert legacy_assignments[0]["deleted_at"] is None
    assert migrated.list_available_assignments(1) == []


def test_create_assignment_redirects_to_dashboard_and_stays_in_selected_classroom(tmp_path):
    app = new_test_app(tmp_path / "assignment-redirect.sqlite3")
    store = DraftStore(app.config["DRAFT_DATABASE_PATH"])
    teacher = create_teacher(store)
    selected = store.create_classroom(teacher["user_id"], "Selected Class", "Writing", "A")
    other = store.create_classroom(teacher["user_id"], "Other Class", "Writing", "B")
    client = app.test_client()
    assert login_student(client, "teacher_one", "teacher-password-1").status_code == 302

    response = client.post(
        "/teacher/assignments",
        data={
            **assignment_payload(title="Redirect Regression Assignment"),
            "classroom_id": str(selected["classroom_id"]),
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert response.request.path == "/teacher"
    assert b"Redirect Regression Assignment" in response.data
    assignments = store.list_teacher_classroom_assignments(
        teacher["user_id"], selected["classroom_id"]
    )
    assert len(assignments) == 1
    assert assignments[0]["title"] == "Redirect Regression Assignment"
    assert assignments[0]["classroom_id"] == selected["classroom_id"]
    assert store.list_teacher_classroom_assignments(
        teacher["user_id"], other["classroom_id"]
    ) == []
