"""Minimal localhost Flask interface for the three writing stages."""

import logging
import hmac
import os
import re
import secrets
import sqlite3
from time import perf_counter
from datetime import timedelta
from pathlib import Path
from typing import Any

from flask import Flask, flash, g, jsonify, redirect, render_template, request, send_file, session, url_for
from werkzeug.exceptions import RequestEntityTooLarge
from werkzeug.security import check_password_hash, generate_password_hash

from services.essay_analysis_service import EssayAnalysisService
from services.tutoring_lessons import load_introduction_lesson, load_feedback_help
from services.draft_store import (
    AssignmentNotFoundError,
    AssignmentDeletedError,
    AssignmentLockedError,
    AlreadySubmittedError,
    ClassroomNotFoundError,
    DraftNotFoundError,
    DraftStore,
    DuplicateEnrollmentError,
    IncompleteEssayError,
    SubmittedAssignmentError,
    UnsavedDraftError,
    WRITING_ACTIVITY_MAX_EVENTS_PER_REQUEST,
)


MAX_TOPIC_LENGTH = 500
MAX_INTRODUCTION_LENGTH = 12_000
MAX_BODY_LENGTH = 30_000
MAX_CONCLUSION_LENGTH = 12_000
MAX_FOCUS_TERMS = 20
MAX_FOCUS_TERM_LENGTH = 120
USERNAME_PATTERN = re.compile(r"[A-Za-z0-9_]{3,32}\Z")
MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_LENGTH = 128
MAX_ASSIGNMENT_TITLE_LENGTH = 120
MAX_ASSIGNMENT_INSTRUCTIONS_LENGTH = 4000
STAGE_TEXT_FIELDS = {
    "INTRODUCTION": "introduction_text",
    "BODY": "body_text",
    "CONCLUSION": "conclusion_text",
}


def _persistent_secret_key(instance_path: str) -> str:
    configured = os.environ.get("ESSAYSCAFF_SECRET_KEY")
    if configured:
        return configured

    key_path = Path(instance_path) / ".flask_secret_key"
    key_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with key_path.open("x", encoding="ascii") as key_file:
            key_file.write(secrets.token_hex(32))
    except FileExistsError:
        pass
    key = key_path.read_text(encoding="ascii").strip()
    if not key:
        raise RuntimeError("The persistent Flask secret key file is empty")
    if os.name != "nt":
        key_path.chmod(0o600)
    return key


