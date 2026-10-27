"""Real Chrome Body repair evidence using only a disposable database."""

import hashlib
import json
import os
from pathlib import Path
import secrets
import shutil
import subprocess
import sys
import tempfile
from threading import Thread

from werkzeug.security import generate_password_hash
from werkzeug.serving import make_server

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app import create_app
from services.draft_store import DraftStore
from services.essay_analysis_service import EssayAnalysisService
from tests.pre_defense_audit import protected_files


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    parent = Path(r"C:\Users\MYPC~1\AppData\Local\Temp\opencode")
    assert parent.is_dir()
    if "--capture-baseline" in sys.argv:
        from services.feedback_service import FeedbackService
        from tests.test_feedback_provenance import BODY_CASES, FIELDS, body_analysis
        destination = ROOT / "tests" / "body_feedback_protected_baseline.json"
        assert not destination.exists(), "Never overwrite the pre-repair feedback snapshot"
        values = {}
        for case, _, _ in BODY_CASES:
            feedback = FeedbackService().generate_body(body_analysis(case))
            values[case] = {field: feedback[field] for field in FIELDS}
        destination.write_text(json.dumps(values, indent=2) + "\n", encoding="utf-8")
        print("Captured actual pre-repair five-field feedback:", destination)
        return 0
    artifacts = Path(tempfile.mkdtemp(prefix="essayscaff-body-repair-", dir=parent))
    print("Artifacts:", artifacts, flush=True)
    protected = protected_files()
    guarded = [ROOT / "services" / name for name in ("introduction_rules.py", "conclusion_rules.py", "stage_evidence.py")]
    source_hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in guarded}
    corpus = json.loads((ROOT / "tests" / "body_feedback_repair_cases.json").read_text(encoding="utf-8"))
    app = create_app(EssayAnalysisService(), secret_key=secrets.token_hex(32))
    app.config.update(TESTING=True, DRAFT_DATABASE_PATH=str(artifacts / "isolated.sqlite3"))
    store = DraftStore(app.config["DRAFT_DATABASE_PATH"])
    password = secrets.token_urlsafe(24)
    student = store.create_user("body_student", generate_password_hash(password))
    teacher = store.create_teacher_user("body_teacher", generate_password_hash(password))
    classroom = store.create_classroom(teacher["user_id"], "Body check class", "English", "Body")
    store.join_classroom(student["user_id"], classroom["enrollment_code"])
    for label, intro in (("A", corpus["introduction"]), ("B", "The second assignment has a different saved Introduction.")):
        assignment = store.create_assignment(teacher["user_id"], classroom["classroom_id"], "Body context " + label,
                                             corpus["assignment_topic"], "Explain your view.", ", ".join(corpus["focus_terms"]))
        workspace = store.get_or_create_assignment_workspace(student["user_id"], assignment["assignment_id"])
        store.save({"assignment_topic": corpus["assignment_topic"], "focus_terms": ", ".join(corpus["focus_terms"]),
                    "introduction_text": intro, "body_text": corpus["cases"]["B01"], "conclusion_text": ""},
                   workspace["draft"]["session_id"], student["user_id"], assignment["assignment_id"])
    server = make_server("127.0.0.1", 0, app, threaded=True)
    Thread(target=server.serve_forever, daemon=True).start()
    mode = "before" if "--before" in sys.argv else "after"
    try:
        result = subprocess.run(["node", str(ROOT / "tests" / "body_feedback_browser_check.cjs"),
                                 f"http://127.0.0.1:{server.server_port}", str(artifacts), mode], cwd=ROOT,
                                env={**os.environ, "ESSAYSCAFF_BODY_PASSWORD": password}, capture_output=True,
                                text=True, encoding="utf-8", timeout=300)
        (artifacts / "browser.log").write_text(result.stdout + result.stderr, encoding="utf-8")
        print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        assert protected == protected_files(), "Original database/research file changed"
        assert source_hashes == {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in guarded}
        with store._connection() as connection:
            assert connection.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
            assert not connection.execute("PRAGMA foreign_key_check").fetchall()
            counts = {t: connection.execute(f"SELECT count(*) FROM {t}").fetchone()[0]
                      for t in ("writing_sessions", "writing_revisions", "submissions")}
        summary = {"mode": mode, "browser_exit_code": result.returncode, "protected_files_sha256": protected,
                   "guarded_sources_sha256": source_hashes, "isolated_counts": counts,
                   "integrity": "ok", "foreign_key_violations": 0}
        (artifacts / "verification-summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
        print("Protected originals unchanged; isolated database:", json.dumps(counts))
        if result.returncode == 0 and "--publish-evidence" in sys.argv:
            before = Path(sys.argv[sys.argv.index("--publish-evidence") + 1]).resolve()
            assert mode == "after" and before.parent == parent.resolve()
            before_summary = json.loads((before / "verification-summary.json").read_text())
            assert before_summary["browser_exit_code"] == 0
            assert before_summary["protected_files_sha256"] == protected
            assert before_summary["guarded_sources_sha256"] == source_hashes, "Introduction, Conclusion and shared clause rules must remain unchanged"
            old = json.loads((before / "before-outputs.json").read_text(encoding="utf-8"))
            new = json.loads((artifacts / "after-outputs.json").read_text(encoding="utf-8"))
            assert set(old["records"]) == set(new["records"]) == set(corpus["cases"])
            assert old["javascriptErrors"] == new["javascriptErrors"] == []
            for key in corpus["cases"]:
                # The repair adds input/context retention and feedback metadata,
                # not a different NLP detector. Compare ALL original observations.
                original = {k: v for k, v in old["records"][key]["analysis"].items() if k != "rule_evaluation_trace"}
                current = {k: v for k, v in new["records"][key]["analysis"].items()
                           if k not in {"input_text", "introduction_context", "rule_evaluation_trace"}}
                assert original == current, f"Original Body observations changed: {key}"
            summary["original_body_observations_unchanged_cases"] = len(corpus["cases"])
            (artifacts / "verification-summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
            evidence = ROOT / "docs" / "body_feedback_repair_evidence"
            images = ROOT / "docs" / "screenshots" / "body-feedback-repair"
            assert evidence.parent.is_dir() and images.parent.is_dir()
            evidence.mkdir(exist_ok=True)
            images.mkdir(exist_ok=True)
            manifest = []
            for phase, folder in (("before", before), ("after", artifacts)):
                for name in (f"{phase}-outputs.json", "browser.log", "verification-summary.json"):
                    shutil.copyfile(folder / name, evidence / (f"{phase}-{name}" if not name.startswith(phase) else name))
                for image in folder.glob(f"{phase}-*.png"):
                    destination = images / image.name
                    shutil.copyfile(image, destination)
                    digest = hashlib.sha256(image.read_bytes()).hexdigest()
                    assert hashlib.sha256(destination.read_bytes()).hexdigest() == digest
                    manifest.append({"file": image.name, "sha256": digest})
            (evidence / "screenshots.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
            comparison = ["# Actual Body tutor before/after results", "",
                          "Generated from authenticated real-Chrome captures. Original Body observations match in all 12 cases; only input/context retention and feedback/presentation change.", ""]
            for key, text in corpus["cases"].items():
                left, right = old["records"][key], new["records"][key]
                metadata = right["decision"]["instructional_feedback"]
                item = metadata["items"][0] if metadata["items"] else None
                comparison += [f"## {key}", "", "> " + text.replace("\n", "\n> "), "",
                               f"- Before Primary / Next Step: `{left['decision']['fields']['Primary Feedback']['selection_branch']}` / `{left['decision']['fields']['Next Step']['selection_branch']}`.",
                               f"- After Primary / Next Step: `{right['decision']['fields']['Primary Feedback']['selection_branch']}` / `{right['decision']['fields']['Next Step']['selection_branch']}`.",
                               f"- Actual status: `{metadata['selection_status']}`.",
                               f"- Trait / skill / lesson: {item['trait'] + ' / ' + item['skill'] + ' / `' + item['lesson_id'] + '`' if item else 'None assigned; neutral observation result.'}",
                               f"- Actual selection condition: {metadata['selection_condition']}.",
                               f"- Recorded strength text: {right['presentation']['displayed_strengths'] or 'None claimed.'}", "",
                               "### Before — exact displayed guidance", "", "```json", json.dumps(left["presentation"]["displayed_guidance"], ensure_ascii=False, indent=2), "```", "",
                               "### After — exact displayed guidance", "", "```json", json.dumps(right["presentation"]["displayed_guidance"], ensure_ascii=False, indent=2), "```", ""]
                if item:
                    comparison += ["Supporting Rule IDs: " + ", ".join(f"`{rule}`" for rule in item["rule_ids"]) + ".", ""]
                    for mark in item["highlight_spans"]:
                        comparison += [f"- Verified source mark [{mark['start']}, {mark['end']}): **{mark['text']}** — {mark['selection_reason']}"]
                    if not item["highlight_spans"]:
                        comparison += ["No precise error span was recorded for this wording comparison; no highlight is invented."]
                else:
                    comparison += ["No error highlight or improvement task is selected."]
                comparison += ["", "Limitation: " + metadata["limitations"][0], ""]
            (evidence / "case-comparison.md").write_text("\n".join(comparison), encoding="utf-8")
            print("Published:", evidence)
        return result.returncode
    finally:
        server.shutdown()


if __name__ == "__main__":
    raise SystemExit(main())
