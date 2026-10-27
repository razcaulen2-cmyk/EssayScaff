"""Teacher stage progress is derived from persisted stage text and revision snapshots."""

import re
import sqlite3

from werkzeug.security import generate_password_hash

from app import create_app
from services.draft_store import DraftStore
from tests.auth_helpers import login_student, register_student


def new_test_app(tmp_path):
    app = create_app(secret_key="student-progress-phase2")
    app.config.update(
        TESTING=True,
        DRAFT_DATABASE_PATH=str(tmp_path / "student-progress.sqlite3"),
    )
    return app


def create_teacher(store, username="progress_teacher"):
    return store.create_teacher_user(
        username, generate_password_hash("teacher-password-1")
    )


def create_assignment(store, teacher):
    classroom = store.create_classroom(
        teacher["user_id"], "English 201", "Academic Writing", "BSCS 2A"
    )
    assignment = store.create_assignment(
        teacher["user_id"],
        classroom["classroom_id"],
        "Progress Essay",
        "social media",
        "Write a three-part essay.",
        "social media",
    )
    return classroom, assignment


def enroll_student(app, classroom, username):
    client = app.test_client()
    assert register_student(client, username).status_code == 302
    response = client.post(
        "/api/classroom-enrollments",
        json={"enrollment_code": classroom["enrollment_code"]},
    )
    assert response.status_code == 200
    return client


def start_workspace(client, assignment):
    response = client.get(f"/api/assignments/{assignment['assignment_id']}/workspace")
    assert response.status_code == 200
    return response.get_json()["draft"]["session_id"]


def revision_payload(assignment, session_id, introduction="", body="", conclusion=""):
    return {
        "assignment_id": assignment["assignment_id"],
        "session_id": session_id,
        "assignment_topic": assignment["topic"],
        "focus_terms": assignment["focus_terms"],
        "introduction_text": introduction,
        "body_text": body,
        "conclusion_text": conclusion,
    }


def save_revision(client, assignment, session_id, **texts):
    response = client.post(
        "/api/revisions",
        json=revision_payload(assignment, session_id, **texts),
    )
    assert response.status_code == 200, response.get_data(as_text=True)
    return response.get_json()


def save_draft(client, assignment, session_id, **texts):
    response = client.post(
        "/api/drafts",
        json=revision_payload(assignment, session_id, **texts),
    )
    assert response.status_code == 200, response.get_data(as_text=True)
    return response.get_json()


def submit(client, assignment, session_id, draft_version):
    response = client.post(
        "/api/submissions",
        json={
            "assignment_id": assignment["assignment_id"],
            "session_id": session_id,
            "draft_version": draft_version,
        },
    )
    assert response.status_code == 200, response.get_data(as_text=True)
    return response.get_json()


def progress_by_student(store, teacher, assignment):
    rows = store.assignment_progress(
        teacher["user_id"], assignment["assignment_id"]
    )
    return {row["username"]: row for row in rows}


def stages_by_name(row):
    return {stage["name"]: stage for stage in row["stages"]}


