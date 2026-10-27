"""Real Chrome before/after explorer checks; production data and processing guarded."""

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


def backend_fingerprints():
    paths = [ROOT / "app.py", ROOT / "requirements.txt"]
    paths += sorted((ROOT / "services").glob("*.py"))
    paths += sorted((ROOT / "content").rglob("*.json"))
    return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    parent = Path(r"C:\Users\MYPC~1\AppData\Local\Temp\opencode")
    assert parent.is_dir()
    artifacts = Path(tempfile.mkdtemp(prefix="essayscaff-process-explorer-", dir=parent))
    print("Artifacts:", artifacts, flush=True)
    before, backend = protected_files(), backend_fingerprints()
    app = create_app(EssayAnalysisService(), secret_key=secrets.token_hex(32))
    app.config.update(TESTING=True, DRAFT_DATABASE_PATH=str(artifacts / "isolated.sqlite3"))
    store = DraftStore(app.config["DRAFT_DATABASE_PATH"])
    password = secrets.token_urlsafe(24)
    student = store.create_user("explorer_student", generate_password_hash(password))
    teacher = store.create_teacher_user("explorer_teacher", generate_password_hash(password))
    classroom = store.create_classroom(teacher["user_id"], "Explorer class", "English", "Explorer")
    store.join_classroom(student["user_id"], classroom["enrollment_code"])
    corpus = json.loads((ROOT / "tests" / "nlp_process_explorer_cases.json").read_text(encoding="utf-8"))
    for label in ("A", "B"):
        assignment = store.create_assignment(teacher["user_id"], classroom["classroom_id"], "Explorer assignment " + label,
                                             corpus["assignment_topic"], "Explain your view.", ", ".join(corpus["focus_terms"]))
        workspace = store.get_or_create_assignment_workspace(student["user_id"], assignment["assignment_id"])
        store.save({"assignment_topic": corpus["assignment_topic"], "focus_terms": ", ".join(corpus["focus_terms"]),
                    "introduction_text": corpus["introduction"] + (" Assignment B context." if label == "B" else ""),
                    "body_text": corpus["body"], "conclusion_text": corpus["conclusion"]},
                   workspace["draft"]["session_id"], student["user_id"], assignment["assignment_id"])
    mode = "before" if "--before" in sys.argv else "after"
    server = make_server("127.0.0.1", 0, app, threaded=True)
    Thread(target=server.serve_forever, daemon=True).start()
    try:
        result = subprocess.run(["node", str(ROOT / "tests" / "nlp_process_explorer_browser_check.cjs"),
                                 f"http://127.0.0.1:{server.server_port}", str(artifacts), mode], cwd=ROOT,
                                env={**os.environ, "ESSAYSCAFF_EXPLORER_PASSWORD": password}, capture_output=True,
                                text=True, encoding="utf-8", timeout=300)
        (artifacts / "browser.log").write_text(result.stdout + result.stderr, encoding="utf-8")
        print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        assert before == protected_files(), "Original database or research data changed"
        assert backend == backend_fingerprints(), "Frontend-only task changed backend processing/content"
        with store._connection() as connection:
            assert connection.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
            assert not connection.execute("PRAGMA foreign_key_check").fetchall()
            counts = {t: connection.execute(f"SELECT count(*) FROM {t}").fetchone()[0] for t in ("writing_sessions", "writing_revisions", "submissions")}
        assert counts == {"writing_sessions": 2 if mode == "before" else 3, "writing_revisions": 0, "submissions": 0}
        summary = {"mode": mode, "browser_exit_code": result.returncode, "protected_data_sha256": before,
                   "backend_sha256": backend, "isolated_counts": counts, "integrity": "ok", "foreign_key_violations": 0}
        (artifacts / "verification-summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
        if result.returncode == 0 and "--publish-evidence" in sys.argv:
            original = Path(sys.argv[sys.argv.index("--publish-evidence") + 1]).resolve()
            assert mode == "after" and original.parent == parent.resolve()
            old_summary = json.loads((original / "verification-summary.json").read_text(encoding="utf-8"))
            assert old_summary["browser_exit_code"] == 0
            assert old_summary["backend_sha256"] == backend and old_summary["protected_data_sha256"] == before
            old = json.loads((original / "before-outputs.json").read_text(encoding="utf-8"))
            new = json.loads((artifacts / "after-outputs.json").read_text(encoding="utf-8"))
            assert old["stable_records"] == new["stable_records"], "Cached analysis/export substance changed"
            evidence = ROOT / "docs" / "nlp_process_explorer_evidence"
            images = ROOT / "docs" / "screenshots" / "nlp-process-explorer"
            assert evidence.parent.is_dir() and images.parent.is_dir()
            evidence.mkdir(exist_ok=True)
            images.mkdir(exist_ok=True)
            manifest = []
            for phase, folder in (("before", original), ("after", artifacts)):
                for name in (f"{phase}-outputs.json", "browser.log", "verification-summary.json"):
                    shutil.copyfile(folder / name, evidence / (name if name.startswith(phase) else phase + "-" + name))
                for image in folder.glob(f"{phase}-*.png"):
                    shutil.copyfile(image, images / image.name)
                    digest = hashlib.sha256(image.read_bytes()).hexdigest()
                    assert hashlib.sha256((images / image.name).read_bytes()).hexdigest() == digest
                    manifest.append({"file": image.name, "sha256": digest})
            (evidence / "screenshots.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
            print("Published:", evidence)
        print("Protected backend/data unchanged; isolated persistence:", json.dumps(counts))
        return result.returncode
    finally:
        server.shutdown()


if __name__ == "__main__":
    raise SystemExit(main())
