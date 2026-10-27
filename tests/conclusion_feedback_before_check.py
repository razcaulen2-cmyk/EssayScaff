"""Reproduce the pre-correction Conclusion UI in isolated Chrome, then restore app.js."""

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

REVERTS = [
    (
        '  const branches = STAGE_PROGRESS_NEUTRAL_BRANCHES[result?.stage_id] || [];\n'
        '  return Boolean(chosen?.branch && branches.includes(chosen.branch));\n',
        '  if (result?.stage_id !== "INTRODUCTION") return false;\n'
        '  const branches = STAGE_PROGRESS_NEUTRAL_BRANCHES[result?.stage_id] || [];\n'
        '  return Boolean(chosen?.branch && branches.includes(chosen.branch));\n',
    ),
    (
        '    const highlightDependent = /\\bhighlighted\\b/i.test(tutor.task) && !excerpt;\n'
        '    taskText = highlightDependent && tutor.task_fallback ? tutor.task_fallback : fillTutorTemplate(tutor.task, slots);\n',
        '    taskText = fillTutorTemplate(tutor.task, slots);\n',
    ),
    (
        '    if (!items[0].working_text) items[0].working_text = recordedWorkingObservation(result, items[0].rule_ids);\n',
        '',
    ),
    (
        '    if (!excerpt && tutor?.task_fallback && /\\bhighlighted\\b/i.test(taskText)) taskText = tutor.task_fallback;\n',
        '',
    ),
]


def main():
    parent = Path(tempfile.gettempdir())
    artifacts = Path(tempfile.mkdtemp(prefix="essayscaff-conclusion-before-", dir=parent))
    source = ROOT / "static" / "app.js"
    original_bytes = source.read_bytes()
    original = original_bytes.decode("utf-8")
    original_hash = hashlib.sha256(original_bytes).hexdigest()
    patched = original
    for old, new in REVERTS:
        assert patched.count(old) == 1, f"revert target not unique: {old[:60]!r}"
        patched = patched.replace(old, new)
    before = protected_files()

    app = create_app(EssayAnalysisService(), secret_key=secrets.token_hex(32))
    app.config.update(TESTING=True, DRAFT_DATABASE_PATH=str(artifacts / "isolated.sqlite3"))
    store = DraftStore(app.config["DRAFT_DATABASE_PATH"])
    password = secrets.token_urlsafe(24)
    store.create_user("conclusion_student", generate_password_hash(password))
    server = make_server("127.0.0.1", 0, app, threaded=True)
    Thread(target=server.serve_forever, daemon=True).start()
    print(f"Artifacts: {artifacts}", flush=True)
    try:
        source.write_bytes(patched.encode("utf-8"))
        result = subprocess.run(
            ["node", str(ROOT / "tests" / "conclusion_feedback_before_check.cjs"),
             f"http://127.0.0.1:{server.server_port}", str(artifacts)],
            cwd=ROOT,
            env={**os.environ, "ESSAYSCAFF_CONCLUSION_PASSWORD": password},
            capture_output=True, text=True, encoding="utf-8", timeout=240,
        )
        (artifacts / "browser.log").write_text(result.stdout + result.stderr, encoding="utf-8")
        print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
    finally:
        source.write_bytes(original_bytes)
        server.shutdown()

    assert hashlib.sha256(source.read_bytes()).hexdigest() == original_hash
    assert before == protected_files(), "Original database/research/static files changed"
    with store._connection() as connection:
        counts = {table: connection.execute(f"SELECT count(*) FROM {table}").fetchone()[0]
                  for table in ("writing_sessions", "writing_revisions", "submissions")}
    assert all(count == 0 for count in counts.values()), counts
    if result.returncode != 0:
        return result.returncode

    captured = json.loads((artifacts / "before-outputs.json").read_text(encoding="utf-8"))
    assert captured["javascriptErrors"] == []
    assert captured["branch"] == "conclusion_ideas_bring_together"
    assert captured["status"] == "PREPARED_INLINE_GUIDANCE", captured["status"]
    assert captured["dimension"] == "Ideas" and captured["skill"] == "Bring Ideas Together"
    assert "highlighted" in captured["tutorItems"][0]["task"].lower()
    assert captured["dom"]["editorMarks"] == [] and captured["dom"]["tutorMarks"] == []
    assert captured["dom"]["stageTitle"] == "No Specific Writing Issue Detected"
    assert captured["dom"]["stageBadge"] == "NO_ISSUE"
    print("Reproduced contradiction: corrective tutor references a highlight; Stage Progress reports no issue.")

    images = ROOT / "docs" / "screenshots" / "conclusion-feedback-correction"
    evidence = ROOT / "docs" / "conclusion_feedback_correction_evidence"
    images.mkdir(parents=True, exist_ok=True)
    evidence.mkdir(exist_ok=True)
    for name in sorted(artifacts.glob("before-*.png")):
        shutil.copyfile(name, images / name.name)
    shutil.copyfile(artifacts / "before-outputs.json", evidence / "before-outputs.json")
    shutil.copyfile(artifacts / "browser.log", evidence / "before-browser.log")
    summary = {"browser_status": "PASS", "reproduction": True, "protected_data_unchanged": True,
               "protected_files_sha256": before, "isolated_persistence_counts": counts}
    (evidence / "before-verification-summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print("Published before evidence:", evidence)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