def test_stage_status_uses_saved_text_and_submitted_snapshots(tmp_path):
    app = new_test_app(tmp_path)
    store = DraftStore(app.config["DRAFT_DATABASE_PATH"])
    teacher = create_teacher(store)
    classroom, assignment = create_assignment(store, teacher)

    enroll_student(app, classroom, "no_writing")

    intro_only = enroll_student(app, classroom, "intro_only")
    intro_session = start_workspace(intro_only, assignment)
    save_revision(intro_only, assignment, intro_session, introduction="Intro A.")

    intro_body = enroll_student(app, classroom, "intro_body")
    intro_body_session = start_workspace(intro_body, assignment)
    save_revision(
        intro_body,
        assignment,
        intro_body_session,
        introduction="Intro A.",
        body="Body A.",
    )

    all_three = enroll_student(app, classroom, "all_three")
    all_three_session = start_workspace(all_three, assignment)
    save_revision(
        all_three,
        assignment,
        all_three_session,
        introduction="Intro A.",
        body="Body A.",
        conclusion="Conclusion A.",
    )

    submitted = enroll_student(app, classroom, "submitted")
    submitted_session = start_workspace(submitted, assignment)
    latest = save_revision(
        submitted,
        assignment,
        submitted_session,
        introduction="Intro A.",
        body="Body A.",
        conclusion="Conclusion A.",
    )
    submit(submitted, assignment, submitted_session, latest["draft_version"])

    # Defensive edge: submitted snapshots are used even if one stage is empty.
    partial_submission = enroll_student(app, classroom, "partial_submission")
    partial_session = start_workspace(partial_submission, assignment)
    save_revision(
        partial_submission,
        assignment,
        partial_session,
        introduction="Intro only.",
    )
    partial_user = store.get_user_for_login("partial_submission")
    with sqlite3.connect(app.config["DRAFT_DATABASE_PATH"]) as connection:
        connection.execute(
            """
            INSERT INTO submissions (
                student_user_id, assignment_id, session_id,
                introduction_snapshot, body_snapshot, conclusion_snapshot
            ) VALUES (?, ?, ?, 'Intro only.', '', '')
            """,
            (partial_user["user_id"], assignment["assignment_id"], partial_session),
        )

    rows = progress_by_student(store, teacher, assignment)

    no_writing_stages = stages_by_name(rows["no_writing"])
    assert rows["no_writing"]["progress"] == "Not Started"
    assert {stage["status"] for stage in no_writing_stages.values()} == {"Not Started"}
    assert {stage["revisions"] for stage in no_writing_stages.values()} == {0}

    intro_only_stages = stages_by_name(rows["intro_only"])
    assert rows["intro_only"]["progress"] == "In Progress"
    assert intro_only_stages["Introduction"]["status"] == "In Progress"
    assert intro_only_stages["Body"]["status"] == "Not Started"
    assert intro_only_stages["Conclusion"]["status"] == "Not Started"
    assert {stage["revisions"] for stage in intro_only_stages.values()} == {0}

    intro_body_stages = stages_by_name(rows["intro_body"])
    assert rows["intro_body"]["progress"] == "In Progress"
    assert intro_body_stages["Introduction"]["status"] == "In Progress"
    assert intro_body_stages["Body"]["status"] == "In Progress"
    assert intro_body_stages["Conclusion"]["status"] == "Not Started"

    all_three_stages = stages_by_name(rows["all_three"])
    assert rows["all_three"]["progress"] == "In Progress"
    assert {stage["status"] for stage in all_three_stages.values()} == {"In Progress"}

    submitted_stages = stages_by_name(rows["submitted"])
    assert rows["submitted"]["progress"] == "Submitted"
    assert {stage["status"] for stage in submitted_stages.values()} == {"Submitted"}
    assert {stage["revisions"] for stage in submitted_stages.values()} == {0}

    partial_stages = stages_by_name(rows["partial_submission"])
    assert rows["partial_submission"]["progress"] == "Submitted"
    assert partial_stages["Introduction"]["status"] == "Submitted"
    assert partial_stages["Body"]["status"] == "Not Started"
    assert partial_stages["Conclusion"]["status"] == "Not Started"