def create_app(analysis_service: Any | None = None, secret_key: str | None = None) -> Flask:
    """Create the Flask app; construct NLP services only when first needed."""
    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = 256 * 1024
    app.secret_key = secret_key or _persistent_secret_key(app.instance_path)
    app.config.update(
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        # This prototype runs over localhost HTTP; enable Secure when served over HTTPS.
        SESSION_COOKIE_SECURE=os.environ.get("ESSAYSCAFF_COOKIE_SECURE") == "1",
        PERMANENT_SESSION_LIFETIME=timedelta(hours=8),
        WRITING_ACTIVITY_ENABLED=(
            os.environ.get("ESSAYSCAFF_ENABLE_WRITING_ACTIVITY") == "1"
        ),
        ANALYSIS_SERVICE_INITIALIZATION_MS=None,
        ANALYSIS_SERVICE_INITIALIZATION_STATUS=(
            "PRECONSTRUCTED_NOT_INSTRUMENTED" if analysis_service is not None else "NOT_YET_INITIALIZED"
        ),
    )
    app.config["ANALYSIS_SERVICE"] = analysis_service
    app.config["DRAFT_DATABASE_PATH"] = f"{app.instance_path}/essay_scaff_drafts.sqlite3"
    draft_stores: dict[str, DraftStore] = {}

    def get_analysis_service() -> Any:
        service = app.config["ANALYSIS_SERVICE"]
        if service is None:
            initialization_started = perf_counter()
            service = EssayAnalysisService()
            app.config["ANALYSIS_SERVICE"] = service
            app.config["ANALYSIS_SERVICE_INITIALIZATION_MS"] = (
                perf_counter() - initialization_started
            ) * 1000
            app.config["ANALYSIS_SERVICE_INITIALIZATION_STATUS"] = "EXECUTED"
        return service

    def get_draft_store() -> DraftStore:
        database_path = str(app.config["DRAFT_DATABASE_PATH"])
        if database_path not in draft_stores:
            draft_stores[database_path] = DraftStore(
                database_path,
                enable_activity_tracking=bool(
                    app.config["WRITING_ACTIVITY_ENABLED"]
                ),
            )
        return draft_stores[database_path]

    def assignment_from_payload(payload: dict[str, Any]):
        assignment_id = payload.get("assignment_id")
        if assignment_id is None:
            return None, None
        if not _valid_record_id(assignment_id):
            raise ValueError("The assignment ID is invalid.")
        assignment = get_draft_store().get_available_assignment(
            g.current_user["user_id"], assignment_id
        )
        if assignment is None:
            raise AssignmentNotFoundError(assignment_id)
        return assignment_id, assignment

    def csrf_token() -> str:
        token = session.get("_csrf_token")
        if not isinstance(token, str):
            token = secrets.token_urlsafe(32)
            session["_csrf_token"] = token
        return token

    def begin_user_session(user: dict[str, Any]) -> None:
        session.clear()
        session["user_id"] = user["user_id"]
        session["_csrf_token"] = secrets.token_urlsafe(32)
        session.permanent = True

    @app.before_request
    def require_account():
        if request.endpoint in {
            "login",
            "register",
            "authenticate_student",
            "create_account",
            "brand_logo",
            "static",
        }:
            return None
        user_id = session.get("user_id")
        if user_id is None:
            if request.path.startswith("/api/"):
                return jsonify(error="Log in to access your writing."), 401
            return redirect(url_for("login"))
        try:
            user_id = int(user_id)
            if not _valid_record_id(user_id):
                raise ValueError("Invalid stored account identity")
        except (TypeError, ValueError):
            session.clear()
            return jsonify(error="Your login session has expired. Log in again."), 401
        try:
            user = get_draft_store().get_user(user_id)
        except (OSError, sqlite3.Error):
            app.logger.exception("Student login session could not be checked")
            return jsonify(error="Account storage is temporarily unavailable. Please try again."), 503
        if user is None or user["role"] not in {"STUDENT", "TEACHER"}:
            session.clear()
            if request.path.startswith("/api/"):
                return jsonify(error="Your login session has expired. Log in again."), 401
            return redirect(url_for("login"))
        g.current_user = user
        student_endpoints = {
            "analyze_introduction", "analyze_stage", "save_draft", "restore_draft",
            "save_revision", "list_revisions", "view_revision", "available_assignments",
            "assignment_workspace", "student_classrooms", "enroll_student",
            "classroom_assignments", "submit_assignment", "student_submission",
            "student_archived_assignments", "record_writing_activity",
            "read_writing_activity",
        }
        teacher_endpoints = {
            "teacher_dashboard", "create_classroom", "create_assignment", "assign_legacy_assignment",
            "edit_assignment", "delete_assignment",
            "teacher_assignment_submissions", "teacher_submission_view",
            "research_inspector", "research_inspector_metadata", "analyze_research_inspector",
        }
        if request.endpoint in student_endpoints and user["role"] != "STUDENT":
            if request.path.startswith("/api/"):
                return jsonify(error="This action is available to student accounts only."), 403
            return "This page is available to student accounts only.", 403
        if request.endpoint in teacher_endpoints and user["role"] != "TEACHER":
            if request.path.startswith("/api/"):
                return jsonify(error="This action is available to teacher accounts only."), 403
            return "This page is available to teacher accounts only.", 403
        # Werkzeug's int converter accepts integers wider than SQLite INTEGER.
        # Deny invalid URL identifiers before binding them in any store query.
        if any(not _valid_record_id(value) for key, value in (request.view_args or {}).items()
               if key in {"assignment_id", "classroom_id", "submission_id"}):
            if request.path.startswith("/api/"):
                return jsonify(error="The record ID is invalid."), 400
            return "Record not found.", 404
        return None

    @app.before_request
    def require_csrf_token():
        if request.method not in {"POST", "PUT", "PATCH", "DELETE"}:
            return None
        expected = session.get("_csrf_token")
        supplied = (
            request.headers.get("X-CSRF-Token")
            if request.is_json
            else request.form.get("csrf_token") or request.headers.get("X-CSRF-Token")
        )
        if not isinstance(expected, str) or not isinstance(supplied, str) or not hmac.compare_digest(expected, supplied):
            message = "Your form could not be verified. Reload the page and try again."
            if request.is_json or request.path.startswith("/api/"):
                return jsonify(error=message), 400
            return message, 400
        return None

    @app.get("/assets/essayscaff-logo.png")
    def brand_logo():
        logo_path = Path(app.root_path) / "75fda169-d79c-4c1f-8efe-fc23bd0267f0.png"
        return send_file(logo_path, mimetype="image/png", conditional=True)

    @app.get("/register")
    def register():
        if session.get("user_id"):
            return redirect(url_for("homepage"))
        return render_template("register.html", csrf_token=csrf_token(), error=None)

    @app.post("/register")
    def create_account():
        username = request.form.get("username", "").strip()
        role = request.form.get("role", "STUDENT").strip().upper()
        password = request.form.get("password", "")
        confirmation = request.form.get("confirm_password", "")
        error = None
        if USERNAME_PATTERN.fullmatch(username) is None:
            error = "Username must be 3–32 characters using letters, numbers, or underscores."
        elif role not in {"STUDENT", "TEACHER"}:
            error = "Choose Student or Teacher as your account type."
        elif not MIN_PASSWORD_LENGTH <= len(password) <= MAX_PASSWORD_LENGTH:
            error = f"Password must be between {MIN_PASSWORD_LENGTH} and {MAX_PASSWORD_LENGTH} characters."
        elif password != confirmation:
            error = "The password and confirmation do not match."
        if error:
            return render_template("register.html", csrf_token=csrf_token(), error=error), 400

        try:
            user = get_draft_store().create_user(
                username, generate_password_hash(password), role
            )
        except sqlite3.IntegrityError:
            return render_template(
                "register.html", csrf_token=csrf_token(), error="That username is already in use."
            ), 409
        except (OSError, sqlite3.Error):
            app.logger.exception("Account could not be created")
            return render_template(
                "register.html", csrf_token=csrf_token(), error="Account could not be created. Please try again."
            ), 500
        begin_user_session(user)
        return redirect(url_for("homepage"))

    @app.get("/login")
    def login():
        if session.get("user_id"):
            return redirect(url_for("homepage"))
        return render_template("login.html", csrf_token=csrf_token(), error=None)

    @app.post("/login")
    def authenticate_student():
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        try:
            user = get_draft_store().get_user_for_login(username)
        except (OSError, sqlite3.Error):
            app.logger.exception("Student login could not be checked")
            return render_template(
                "login.html", csrf_token=csrf_token(), error="Login could not be completed. Please try again."
            ), 500
        if user is None or user["role"] not in {"STUDENT", "TEACHER"} or not check_password_hash(user["password_hash"], password):
            return render_template(
                "login.html", csrf_token=csrf_token(), error="Incorrect username or password."
            ), 401
        begin_user_session(user)
        return redirect(url_for("homepage"))

    @app.post("/logout")
    def logout():
        session.clear()
        return redirect(url_for("login"))

    @app.get("/account")
    def account_settings():
        return render_template(
            "account.html",
            username=g.current_user["username"],
            role=g.current_user["role"],
            csrf_token=csrf_token(),
            error=None,
        )

    @app.post("/account/delete")
    def delete_account():
        username = g.current_user["username"]
        role = g.current_user["role"]
        password = request.form.get("password", "")
        confirmed = request.form.get("confirm_delete") == "yes"
        if not confirmed:
            return render_template(
                "account.html", username=username, role=role,
                csrf_token=csrf_token(), error="Confirm the deletion checkbox to continue.",
            ), 400
        try:
            user = get_draft_store().get_user_for_login(username)
        except (OSError, sqlite3.Error):
            app.logger.exception("Account could not be verified for deletion")
            return render_template(
                "account.html", username=username, role=role,
                csrf_token=csrf_token(), error="Account storage is temporarily unavailable. Please try again.",
            ), 503
        if user is None or not check_password_hash(user["password_hash"], password):
            return render_template(
                "account.html", username=username, role=role,
                csrf_token=csrf_token(), error="The current password is incorrect.",
            ), 400
        try:
            get_draft_store().delete_user_and_linked_records(g.current_user["user_id"])
        except KeyError:
            session.clear()
            return redirect(url_for("login"))
        except (OSError, sqlite3.Error):
            app.logger.exception("Account and linked records could not be deleted")
            return render_template(
                "account.html", username=username, role=role,
                csrf_token=csrf_token(), error="The account could not be deleted. No linked records were removed.",
            ), 500
        session.clear()
        flash("Your account and its associated records were permanently deleted.", "success")
        return redirect(url_for("login"))

    @app.get("/")
    def homepage():
        if g.current_user["role"] == "TEACHER":
            return redirect(url_for("teacher_dashboard"))
        return render_template(
            "index.html",
            csrf_token=csrf_token(),
            username=g.current_user["username"],
            assignment_mode=False,
            assignment_title="",
            assignment_instructions="",
            introduction_lesson=load_introduction_lesson(),
            feedback_help=load_feedback_help(),
        )

    @app.get("/teacher")
    def teacher_dashboard():
        try:
            store = get_draft_store()
            classrooms = store.list_teacher_classrooms(g.current_user["user_id"])
            all_assignments = []
            student_ids = set()
            student_progress = []
            submitted_essays = 0
            for classroom in classrooms:
                classroom["students"] = store.list_teacher_classroom_students(
                    g.current_user["user_id"], classroom["classroom_id"]
                )
                student_ids.update(student["user_id"] for student in classroom["students"])
                classroom["assignments"] = store.list_teacher_classroom_assignments(
                    g.current_user["user_id"], classroom["classroom_id"]
                )
                for assignment in classroom["assignments"]:
                    assignment["progress"] = store.assignment_progress(
                        g.current_user["user_id"], assignment["assignment_id"]
                    )
                    assignment["submissions"] = store.list_teacher_submissions(
                        g.current_user["user_id"], assignment["assignment_id"]
                    )
                    assignment["classroom_name"] = classroom["classroom_name"]
                    assignment["section"] = classroom["section"]
                    assignment["has_student_work"] = store.assignment_has_student_work(
                        assignment["assignment_id"]
                    )
                    all_assignments.append(assignment)
                    submitted_essays += len(assignment["submissions"])
                    submitted_by_student = {
                        item["username"]: item for item in assignment["submissions"]
                    }
                    for progress in assignment["progress"]:
                        submitted = submitted_by_student.get(progress["username"])
                        student_progress.append(
                            {
                                "username": progress["username"],
                                "assignment_title": assignment["title"],
                                "classroom_name": classroom["classroom_name"],
                                "status": progress["progress"],
                                "stages": progress["stages"],
                                "submitted_at": submitted["submitted_at"] if submitted else None,
                                "submission_id": submitted["submission_id"] if submitted else None,
                            }
                        )
            unassigned_assignments = store.list_unassigned_teacher_assignments(
                g.current_user["user_id"]
            )
            for assignment in unassigned_assignments:
                assignment["classroom_name"] = "Unassigned"
                assignment["section"] = ""
                assignment["progress"] = []
                assignment["submissions"] = []
                assignment["has_student_work"] = store.assignment_has_student_work(
                    assignment["assignment_id"]
                )
                all_assignments.append(assignment)
            deleted_assignments = store.list_teacher_deleted_assignments(
                g.current_user["user_id"]
            )
            stats = {
                "classrooms": len(classrooms),
                "students": len(student_ids),
                "assignments": len(all_assignments),
                "submissions": submitted_essays,
            }
        except (OSError, sqlite3.Error):
            app.logger.exception("Teacher assignments could not be loaded")
            classrooms = []
            unassigned_assignments = []
            deleted_assignments = []
            all_assignments = []
            student_progress = []
            stats = {"classrooms": 0, "students": 0, "assignments": 0, "submissions": 0}
            error = "Assignments could not be loaded. Please try again."
        else:
            error = None
        return render_template(
            "teacher.html",
            username=g.current_user["username"],
            csrf_token=csrf_token(),
            classrooms=classrooms,
            unassigned_assignments=unassigned_assignments,
            deleted_assignments=deleted_assignments,
            all_assignments=all_assignments,
            student_progress=student_progress,
            stats=stats,
            initial_view="dashboard",
            error=error,
        )

    @app.get("/teacher/research-inspector")
    def research_inspector():
        return render_template(
            "research_inspector.html",
            username=g.current_user["username"],
            csrf_token=csrf_token(),
        )

    @app.get("/api/research-inspector/metadata")
    def research_inspector_metadata():
        from services.research_inspector import inspector_metadata

        try:
            service = get_analysis_service()
            result = inspector_metadata(service.nlp_service)
            result["runtime"]["analysis_service_initialization"] = {
                "status": app.config.get("ANALYSIS_SERVICE_INITIALIZATION_STATUS"),
                "duration_ms": app.config.get("ANALYSIS_SERVICE_INITIALIZATION_MS"),
                "note": "Model/service construction is timed only when Flask creates the service lazily; injected preconstructed services are not timed here.",
            }
            return jsonify(result)
        except Exception:
            app.logger.exception("Research Inspector metadata could not be loaded")
            return jsonify(error="Research Inspector metadata could not be loaded."), 500

    @app.post("/teacher/classrooms")
    def create_classroom():
        name = request.form.get("classroom_name", "").strip()
        subject = request.form.get("subject", "").strip()
        section = request.form.get("section", "").strip()
        error = None
        if not name or len(name) > 120:
            error = "Enter a classroom name of 1–120 characters."
        elif not subject or len(subject) > 120:
            error = "Enter a subject of 1–120 characters."
        elif not section or len(section) > 80:
            error = "Enter a section of 1–80 characters."
        if error:
            return teacher_dashboard_with_error(error, "classrooms"), 400
        try:
            get_draft_store().create_classroom(
                g.current_user["user_id"], name, subject, section
            )
        except (OSError, sqlite3.Error):
            app.logger.exception("Classroom could not be created")
            return teacher_dashboard_with_error("Classroom could not be created. Please try again.", "classrooms"), 500
        return redirect(url_for("teacher_dashboard"))

    @app.post("/teacher/assignments")
    def create_assignment():
        classroom_value = request.form.get("classroom_id", "")
        title = request.form.get("title", "").strip()
        topic = request.form.get("topic", "").strip()
        instructions = request.form.get("instructions", "").strip()
        focus_terms = request.form.get("focus_terms", "").strip()
        error = None
        if not title or len(title) > MAX_ASSIGNMENT_TITLE_LENGTH:
            error = f"Enter an Assignment Title of 1–{MAX_ASSIGNMENT_TITLE_LENGTH} characters."
        elif re.fullmatch(r"[0-9]{1,10}", classroom_value) is None or int(classroom_value) < 1:
            error = "Choose one of your classrooms for this assignment."
        elif not topic or len(topic) > MAX_TOPIC_LENGTH:
            error = f"Enter a Writing Topic of 1–{MAX_TOPIC_LENGTH} characters."
        elif not instructions or len(instructions) > MAX_ASSIGNMENT_INSTRUCTIONS_LENGTH:
            error = f"Enter Instructions of 1–{MAX_ASSIGNMENT_INSTRUCTIONS_LENGTH} characters."
        elif len(focus_terms) > 2400:
            error = "Topic Focus Terms must be 2400 characters or fewer."
        else:
            focus_validation = _parse_focus_terms(focus_terms)
            if isinstance(focus_validation, str):
                error = focus_validation
        if error:
            return teacher_dashboard_with_error(error, "assignments"), 400
        try:
            get_draft_store().create_assignment(
                g.current_user["user_id"], int(classroom_value), title, topic, instructions, focus_terms
            )
        except ClassroomNotFoundError:
            return teacher_dashboard_with_error("Choose one of your classrooms for this assignment.", "assignments"), 404
        except sqlite3.Error:
            app.logger.exception("Assignment could not be created")
            return teacher_dashboard_with_error("Assignment could not be created. Please try again.", "assignments"), 500
        return redirect(url_for("teacher_dashboard"))

    @app.route("/teacher/assignments/<int:assignment_id>/edit", methods=["GET", "POST"])
    def edit_assignment(assignment_id: int):
        try:
            store = get_draft_store()
            assignment = store.get_teacher_assignment_for_edit(
                g.current_user["user_id"], assignment_id
            )
        except (OSError, sqlite3.Error):
            app.logger.exception("Assignment could not be loaded for editing")
            return "Assignment storage is temporarily unavailable. Please try again.", 503
        if assignment is None:
            return "Assignment not found.", 404
        if request.method in {"GET", "HEAD"}:
            return render_template(
                "teacher_edit_assignment.html",
                username=g.current_user["username"],
                csrf_token=csrf_token(),
                assignment=assignment,
                values=assignment,
                error=None,
            )

        values = {
            key: request.form.get(key, assignment[key]).strip()
            for key in ("title", "topic", "instructions", "focus_terms")
        }
        error = None
        if not values["title"] or len(values["title"]) > MAX_ASSIGNMENT_TITLE_LENGTH:
            error = f"Enter an Assignment Title of 1–{MAX_ASSIGNMENT_TITLE_LENGTH} characters."
        elif not values["topic"] or len(values["topic"]) > MAX_TOPIC_LENGTH:
            error = f"Enter a Writing Topic of 1–{MAX_TOPIC_LENGTH} characters."
        elif not values["instructions"] or len(values["instructions"]) > MAX_ASSIGNMENT_INSTRUCTIONS_LENGTH:
            error = f"Enter Instructions of 1–{MAX_ASSIGNMENT_INSTRUCTIONS_LENGTH} characters."
        elif len(values["focus_terms"]) > 2400:
            error = "Topic Focus Terms must be 2400 characters or fewer."
        else:
            focus_validation = _parse_focus_terms(values["focus_terms"])
            if isinstance(focus_validation, str):
                error = focus_validation
        if error:
            return render_template(
                "teacher_edit_assignment.html",
                username=g.current_user["username"], csrf_token=csrf_token(),
                assignment=assignment, values=values, error=error,
            ), 400
        try:
            store.update_assignment(
                g.current_user["user_id"], assignment_id,
                values["title"], values["topic"], values["instructions"], values["focus_terms"],
            )
        except AssignmentLockedError:
            assignment = store.get_teacher_assignment_for_edit(
                g.current_user["user_id"], assignment_id
            )
            return render_template(
                "teacher_edit_assignment.html",
                username=g.current_user["username"], csrf_token=csrf_token(),
                assignment=assignment, values=assignment,
                error="Students already have work for this assignment. Only the title can be changed.",
            ), 409
        except (AssignmentNotFoundError, AssignmentDeletedError):
            return "Assignment not found.", 404
        except sqlite3.Error:
            app.logger.exception("Assignment could not be updated")
            return render_template(
                "teacher_edit_assignment.html",
                username=g.current_user["username"], csrf_token=csrf_token(),
                assignment=assignment, values=values,
                error="Assignment could not be updated. Please try again.",
            ), 500
        flash("Assignment updated successfully.", "success")
        return redirect(url_for("teacher_dashboard"))

    @app.post("/teacher/assignments/<int:assignment_id>/delete")
    def delete_assignment(assignment_id: int):
        try:
            get_draft_store().soft_delete_assignment(
                g.current_user["user_id"], assignment_id
            )
        except AssignmentNotFoundError:
            return "Assignment not found.", 404
        except sqlite3.Error:
            app.logger.exception("Assignment could not be archived")
            return teacher_dashboard_with_error(
                "Assignment could not be archived. Please try again.", "assignments"
            ), 500
        flash(
            "Assignment deleted from active classrooms. Existing student drafts, revisions, and submissions are retained.",
            "success",
        )
        return redirect(url_for("teacher_dashboard"))

    def teacher_dashboard_with_error(error: str, initial_view: str = "dashboard"):
        store = get_draft_store()
        classrooms = store.list_teacher_classrooms(g.current_user["user_id"])
        all_assignments = []
        student_ids = set()
        student_progress = []
        submitted_essays = 0
        for classroom in classrooms:
            classroom["students"] = store.list_teacher_classroom_students(
                g.current_user["user_id"], classroom["classroom_id"]
            )
            student_ids.update(student["user_id"] for student in classroom["students"])
            classroom["assignments"] = store.list_teacher_classroom_assignments(
                g.current_user["user_id"], classroom["classroom_id"]
            )
            for assignment in classroom["assignments"]:
                assignment["progress"] = store.assignment_progress(
                    g.current_user["user_id"], assignment["assignment_id"]
                )
                assignment["submissions"] = store.list_teacher_submissions(
                    g.current_user["user_id"], assignment["assignment_id"]
                )
                assignment["has_student_work"] = store.assignment_has_student_work(
                    assignment["assignment_id"]
                )
                assignment["classroom_name"] = classroom["classroom_name"]
                assignment["section"] = classroom["section"]
                all_assignments.append(assignment)
                submitted_essays += len(assignment["submissions"])
                submitted_by_student = {item["username"]: item for item in assignment["submissions"]}
                for progress in assignment["progress"]:
                    submitted = submitted_by_student.get(progress["username"])
                    student_progress.append({
                        "username": progress["username"],
                        "assignment_title": assignment["title"],
                        "classroom_name": classroom["classroom_name"],
                        "status": progress["progress"],
                        "stages": progress["stages"],
                        "submitted_at": submitted["submitted_at"] if submitted else None,
                        "submission_id": submitted["submission_id"] if submitted else None,
                    })
        unassigned_assignments = store.list_unassigned_teacher_assignments(g.current_user["user_id"])
        for assignment in unassigned_assignments:
            assignment.update(classroom_name="Unassigned", section="", progress=[], submissions=[])
            assignment["has_student_work"] = store.assignment_has_student_work(assignment["assignment_id"])
            all_assignments.append(assignment)
        return render_template(
            "teacher.html", username=g.current_user["username"], csrf_token=csrf_token(),
            classrooms=classrooms,
            unassigned_assignments=unassigned_assignments,
            deleted_assignments=store.list_teacher_deleted_assignments(g.current_user["user_id"]),
            all_assignments=all_assignments,
            student_progress=student_progress,
            stats={
                "classrooms": len(classrooms),
                "students": len(student_ids),
                "assignments": len(all_assignments),
                "submissions": submitted_essays,
            },
            initial_view=initial_view,
            error=error,
        )

    @app.post("/teacher/assignments/<int:assignment_id>/classroom")
    def assign_legacy_assignment(assignment_id: int):
        classroom_value = request.form.get("classroom_id", "")
        if re.fullmatch(r"[0-9]{1,10}", classroom_value) is None or int(classroom_value) < 1:
            return teacher_dashboard_with_error("Choose one of your classrooms.", "assignments"), 400
        try:
            get_draft_store().assign_existing_assignment_to_classroom(
                g.current_user["user_id"], assignment_id, int(classroom_value)
            )
        except (AssignmentNotFoundError, ClassroomNotFoundError):
            return teacher_dashboard_with_error("That unassigned item or classroom was not found.", "assignments"), 404
        except sqlite3.Error:
            app.logger.exception("Legacy assignment could not be assigned to a classroom")
            return teacher_dashboard_with_error("Assignment could not be assigned. Please try again.", "assignments"), 500
        return redirect(url_for("teacher_dashboard"))

    @app.get("/api/assignments")
    def available_assignments():
        try:
            assignments = get_draft_store().list_available_assignments(g.current_user["user_id"])
            return jsonify(assignments=assignments)
        except (OSError, sqlite3.Error):
            app.logger.exception("Available assignments could not be loaded")
            return jsonify(error="Assignments could not be loaded. Please try again."), 500

    @app.get("/api/student-history")
    def student_history():
        try:
            assignments = get_draft_store().list_student_history(
                g.current_user["user_id"]
            )
            return jsonify(assignments=assignments)
        except (OSError, sqlite3.Error):
            app.logger.exception("Student history could not be loaded")
            return jsonify(error="Student history could not be loaded. Please try again."), 500

    @app.get("/api/classrooms")
    def student_classrooms():
        try:
            classrooms = get_draft_store().list_student_classrooms(g.current_user["user_id"])
            return jsonify(classrooms=classrooms)
        except (OSError, sqlite3.Error):
            app.logger.exception("Student classrooms could not be loaded")
            return jsonify(error="Classrooms could not be loaded. Please try again."), 500

    @app.post("/api/classroom-enrollments")
    def enroll_student():
        if not request.is_json:
            return jsonify(error="Send the enrollment code as JSON."), 400
        payload = request.get_json(silent=True)
        code = payload.get("enrollment_code") if isinstance(payload, dict) else None
        if not isinstance(code, str) or not 6 <= len(code.strip()) <= 32:
            return jsonify(error="Enter a valid classroom enrollment code."), 400
        try:
            classroom = get_draft_store().join_classroom(
                g.current_user["user_id"], code.strip()
            )
            return jsonify(
                classroom={key: classroom[key] for key in (
                    "classroom_id", "classroom_name", "subject", "section"
                )}
            )
        except ClassroomNotFoundError:
            return jsonify(error="That enrollment code was not found."), 404
        except DuplicateEnrollmentError:
            return jsonify(error="You have already joined that classroom."), 409
        except sqlite3.Error:
            app.logger.exception("Classroom enrollment failed")
            return jsonify(error="You could not join the classroom. Please try again."), 500

    @app.get("/api/classrooms/<int:classroom_id>/assignments")
    def classroom_assignments(classroom_id: int):
        try:
            assignments = get_draft_store().list_classroom_assignments_for_student(
                g.current_user["user_id"], classroom_id
            )
            return jsonify(assignments=assignments)
        except ClassroomNotFoundError:
            return jsonify(error="That classroom is not available to this student."), 404
        except sqlite3.Error:
            app.logger.exception("Classroom assignments could not be loaded")
            return jsonify(error="Assignments could not be loaded. Please try again."), 500

    @app.get("/api/assignments/<int:assignment_id>/workspace")
    def assignment_workspace(assignment_id: int):
        try:
            workspace = get_draft_store().get_or_create_assignment_workspace(
                g.current_user["user_id"], assignment_id
            )
            assignment = workspace["assignment"]
            draft = workspace["draft"]
            return jsonify(
                assignment={
                    key: assignment[key]
                    for key in (
                        "assignment_id", "classroom_id", "classroom_name", "subject", "section",
                        "title", "topic", "instructions", "focus_terms", "created_at", "deleted_at",
                    )
                },
                draft={
                    key: draft[key]
                    for key in (
                        "session_id", "assignment_topic", "focus_terms", "introduction_text",
                        "body_text", "conclusion_text", "created_at", "updated_at",
                    )
                },
                draft_version=get_draft_store().draft_version(draft),
                activity_tracking_enabled=bool(
                    app.config["WRITING_ACTIVITY_ENABLED"]
                ),
                submission=(
                    {
                        key: workspace["submission"][key]
                        for key in (
                            "submission_id", "submitted_at", "introduction_snapshot",
                            "body_snapshot", "conclusion_snapshot",
                        )
                    }
                    if workspace["submission"] is not None
                    else None
                ),
            )
        except AssignmentNotFoundError:
            return jsonify(error="That assignment was not found."), 404
        except AssignmentDeletedError:
            return jsonify(error="This assignment was deleted and has no saved work to restore."), 410
        except (OSError, sqlite3.Error):
            app.logger.exception("Assignment workspace could not be opened")
            return jsonify(error="Assignment could not be opened. Please try again."), 500

    @app.post("/api/submissions")
    def submit_assignment():
        if not request.is_json:
            return jsonify(error="Send the submission request as JSON."), 400
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return jsonify(error="The request must contain a JSON object."), 400
        assignment_id = payload.get("assignment_id")
        session_id = payload.get("session_id")
        draft_version = payload.get("draft_version")
        if not _valid_record_id(assignment_id):
            return jsonify(error="Choose a valid classroom assignment."), 400
        if not _valid_session_id(session_id):
            return jsonify(error="The writing session is invalid."), 400
        if not isinstance(draft_version, str) or re.fullmatch(r"[0-9a-f]{64}", draft_version) is None:
            return jsonify(error="Save your latest draft before submitting."), 409
        try:
            submission = get_draft_store().create_submission(
                g.current_user["user_id"], assignment_id, session_id, draft_version
            )
            return jsonify(
                submission_id=submission["submission_id"],
                assignment_id=submission["assignment_id"],
                session_id=submission["session_id"],
                submitted_at=submission["submitted_at"],
                introduction_snapshot=submission["introduction_snapshot"],
                body_snapshot=submission["body_snapshot"],
                conclusion_snapshot=submission["conclusion_snapshot"],
            )
        except (DraftNotFoundError, AssignmentNotFoundError):
            return jsonify(error="That writing session is not available for this assignment."), 404
        except AssignmentDeletedError:
            return jsonify(error="This assignment was deleted and cannot accept submissions."), 409
        except IncompleteEssayError:
            return jsonify(error="Write and save the Introduction, Body, and Conclusion before submitting."), 400
        except UnsavedDraftError:
            return jsonify(error="The saved draft changed. Save the latest writing before submitting."), 409
        except AlreadySubmittedError:
            return jsonify(error="This assignment has already been submitted."), 409
        except (OSError, sqlite3.Error):
            app.logger.exception("Essay submission could not be saved")
            return jsonify(error="Essay could not be submitted. Please try again."), 500

    @app.get("/api/submissions/<int:assignment_id>")
    def student_submission(assignment_id: int):
        try:
            submission = get_draft_store().get_student_submission(
                g.current_user["user_id"], assignment_id
            )
            if submission is None:
                return jsonify(error="No submitted essay was found for this assignment."), 404
            return jsonify(submission)
        except (OSError, sqlite3.Error):
            app.logger.exception("Student submission could not be loaded")
            return jsonify(error="Submitted essay could not be loaded. Please try again."), 500

    @app.get("/teacher/assignments/<int:assignment_id>/submissions")
    def teacher_assignment_submissions(assignment_id: int):
        store = get_draft_store()
        try:
            assignment = store.get_assignment(assignment_id)
            if assignment is None or assignment["teacher_user_id"] != g.current_user["user_id"]:
                return "Assignment not found.", 404
            submissions = (
                store.list_teacher_submissions(g.current_user["user_id"], assignment_id)
                if assignment["classroom_id"] is not None
                else []
            )
            return render_template(
                "teacher_submissions.html",
                username=g.current_user["username"],
                csrf_token=csrf_token(),
                assignment=assignment,
                submissions=submissions,
            )
        except AssignmentNotFoundError:
            return "Assignment not found.", 404
        except (OSError, sqlite3.Error):
            app.logger.exception("Teacher submission list could not be loaded")
            return "Submissions could not be loaded. Please try again.", 500

    @app.get("/teacher/submissions/<int:submission_id>")
    def teacher_submission_view(submission_id: int):
        try:
            submission = get_draft_store().get_teacher_submission(
                g.current_user["user_id"], submission_id
            )
            if submission is None:
                return "Submission not found.", 404
            return render_template(
                "teacher_submission.html",
                username=g.current_user["username"],
                csrf_token=csrf_token(),
                submission=submission,
            )
        except (OSError, sqlite3.Error):
            app.logger.exception("Teacher submission could not be opened")
            return "Submission could not be opened. Please try again.", 500

    @app.post("/api/analyze-introduction")
    def analyze_introduction():
        if not request.is_json:
            return jsonify(error="Send the form data as JSON."), 400
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return jsonify(error="The request must contain a JSON object."), 400
        return analyze_payload(payload, "INTRODUCTION")

    @app.post("/api/analyze-stage")
    def analyze_stage():
        if not request.is_json:
            return jsonify(error="Send the form data as JSON."), 400
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return jsonify(error="The request must contain a JSON object."), 400
        stage_id = payload.get("stage_id")
        if not isinstance(stage_id, str) or stage_id not in STAGE_TEXT_FIELDS:
            return jsonify(error="Choose Introduction, Body, or Conclusion to analyze."), 400
        include_transparency_trace = payload.get("include_transparency_trace", False)
        if not isinstance(include_transparency_trace, bool):
            return jsonify(error="include_transparency_trace must be a boolean."), 400
        return analyze_payload(
            payload, stage_id, include_research_trace=include_transparency_trace
        )

    @app.post("/api/research-inspector/analyze")
    def analyze_research_inspector():
        if not request.is_json:
            return jsonify(error="Send the research sample as JSON."), 400
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return jsonify(error="The request must contain a JSON object."), 400
        stage_id = payload.get("stage_id")
        if not isinstance(stage_id, str) or stage_id not in STAGE_TEXT_FIELDS:
            return jsonify(error="Choose Introduction, Body, or Conclusion to analyze."), 400
        if any(key in payload for key in ("assignment_id", "session_id", "user_id")):
            return jsonify(error="Research samples cannot reference saved assignments or writing sessions."), 400
        return analyze_payload(payload, stage_id, research_inspector_request=True)

    @app.post("/api/drafts")
    def save_draft():
        if not request.is_json:
            return jsonify(error="Send the draft as JSON."), 400
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return jsonify(error="The request must contain a JSON object."), 400

        draft, validation_error = _validated_draft(payload)
        assignment_id = payload.get("assignment_id")
        assignment = None
        if assignment_id is not None:
            if not _valid_record_id(assignment_id):
                return jsonify(error="The assignment ID is invalid."), 400
            try:
                assignment = get_draft_store().get_available_assignment(
                    g.current_user["user_id"], assignment_id
                )
            except (OSError, sqlite3.Error):
                app.logger.exception("Assignment could not be loaded for draft saving")
                return jsonify(error="Assignment could not be loaded. Please try again."), 500
            if assignment is None:
                return jsonify(error="That assignment was not found."), 404
            payload = {
                **payload,
                "assignment_topic": assignment["topic"],
                "focus_terms": assignment["focus_terms"],
            }
            draft, validation_error = _validated_draft(payload)
        if validation_error:
            return jsonify(error=validation_error), 400

        session_id = payload.get("session_id")
        if session_id is not None and (
            not isinstance(session_id, str) or re.fullmatch(r"[0-9a-f]{32}", session_id) is None
        ):
            return jsonify(error="The writing session ID is invalid."), 400

        try:
            store = get_draft_store()
            if assignment_id is not None and session_id is None:
                session_id = store.get_or_create_assignment_workspace(
                    g.current_user["user_id"], assignment_id
                )["draft"]["session_id"]
            saved = store.save(draft, session_id, g.current_user["user_id"], assignment_id)
            return jsonify(
                session_id=saved["session_id"],
                updated_at=saved["updated_at"],
                draft_version=store.draft_version(saved),
            )
        except DraftNotFoundError:
            return jsonify(error="That writing session was not found. Start a new draft session."), 404
        except SubmittedAssignmentError:
            return jsonify(error="This assignment has been submitted and is read-only."), 409
        except AssignmentDeletedError:
            return jsonify(error="This assignment was deleted and is read-only."), 409
        except (OSError, sqlite3.Error):
            app.logger.exception("Draft could not be saved")
            return jsonify(error="Draft could not be saved. Please try again."), 500

    @app.get("/api/drafts")
    def restore_draft():
        session_id = request.args.get("session_id")
        if not session_id:
            return jsonify(error="A writing session ID is required."), 400
        if re.fullmatch(r"[0-9a-f]{32}", session_id) is None:
            return jsonify(error="The writing session ID is invalid."), 400
        try:
            draft = get_draft_store().get(session_id, g.current_user["user_id"])
            if draft is None:
                return jsonify(error="That writing session was not found."), 404
            return jsonify(draft)
        except (OSError, sqlite3.Error):
            app.logger.exception("Draft could not be restored")
            return jsonify(error="Draft could not be restored. Please try again."), 500

    @app.get("/api/writing-activity")
    def read_writing_activity():
        assignment_id = request.args.get("assignment_id", type=int)
        if not _valid_record_id(assignment_id):
            return jsonify(error="Choose a valid classroom assignment."), 400
        try:
            seconds = get_draft_store().get_writing_activity_seconds(
                g.current_user["user_id"], assignment_id
            )
            return jsonify(
                recorded_seconds=seconds,
                tracking_enabled=bool(app.config["WRITING_ACTIVITY_ENABLED"]),
            )
        except AssignmentNotFoundError:
            return jsonify(error="That assignment was not found."), 404
        except (OSError, sqlite3.Error):
            app.logger.exception("Writing activity could not be loaded")
            return jsonify(error="Recorded writing time could not be loaded."), 500

    @app.post("/api/writing-activity")
    def record_writing_activity():
        if not app.config["WRITING_ACTIVITY_ENABLED"]:
            return jsonify(
                error="Active writing time tracking is not enabled."
            ), 503
        if not request.is_json:
            return jsonify(error="Send the activity report as JSON."), 400
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return jsonify(error="The request must contain a JSON object."), 400
        assignment_id = payload.get("assignment_id")
        session_id = payload.get("session_id")
        events = payload.get("events")
        if not _valid_record_id(assignment_id):
            return jsonify(error="Choose a valid classroom assignment."), 400
        if not _valid_session_id(session_id):
            return jsonify(error="The writing session is invalid."), 400
        if (
            not isinstance(events, list)
            or not events
            or len(events) > WRITING_ACTIVITY_MAX_EVENTS_PER_REQUEST
        ):
            return jsonify(error="Send between 1 and 24 activity intervals."), 400
        try:
            result = get_draft_store().record_writing_activity(
                g.current_user["user_id"], assignment_id, session_id, events
            )
            return jsonify(recorded=result["recorded"])
        except ValueError as error:
            return jsonify(error=str(error)), 400
        except (DraftNotFoundError, AssignmentNotFoundError):
            return jsonify(error="That writing session is not available for this assignment."), 404
        except (AssignmentDeletedError, SubmittedAssignmentError):
            return jsonify(error="This assignment no longer accepts writing activity."), 409
        except (OSError, sqlite3.Error):
            app.logger.exception("Writing activity could not be recorded")
            return jsonify(error="Writing activity could not be saved."), 500

    @app.post("/api/revisions")
    def save_revision():
        if not request.is_json:
            return jsonify(error="Send the revision as JSON."), 400
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return jsonify(error="The request must contain a JSON object."), 400
        draft, validation_error = _validated_draft(payload)
        assignment_id = payload.get("assignment_id")
        assignment = None
        if assignment_id is not None:
            if not _valid_record_id(assignment_id):
                return jsonify(error="The assignment ID is invalid."), 400
            try:
                assignment = get_draft_store().get_available_assignment(
                    g.current_user["user_id"], assignment_id
                )
            except (OSError, sqlite3.Error):
                app.logger.exception("Assignment could not be loaded for revision saving")
                return jsonify(error="Assignment could not be loaded. Please try again."), 500
            if assignment is None:
                return jsonify(error="That assignment was not found."), 404
            payload = {
                **payload,
                "assignment_topic": assignment["topic"],
                "focus_terms": assignment["focus_terms"],
            }
            draft, validation_error = _validated_draft(payload)
        if validation_error:
            return jsonify(error=validation_error), 400
        session_id = payload.get("session_id")
        if session_id is not None and not _valid_session_id(session_id):
            return jsonify(error="The writing session ID is invalid."), 400

        try:
            store = get_draft_store()
            if assignment_id is not None and session_id is None:
                session_id = store.get_or_create_assignment_workspace(
                    g.current_user["user_id"], assignment_id
                )["draft"]["session_id"]
            saved = store.save_revision(
                draft, session_id, g.current_user["user_id"], assignment_id
            )
            revision = saved["revision"]
            return jsonify(
                session_id=saved["session"]["session_id"],
                revision_id=revision["revision_id"],
                revision_number=revision["revision_number"],
                created_at=revision["created_at"],
                created=saved["created"],
                updated_at=saved["session"]["updated_at"],
                draft_version=get_draft_store().draft_version(saved["session"]),
            )
        except DraftNotFoundError:
            return jsonify(error="That writing session was not found. Start a new draft session."), 404
        except SubmittedAssignmentError:
            return jsonify(error="This assignment has been submitted and is read-only."), 409
        except AssignmentDeletedError:
            return jsonify(error="This assignment was deleted and is read-only."), 409
        except (OSError, sqlite3.Error):
            app.logger.exception("Revision could not be saved")
            return jsonify(error="Revision could not be saved. Please try again."), 500

    @app.get("/api/revisions")
    def list_revisions():
        session_id = request.args.get("session_id")
        if not session_id:
            return jsonify(error="A writing session ID is required."), 400
        if not _valid_session_id(session_id):
            return jsonify(error="The writing session ID is invalid."), 400
        try:
            revisions = get_draft_store().list_revisions(session_id, g.current_user["user_id"])
            return jsonify(revisions=revisions)
        except DraftNotFoundError:
            return jsonify(error="That writing session was not found."), 404
        except (OSError, sqlite3.Error):
            app.logger.exception("Revision history could not be loaded")
            return jsonify(error="Revision history could not be loaded. Please try again."), 500

    @app.get("/api/revisions/<revision_id>")
    def view_revision(revision_id: str):
        session_id = request.args.get("session_id")
        if not session_id:
            return jsonify(error="A writing session ID is required."), 400
        if not _valid_session_id(session_id):
            return jsonify(error="The writing session ID is invalid."), 400
        if re.fullmatch(r"[0-9]{1,19}", revision_id) is None or not _valid_record_id(int(revision_id)):
            return jsonify(error="The revision ID is invalid."), 400
        try:
            revision = get_draft_store().get_revision(
                session_id, int(revision_id), g.current_user["user_id"]
            )
            if revision is None:
                return jsonify(error="That revision was not found for this writing session."), 404
            return jsonify(revision)
        except (OSError, sqlite3.Error):
            app.logger.exception("Revision could not be loaded")
            return jsonify(error="Revision could not be loaded. Please try again."), 500

    def compact_student_transparency_trace(
        trace: dict[str, Any], stage_id: str
    ) -> dict[str, Any]:
        """Drop student-response copies already present in the selected stage analysis."""
        compact = dict(trace)
        stages = dict(trace.get("stages", {}))
        stage_trace = stages.get(stage_id)
        if not isinstance(stage_trace, dict):
            return compact

        selected = dict(stage_trace)
        input_sections = selected.get("input_sections")
        if isinstance(input_sections, dict):
            input_sections = dict(input_sections)
            input_sections.pop(stage_id.casefold(), None)
            selected["input_sections"] = input_sections
        if stage_id != "BODY":
            selected.pop("linguistic_observations", None)
        selected.pop("rule_evaluation_trace", None)
        selected.pop("cross_stage_comparison_inputs", None)

        topic_trace = selected.get("topic_service")
        if isinstance(topic_trace, dict) and isinstance(topic_trace.get("steps"), list):
            compact_topic_trace = dict(topic_trace)
            compact_steps = []
            for item in topic_trace["steps"]:
                step = dict(item)
                if step.get("id") == "topic_matching":
                    step.pop("output", None)
                compact_steps.append(step)
            compact_topic_trace["steps"] = compact_steps
            selected["topic_service"] = compact_topic_trace

        stages[stage_id] = selected
        compact["stages"] = stages
        return compact

    def compact_student_feedback(feedback: dict[str, Any]) -> dict[str, Any]:
        """Keep feedback-to-rule links; the selected analysis already has full events."""
        compact = dict(feedback)
        provenance = feedback.get("Feedback Provenance")
        if isinstance(provenance, list):
            compact["Feedback Provenance"] = [
                {
                    key: item[key]
                    for key in ("feedback_field", "rule_id")
                    if key in item
                }
                for item in provenance
            ]
        return compact

    def analyze_payload(
        payload: dict[str, Any],
        stage_id: str,
        *,
        research_inspector_request: bool = False,
        include_research_trace: bool = False,
    ):
        handler_started = perf_counter() if research_inspector_request else None
        assignment_id = payload.get("assignment_id")
        if assignment_id is not None:
            if research_inspector_request:
                return jsonify(error="Research samples cannot reference saved assignments."), 400
            if not _valid_record_id(assignment_id):
                return jsonify(error="The assignment ID is invalid."), 400
            try:
                assignment = get_draft_store().get_available_assignment(
                    g.current_user["user_id"], assignment_id
                )
            except (OSError, sqlite3.Error):
                app.logger.exception("Assignment could not be loaded for analysis")
                return jsonify(error="Assignment could not be loaded. Please try again."), 500
            if assignment is None:
                return jsonify(error="That assignment was not found."), 404
            topic = assignment["topic"]
            focus_terms = _parse_focus_terms(assignment["focus_terms"])
        else:
            topic = payload.get("assignment_topic")
            focus_terms = _parse_focus_terms(payload.get("focus_terms"))
        text_field = STAGE_TEXT_FIELDS[stage_id]
        stage_name = stage_id.title()
        stage_text = payload.get(text_field)

        if not isinstance(topic, str) or not topic.strip():
            return jsonify(error="Enter an assignment topic."), 400
        if len(topic) > MAX_TOPIC_LENGTH:
            return jsonify(error=f"The assignment topic must be {MAX_TOPIC_LENGTH} characters or fewer."), 400
        if not isinstance(stage_text, str) or not stage_text.strip():
            return jsonify(error=f"Write your {stage_name} before analyzing it."), 400
        text_limit = {
            "INTRODUCTION": MAX_INTRODUCTION_LENGTH,
            "BODY": MAX_BODY_LENGTH,
            "CONCLUSION": MAX_CONCLUSION_LENGTH,
        }[stage_id]
        if len(stage_text) > text_limit:
            return jsonify(error=f"Your {stage_name} must be {text_limit} characters or fewer."), 400
        if isinstance(focus_terms, str):
            return jsonify(error=focus_terms), 400

        introduction = payload.get("introduction_text")
        body = payload.get("body_text")
        for context_name, context_text, limit in (
            ("Introduction", introduction, MAX_INTRODUCTION_LENGTH),
            ("Body", body, MAX_BODY_LENGTH),
        ):
            if context_text is not None and not isinstance(context_text, str):
                return jsonify(error=f"{context_name} context must be text."), 400
            if isinstance(context_text, str) and len(context_text) > limit:
                return jsonify(error=f"{context_name} context is too long."), 400
        introduction = introduction if isinstance(introduction, str) and introduction.strip() else None
        body = body if isinstance(body, str) and body.strip() else None

        if stage_id == "INTRODUCTION":
            introduction, body = stage_text, None
            conclusion = None
        elif stage_id == "BODY":
            body = stage_text
            conclusion = None
        else:
            conclusion = stage_text

        try:
            analysis_inputs = {
                "assignment_topic": topic.strip(),
                "focus_terms": focus_terms or None,
            }
            for field, text in (
                ("introduction_text", introduction),
                ("body_text", body),
                ("conclusion_text", conclusion),
            ):
                if text is not None:
                    analysis_inputs[field] = text
            validation_and_resolution_ms = (
                (perf_counter() - handler_started) * 1000 if handler_started is not None else 0.0
            )
            service_initialization_started = perf_counter() if research_inspector_request else None
            service = get_analysis_service()
            service_initialization_ms = (
                (perf_counter() - service_initialization_started) * 1000
                if service_initialization_started is not None else 0.0
            )
            service_started = perf_counter() if research_inspector_request else None
            trace_requested = research_inspector_request or include_research_trace
            if trace_requested:
                result = service.analyze(**analysis_inputs, include_research_trace=True)
            else:
                result = service.analyze(**analysis_inputs)
            service_ms = (perf_counter() - service_started) * 1000 if service_started is not None else 0.0
            stage = result["stages"][stage_id]
            response_analysis = stage["analysis"]
            response_feedback = stage["feedback"]
            if trace_requested and not research_inspector_request:
                response_analysis = dict(response_analysis)
                response_feedback = compact_student_feedback(response_feedback)
                if stage_id == "INTRODUCTION":
                    response_analysis.pop("input_text", None)
            response = {
                "stage_id": stage["stage_id"],
                "availability": stage["availability"],
                "analysis": response_analysis,
                "feedback": response_feedback,
                "interpretation_limit": result["interpretation_limit"],
            }
            if "related_topic_concept_evidence" in stage:
                # A separate informational field, not an input to feedback/rules.
                response["related_topic_concept_evidence"] = stage["related_topic_concept_evidence"]
            if trace_requested:
                root_trace = result.get("research_trace", {})
                if not research_inspector_request:
                    root_trace = compact_student_transparency_trace(root_trace, stage_id)
                if root_trace.get("runtime") is not None:
                    root_trace["runtime"]["analysis_service_initialization"] = {
                        "status": app.config.get("ANALYSIS_SERVICE_INITIALIZATION_STATUS"),
                        "duration_ms": app.config.get("ANALYSIS_SERVICE_INITIALIZATION_MS"),
                        "note": "Model/service construction is timed only when Flask creates the service lazily; injected preconstructed services are not timed here.",
                    }
                response["research_trace"] = {
                    **root_trace,
                    "selected_stage": stage_id,
                    "stages": {stage_id: root_trace.get("stages", {}).get(stage_id, {})},
                    "request_validation_and_assignment_resolution_ms": round(validation_and_resolution_ms, 3),
                    "analysis_service_lookup_ms": round(service_initialization_ms, 3),
                    "analysis_service_total_ms": round(service_ms, 3),
                    "api_authentication_and_csrf_timing": "NOT_INSTRUMENTED",
                    "json_response_serialization_timing": "NOT_INSTRUMENTED",
                }
            return jsonify(response)
        except (TypeError, ValueError) as error:
            return jsonify(error=f"The submitted information could not be analyzed: {error}"), 400
        except Exception:
            app.logger.exception("%s analysis failed", stage_name)
            return jsonify(error=f"{stage_name} analysis could not be completed. Please try again."), 500

    @app.errorhandler(RequestEntityTooLarge)
    def request_too_large(_error):
        return jsonify(error="The request is too large. Shorten the writing and try again."), 413

    @app.after_request
    def prevent_cached_account_pages(response):
        # Avoid showing a previous student's rendered workspace after account switching.
        response.headers["Cache-Control"] = "no-store"
        response.headers["Pragma"] = "no-cache"
        return response

    return app


