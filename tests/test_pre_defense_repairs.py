"""Pre-defense defects reproduced against real Flask/storage and app.js."""

import inspect
import secrets
import sqlite3

import pytest

from app import create_app
from services.draft_store import DraftStore
from services.essay_analysis_service import EssayAnalysisService
from services.introduction_rules import IntroductionRuleBase
from tests.auth_helpers import login_student, register_student
from tests.test_workspace_frontend import _run_workspace_frontend
from werkzeug.security import generate_password_hash


@pytest.fixture
def accounts(tmp_path):
    app = create_app(secret_key=secrets.token_hex(32))
    app.config.update(TESTING=True, DRAFT_DATABASE_PATH=str(tmp_path / "audit.sqlite3"))
    student = app.test_client()
    register_student(student, "audit_student", secrets.token_urlsafe(18))
    store = DraftStore(app.config["DRAFT_DATABASE_PATH"])
    password = secrets.token_urlsafe(18)
    store.create_teacher_user("audit_teacher", generate_password_hash(password))
    teacher = app.test_client()
    assert login_student(teacher, "audit_teacher", password).status_code == 302
    return app, student, teacher


@pytest.mark.parametrize("path,role", [
    ("/api/assignments/{id}/workspace", "student"),
    ("/api/classrooms/{id}/assignments", "student"),
    ("/api/submissions/{id}", "student"),
    ("/api/revisions/{id}?session_id=" + "a" * 32, "student"),
    ("/teacher/assignments/{id}/edit", "teacher"),
    ("/teacher/assignments/{id}/submissions", "teacher"),
    ("/teacher/submissions/{id}", "teacher"),
])
def test_out_of_sqlite_range_url_ids_are_clean_denials(accounts, path, role):
    _, student, teacher = accounts
    response = (student if role == "student" else teacher).get(path.format(id=2 ** 80))
    assert response.status_code in {400, 404}
    if path.startswith("/api/"):
        assert response.is_json and response.get_json()["error"]


@pytest.mark.parametrize("endpoint", ["/api/drafts", "/api/revisions", "/api/submissions", "/api/analyze-stage"])
def test_out_of_sqlite_range_json_ids_do_not_reach_sqlite(accounts, endpoint):
    _, student, _ = accounts
    payload = dict(assignment_id=2 ** 80, stage_id="INTRODUCTION", assignment_topic="Reading",
                   focus_terms="reading", introduction_text="Students read.", body_text="", conclusion_text="",
                   session_id="a" * 32, draft_version="a" * 64)
    response = student.post(endpoint, json=payload)
    assert response.status_code == 400
    assert response.is_json


def test_oversized_session_identity_expires_cleanly(accounts):
    _, student, _ = accounts
    with student.session_transaction() as session:
        session["user_id"] = 2 ** 80
    assert student.get("/api/classrooms").status_code == 401


def test_submission_for_missing_assignment_is_json_not_found(accounts):
    _, student, _ = accounts
    response = student.post("/api/submissions", json={"assignment_id": 999999,
                             "session_id": "a" * 32, "draft_version": "a" * 64})
    assert response.status_code == 404
    assert response.is_json and response.get_json()["error"]


def test_head_edit_is_read_only(accounts, monkeypatch):
    app, _, teacher = accounts
    store = DraftStore(app.config["DRAFT_DATABASE_PATH"])
    user = store.get_user_for_login("audit_teacher")
    classroom = store.create_classroom(user["user_id"], "Audit", "English", "A")
    assignment = store.create_assignment(user["user_id"], classroom["classroom_id"], "Title", "Topic", "Instructions", "")
    def forbidden(*args, **kwargs):
        raise AssertionError("HEAD must not update an assignment")
    monkeypatch.setattr(DraftStore, "update_assignment", forbidden)
    response = teacher.head(f"/teacher/assignments/{assignment['assignment_id']}/edit")
    assert response.status_code == 200 and response.data == b""


@pytest.fixture(scope="module")
def analyzer():
    return EssayAnalysisService()


