r"""Reproducible isolated route, link, startup and real-Chrome system audit.

Run from the project: .venv\Scripts\python.exe -B tests/pre_defense_audit.py
Generated artifacts contain statuses/schema/counts, never passwords or cookies.
"""

import ast
import hashlib
from html.parser import HTMLParser
import inspect
import json
import os
from pathlib import Path
import re
import secrets
import shutil
import socket
import sqlite3
import subprocess
import sys
import tempfile
from threading import Thread
import time
from urllib.error import HTTPError
from urllib.parse import urlsplit
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from flask import url_for
from werkzeug.security import generate_password_hash
from werkzeug.serving import make_server

from app import create_app
from services.draft_store import DraftStore
from services.essay_analysis_service import EssayAnalysisService
from tests.auth_helpers import login_student

STUDENT_ENDPOINTS = {
    "analyze_introduction", "analyze_stage", "save_draft", "restore_draft", "save_revision",
    "list_revisions", "view_revision", "available_assignments", "assignment_workspace",
    "student_classrooms", "enroll_student", "classroom_assignments", "submit_assignment",
    "student_submission", "student_archived_assignments", "record_writing_activity",
    "read_writing_activity",
}
TEACHER_ENDPOINTS = {
    "teacher_dashboard", "create_classroom", "create_assignment", "edit_assignment", "delete_assignment",
    "assign_legacy_assignment", "teacher_assignment_submissions", "teacher_submission_view",
    "research_inspector", "research_inspector_metadata", "analyze_research_inspector",
}
PUBLIC = {"static", "brand_logo", "register", "create_account", "login", "authenticate_student"}
DRAFT = {"assignment_topic": "Reading habits", "focus_terms": "reading, students",
         "introduction_text": "Students should read daily because reading helps students learn.",
         "body_text": "Students read books. For example, they discuss a story with classmates.",
         "conclusion_text": "Overall, students should read daily."}


def seed(app):
    store = DraftStore(app.config["DRAFT_DATABASE_PATH"])
    password = secrets.token_urlsafe(24)
    users = {name: store.create_user("audit_" + name, generate_password_hash(password), role)
             for name, role in [("student", "STUDENT"), ("outsider", "STUDENT"), ("teacher", "TEACHER"),
                                ("other_teacher", "TEACHER"), ("deletable", "STUDENT"), ("joiner", "STUDENT")]}
    classes = [store.create_classroom(users["teacher"]["user_id"], "Audit English", "English", "A"),
               store.create_classroom(users["other_teacher"]["user_id"], "Other teacher class", "English", "B")]
    store.join_classroom(users["student"]["user_id"], classes[0]["enrollment_code"])
    assignments = {name: store.create_assignment(users["teacher"]["user_id"], classes[0]["classroom_id"],
                   "Audit " + name, "Should students read daily?", "Explain your point with a reason.", "reading, students")
                   for name in ["active", "submitted", "editable", "archive", "activity"]}
    foreign = store.create_assignment(users["other_teacher"]["user_id"], classes[1]["classroom_id"],
                                     "Foreign task", "Other topic", "Other instructions", "other")
    with store._connection() as connection:
        cursor = connection.execute("INSERT INTO assignments (teacher_user_id,title,topic,instructions,focus_terms) VALUES (?,?,?,?,?)",
                                    (users["teacher"]["user_id"], "Legacy", "Reading", "Write your view.", "reading"))
        legacy = cursor.lastrowid
        connection.execute("INSERT INTO assignments (teacher_user_id,title,topic,instructions,focus_terms) VALUES (?,?,?,?,?)",
                           (users["teacher"]["user_id"], "Browser legacy task", "Reading", "Write your view.", "reading"))
    practice = store.save(DRAFT, user_id=users["student"]["user_id"])
    revision = store.save_revision(DRAFT, practice["session_id"], users["student"]["user_id"])["revision"]
    assigned = {}
    for name in ("active", "submitted", "activity"):
        assignment_id = assignments[name]["assignment_id"]
        draft = {**DRAFT, "assignment_topic": assignments[name]["topic"], "focus_terms": assignments[name]["focus_terms"]}
        ws = store.get_or_create_assignment_workspace(users["student"]["user_id"], assignment_id)
        assigned[name] = store.save(draft, ws["draft"]["session_id"], users["student"]["user_id"], assignment_id)
    submission = store.create_submission(users["student"]["user_id"], assignments["submitted"]["assignment_id"],
                                         assigned["submitted"]["session_id"], store.draft_version(assigned["submitted"]))
    clients = {}
    for name in users:
        clients[name] = app.test_client()
        assert login_student(clients[name], "audit_" + name, password).status_code == 302
    return dict(store=store, password=password, clients=clients, users=users, classes=classes,
                assignments=assignments, foreign=foreign, legacy=legacy, practice=practice,
                revision=revision, assigned=assigned, submission=submission)


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.ids = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            self.ids.append(attrs["id"])
        for key in ("href", "src", "action"):
            if attrs.get(key):
                self.links.append((tag, key, attrs[key], attrs.get("method", "get").upper()))


