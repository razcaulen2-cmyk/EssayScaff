"""Estimated active writing time is recorded idempotently and scoped by records."""

import sqlite3
import threading
import time

from werkzeug.security import generate_password_hash

from app import create_app
from services.draft_store import DraftStore
from tests.auth_helpers import login_student, register_student


def new_test_app(tmp_path, activity_enabled=True):
    app = create_app(secret_key="student-progress-phase3")
    app.config.update(
        TESTING=True,
        DRAFT_DATABASE_PATH=str(tmp_path / "writing-activity.sqlite3"),
        WRITING_ACTIVITY_ENABLED=activity_enabled,
    )
    return app


def new_test_store(app):
    return DraftStore(
        app.config["DRAFT_DATABASE_PATH"],
        enable_activity_tracking=bool(app.config["WRITING_ACTIVITY_ENABLED"]),
    )


def create_teacher(store, username="activity_teacher"):
    return store.create_teacher_user(
        username, generate_password_hash("teacher-password-1")
    )


def create_classroom_assignment(store, teacher, name="English 301", section="A"):
    classroom = store.create_classroom(
        teacher["user_id"], name, "Academic Writing", section
    )
    assignment = store.create_assignment(
        teacher["user_id"],
        classroom["classroom_id"],
        "Active Time Essay",
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


def aligned_bucket(offset_seconds=0):
    timestamp = int(time.time()) - offset_seconds
    return timestamp - (timestamp % 5)


def activity_events(stage, count, offset=0, seconds=5):
    start = aligned_bucket(offset)
    return [
        {"stage": stage, "bucket_start": start - index * 5, "seconds": seconds}
        for index in range(count)
    ]


def post_activity(client, assignment, session_id, events):
    return client.post(
        "/api/writing-activity",
        json={
            "assignment_id": assignment["assignment_id"],
            "session_id": session_id,
            "events": events,
        },
    )


def progress_by_student(store, teacher, assignment):
    return {
        row["username"]: row
        for row in store.assignment_progress(
            teacher["user_id"], assignment["assignment_id"]
        )
    }


def stages_by_name(row):
    return {stage["name"]: stage for stage in row["stages"]}


def save_revision_payload(assignment, session_id, introduction="", body="", conclusion=""):
    return {
        "assignment_id": assignment["assignment_id"],
        "session_id": session_id,
        "assignment_topic": assignment["topic"],
        "focus_terms": assignment["focus_terms"],
        "introduction_text": introduction,
        "body_text": body,
        "conclusion_text": conclusion,
    }


def test_activity_is_attributed_deduped_and_persists(tmp_path):
    app = new_test_app(tmp_path)
    store = new_test_store(app)
    teacher = create_teacher(store)
    classroom, assignment = create_classroom_assignment(store, teacher)

    writer = enroll_student(app, classroom, "activity_writer")
    session_id = start_workspace(writer, assignment)

    intro_events = activity_events("INTRODUCTION", 3)
    body_events = activity_events("BODY", 2, offset=20)
    assert post_activity(writer, assignment, session_id, intro_events).status_code == 200
    assert post_activity(writer, assignment, session_id, body_events).status_code == 200

    # An identical retry is an idempotent bucket, not extra time.
    assert post_activity(writer, assignment, session_id, intro_events).status_code == 200

    rows = progress_by_student(store, teacher, assignment)
    stages = stages_by_name(rows["activity_writer"])
    assert stages["Introduction"]["activity_seconds"] == 15
    assert stages["Body"]["activity_seconds"] == 10
    assert stages["Conclusion"]["activity_seconds"] is None
    # Activity is not saved writing and must not change Phase 2 status/revisions.
    assert {stage["status"] for stage in stages.values()} == {"Not Started"}
    assert {stage["revisions"] for stage in stages.values()} == {0}

    assert writer.post("/logout").status_code == 302
    returning = app.test_client()
    assert login_student(returning, "activity_writer").status_code == 302
    start_workspace(returning, assignment)
    assert post_activity(
        returning, assignment, session_id, activity_events("INTRODUCTION", 1, offset=40)
    ).status_code == 200

    rows = progress_by_student(store, teacher, assignment)
    stages = stages_by_name(rows["activity_writer"])
    assert stages["Introduction"]["activity_seconds"] == 20
    assert stages["Body"]["activity_seconds"] == 10

    revision = returning.post(
        "/api/revisions",
        json=save_revision_payload(
            assignment, session_id, introduction="Intro.", body="Body."
        ),
    )
    assert revision.status_code == 200
    rows = progress_by_student(store, teacher, assignment)
    stages = stages_by_name(rows["activity_writer"])
    assert stages["Introduction"]["status"] == "In Progress"
    assert stages["Introduction"]["revisions"] == 0
    assert stages["Introduction"]["activity_seconds"] == 20
    assert stages["Body"]["revisions"] == 0

    assert post_activity(
        returning, assignment, session_id,
        activity_events("CONCLUSION", 13, offset=60),
    ).status_code == 200
    enroll_student(app, classroom, "quiet_student")
    rows = progress_by_student(store, teacher, assignment)
    stages = stages_by_name(rows["activity_writer"])
    assert stages["Conclusion"]["activity_seconds"] == 65

    teacher_client = app.test_client()
    assert login_student(
        teacher_client, "activity_teacher", "teacher-password-1"
    ).status_code == 302
    html = teacher_client.get("/teacher").get_data(as_text=True)
    assert "Estimated Active Writing Time" in html
    assert "20 sec" in html
    assert "10 sec" in html
    assert "1.1 min" in html
    assert "Saved Revisions" in html
    assert html.count("No recorded data") >= 1


def test_activity_is_scoped_by_student_assignment_and_role(tmp_path):
    app = new_test_app(tmp_path)
    store = new_test_store(app)
    teacher_a = create_teacher(store, "teacher_a")
    teacher_b = create_teacher(store, "teacher_b")
    classroom_a, assignment_a = create_classroom_assignment(
        store, teacher_a, "English 301", "A"
    )
    classroom_b, assignment_b = create_classroom_assignment(
        store, teacher_b, "English 302", "B"
    )

    student_a = enroll_student(app, classroom_a, "student_a")
    session_a = start_workspace(student_a, assignment_a)
    student_b = enroll_student(app, classroom_b, "student_b")
    session_b = start_workspace(student_b, assignment_b)

    assert post_activity(
        student_b, assignment_b, session_b, activity_events("BODY", 2)
    ).status_code == 200

    # A student cannot attach activity to another student's session or assignment.
    assert post_activity(
        student_a, assignment_a, session_b, activity_events("INTRODUCTION", 1)
    ).status_code == 404
    assert post_activity(
        student_a, assignment_b, session_b, activity_events("INTRODUCTION", 1)
    ).status_code == 404

    teacher_client = app.test_client()
    assert login_student(
        teacher_client, "teacher_a", "teacher-password-1"
    ).status_code == 302
    assert post_activity(
        teacher_client, assignment_a, session_a, activity_events("INTRODUCTION", 1)
    ).status_code == 403

    page_a = teacher_client.get("/teacher").get_data(as_text=True)
    page_b_client = app.test_client()
    assert login_student(
        page_b_client, "teacher_b", "teacher-password-1"
    ).status_code == 302
    page_b = page_b_client.get("/teacher").get_data(as_text=True)

    assert "student_a" in page_a
    assert "student_b" not in page_a
    assert "student_b" in page_b
    assert "student_a" not in page_b
    assert "No recorded data" in page_a
    assert "10 sec" in page_b
    assert store.assignment_progress(
        teacher_a["user_id"], assignment_b["assignment_id"]
    ) == []

    student_denied = app.test_client()
    assert register_student(student_denied, "outside_student").status_code == 302
    assert student_denied.get("/teacher").status_code == 403

    anonymous = app.test_client()
    anonymous.get("/login")
    denied = anonymous.post(
        "/api/writing-activity",
        json={
            "assignment_id": assignment_a["assignment_id"],
            "session_id": session_a,
            "events": activity_events("INTRODUCTION", 1),
        },
    )
    assert denied.status_code in {400, 401}


def test_activity_validation_rejects_invalid_events(tmp_path):
    app = new_test_app(tmp_path)
    store = new_test_store(app)
    teacher = create_teacher(store)
    classroom, assignment = create_classroom_assignment(store, teacher)
    student = enroll_student(app, classroom, "validated_writer")
    session_id = start_workspace(student, assignment)

    valid = activity_events("INTRODUCTION", 1)
    cases = [
        [],
        [{"stage": "INTRO", "bucket_start": aligned_bucket(), "seconds": 5}],
        [{**valid[0], "seconds": 0}],
        [{**valid[0], "seconds": 6}],
        [{**valid[0], "seconds": 31}],
        [{**valid[0], "seconds": True}],
        [{**valid[0], "bucket_start": aligned_bucket(700)}],
        [{**valid[0], "bucket_start": aligned_bucket(-120)}],
        activity_events("BODY", 25),
    ]
    for events in cases:
        response = post_activity(student, assignment, session_id, events)
        assert response.status_code == 400, events

    assert post_activity(
        student, assignment, session_id, activity_events("INTRODUCTION", 1)
    ).status_code == 200
    rows = progress_by_student(store, teacher, assignment)
    stages = stages_by_name(rows["validated_writer"])
    assert stages["Introduction"]["activity_seconds"] == 5
    assert stages["Body"]["activity_seconds"] is None

    # Storage rejects invalid data even when a caller bypasses the HTTP layer.
    user = store.get_user_for_login("validated_writer")
    try:
        store.record_writing_activity(
            user["user_id"],
            assignment["assignment_id"],
            session_id,
            [{"stage": "INTRODUCTION", "bucket_start": aligned_bucket(), "seconds": 0}],
        )
    except ValueError:
        pass
    else:
        raise AssertionError("Store accepted an invalid activity duration")


def test_activity_stops_after_submission(tmp_path):
    app = new_test_app(tmp_path)
    store = new_test_store(app)
    teacher = create_teacher(store)
    classroom, assignment = create_classroom_assignment(store, teacher)
    student = enroll_student(app, classroom, "submitted_writer")
    session_id = start_workspace(student, assignment)

    assert post_activity(
        student, assignment, session_id, activity_events("INTRODUCTION", 2)
    ).status_code == 200
    revision = student.post(
        "/api/revisions",
        json=save_revision_payload(
            assignment,
            session_id,
            introduction="Intro.",
            body="Body.",
            conclusion="Conclusion.",
        ),
    )
    assert revision.status_code == 200
    submission = student.post(
        "/api/submissions",
        json={
            "assignment_id": assignment["assignment_id"],
            "session_id": session_id,
            "draft_version": revision.get_json()["draft_version"],
        },
    )
    assert submission.status_code == 200

    stopped = post_activity(
        student, assignment, session_id, activity_events("CONCLUSION", 1)
    )
    assert stopped.status_code == 409
    rows = progress_by_student(store, teacher, assignment)
    stages = stages_by_name(rows["submitted_writer"])
    assert stages["Introduction"]["activity_seconds"] == 10
    assert stages["Conclusion"]["activity_seconds"] is None


def test_activity_store_sums_days_and_keeps_assignments_separate(tmp_path):
    app = new_test_app(tmp_path)
    store = new_test_store(app)
    teacher = create_teacher(store)
    classroom, first_assignment = create_classroom_assignment(store, teacher)
    second_assignment = store.create_assignment(
        teacher["user_id"],
        classroom["classroom_id"],
        "Second Essay",
        "reading",
        "Write a second essay.",
        "reading",
    )
    student = enroll_student(app, classroom, "multi_day_writer")
    user = store.get_user_for_login("multi_day_writer")
    first_workspace = store.get_or_create_assignment_workspace(
        user["user_id"], first_assignment["assignment_id"]
    )
    second_workspace = store.get_or_create_assignment_workspace(
        user["user_id"], second_assignment["assignment_id"]
    )

    day_one = int(time.time()) - 86_400
    day_one_bucket = day_one - (day_one % 5)
    day_two = int(time.time())
    day_two_bucket = day_two - (day_two % 5)
    store.record_writing_activity(
        user["user_id"],
        first_assignment["assignment_id"],
        first_workspace["draft"]["session_id"],
        [
            {"stage": "INTRODUCTION", "bucket_start": day_one_bucket - offset, "seconds": 5}
            for offset in (0, 5, 10)
        ],
        now=day_one,
    )
    store.record_writing_activity(
        user["user_id"],
        first_assignment["assignment_id"],
        first_workspace["draft"]["session_id"],
        [
            {"stage": "INTRODUCTION", "bucket_start": day_two_bucket - offset, "seconds": 5}
            for offset in (0, 5)
        ],
        now=day_two,
    )
    store.record_writing_activity(
        user["user_id"],
        second_assignment["assignment_id"],
        second_workspace["draft"]["session_id"],
        [
            {"stage": "BODY", "bucket_start": day_two_bucket - offset, "seconds": 5}
            for offset in (0, 5, 10, 15)
        ],
        now=day_two,
    )

    first_rows = progress_by_student(store, teacher, first_assignment)
    first_stages = stages_by_name(first_rows["multi_day_writer"])
    assert first_stages["Introduction"]["activity_seconds"] == 25
    assert first_stages["Body"]["activity_seconds"] is None

    second_rows = progress_by_student(store, teacher, second_assignment)
    second_stages = stages_by_name(second_rows["multi_day_writer"])
    assert second_stages["Introduction"]["activity_seconds"] is None
    assert second_stages["Body"]["activity_seconds"] == 20


def test_account_deletion_removes_activity_before_linked_records(tmp_path):
    app = new_test_app(tmp_path)
    store = new_test_store(app)
    teacher = create_teacher(store)
    classroom, assignment = create_classroom_assignment(store, teacher)

    student = enroll_student(app, classroom, "deleted_writer")
    session_id = start_workspace(student, assignment)
    assert post_activity(
        student, assignment, session_id, activity_events("INTRODUCTION", 1)
    ).status_code == 200
    student_user = store.get_user_for_login("deleted_writer")
    store.delete_user_and_linked_records(student_user["user_id"])

    with sqlite3.connect(app.config["DRAFT_DATABASE_PATH"]) as connection:
        assert connection.execute("SELECT COUNT(*) FROM writing_activity").fetchone()[0] == 0
        assert list(connection.execute("PRAGMA foreign_key_check")) == []

    teacher_writer = enroll_student(app, classroom, "teacher_removed_writer")
    teacher_session = start_workspace(teacher_writer, assignment)
    assert post_activity(
        teacher_writer, assignment, teacher_session, activity_events("BODY", 1)
    ).status_code == 200
    store.delete_user_and_linked_records(teacher["user_id"])

    with sqlite3.connect(app.config["DRAFT_DATABASE_PATH"]) as connection:
        assert connection.execute("SELECT COUNT(*) FROM writing_activity").fetchone()[0] == 0
        assert list(connection.execute("PRAGMA foreign_key_check")) == []


def test_tracking_disabled_by_default_creates_no_table(tmp_path):
    app = new_test_app(tmp_path, activity_enabled=False)
    store = new_test_store(app)
    teacher = create_teacher(store)
    classroom, assignment = create_classroom_assignment(store, teacher)
    student = enroll_student(app, classroom, "disabled_writer")
    session_id = start_workspace(student, assignment)

    response = post_activity(
        student, assignment, session_id, activity_events("INTRODUCTION", 1)
    )
    assert response.status_code == 503

    with sqlite3.connect(app.config["DRAFT_DATABASE_PATH"]) as connection:
        table = connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'writing_activity'"
        ).fetchone()
    assert table is None

    rows = progress_by_student(store, teacher, assignment)
    stages = stages_by_name(rows["disabled_writer"])
    assert {stage["activity_seconds"] for stage in stages.values()} == {None}

    teacher_client = app.test_client()
    assert login_student(
        teacher_client, "activity_teacher", "teacher-password-1"
    ).status_code == 302
    html = teacher_client.get("/teacher").get_data(as_text=True)
    assert "Estimated Active Writing Time" in html
    assert html.count("No recorded data") >= 3