@pytest.mark.parametrize("reason,rule", [
    ("students can use educational apps during class", "INTRO.REASON.CLAUSE_TOPIC_OVERLAP"),
    ("invisible dragons control the price of bananas on Mars", "INTRO.REASON.NO_CLAUSE_TOPIC_OVERLAP"),
])
def test_reason_source_mapping_resolves_actual_introduction_helper(analyzer, reason, rule):
    result = analyzer.analyze("Smartphones in class", ["smartphones", "students", "class"],
                              introduction_text="Smartphones can support learning in the classroom when teachers guide students. Clear classroom rules may help reduce distractions during lessons. Schools should allow smartphones because " + reason + ".",
                              include_research_trace=True)
    rows = result["stages"]["INTRODUCTION"]["analysis"]["rule_evaluation_trace"]
    row = next(r for r in rows if r["rule_id"] == rule)
    source = row["implementation"]
    lines, start = inspect.getsourcelines(IntroductionRuleBase._reason_clause_lexical_check)
    assert source["class"] == "IntroductionRuleBase"
    assert source["function"] == "_reason_clause_lexical_check"
    assert source["file"].replace("\\", "/") == "services/introduction_rules.py"
    assert (source["start_line"], source["end_line"]) == (start, start + len(lines) - 1)


def test_assignment_switch_loads_current_revision_history(tmp_path):
    _run_workspace_frontend(tmp_path, r'''
    (async()=>{
      const page=makeWorkspace(fetch,new Map());await waitForRestoration(page);
      await click(page.appLinks.find(x=>x.dataset.appLink==="workspace"));
      const e=page.elements;
      // Seed a saved revision using the real frontend save handler.
      e["assignment-topic"].value="Reading";e["stage-text"].value="Practice revision.";
      await input(e["stage-text"]);await click(e["save-revision-button"]);
      assert.equal(e["revision-list"].children.length,1);
      const calls=[];
      const wrapped=page.context.fetch;
      page.context.fetch=(url,options)=>{calls.push(String(url));return wrapped(url,options);};
      await value(page,"selectAssignment(101)");
      const sessionId=value(page,"state.sessionId");
      assert.ok(calls.includes(`/api/revisions?session_id=${encodeURIComponent(sessionId)}`),"opening an assignment must load that session's revision history");
      console.log("Feedback presentation scenarios completed.");
    })().catch(e=>{console.error(e);process.exitCode=1;});
    ''')


def test_workspace_switch_waits_for_in_flight_clean_save(tmp_path):
    _run_workspace_frontend(tmp_path, r'''
    (async()=>{
      const page=makeWorkspace(fetch,new Map());await waitForRestoration(page);
      await click(page.appLinks.find(x=>x.dataset.appLink==="workspace"));
      const e=page.elements;
      e["assignment-topic"].value="Reading";e["stage-text"].value="Practice draft.";
      await input(e["stage-text"]);await click(e["save-revision-button"]);
      const saving=click(e["save-button"]);
      assert.equal(value(page,"state.saving"),true);
      await value(page,"selectAssignment(101)");
      assert.equal(value(page,"state.assignmentId"),null,"in-flight save must not write its session id into another assignment");
      completeSave();await saving;
      await value(page,"selectAssignment(101)");
      assert.equal(value(page,"state.assignmentId"),101);
      console.log("Feedback presentation scenarios completed.");
    })().catch(e=>{console.error(e);process.exitCode=1;});
    ''')


def test_teacher_edit_storage_failure_returns_controlled_response(accounts, monkeypatch):
    _, _, teacher = accounts
    def unavailable(*args, **kwargs):
        raise sqlite3.OperationalError("isolated injected outage")
    monkeypatch.setattr(DraftStore, "get_teacher_assignment_for_edit", unavailable)
    response = teacher.get("/teacher/assignments/1/edit")
    assert response.status_code == 503
    assert b"temporarily unavailable" in response.data


def test_late_revision_preview_does_not_cross_workspace_boundaries(tmp_path):
    _run_workspace_frontend(tmp_path, r'''
    (async()=>{
      const page=makeWorkspace(fetch,new Map());await waitForRestoration(page);
      await click(page.appLinks.find(x=>x.dataset.appLink==="workspace"));
      const e=page.elements;
      e["assignment-topic"].value="Reading";e["stage-text"].value="Old practice revision.";
      await input(e["stage-text"]);await click(e["save-revision-button"]);
      let release;
      const original=page.context.fetch;
      page.context.fetch=async(...args)=>{const r=await original(...args);return String(args[0]).startsWith('/api/revisions/')?new Promise(resolve=>{release=()=>resolve(r);}):r;};
      const preview=value(page,"viewRevision(1)");
      for(let i=0;i<10&&!release;i++)await new Promise(r=>setImmediate(r));
      assert.ok(release);
      await value(page,"selectAssignment(101)");
      assert.equal(e["revision-preview"].hidden,true);
      release();await preview;
      assert.equal(e["revision-preview"].hidden,true,"an old revision must not appear under the new assignment");
      console.log("Feedback presentation scenarios completed.");
    })().catch(e=>{console.error(e);process.exitCode=1;});
    ''')