def test_stage_revision_counts_change_only_the_stage_that_changed(tmp_path):
    app = new_test_app(tmp_path)
    store = DraftStore(app.config["DRAFT_DATABASE_PATH"])
    teacher = create_teacher(store)
    classroom, assignment = create_assignment(store, teacher)

    body_reviser = enroll_student(app, classroom, "body_reviser")
    body_session = start_workspace(body_reviser, assignment)
    save_revision(
        body_reviser,
        assignment,
        body_session,
        introduction="Intro A.",
        body="Body A.",
    )
    save_revision(
        body_reviser,
        assignment,
        body_session,
        introduction="Intro A.",
        body="Body B.",
    )

    staged_reviser = enroll_student(app, classroom, "staged_reviser")
    staged_session = start_workspace(staged_reviser, assignment)
    save_revision(
        staged_reviser, assignment, staged_session,
        introduction="Intro A.", body="Body A.",
    )
    save_revision(
        staged_reviser, assignment, staged_session,
        introduction="Intro B.", body="Body A.",
    )
    save_revision(
        staged_reviser, assignment, staged_session,
        introduction="Intro B.", body="Body B.",
    )
    save_revision(
        staged_reviser, assignment, staged_session,
        introduction="Intro B.", body="Body B.", conclusion="Conclusion C.",
    )

    unchanged = enroll_student(app, classroom, "unchanged")
    unchanged_session = start_workspace(unchanged, assignment)
    first = save_revision(
        unchanged, assignment, unchanged_session,
        introduction="Intro A.", body="Body A.",
    )
    duplicate = save_revision(
        unchanged, assignment, unchanged_session,
        introduction="Intro A.", body="Body A.",
    )
    assert duplicate["created"] is False
    assert duplicate["revision_id"] == first["revision_id"]
    save_revision(
        unchanged, assignment, unchanged_session,
        introduction="Intro A.", body="Body B.",
    )

    cleared = enroll_student(app, classroom, "cleared")
    cleared_session = start_workspace(cleared, assignment)
    save_revision(
        cleared, assignment, cleared_session,
        introduction="Intro A.",
    )
    save_revision(
        cleared, assignment, cleared_session,
        introduction="",
        body="Body B.",
    )

    rows = progress_by_student(store, teacher, assignment)

    body_stages = stages_by_name(rows["body_reviser"])
    assert body_stages["Introduction"]["revisions"] == 0
    assert body_stages["Body"]["revisions"] == 1
    assert body_stages["Conclusion"]["revisions"] == 0

    staged_stages = stages_by_name(rows["staged_reviser"])
    assert staged_stages["Introduction"]["revisions"] == 1
    assert staged_stages["Body"]["revisions"] == 1
    assert staged_stages["Conclusion"]["revisions"] == 0

    unchanged_stages = stages_by_name(rows["unchanged"])
    assert unchanged_stages["Introduction"]["revisions"] == 0
    assert unchanged_stages["Body"]["revisions"] == 1

    cleared_stages = stages_by_name(rows["cleared"])
    assert cleared_stages["Introduction"]["revisions"] == 1
    assert cleared_stages["Body"]["revisions"] == 0
    assert cleared_stages["Conclusion"]["revisions"] == 0

    body_user = store.get_user_for_login("body_reviser")
    assert [item["revision_number"] for item in store.list_revisions(
        body_session, body_user["user_id"]
    )] == [2, 1]
    assert len(store.list_revisions(
        unchanged_session, store.get_user_for_login("unchanged")["user_id"]
    )) == 2