def test_cross_stage_bucket_is_recorded_once_and_keeps_first_stage(tmp_path):
    app = new_test_app(tmp_path)
    store = new_test_store(app)
    teacher = create_teacher(store)
    classroom, assignment = create_classroom_assignment(store, teacher)
    writer = enroll_student(app, classroom, "crosstage_writer")
    session_id = start_workspace(writer, assignment)
    bucket = aligned_bucket()

    for stage in ("INTRODUCTION", "BODY", "CONCLUSION"):
        assert post_activity(
            writer,
            assignment,
            session_id,
            [{"stage": stage, "bucket_start": bucket, "seconds": 5}],
        ).status_code == 200

    with sqlite3.connect(app.config["DRAFT_DATABASE_PATH"]) as connection:
        rows = connection.execute(
            "SELECT stage, bucket_start, seconds FROM writing_activity"
        ).fetchall()
    assert rows == [("INTRODUCTION", bucket, 5)]

    stages = stages_by_name(
        progress_by_student(store, teacher, assignment)["crosstage_writer"]
    )
    assert stages["Introduction"]["activity_seconds"] == 5
    assert stages["Body"]["activity_seconds"] is None
    assert stages["Conclusion"]["activity_seconds"] is None
    assert sum(stage["activity_seconds"] or 0 for stage in stages.values()) == 5

    assert post_activity(
        writer,
        assignment,
        session_id,
        [{"stage": "INTRODUCTION", "bucket_start": bucket, "seconds": 5}],
    ).status_code == 200
    with sqlite3.connect(app.config["DRAFT_DATABASE_PATH"]) as connection:
        assert connection.execute(
            "SELECT stage, seconds FROM writing_activity"
        ).fetchall() == [("INTRODUCTION", 5)]

    assert post_activity(
        writer,
        assignment,
        session_id,
        [{"stage": "BODY", "bucket_start": bucket - 5, "seconds": 5}],
    ).status_code == 200
    stages = stages_by_name(
        progress_by_student(store, teacher, assignment)["crosstage_writer"]
    )
    assert stages["Introduction"]["activity_seconds"] == 5
    assert stages["Body"]["activity_seconds"] == 5

    other_writer = enroll_student(app, classroom, "crosstage_other_writer")
    other_session = start_workspace(other_writer, assignment)
    assert post_activity(
        other_writer,
        assignment,
        other_session,
        [{"stage": "CONCLUSION", "bucket_start": bucket, "seconds": 5}],
    ).status_code == 200
    other_stages = stages_by_name(
        progress_by_student(store, teacher, assignment)["crosstage_other_writer"]
    )
    assert other_stages["Conclusion"]["activity_seconds"] == 5
    assert other_stages["Introduction"]["activity_seconds"] is None

    second_assignment = store.create_assignment(
        teacher["user_id"],
        classroom["classroom_id"],
        "Second Active Time Essay",
        "reading",
        "Write a second essay.",
        "reading",
    )
    second_session = start_workspace(writer, second_assignment)
    assert post_activity(
        writer,
        second_assignment,
        second_session,
        [{"stage": "BODY", "bucket_start": bucket, "seconds": 5}],
    ).status_code == 200
    second_stages = stages_by_name(
        progress_by_student(store, teacher, second_assignment)["crosstage_writer"]
    )
    assert second_stages["Body"]["activity_seconds"] == 5
    first_stages = stages_by_name(
        progress_by_student(store, teacher, assignment)["crosstage_writer"]
    )
    assert first_stages["Body"]["activity_seconds"] == 5
    assert first_stages["Introduction"]["activity_seconds"] == 5