def route_audit(app, fixture):
    """Cover every discovered rule, its methods, role guard and csrf boundary."""
    f = fixture
    assert set(app.view_functions) == STUDENT_ENDPOINTS | TEACHER_ENDPOINTS | PUBLIC | {"homepage", "logout", "account_settings", "delete_account"}, "Every new route requires an explicit permission classification"
    cs = f["clients"]
    assignments = f["assignments"]
    analysis = {"stage_id": "INTRODUCTION", "assignment_topic": DRAFT["assignment_topic"],
                "focus_terms": DRAFT["focus_terms"], "introduction_text": DRAFT["introduction_text"],
                "include_transparency_trace": True}
    values = {"static": {"filename": "style.css"},
              "edit_assignment": {"assignment_id": assignments["editable"]["assignment_id"]},
              "delete_assignment": {"assignment_id": assignments["archive"]["assignment_id"]},
              "assign_legacy_assignment": {"assignment_id": f["legacy"]},
              "classroom_assignments": {"classroom_id": f["classes"][0]["classroom_id"]},
              "assignment_workspace": {"assignment_id": assignments["active"]["assignment_id"]},
              "student_submission": {"assignment_id": assignments["submitted"]["assignment_id"]},
              "teacher_assignment_submissions": {"assignment_id": assignments["submitted"]["assignment_id"]},
              "teacher_submission_view": {"submission_id": f["submission"]["submission_id"]},
              "view_revision": {"revision_id": str(f["revision"]["revision_id"])}}
    forms = {
        "create_account": {"username": "audit_registered", "password": f["password"], "confirm_password": f["password"]},
        "authenticate_student": {"username": "audit_student", "password": f["password"]},
        "delete_account": {"confirm_delete": "yes", "password": f["password"]},
        "create_classroom": {"classroom_name": "Route created", "subject": "English", "section": "C"},
        "create_assignment": {"classroom_id": str(f["classes"][0]["classroom_id"]), "title": "Created route task",
                              "topic": "Reading", "instructions": "Write your point.", "focus_terms": "reading"},
        "edit_assignment": {"title": "Edited route task", "topic": "Reading", "instructions": "Explain your point.", "focus_terms": "reading"},
        "assign_legacy_assignment": {"classroom_id": str(f["classes"][0]["classroom_id"])},
    }
    json_bodies = {
        "enroll_student": {"enrollment_code": f["classes"][0]["enrollment_code"]},
        "submit_assignment": {"assignment_id": assignments["active"]["assignment_id"],
                              "session_id": f["assigned"]["active"]["session_id"],
                              "draft_version": f["store"].draft_version(f["assigned"]["active"])},
        "analyze_introduction": analysis, "analyze_stage": analysis, "analyze_research_inspector": analysis,
        "save_draft": {**DRAFT, "session_id": f["practice"]["session_id"]},
        "save_revision": {**DRAFT, "session_id": f["practice"]["session_id"]},
        "record_writing_activity": {
            "assignment_id": assignments["activity"]["assignment_id"],
            "session_id": f["assigned"]["activity"]["session_id"],
            "events": [{"stage": "INTRODUCTION",
                        "bucket_start": int(time.time()) - int(time.time()) % 5,
                        "seconds": 5}],
        },
    }
    query = {name: {"session_id": f["practice"]["session_id"]} for name in ("restore_draft", "list_revisions", "view_revision")}
    query["read_writing_activity"] = {"assignment_id": assignments["activity"]["assignment_id"]}
    rows, pages, denials = [], [], []
    for rule in app.url_map.iter_rules():
        endpoint = rule.endpoint
        role = "teacher" if endpoint in TEACHER_ENDPOINTS else "student"
        client = cs["deletable"] if endpoint == "delete_account" else cs["joiner"] if endpoint in {"enroll_student", "logout"} else cs[role]
        if endpoint == "logout":
            client = app.test_client()
            assert login_student(client, "audit_joiner", f["password"]).status_code == 302
        if endpoint in {"register", "create_account", "login", "authenticate_student"}:
            client = app.test_client()
            client.get("/login")
        with client.session_transaction() as session:
            token = session.get("_csrf_token", "")
        with app.test_request_context():
            path = url_for(endpoint, **values.get(endpoint, {}))
        method_results = []
        for method in sorted(rule.methods - {"OPTIONS", "HEAD"}):
            opts = dict(query_string=query.get(endpoint, {}), headers={"X-CSRF-Token": token})
            if method == "POST":
                if endpoint in json_bodies:
                    opts["json"] = json_bodies[endpoint]
                else:
                    opts["data"] = {**forms.get(endpoint, {}), "csrf_token": token}
            response = client.open(path, method=method, **opts)
            expected = 302 if method == "POST" and not path.startswith("/api/") else 200
            assert response.status_code == expected, (endpoint, method, response.status_code, response.get_data(as_text=True)[:200])
            if path.startswith("/api/"):
                assert response.is_json and isinstance(response.get_json(), dict), endpoint
            if response.mimetype == "text/html" and method == "GET":
                pages.append((client, path, response.get_data(as_text=True)))
            method_results.append({"method": method, "status": response.status_code,
                                   "redirect": response.headers.get("Location"), "classification": "PASS"})
        if "HEAD" in rule.methods:
            response = client.head(path, query_string=query.get(endpoint, {}))
            assert response.status_code == 200 and response.data == b"", endpoint
            method_results.append({"method": "HEAD", "status": response.status_code, "classification": "PASS"})
        response = client.options(path)
        # Logout/deletion intentionally invalidate the current session.
        assert response.status_code in {200, 302}, endpoint
        method_results.append({"method": "OPTIONS", "status": response.status_code,
                               "classification": "PASS" if response.status_code == 200 else "EXPECTED DENIAL"})
        if endpoint not in PUBLIC:
            method = "GET" if "GET" in rule.methods else "POST"
            anonymous = app.test_client().open(path, method=method, json={} if method == "POST" else None)
            assert anonymous.status_code == (401 if path.startswith("/api/") else 302), endpoint
            denials.append({"endpoint": endpoint, "case": "anonymous", "status": anonymous.status_code,
                            "redirect": anonymous.headers.get("Location"), "classification": "EXPECTED DENIAL"})
            if endpoint in STUDENT_ENDPOINTS | TEACHER_ENDPOINTS:
                wrong = cs["student" if role == "teacher" else "teacher"].open(path, method=method, json={} if method == "POST" else None)
                assert wrong.status_code == 403, endpoint
                denials.append({"endpoint": endpoint, "case": "wrong role", "status": 403, "classification": "EXPECTED DENIAL"})
        if "POST" in rule.methods:
            protected = cs[role] if endpoint not in PUBLIC else app.test_client()
            if endpoint in PUBLIC:
                protected.get("/login")
            denied = protected.post(path, data={"csrf_token": ""}, headers={"X-CSRF-Token": ""})
            assert denied.status_code == 400, (endpoint, denied.status_code)
            denials.append({"endpoint": endpoint, "case": "missing CSRF", "status": 400, "classification": "EXPECTED DENIAL"})
        wrong_method = cs[role].open(path, method="PUT", headers={"X-CSRF-Token": token})
        # For public one-off sessions use the right client's token for this probe.
        if wrong_method.status_code == 400:
            with cs[role].session_transaction() as session:
                retry_token = session["_csrf_token"]
            wrong_method = cs[role].open(path, method="PUT", headers={"X-CSRF-Token": retry_token})
        assert wrong_method.status_code == 405, (endpoint, wrong_method.status_code)
        denials.append({"endpoint": endpoint, "case": "unsupported PUT", "status": 405, "classification": "EXPECTED DENIAL"})
        rows.append({"url": rule.rule, "endpoint": endpoint, "methods": sorted(rule.methods),
                     "function": app.view_functions[endpoint].__qualname__,
                     "source_line": inspect.getsourcelines(app.view_functions[endpoint])[1],
                     "permission": "public" if endpoint in PUBLIC else "TEACHER + ownership" if endpoint in TEACHER_ENDPOINTS else "STUDENT + ownership/enrollment" if endpoint in STUDENT_ENDPOINTS else "authenticated STUDENT/TEACHER",
                     "expected": "JSON object" if path.startswith("/api/") else "asset" if endpoint in {"static", "brand_logo"} else "HTML page or successful form redirect",
                     "results": method_results, "classification": "PASS"})
    links = []
    adapter = app.url_map.bind("localhost")
    for client, page_path, html in pages:
        parsed = Links()
        parsed.feed(html)
        assert len(parsed.ids) == len(set(parsed.ids)), (page_path, "duplicate ids")
        for tag, attr, target, method in parsed.links:
            split = urlsplit(target)
            if split.scheme or split.netloc:
                links.append({"page": page_path, "target": target, "classification": "NOT TESTED", "reason": "external reference"})
            elif target.startswith("#"):
                links.append({"page": page_path, "target": target, "classification": "PASS", "reason": "frontend hash view; actual activation checked by Chrome"})
            else:
                endpoint, _ = adapter.match(split.path, method=method if attr == "action" else "GET")
                if attr == "src" or endpoint in {"static", "brand_logo"}:
                    assert client.get(target).status_code == 200, (page_path, target)
                links.append({"page": page_path, "target": target, "method": method if attr == "action" else "GET", "endpoint": endpoint, "classification": "PASS"})
    negative = []
    for endpoint in json_bodies:
        with app.test_request_context():
            path = url_for(endpoint)
        client = cs["teacher"] if endpoint in TEACHER_ENDPOINTS else cs["student"]
        for body in [[], None, "invalid", 42]:
            response = client.post(path, data=json.dumps(body), content_type="application/json")
            assert response.status_code == 400 and response.is_json, (endpoint, body, response.status_code)
        negative.append({"endpoint": endpoint, "case": "array/null/string/number JSON", "status": 400, "classification": "EXPECTED DENIAL"})
    for path, client in [(f"/teacher/assignments/{f['foreign']['assignment_id']}/edit", cs["teacher"]),
                         (f"/teacher/assignments/{f['foreign']['assignment_id']}/submissions", cs["teacher"]),
                         (f"/teacher/submissions/{f['submission']['submission_id']}", cs["other_teacher"]),
                         (f"/api/assignments/{assignments['active']['assignment_id']}/workspace", cs["outsider"]),
                         (f"/api/writing-activity?assignment_id={assignments['active']['assignment_id']}", cs["outsider"]),
                         (f"/api/drafts?session_id={f['practice']['session_id']}", cs["outsider"]),
                         (f"/api/revisions/{f['revision']['revision_id']}?session_id={f['practice']['session_id']}", cs["outsider"])]:
        response = client.get(path)
        assert response.status_code == 404, path
        negative.append({"url": path, "case": "foreign ownership/enrollment", "status": 404, "classification": "EXPECTED DENIAL"})
    js_refs = []
    for file in (ROOT / "static").glob("*.js"):
        for _, target in re.findall(r"fetch\(\s*([\"'`])(.+?)\1", file.read_text(encoding="utf-8"), re.DOTALL):
            resolved = re.sub(r"\$\{[^}]+\}", "1", target)
            if not resolved.startswith("/"):
                continue
            allowed = adapter.allowed_methods(urlsplit(resolved).path)
            assert allowed, (file.name, target, "frontend URL missing from Flask")
            js_refs.append({"file": file.name, "target": target, "route_methods": sorted(allowed), "classification": "PASS"})
    with f["store"]._connection() as connection:
        integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
        fk = list(connection.execute("PRAGMA foreign_key_check"))
    assert integrity == "ok" and fk == []
    return dict(routes=rows, denials=denials, negative_inputs=negative, links=links, javascript_urls=js_refs,
                blueprint_count=len(app.blueprints), sqlite_integrity=integrity, foreign_key_violations=len(fk))


