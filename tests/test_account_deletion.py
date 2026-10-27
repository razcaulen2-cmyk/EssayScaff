"""Self-service account deletion is authenticated and removes linked data transactionally."""

import sqlite3

from werkzeug.security import generate_password_hash

from app import create_app
from services.draft_store import DraftStore
from tests.auth_helpers import form_csrf_token, login_student


ESSAY = {
    "assignment_topic": "Reading habits",
    "focus_terms": "reading, students",
    "introduction_text": "Reading introduces new ideas.",
    "body_text": "Students can practice and learn.",
    "conclusion_text": "Daily reading supports learning.",
}


def new_account_app(database_path):
    app = create_app(secret_key="account-deletion-test-secret")
    app.config.update(TESTING=True, DRAFT_DATABASE_PATH=str(database_path))
    return app, DraftStore(database_path)


def create_account(store, username, role, password):
    return store.create_user(username, generate_password_hash(password), role)


def create_classroom_assignment(store, teacher, name):
    classroom = store.create_classroom(teacher["user_id"], name, "Writing", "Section A")
    assignment = store.create_assignment(
        teacher["user_id"], classroom["classroom_id"],
        f"{name} essay", "Reading habits", "Write an essay.", "reading, students",
    )
    return classroom, assignment


def add_student_records(store, student_id, classroom, assignment, *, submit=False):
    store.join_classroom(student_id, classroom["enrollment_code"])
    workspace = store.get_or_create_assignment_workspace(student_id, assignment["assignment_id"])
    draft = {
        **ESSAY,
        "assignment_topic": assignment["topic"],
        "focus_terms": assignment["focus_terms"],
    }
    saved = store.save(
        draft, workspace["draft"]["session_id"], student_id, assignment["assignment_id"]
    )
    revised = store.save_revision(draft, saved["session_id"], student_id, assignment["assignment_id"])
    if submit:
        store.create_submission(
            student_id, assignment["assignment_id"], saved["session_id"],
            store.draft_version(revised["session"]),
        )
    return revised["session"]


def delete_form(client, password, *, confirmed="yes", csrf=None):
    page = client.get("/account")
    return client.post(
        "/account/delete",
        data={
            "csrf_token": csrf if csrf is not None else form_csrf_token(page),
            "password": password,
            "confirm_delete": confirmed,
        },
        follow_redirects=True,
    )


def test_student_can_delete_own_account_and_only_own_linked_work(tmp_path):
    app, store = new_account_app(tmp_path / "student-delete.sqlite3")
    teacher = create_account(store, "teacher_one", "TEACHER", "teacher-password-1")
    classroom, assignment = create_classroom_assignment(store, teacher, "English")
    student = create_account(store, "student_one", "STUDENT", "student-password-1")
    other_student = create_account(store, "student_two", "STUDENT", "student-password-2")
    add_student_records(store, student["user_id"], classroom, assignment, submit=True)
    retained = add_student_records(store, other_student["user_id"], classroom, assignment)

    client = app.test_client()
    assert login_student(client, "student_one", "student-password-1").status_code == 302
    page = client.get("/account")
    assert page.status_code == 200
    assert b"drafts, revision history, and essay submissions" in page.data
    no_csrf = client.post(
        "/account/delete",
        data={"password": "student-password-1", "confirm_delete": "yes"},
        headers={"X-CSRF-Token": ""},
    )
    assert no_csrf.status_code == 400
    not_confirmed = delete_form(client, "student-password-1", confirmed="")
    assert not_confirmed.status_code == 400
    wrong_password = delete_form(client, "wrong-password")
    assert wrong_password.status_code == 400
    assert store.get_user_for_login("student_one") is not None

    deleted = delete_form(client, "student-password-1")
    assert deleted.status_code == 200
    assert b"account and its associated records were permanently deleted" in deleted.data
    assert store.get_user_for_login("student_one") is None
    assert store.get_user_for_login("student_two") is not None
    assert store.get_user_for_login("teacher_one") is not None
    assert store.get_assignment(assignment["assignment_id"]) is not None
    assert store.list_teacher_classrooms(teacher["user_id"])[0]["student_count"] == 1
    assert store.get(retained["session_id"], other_student["user_id"], assignment["assignment_id"]) is not None
    assert len(store.list_revisions(retained["session_id"], other_student["user_id"])) == 1
    with sqlite3.connect(store.database_path) as connection:
        assert connection.execute("SELECT COUNT(*) FROM submissions").fetchone()[0] == 0
        assert connection.execute(
            "SELECT COUNT(*) FROM writing_sessions WHERE user_id = ?", (student["user_id"],)
        ).fetchone()[0] == 0

    assert client.get("/").location.endswith("/login")
    assert login_student(client, "student_one", "student-password-1").status_code == 401


def test_teacher_can_delete_account_and_linked_classroom_student_records(tmp_path):
    app, store = new_account_app(tmp_path / "teacher-delete.sqlite3")
    teacher = create_account(store, "teacher_one", "TEACHER", "teacher-password-1")
    other_teacher = create_account(store, "teacher_two", "TEACHER", "teacher-password-2")
    classroom, assignment = create_classroom_assignment(store, teacher, "Teacher One Class")
    other_classroom, other_assignment = create_classroom_assignment(store, other_teacher, "Teacher Two Class")
    student = create_account(store, "student_one", "STUDENT", "student-password-1")
    other_student = create_account(store, "student_two", "STUDENT", "student-password-2")
    removed_work = add_student_records(store, student["user_id"], classroom, assignment, submit=True)
    retained_work = add_student_records(store, other_student["user_id"], other_classroom, other_assignment, submit=True)

    client = app.test_client()
    assert login_student(client, "teacher_one", "teacher-password-1").status_code == 302
    page = client.get("/account")
    assert b"removes your classrooms and assignments" in page.data
    assert b"student enrollments, drafts, revisions, and submissions" in page.data
    response = delete_form(client, "teacher-password-1")
    assert response.status_code == 200
    assert store.get_user_for_login("teacher_one") is None
    assert store.get_user_for_login("teacher_two") is not None
    assert store.get_user_for_login("student_one") is not None
    assert store.get_user_for_login("student_two") is not None
    assert store.get_assignment(assignment["assignment_id"]) is None
    assert store.get_assignment(other_assignment["assignment_id"]) is not None
    assert store.list_student_classrooms(student["user_id"]) == []
    assert store.list_student_classrooms(other_student["user_id"])
    assert store.get(removed_work["session_id"], student["user_id"], assignment["assignment_id"]) is None
    assert store.get(retained_work["session_id"], other_student["user_id"], other_assignment["assignment_id"]) is not None
    assert len(store.list_revisions(retained_work["session_id"], other_student["user_id"])) == 1
    with sqlite3.connect(store.database_path) as connection:
        assert connection.execute(
            "SELECT COUNT(*) FROM submissions WHERE assignment_id = ?", (assignment["assignment_id"],)
        ).fetchone()[0] == 0
        assert connection.execute(
            "SELECT COUNT(*) FROM submissions WHERE assignment_id = ?", (other_assignment["assignment_id"],)
        ).fetchone()[0] == 1
    assert client.get("/").location.endswith("/login")