def test_analysis_and_draft_saves_do_not_create_stage_revisions(tmp_path):
    app = new_test_app(tmp_path)
    store = DraftStore(app.config["DRAFT_DATABASE_PATH"])
    teacher = create_teacher(store)
    classroom, assignment = create_assignment(store, teacher)

    analyser = enroll_student(app, classroom, "analyser")
    analyser_session = start_workspace(analyser, assignment)
    first = save_revision(
        analyser, assignment, analyser_session, introduction="Intro A."
    )
    analysed = analyser.post(
        "/api/analyze-stage",
        json={
            "assignment_id": assignment["assignment_id"],
            "stage_id": "INTRODUCTION",
            "introduction_text": "Different text that was never saved.",
        },
    )
    assert analysed.status_code == 200
    analyser_user = store.get_user_for_login("analyser")
    assert len(store.list_revisions(
        analyser_session, analyser_user["user_id"]
    )) == 1

    draft_editor = enroll_student(app, classroom, "draft_editor")
    draft_session = start_workspace(draft_editor, assignment)
    save_revision(
        draft_editor, assignment, draft_session, introduction="Intro A."
    )
    save_draft(
        draft_editor, assignment, draft_session, introduction="Intro B."
    )
    draft_user = store.get_user_for_login("draft_editor")
    assert len(store.list_revisions(
        draft_session, draft_user["user_id"]
    )) == 1

    rows = progress_by_student(store, teacher, assignment)
    analyser_stages = stages_by_name(rows["analyser"])
    assert analyser_stages["Introduction"]["revisions"] == 0
    assert analyser_stages["Introduction"]["status"] == "In Progress"
    assert store.get_or_create_assignment_workspace(
        analyser_user["user_id"], assignment["assignment_id"]
    )["draft"]["introduction_text"] == "Intro A."
    draft_stages = stages_by_name(rows["draft_editor"])
    assert draft_stages["Introduction"]["revisions"] == 0
    assert first["created"] is True

    save_revision(
        draft_editor, assignment, draft_session, introduction="Intro B."
    )
    save_revision(
        analyser, assignment, analyser_session, introduction="Intro B."
    )
    rows = progress_by_student(store, teacher, assignment)
    assert stages_by_name(rows["analyser"])["Introduction"]["revisions"] == 1
    assert stages_by_name(rows["draft_editor"])["Introduction"]["revisions"] == 1


def test_stage_counts_persist_after_logout_and_relogin(tmp_path):
    app = new_test_app(tmp_path)
    store = DraftStore(app.config["DRAFT_DATABASE_PATH"])
    teacher = create_teacher(store)
    classroom, assignment = create_assignment(store, teacher)

    writer = enroll_student(app, classroom, "returning_writer")
    session_id = start_workspace(writer, assignment)
    save_revision(writer, assignment, session_id, introduction="Intro A.")
    assert writer.post("/logout").status_code == 302

    returning = app.test_client()
    assert login_student(returning, "returning_writer").status_code == 302
    save_revision(returning, assignment, session_id, introduction="Intro B.")

    rows = progress_by_student(store, teacher, assignment)
    stages = stages_by_name(rows["returning_writer"])
    assert stages["Introduction"]["status"] == "In Progress"
    assert stages["Introduction"]["revisions"] == 1
    assert stages["Body"]["revisions"] == 0


def test_submitted_essay_uses_submission_snapshots_for_stage_status(tmp_path):
    app = new_test_app(tmp_path)
    store = DraftStore(app.config["DRAFT_DATABASE_PATH"])
    teacher = create_teacher(store)
    classroom, assignment = create_assignment(store, teacher)
    student = enroll_student(app, classroom, "submitted_writer")
    session_id = start_workspace(student, assignment)
    save_revision(
        student, assignment, session_id,
        introduction="Intro A.", body="Body A.", conclusion="Conclusion A.",
    )
    latest = save_revision(
        student, assignment, session_id,
        introduction="Intro B.", body="Body A.", conclusion="Conclusion A.",
    )
    submit(student, assignment, session_id, latest["draft_version"])

    rows = progress_by_student(store, teacher, assignment)
    stages = stages_by_name(rows["submitted_writer"])
    assert rows["submitted_writer"]["progress"] == "Submitted"
    assert {stage["status"] for stage in stages.values()} == {"Submitted"}
    assert stages["Introduction"]["revisions"] == 1
    assert stages["Body"]["revisions"] == 0
    assert stages["Conclusion"]["revisions"] == 0

    teacher_client = app.test_client()
    assert login_student(
        teacher_client, "progress_teacher", "teacher-password-1"
    ).status_code == 302
    html = teacher_client.get("/teacher").get_data(as_text=True)
    assert "Essay Stage" in html
    assert "Saved Revisions" in html
    assert html.count("View Essay") == 1


