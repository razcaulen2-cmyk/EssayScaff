"""Isolated actual-Chrome Introduction Ideas before/after verification."""

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


def publish_evidence(before_artifacts, artifacts, summary):
    """Publish only verified, authored-case outputs and Chrome screenshots."""
    parent = artifacts.parent.resolve()
    before_artifacts = before_artifacts.resolve()
    assert before_artifacts.parent == parent and before_artifacts.is_dir()
    corpus = json.loads((ROOT / "tests" / "introduction_ideas_cases.json").read_text(encoding="utf-8"))
    snapshots = {}
    for mode, source in (("before", before_artifacts), ("after", artifacts)):
        captured = json.loads((source / f"{mode}-outputs.json").read_text(encoding="utf-8"))
        assert captured["javascriptErrors"] == []
        assert set(captured["records"]) == set(corpus["cases"])
        assert all(captured["records"][key]["text"] == text for key, text in corpus["cases"].items())
        snapshots[mode] = captured
    assert summary["browser_status"] == "PASS" and summary["protected_data_unchanged"]
    docs = ROOT / "docs"
    assert docs.is_dir() and (docs / "screenshots").is_dir()
    evidence = docs / "introduction_ideas_evidence"
    images = docs / "screenshots" / "introduction-ideas"
    evidence.mkdir(exist_ok=True)
    images.mkdir(exist_ok=True)
    manifest = []
    for mode, source in (("before", before_artifacts), ("after", artifacts)):
        shutil.copyfile(source / f"{mode}-outputs.json", evidence / f"{mode}-outputs.json")
        shutil.copyfile(source / "browser.log", evidence / f"{mode}-browser.log")
        names = [f"{mode}-{key}-desktop.png" for key in ("T01", "T03", "T04", "T05")]
        names.append(f"{mode}-T04-mobile.png")
        if mode == "after":
            names += ["after-student-framework-trace.png", "after-professor-framework-trace.png",
                      "after-professor-evidence-detail.png"]
        for name in names:
            shutil.copyfile(source / name, images / name)
            digest = hashlib.sha256((source / name).read_bytes()).hexdigest()
            assert hashlib.sha256((images / name).read_bytes()).hexdigest() == digest
            manifest.append({"file": str((images / name).relative_to(docs)).replace("\\", "/"),
                             "sha256": digest, "mode": mode})
    shutil.copyfile(artifacts / "verification-summary.json", evidence / "verification-summary.json")
    (evidence / "screenshots.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    comparison = ["# Actual T01–T13 before/after outputs", "",
                  "Generated from the real authenticated Chrome runs; the JSON snapshots retain the recorded metadata.", ""]
    for key, text in corpus["cases"].items():
        old, new = (snapshots[mode]["records"][key] for mode in ("before", "after"))
        item = new["instructional_feedback"]["items"][0]
        comparison += [f"## {key}", "", f"> {text}", "",
                       f"- Before: `{old['branch']}` — {old['trait']} / {old['skill']} / `{old['lesson']}`.",
                       f"- After: `{new['branch']}` — {new['trait']} / {new['skill']} / `{new['lesson']}`.",
                       f"- Actual condition: {item['selection_condition']}.",
                       f"- Purpose: `{item['feedback_purpose']}`.",
                       f"- Recorded strength: {item['working_text'] or 'None claimed.'}",
                       f"- Supporting Rule IDs: {', '.join('`' + rule + '`' for rule in item['rule_ids'])}.",
                       f"- Central candidates: {old['central_count']} → {new['central_count']}; qualifying predicates: {old['development_count']} → {new['development_count']}.", ""]
        for label in ("What I noticed", "Why it matters", "How to improve"):
            comparison += [f"**{label} — before:** {old['guidance'][label]}", "",
                           f"**{label} — after:** {new['guidance'][label]}", ""]
        for span in item["highlight_spans"]:
            comparison += [f"**Verified mark [{span['start']}, {span['end']}):** {span['text']}", "",
                           f"**Why this location:** {span['selection_reason']}", ""]
    (evidence / "case-comparison.md").write_text("\n".join(comparison), encoding="utf-8")
    print("Published verified evidence:", evidence)


def main():
    parent = Path(r"C:\Users\MYPC~1\AppData\Local\Temp\opencode")
    assert parent.is_dir()
    if "--capture-baseline" in sys.argv:
        from types import SimpleNamespace
        from tests.test_nlp_transparency import transparency_responses
        from copy import deepcopy
        directory = Path(tempfile.mkdtemp(prefix="ideas-protected-baseline-", dir=parent))
        response = transparency_responses.__wrapped__(SimpleNamespace(mktemp=lambda name: directory))["introduction_exact"]
        protected = {"analysis": deepcopy(response["analysis"]), "feedback": response["feedback"],
                     "feedback_decisions": response["research_trace"]["stages"]["INTRODUCTION"]["feedback_decisions"]}
        destination = ROOT / "tests" / "introduction_ideas_protected_baseline.json"
        assert not destination.exists(), "Do not overwrite the captured pre-change fixture"
        destination.write_text(json.dumps(protected, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("Captured actual pre-change protected API fields:", destination)
        return 0
    artifacts = Path(tempfile.mkdtemp(prefix="essayscaff-intro-ideas-", dir=parent))
    before = protected_files()
    app = create_app(EssayAnalysisService(), secret_key=secrets.token_hex(32))
    app.config.update(TESTING=True, DRAFT_DATABASE_PATH=str(artifacts / "isolated.sqlite3"))
    store = DraftStore(app.config["DRAFT_DATABASE_PATH"])
    password = secrets.token_urlsafe(24)
    store.create_user("ideas_student", generate_password_hash(password))
    store.create_teacher_user("ideas_teacher", generate_password_hash(password))
    server = make_server("127.0.0.1", 0, app, threaded=True)
    Thread(target=server.serve_forever, daemon=True).start()
    print(f"Artifacts: {artifacts}", flush=True)
    try:
        result = subprocess.run(["node", str(ROOT / "tests" / "introduction_ideas_browser_check.cjs"),
                                 f"http://127.0.0.1:{server.server_port}", str(artifacts),
                                 "before" if "--before" in sys.argv else "after"], cwd=ROOT,
                                env={**os.environ, "ESSAYSCAFF_IDEAS_PASSWORD": password},
                                capture_output=True, text=True, encoding="utf-8", timeout=240)
        (artifacts / "browser.log").write_text(result.stdout + result.stderr, encoding="utf-8")
        print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        assert before == protected_files(), "Original database/research files changed"
        with store._connection() as connection:
            counts = {t: connection.execute(f"SELECT count(*) FROM {t}").fetchone()[0]
                      for t in ("writing_sessions", "writing_revisions", "submissions")}
        assert all(n == 0 for n in counts.values())
        print("Protected data unchanged; isolated writing/revision/submission counts:", json.dumps(counts))
        if result.returncode == 0:
            summary = {"mode": "before" if "--before" in sys.argv else "after", "browser_status": "PASS",
                       "protected_data_unchanged": True, "protected_files_sha256": before,
                       "isolated_persistence_counts": counts}
            (artifacts / "verification-summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
            if "--publish-evidence" in sys.argv:
                assert summary["mode"] == "after", "Publish from an after run with the original before artifacts"
                index = sys.argv.index("--publish-evidence")
                assert len(sys.argv) > index + 1, "--publish-evidence requires the original before-artifact directory"
                publish_evidence(Path(sys.argv[index + 1]), artifacts, summary)
        return result.returncode
    finally:
        server.shutdown()


if __name__ == "__main__":
    raise SystemExit(main())
