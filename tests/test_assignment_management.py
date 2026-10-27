"""Teacher assignment edits and soft deletion preserve student history."""

import sqlite3

import pytest
from werkzeug.security import generate_password_hash

from app import create_app
from services.draft_store import DraftStore
from tests.auth_helpers import form_csrf_token, login_student, register_student


def setup_management(tmp_path):
    app = create_app(secret_key="assignment-management-test-secret")
    app.config.update(TESTING=True, DRAFT_DATABASE_PATH=str(tmp_path / "assignment-management.sqlite3"))
    store = DraftStore(app.config["DRAFT_DATABASE_PATH"])
    owner = store.create_teacher_user("owner_teacher", generate_password_hash("owner-password-1"))
    other = store.create_teacher_user("other_teacher", generate_password_hash("other-password-1"))
    classroom = store.create_classroom(owner["user_id"], "Writing 101", "Writing", "Section A")
    assignment = store.create_assignment(
        owner["user_id"], classroom["classroom_id"],
        "Original title", "Original topic", "Original instructions", "original, focus",
    )
    teacher = app.test_client()
    other_teacher = app.test_client()
    assert login_student(teacher, "owner_teacher", "owner-password-1").status_code == 302
    assert login_student(other_teacher, "other_teacher", "other-password-1").status_code == 302
    student = app.test_client()
    assert register_student(student, "work_student").status_code == 302
    assert student.post(
        "/api/classroom-enrollments", json={"enrollment_code": classroom["enrollment_code"]}
    ).status_code == 200
    return app, store, owner, other, classroom, assignment, teacher, other_teacher, student


def edit_values(**changes):
    values = {
        "title": "Updated title",
        "topic": "Updated topic",
        "instructions": "Updated instructions",
        "focus_terms": "updated, terms",
    }
    values.update(changes)
    return values


ESSAY = {
    "introduction_text": "Students should read every day.",
    "body_text": "Reading helps students build knowledge.",
    "conclusion_text": "Daily reading supports learning.",
}