def test_teacher_progress_render_and_authorization_keep_students_scoped(tmp_path):
    app = new_test_app(tmp_path)
    store = DraftStore(app.config["DRAFT_DATABASE_PATH"])
    teacher_a = create_teacher(store, "teacher_a")
    teacher_b = create_teacher(store, "teacher_b")
    classroom_a, assignment_a = create_assignment_for_teacher(
        store, teacher_a, "English 201", "A"
    )
    classroom_b, assignment_b = create_assignment_for_teacher(
        store, teacher_b, "English 202", "B"
    )

    student_a = enroll_student(app, classroom_a, "student_a")
    session_a = start_workspace(student_a, assignment_a)
    save_revision(
        student_a, assignment_a, session_a,
        introduction="Secret intro text.", body="Body A.",
    )
    save_revision(
        student_a, assignment_a, session_a,
        introduction="Secret intro text.", body="Body B.",
    )

    student_b = enroll_student(app, classroom_b, "student_b")
    session_b = start_workspace(student_b, assignment_b)
    save_revision(student_b, assignment_b, session_b, introduction="Other intro.")

    page_a_client = app.test_client()
    page_b_client = app.test_client()
    assert login_student(
        page_a_client, "teacher_a", "teacher-password-1"
    ).status_code == 302
    assert login_student(
        page_b_client, "teacher_b", "teacher-password-1"
    ).status_code == 302
    page_a = page_a_client.get("/teacher").get_data(as_text=True)
    page_b = page_b_client.get("/teacher").get_data(as_text=True)

    assert "student_a" in page_a
    assert "student_b" not in page_a
    assert "Other intro." not in page_a
    assert "Secret intro text." not in page_a
    assert page_a.count("Essay Stage") == 1
    assert re.search(
        r"<td>Body</td><td><span[^>]*>In Progress</span></td>"
        r"<td><span class=\"table-subtext\">No recorded data</span></td><td>1</td>",
        page_a,
    )
    assert re.search(
        r"<td>Introduction</td><td><span[^>]*>In Progress</span></td>"
        r"<td><span class=\"table-subtext\">No recorded data</span></td><td>0</td>",
        page_a,
    )

    assert "student_b" in page_b
    assert "student_a" not in page_b
    assert "Secret intro text." not in page_b
    assert store.assignment_progress(teacher_b["user_id"], assignment_a["assignment_id"]) == []

    student_denied = app.test_client()
    assert register_student(student_denied, "outside_student").status_code == 302
    denied = student_denied.get("/teacher")
    assert denied.status_code == 403
    assert b"teacher accounts only" in denied.data


def test_incomplete_revision_history_shows_unavailable_counts(tmp_path):
    app = new_test_app(tmp_path)
    store = DraftStore(app.config["DRAFT_DATABASE_PATH"])
    teacher = create_teacher(store)
    classroom, assignment = create_assignment(store, teacher)
    student = enroll_student(app, classroom, "gapped_history")
    session_id = start_workspace(student, assignment)
    save_revision(student, assignment, session_id, introduction="Intro A.")
    save_revision(student, assignment, session_id, introduction="Intro B.")

    with sqlite3.connect(app.config["DRAFT_DATABASE_PATH"]) as connection:
        connection.execute(
            "DELETE FROM writing_revisions WHERE session_id = ? AND revision_number = 1",
            (session_id,),
        )

    rows = progress_by_student(store, teacher, assignment)
    stages = stages_by_name(rows["gapped_history"])
    assert rows["gapped_history"]["progress"] == "In Progress"
    assert stages["Introduction"]["status"] == "In Progress"
    assert {stage["revisions"] for stage in stages.values()} == {None}

    teacher_client = app.test_client()
    assert login_student(
        teacher_client, "progress_teacher", "teacher-password-1"
    ).status_code == 302
    html = teacher_client.get("/teacher").get_data(as_text=True)
    assert html.count("Unavailable") == 3


def create_assignment_for_teacher(store, teacher, classroom_name, section):
    classroom = store.create_classroom(
        teacher["user_id"], classroom_name, "Academic Writing", section
    )
    assignment = store.create_assignment(
        teacher["user_id"],
        classroom["classroom_id"],
        "Scoped Essay",
        "social media",
        "Write a three-part essay.",
        "social media",
    )
    return classroom, assignment
