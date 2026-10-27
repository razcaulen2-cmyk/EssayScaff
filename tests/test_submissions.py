"""Final essay submissions are immutable and visible only to their student and teacher."""

import sqlite3

from werkzeug.security import generate_password_hash

from app import create_app
from services.draft_store import DraftStore
from tests.auth_helpers import login_student, register_student


ESSAY = {
    "introduction_text": "Students should have time to read every day.",
    "body_text": "\n\nReading builds knowledge and helps students practice careful thinking.",
    "conclusion_text": "Daily reading can support students in many subjects.",
}


def setup_classroom(tmp_path):
    app = create_app(secret_key="phase6c-test-secret")
    app.config.update(TESTING=True, DRAFT_DATABASE_PATH=str(tmp_path / "submissions.sqlite3"))
    store = DraftStore(app.config["DRAFT_DATABASE_PATH"])
    teacher = store.create_teacher_user("teacher_one", generate_password_hash("teacher-password-1"))
    other_teacher = store.create_teacher_user("teacher_two", generate_password_hash("teacher-password-2"))
    classroom = store.create_classroom(teacher["user_id"], "English 101", "Writing", "BSCS 3A")
    assignment = store.create_assignment(
        teacher["user_id"], classroom["classroom_id"], "Reading Essay", "Daily reading", "Write an essay.", "reading"
    )
    student = app.test_client()
    assert register_student(student, "student_one").status_code == 302
    assert student.post(
        "/api/classroom-enrollments", json={"enrollment_code": classroom["enrollment_code"]}
    ).status_code == 200
    other_student = app.test_client()
    assert register_student(other_student, "student_two").status_code == 302
    teacher_client = app.test_client()
    assert login_student(teacher_client, "teacher_one", "teacher-password-1").status_code == 302
    other_teacher_client = app.test_client()
    assert login_student(other_teacher_client, "teacher_two", "teacher-password-2").status_code == 302
    return app, store, assignment, student, other_student, teacher_client, other_teacher_client


def test_student_submits_saved_snapshot_and_assignment_becomes_read_only(tmp_path):
    _app, store, assignment, student, _other_student, teacher, other_teacher = setup_classroom(tmp_path)
    assignment_id = assignment["assignment_id"]
    workspace = student.get(f"/api/assignments/{assignment_id}/workspace").get_json()
    session_id = workspace["draft"]["session_id"]

    incomplete = student.post(
        "/api/submissions",
        json={
            "assignment_id": assignment_id,
            "session_id": session_id,
            "draft_version": workspace["draft_version"],
        },
    )
    assert incomplete.status_code == 400

    payload = {
        **ESSAY,
        "assignment_id": assignment_id,
        "session_id": session_id,
        "assignment_topic": "Forged topic is ignored",
        "focus_terms": "forged terms",
    }
    saved = student.post("/api/drafts", json=payload)
    assert saved.status_code == 200
    stale = student.post(
        "/api/submissions",
        json={
            "assignment_id": assignment_id,
            "session_id": session_id,
            "draft_version": workspace["draft_version"],
        },
    )
    assert stale.status_code == 409

    current_workspace = student.get(f"/api/assignments/{assignment_id}/workspace").get_json()
    version = current_workspace["draft_version"]
    submitted = student.post(
        "/api/submissions",
        json={"assignment_id": assignment_id, "session_id": session_id, "draft_version": version},
    )
    assert submitted.status_code == 200
    submission = submitted.get_json()
    assert submission["introduction_snapshot"] == ESSAY["introduction_text"]
    assert submission["body_snapshot"] == ESSAY["body_text"]
    assert submission["conclusion_snapshot"] == ESSAY["conclusion_text"]

    duplicate = student.post(
        "/api/submissions",
        json={"assignment_id": assignment_id, "session_id": session_id, "draft_version": version},
    )
    assert duplicate.status_code == 409
    for endpoint, body in (
        ("/api/drafts", payload),
        ("/api/revisions", payload),
    ):
        locked = student.post(endpoint, json={**body, "introduction_text": "Changed after submission."})
        assert locked.status_code == 409

    student_copy = student.get(f"/api/submissions/{assignment_id}")
    assert student_copy.status_code == 200
    assert student_copy.get_json()["body_snapshot"] == ESSAY["body_text"]
    assert _other_student.get(f"/api/submissions/{assignment_id}").status_code == 404

    teacher_page = teacher.get("/teacher")
    assert b"Submitted" in teacher_page.data
    submissions_page = teacher.get(f"/teacher/assignments/{assignment_id}/submissions")
    assert b"student_one" in submissions_page.data
    assert b"View Essay" in submissions_page.data
    essay_page = teacher.get(f"/teacher/submissions/{submission['submission_id']}")
    assert ESSAY["introduction_text"].encode() in essay_page.data
    assert other_teacher.get(f"/teacher/submissions/{submission['submission_id']}").status_code == 404
    student_id = store.get_user_for_login("student_one")["user_id"]
    assert store.get_student_submission(student_id, assignment_id) is not None


def test_submission_requires_csrf_and_student_assignment_membership(tmp_path):
    _app, _store, assignment, student, outsider, _teacher, _other_teacher = setup_classroom(tmp_path)
    workspace = student.get(f"/api/assignments/{assignment['assignment_id']}/workspace").get_json()
    no_csrf = student.post(
        "/api/submissions",
        json={
            "assignment_id": assignment["assignment_id"],
            "session_id": workspace["draft"]["session_id"],
            "draft_version": workspace["draft_version"],
        },
        headers={"X-CSRF-Token": ""},
    )
    assert no_csrf.status_code == 400
    assert outsider.post(
        "/api/drafts",
        json={**ESSAY, "assignment_id": assignment["assignment_id"]},
    ).status_code == 404
    assert outsider.post(
        "/api/revisions",
        json={**ESSAY, "assignment_id": assignment["assignment_id"]},
    ).status_code == 404


def test_existing_submissions_schema_is_migrated_without_losing_rows(tmp_path):
    database = tmp_path / "existing-submissions.sqlite3"
    store = DraftStore(database)
    teacher = store.create_teacher_user("legacy_teacher", "not-a-real-hash")
    student = store.create_user("legacy_student", "not-a-real-hash")
    classroom = store.create_classroom(teacher["user_id"], "Old class", "Writing", "A")
    store.join_classroom(student["user_id"], classroom["enrollment_code"])
    assignment = store.create_assignment(
        teacher["user_id"], classroom["classroom_id"], "Old assignment", "Topic", "Instructions", ""
    )
    workspace = store.get_or_create_assignment_workspace(student["user_id"], assignment["assignment_id"])
    draft = {
        "assignment_topic": "Topic",
        "focus_terms": "",
        **ESSAY,
    }
    saved = store.save(
        draft,
        workspace["draft"]["session_id"],
        student["user_id"],
        assignment["assignment_id"],
    )
    original = store.create_submission(
        student["user_id"], assignment["assignment_id"], saved["session_id"], store.draft_version(saved)
    )

    with sqlite3.connect(database) as connection:
        connection.execute("DROP INDEX submissions_unique_student_assignment")

    migrated = DraftStore(database)
    restored = migrated.get_student_submission(student["user_id"], assignment["assignment_id"])
    assert restored["submission_id"] == original["submission_id"]
    assert restored["body_snapshot"] == ESSAY["body_text"]
    with sqlite3.connect(database) as connection:
        index = connection.execute(
            "SELECT sql FROM sqlite_master WHERE type = 'index' AND name = ?",
            ("submissions_unique_student_assignment",),
        ).fetchone()
    assert index is not None