def test_simultaneous_cross_stage_requests_create_one_bucket(tmp_path):
    app = new_test_app(tmp_path)
    store = new_test_store(app)
    teacher = create_teacher(store)
    classroom, assignment = create_classroom_assignment(store, teacher)
    enroll_student(app, classroom, "concurrent_writer")
    user = store.get_user_for_login("concurrent_writer")
    workspace = store.get_or_create_assignment_workspace(
        user["user_id"], assignment["assignment_id"]
    )
    session_id = workspace["draft"]["session_id"]
    bucket = aligned_bucket()

    barrier = threading.Barrier(2)
    outcomes = [None, None]

    def submit(index, stage):
        barrier.wait(timeout=5)
        try:
            outcomes[index] = store.record_writing_activity(
                user["user_id"],
                assignment["assignment_id"],
                session_id,
                [{"stage": stage, "bucket_start": bucket, "seconds": 5}],
            )
        except Exception as error:  # pragma: no cover - surfaced by the assertion
            outcomes[index] = error

    threads = [
        threading.Thread(target=submit, args=(index, stage))
        for index, stage in enumerate(("BODY", "CONCLUSION"))
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert all(isinstance(outcome, dict) for outcome in outcomes), outcomes
    with sqlite3.connect(app.config["DRAFT_DATABASE_PATH"]) as connection:
        rows = connection.execute(
            "SELECT stage, seconds FROM writing_activity"
        ).fetchall()
        assert list(connection.execute("PRAGMA foreign_key_check")) == []
    assert len(rows) == 1
    assert rows[0][0] in {"BODY", "CONCLUSION"}
    assert rows[0][1] == 5


def test_student_activity_summary_is_read_only_and_scoped(tmp_path):
    app = new_test_app(tmp_path)
    store = new_test_store(app)
    teacher_a = create_teacher(store, "summary_teacher_a")
    teacher_b = create_teacher(store, "summary_teacher_b")
    classroom_a, assignment_a = create_classroom_assignment(
        store, teacher_a, "English 401", "A"
    )
    classroom_b, assignment_b = create_classroom_assignment(
        store, teacher_b, "English 402", "B"
    )
    writer = enroll_student(app, classroom_a, "summary_writer")
    other = enroll_student(app, classroom_a, "summary_other")
    outsider = enroll_student(app, classroom_b, "summary_outsider")
    session_id = start_workspace(writer, assignment_a)
    assert post_activity(
        writer, assignment_a, session_id, activity_events("INTRODUCTION", 3)
    ).status_code == 200
    assert post_activity(
        writer, assignment_a, session_id, activity_events("BODY", 2, offset=20)
    ).status_code == 200

    own = writer.get(
        f"/api/writing-activity?assignment_id={assignment_a['assignment_id']}"
    )
    assert own.status_code == 200
    assert own.get_json() == {"recorded_seconds": 25, "tracking_enabled": True}

    no_records = other.get(
        f"/api/writing-activity?assignment_id={assignment_a['assignment_id']}"
    )
    assert no_records.status_code == 200
    assert no_records.get_json()["recorded_seconds"] is None

    assert outsider.get(
        f"/api/writing-activity?assignment_id={assignment_a['assignment_id']}"
    ).status_code == 404
    assert writer.get(
        f"/api/writing-activity?assignment_id={assignment_b['assignment_id']}"
    ).status_code == 404
    assert writer.get("/api/writing-activity?assignment_id=invalid").status_code == 400
    assert writer.get("/api/writing-activity").status_code == 400

    teacher_client = app.test_client()
    assert login_student(
        teacher_client, "summary_teacher_a", "teacher-password-1"
    ).status_code == 302
    assert teacher_client.get(
        f"/api/writing-activity?assignment_id={assignment_a['assignment_id']}"
    ).status_code == 403

    anonymous = app.test_client()
    anonymous.get("/login")
    assert anonymous.get(
        f"/api/writing-activity?assignment_id={assignment_a['assignment_id']}"
    ).status_code == 401


def test_activity_summary_does_not_create_schema_when_tracking_is_disabled(tmp_path):
    app = new_test_app(tmp_path, activity_enabled=False)
    store = new_test_store(app)
    teacher = create_teacher(store)
    classroom, assignment = create_classroom_assignment(store, teacher)
    student = enroll_student(app, classroom, "disabled_writer")
    start_workspace(student, assignment)

    response = student.get(
        f"/api/writing-activity?assignment_id={assignment['assignment_id']}"
    )
    assert response.status_code == 200
    assert response.get_json() == {"recorded_seconds": None, "tracking_enabled": False}

    with sqlite3.connect(app.config["DRAFT_DATABASE_PATH"]) as connection:
        table = connection.execute(
            "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'writing_activity'"
        ).fetchone()
    assert table is None