def protected_files():
    paths = [p for p in (ROOT / "instance").glob("*.sqlite3*") if p.is_file()]
    paths += [p for p in (ROOT / "experiments" / "semantic_feasibility").glob("*.json") if p.is_file()]
    return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}


def nlp_audit(service):
    """Record actual stage outputs; expected concerns are checked in stage regressions."""
    topic = "Should students be allowed to use smartphones during class?"
    focus = ["smartphones", "students", "classroom", "learning", "distractions"]
    intro = "Smartphones help students learn. Teachers guide students during classroom activities."
    body = "Students use smartphones for reading. For example, students look up difficult words.\n\nTeachers guide classroom learning and explain new words."
    cases = {
        "INTRODUCTION": {
            "empty": "", "topic-only": "Smartphones.",
            "main-statement": "Schools should allow smartphones for learning.",
            "explanation": "Schools should allow smartphones because students can use educational apps during class.",
            "because-incomplete": "Because students can use smartphones for learning.",
            "because-complete": "Teachers use smartphones because students can use educational apps during class.",
            "although-incomplete": "Although smartphones can interrupt lessons.",
            "although-complete": "Although smartphones can distract students, teachers can use them for learning.",
            "unrelated-sentence": intro + " We had a slumber party at my aunt's house.",
            "pronoun-context": intro + " She helped me understand the lesson better.",
            "keyword-rich-unrelated": intro + " Students can communicate with invisible dragons during class.",
            "simultaneous-concerns": intro + " Although smartphones can interrupt lessons. And have slumber party at my aunt house",
        },
        "BODY": {
            "one-paragraph": "Students use smartphones for learning.", "multiple-paragraphs": body,
            "no-detail-candidate": "Students use smartphones.",
            "example": "Students use smartphones for learning. For example, they read educational articles.",
            "unrelated-example": "Students use smartphones. For example, invisible dragons visit Mars.",
            "repeated-openings": "Students read books daily. Students read books at home.",
            "disconnected": "Students use smartphones.\n\nOrchestras perform symphonies.",
            "developed": body, "missing-introduction": body,
        },
        "CONCLUSION": {
            "valid-ending": "Overall, students should use smartphones for guided classroom learning.",
            "empty": "", "no-closing-statement": "Smartphones.",
            "repeated-main-idea": "Schools should allow smartphones for learning.",
            "new-topic": "Overall, students should use smartphones. Satellites explore distant galaxies.",
            "paraphrase": "Teachers can guide learners as they read and look up new words.",
            "missing-earlier-context": "Overall, students should use smartphones carefully.",
        },
    }
    rows = []
    for stage, samples in cases.items():
        for name, text in samples.items():
            inputs = {stage.lower() + "_text": text}
            if stage != "INTRODUCTION" and not name.startswith("missing-"):
                inputs["introduction_text"] = intro
                if stage == "CONCLUSION":
                    inputs["body_text"] = body
            result = service.analyze(topic, focus, **inputs, include_research_trace=True)
            selected = result["stages"][stage]
            assert selected["supplied_text"] == text
            events = {e["rule_id"] for e in selected["analysis"]["rule_evidence"]}
            decisions = result["research_trace"]["stages"][stage]["feedback_decisions"]["fields"]
            for field in ("Current Goal", "Primary Feedback", "What's Working", "Needs Attention", "Next Step"):
                assert set(decisions[field]["rule_ids"]) <= events
                if isinstance(selected["feedback"][field], str):
                    assert decisions[field]["selected_message"] == selected["feedback"][field]
            if name in {"because-incomplete", "although-incomplete"}:
                assert decisions["Primary Feedback"]["selection_branch"] == "intro_sentence_fluency_complete_sentence"
            if name in {"because-complete", "although-complete"}:
                assert not selected["analysis"]["observable_structure"]["incomplete_subordinator_candidates"]
            rows.append({"stage": stage, "case": name, "input": inputs,
                         "availability": selected["availability"], "events": sorted(events),
                         "branch": decisions["Primary Feedback"]["selection_branch"],
                         "primary_feedback": selected["feedback"]["Primary Feedback"],
                         "classification": "PASS", "limitation": "Observational regression only; no semantic accuracy claim."})
    return rows