def _parse_focus_terms(value: Any) -> list[str] | str:
    """Accept either a comma-separated form value or a JSON string list."""
    if value is None or value == "":
        return []
    if isinstance(value, str):
        terms = [term.strip() for term in value.split(",") if term.strip()]
    elif isinstance(value, list) and all(isinstance(term, str) for term in value):
        terms = [term.strip() for term in value if term.strip()]
    else:
        return "Focus terms must be text or a list of text values."

    if len(terms) > MAX_FOCUS_TERMS:
        return f"Enter no more than {MAX_FOCUS_TERMS} focus terms."
    if any(len(term) > MAX_FOCUS_TERM_LENGTH for term in terms):
        return f"Each focus term must be {MAX_FOCUS_TERM_LENGTH} characters or fewer."
    return terms


def _valid_session_id(session_id: Any) -> bool:
    return isinstance(session_id, str) and re.fullmatch(r"[0-9a-f]{32}", session_id) is not None


def _valid_record_id(value: Any) -> bool:
    """Accept positive IDs representable by SQLite's signed 64-bit INTEGER."""
    return type(value) is int and 0 < value <= 2**63 - 1


def _validated_draft(payload: dict[str, Any]) -> tuple[dict[str, str], str | None]:
    fields = (
        "assignment_topic",
        "focus_terms",
        "introduction_text",
        "body_text",
        "conclusion_text",
    )
    draft = {field: payload.get(field) for field in fields}
    if any(not isinstance(value, str) for value in draft.values()):
        return draft, "Topic, focus terms, and all three drafts must be text."
    if len(draft["assignment_topic"]) > MAX_TOPIC_LENGTH:
        return draft, f"The assignment topic must be {MAX_TOPIC_LENGTH} characters or fewer."
    if len(draft["focus_terms"]) > 2400:
        return draft, "Teacher focus terms must be 2400 characters or fewer."
    focus_validation = _parse_focus_terms(draft["focus_terms"])
    if isinstance(focus_validation, str):
        return draft, focus_validation
    for field, limit in (
        ("introduction_text", MAX_INTRODUCTION_LENGTH),
        ("body_text", MAX_BODY_LENGTH),
        ("conclusion_text", MAX_CONCLUSION_LENGTH),
    ):
        if len(draft[field]) > limit:
            stage = field.replace("_text", "").title()
            return draft, f"{stage} must be {limit} characters or fewer."
    return draft, None


app = create_app()


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