def test_edit_assignment_updates_the_existing_record_and_shows_success(tmp_path):
    _app, store, owner, _other, _classroom, assignment, teacher, _other_teacher, _student = setup_management(tmp_path)
    page = teacher.get(f"/teacher/assignments/{assignment['assignment_id']}/edit")
    assert page.status_code == 200
    assert b"Original topic" in page.data
    assert b"Original instructions" in page.data
    response = teacher.post(
        f"/teacher/assignments/{assignment['assignment_id']}/edit",
        data={**edit_values(), "csrf_token": form_csrf_token(page)},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Assignment updated successfully" in response.data
    updated = store.get_assignment(assignment["assignment_id"])
    assert updated["title"] == "Updated title"
    assert updated["topic"] == "Updated topic"
    assert updated["instructions"] == "Updated instructions"
    assert updated["focus_terms"] == "updated, terms"
    assert len(store.list_teacher_assignments(owner["user_id"])) == 1


@pytest.mark.parametrize("work_kind", ["draft", "revision", "submission"])
def test_task_fields_are_locked_server_side_after_any_student_work(tmp_path, work_kind):
    _app, store, _owner, _other, _classroom, assignment, teacher, _other_teacher, student = setup_management(tmp_path)
    workspace = student.get(f"/api/assignments/{assignment['assignment_id']}/workspace").get_json()
    session_id = workspace["draft"]["session_id"]
    student_id = store.get_user_for_login("work_student")["user_id"]
    draft = {
        "assignment_topic": assignment["topic"],
        "focus_terms": assignment["focus_terms"],
        **(ESSAY if work_kind in {"draft", "submission"} else {
            "introduction_text": "", "body_text": "", "conclusion_text": ""
        }),
    }
    saved = store.save(draft, session_id, student_id, assignment["assignment_id"])
    if work_kind == "revision":
        store.save_revision(draft, session_id, student_id, assignment["assignment_id"])
    elif work_kind == "submission":
        store.create_submission(
            student_id, assignment["assignment_id"], session_id, store.draft_version(saved)
        )

    page = teacher.get(f"/teacher/assignments/{assignment['assignment_id']}/edit")
    assert page.status_code == 200
    assert b"Only the assignment title can be changed" in page.data
    assert b'name="topic"' in page.data and b'readonly' in page.data
    locked = teacher.post(
        f"/teacher/assignments/{assignment['assignment_id']}/edit",
        data={**edit_values(title="Attempted title"), "csrf_token": form_csrf_token(page)},
    )
    assert locked.status_code == 409
    unchanged = store.get_assignment(assignment["assignment_id"])
    assert unchanged["title"] == "Original title"
    assert unchanged["topic"] == "Original topic"
    assert unchanged["instructions"] == "Original instructions"
    assert unchanged["focus_terms"] == "original, focus"

    page = teacher.get(f"/teacher/assignments/{assignment['assignment_id']}/edit")
    title_only = teacher.post(
        f"/teacher/assignments/{assignment['assignment_id']}/edit",
        data={"title": "Title only", "csrf_token": form_csrf_token(page)},
    )
    assert title_only.status_code == 302
    updated = store.get_assignment(assignment["assignment_id"])
    assert updated["title"] == "Title only"
    assert updated["topic"] == "Original topic"
    assert updated["instructions"] == "Original instructions"
    assert updated["focus_terms"] == "original, focus"


def test_edit_delete_routes_enforce_teacher_owner_role_and_csrf(tmp_path):
    app, store, _owner, other, _classroom, assignment, teacher, other_teacher, student = setup_management(tmp_path)
    foreign_classroom = store.create_classroom(other["user_id"], "Other class", "Writing", "B")
    foreign = store.create_assignment(
        other["user_id"], foreign_classroom["classroom_id"],
        "Other assignment", "Topic", "Instructions", "",
    )
    assert teacher.get(f"/teacher/assignments/{foreign['assignment_id']}/edit").status_code == 404
    foreign_post = teacher.post(
        f"/teacher/assignments/{foreign['assignment_id']}/edit", data=edit_values(),
        headers={"X-CSRF-Token": ""},
    )
    assert foreign_post.status_code == 400
    foreign_post = teacher.post(
        f"/teacher/assignments/{foreign['assignment_id']}/edit", data=edit_values()
    )
    assert foreign_post.status_code == 404
    page = teacher.get("/teacher")
    csrf = form_csrf_token(page)
    foreign_post = teacher.post(
        f"/teacher/assignments/{foreign['assignment_id']}/edit",
        data={**edit_values(), "csrf_token": csrf},
    )
    assert foreign_post.status_code == 404
    assert teacher.post(
        f"/teacher/assignments/{foreign['assignment_id']}/delete", data={"csrf_token": csrf}
    ).status_code == 404
    assert student.get(f"/teacher/assignments/{assignment['assignment_id']}/edit").status_code == 403
    assert student.post(
        f"/teacher/assignments/{assignment['assignment_id']}/delete",
        data={"csrf_token": "irrelevant"},
    ).status_code == 403
    assert other_teacher.get(f"/teacher/assignments/{assignment['assignment_id']}/edit").status_code == 404
    assert app.testing


def test_edit_validation_returns_error_without_changing_assignment(tmp_path):
    _app, store, _owner, _other, _classroom, assignment, teacher, _other_teacher, _student = setup_management(tmp_path)
    page = teacher.get(f"/teacher/assignments/{assignment['assignment_id']}/edit")
    response = teacher.post(
        f"/teacher/assignments/{assignment['assignment_id']}/edit",
        data={**edit_values(title=""), "csrf_token": form_csrf_token(page)},
    )
    assert response.status_code == 400
    assert b"Enter an Assignment Title" in response.data
    assert store.get_assignment(assignment["assignment_id"])["title"] == "Original title"


def test_delete_soft_archives_and_preserves_student_records_and_read_only_history(tmp_path):
    _app, store, owner, other, classroom, assignment, teacher, _other_teacher, student = setup_management(tmp_path)
    assignment_id = assignment["assignment_id"]
    workspace = student.get(f"/api/assignments/{assignment_id}/workspace").get_json()
    session_id = workspace["draft"]["session_id"]
    payload = {
        **ESSAY,
        "assignment_id": assignment_id,
        "session_id": session_id,
        "assignment_topic": "Ignored browser topic",
        "focus_terms": "ignored",
    }
    saved = student.post("/api/drafts", json=payload)
    assert saved.status_code == 200
    revision = student.post("/api/revisions", json=payload)
    assert revision.status_code == 200
    version = student.get(f"/api/assignments/{assignment_id}/workspace").get_json()["draft_version"]
    submission = student.post(
        "/api/submissions",
        json={"assignment_id": assignment_id, "session_id": session_id, "draft_version": version},
    )
    assert submission.status_code == 200
    student_id = store.get_user_for_login("work_student")["user_id"]
    with sqlite3.connect(store.database_path) as connection:
        before = tuple(connection.execute(
            "SELECT (SELECT COUNT(*) FROM writing_sessions WHERE assignment_id=?), "
            "(SELECT COUNT(*) FROM writing_revisions r JOIN writing_sessions s ON s.session_id=r.session_id WHERE s.assignment_id=?), "
            "(SELECT COUNT(*) FROM submissions WHERE assignment_id=?)",
            (assignment_id, assignment_id, assignment_id),
        ).fetchone())
    assert before == (1, 1, 1)

    dashboard = teacher.get("/teacher")
    csrf = form_csrf_token(dashboard)
    no_csrf = teacher.post(
        f"/teacher/assignments/{assignment_id}/delete", data={},
        headers={"X-CSRF-Token": ""},
    )
    assert no_csrf.status_code == 400
    response = teacher.post(
        f"/teacher/assignments/{assignment_id}/delete",
        data={"csrf_token": csrf}, follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Existing student drafts, revisions, and submissions are retained" in response.data
    assert b"Archived assignments" in response.data
    assert b"Original title" in response.data
    assert store.get_assignment(assignment_id)["deleted_at"] is not None
    assert store.list_teacher_classroom_assignments(owner["user_id"], classroom["classroom_id"]) == []
    assert store.list_teacher_deleted_assignments(owner["user_id"])[0]["assignment_id"] == assignment_id
    assert store.list_teacher_deleted_assignments(other["user_id"]) == []

    assert student.get("/api/assignments").get_json()["assignments"] == []
    assert student.get(f"/api/classrooms/{classroom['classroom_id']}/assignments").get_json()["assignments"] == []
    archived = student.get("/api/archived-assignments").get_json()["assignments"]
    assert [item["assignment_id"] for item in archived] == [assignment_id]
    retained_workspace = student.get(f"/api/assignments/{assignment_id}/workspace")
    assert retained_workspace.status_code == 200
    assert retained_workspace.get_json()["assignment"]["deleted_at"] is not None
    assert retained_workspace.get_json()["draft"]["body_text"] == ESSAY["body_text"]
    assert student.get(f"/api/submissions/{assignment_id}").get_json()["body_snapshot"] == ESSAY["body_text"]
    assert student.post("/api/drafts", json=payload).status_code == 404
    assert student.post("/api/revisions", json=payload).status_code == 404
    assert student.post(
        "/api/submissions",
        json={"assignment_id": assignment_id, "session_id": session_id, "draft_version": version},
    ).status_code == 409

    new_student = _app.test_client()
    assert register_student(new_student, "new_student").status_code == 302
    assert new_student.post(
        "/api/classroom-enrollments", json={"enrollment_code": classroom["enrollment_code"]}
    ).status_code == 200
    no_new_workspace = new_student.get(f"/api/assignments/{assignment_id}/workspace")
    assert no_new_workspace.status_code == 410
    assert store.get_student_submission(student_id, assignment_id) is not None
    assert store.list_teacher_classrooms(owner["user_id"])[0]["student_count"] == 2
    with sqlite3.connect(store.database_path) as connection:
        after = connection.execute(
            "SELECT (SELECT COUNT(*) FROM writing_sessions WHERE assignment_id=?), "
            "(SELECT COUNT(*) FROM writing_revisions r JOIN writing_sessions s ON s.session_id=r.session_id WHERE s.assignment_id=?), "
            "(SELECT COUNT(*) FROM submissions WHERE assignment_id=?)",
            (assignment_id, assignment_id, assignment_id),
        ).fetchone()
    assert tuple(after) == before


def test_delete_confirmation_text_is_present_on_teacher_dashboard(tmp_path):
    _app, _store, _owner, _other, _classroom, assignment, teacher, _other_teacher, _student = setup_management(tmp_path)
    page = teacher.get("/teacher")
    assert page.status_code == 200
    assert b"Are you sure you want to delete this assignment? It will no longer appear in active classroom assignments." in page.data
    assert f"/teacher/assignments/{assignment['assignment_id']}/delete".encode() in page.data