def database_inspection():
    results = []
    for path in (ROOT / "instance").glob("*.sqlite3"):
        with sqlite3.connect(path.as_uri() + "?mode=ro", uri=True) as connection:
            schema = [{"table": name, "columns": [r[1] for r in connection.execute(f'PRAGMA table_info("{name}")')]}
                      for (name,) in connection.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")]
            results.append({"file": path.name, "mode": "read-only", "schema": schema,
                            "integrity": connection.execute("PRAGMA integrity_check").fetchone()[0],
                            "foreign_key_violations": len(connection.execute("PRAGMA foreign_key_check").fetchall())})
    return results


def clean_startup(artifacts):
    probe = socket.socket()
    try:
        probe.bind(("127.0.0.1", 5000))
    except OSError:
        return {"classification": "NOT TESTED", "reason": "Port 5000 already occupied; no existing process was stopped."}
    finally:
        probe.close()
    process = subprocess.Popen([str(ROOT / ".venv" / "Scripts" / "python.exe"), "-B", "app.py"], cwd=ROOT,
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8")
    try:
        for _ in range(100):
            if process.poll() is not None:
                raise AssertionError("app.py exited during startup")
            try:
                with urlopen("http://127.0.0.1:5000/login", timeout=1) as response:
                    assert response.status == 200 and "Log in" in response.read().decode()
                break
            except OSError:
                time.sleep(0.1)
        else:
            raise AssertionError("Startup timed out")
        return {"classification": "PASS", "command": '.venv\\Scripts\\python.exe -B app.py',
                "status": "running; real HTTP /login 200; terminated only audit child after check", "debug": False}
    finally:
        process.terminate()
        output, _ = process.communicate(timeout=15)
        (artifacts / "startup.log").write_text(output, encoding="utf-8")


def main():
    parent = Path(r"C:\Users\MYPC~1\AppData\Local\Temp\opencode")
    assert parent.is_dir()
    artifacts = Path(tempfile.mkdtemp(prefix="essayscaff-pre-defense-", dir=parent))
    print(f"Artifacts: {artifacts}", flush=True)
    before = protected_files()
    startup = clean_startup(artifacts)
    service = EssayAnalysisService()
    app = create_app(service, secret_key=secrets.token_hex(32))
    app.config.update(TESTING=True, DRAFT_DATABASE_PATH=str(artifacts / "isolated.sqlite3"))
    fixture = seed(app)
    routes = route_audit(app, fixture)
    (artifacts / "route-audit.json").write_text(json.dumps(routes, indent=2), encoding="utf-8")
    nlp = nlp_audit(service)
    (artifacts / "nlp-audit.json").write_text(json.dumps(nlp, indent=2), encoding="utf-8")
    syntax = []
    for path in ROOT.rglob("*.py"):
        if any(part in {".venv", "__pycache__", "_rollback_feedback_replacement", ".freebuff"} for part in path.relative_to(ROOT).parts):
            continue
        ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(path))
        syntax.append(str(path.relative_to(ROOT)))
    for template in app.jinja_env.list_templates():
        app.jinja_env.get_template(template)
    env = {**os.environ, "ESSAYSCAFF_AUDIT_PASSWORD": fixture["password"]}
    server = make_server("127.0.0.1", 0, app, threaded=True)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        browser = subprocess.run(["node", str(ROOT / "tests" / "pre_defense_browser_check.cjs"),
                                  f"http://127.0.0.1:{server.server_port}", str(artifacts)],
                                 cwd=ROOT, env=env, capture_output=True, text=True, encoding="utf-8", timeout=300)
        (artifacts / "browser.log").write_text(browser.stdout + browser.stderr, encoding="utf-8")
        assert browser.returncode == 0, browser.stdout + browser.stderr
    finally:
        server.shutdown()
    after = protected_files()
    assert before == after, "Original database or research JSON changed"
    with fixture["store"]._connection() as connection:
        integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
        fk = len(connection.execute("PRAGMA foreign_key_check").fetchall())
    summary = {"startup": startup, "route_rules": len(routes["routes"]),
               "route_method_results": sum(len(r["results"]) for r in routes["routes"]),
               "role_csrf_method_denials": len(routes["denials"]), "negative_input_groups": len(routes["negative_inputs"]),
               "links_checked": len(routes["links"]), "python_files_parsed": len(syntax),
               "javascript_fetch_urls_checked": len(routes["javascript_urls"]),
               "nlp_real_analysis_cases": len(nlp),
               "templates_compiled": len(app.jinja_env.list_templates()), "protected_files_unchanged": sorted(before),
               "original_databases": database_inspection(), "isolated_database_integrity": integrity,
               "isolated_foreign_key_violations": fk, "browser_status": "PASS", "artifacts": str(artifacts)}
    (artifacts / "audit-summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    if "--publish-evidence" in sys.argv:
        assert (ROOT / "docs").is_dir()
        evidence_dir = ROOT / "docs" / "pre_defense_evidence"
        images_dir = ROOT / "docs" / "screenshots" / "pre-defense"
        evidence_dir.mkdir(parents=True, exist_ok=True)
        images_dir.mkdir(parents=True, exist_ok=True)
        for name in ("audit-summary.json", "route-audit.json", "nlp-audit.json", "workflow-browser.json", "startup.log", "browser.log"):
            shutil.copyfile(artifacts / name, evidence_dir / name)
        table = ["# Generated Flask route audit", "", "All rows are discovered from the real `app.url_map`.", "",
                 "| URL | Endpoint / function | Methods | Permission | Expected | Actual | Redirect | Status |",
                 "|---|---|---|---|---|---|---|---|"]
        for row in routes["routes"]:
            actual = "; ".join(f"{r['method']} {r['status']}" for r in row["results"])
            redirects = ", ".join(sorted({r["redirect"] for r in row["results"] if r.get("redirect")})) or "—"
            table.append(f"| `{row['url']}` | `{row['endpoint']}` / `{row['function']}` | {', '.join(row['methods'])} | {row['permission']} | {row['expected']} | {actual} | {redirects} | PASS |")
        (evidence_dir / "route-matrix.md").write_text("\n".join(table) + "\n", encoding="utf-8")
        manifest = []
        for image in artifacts.glob("audit-*.png"):
            shutil.copyfile(image, images_dir / image.name)
            manifest.append({"file": image.name, "sha256": hashlib.sha256(image.read_bytes()).hexdigest()})
        (evidence_dir / "screenshots.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
