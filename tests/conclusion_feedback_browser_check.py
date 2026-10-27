"""Isolated actual-Chrome verification for the Conclusion feedback correction."""

import json
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
    parent = Path(tempfile.gettempdir())
    artifacts = Path(tempfile.mkdtemp(prefix="essayscaff-conclusion-", dir=parent))
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
        result = subprocess.run(
            ["node", str(ROOT / "tests" / "conclusion_feedback_browser_check.cjs"),
             f"http://127.0.0.1:{server.server_port}", str(artifacts)],
            cwd=ROOT,
            env={**__import__("os").environ, "ESSAYSCAFF_CONCLUSION_PASSWORD": password},
            capture_output=True, text=True, encoding="utf-8", timeout=240,
        )
        (artifacts / "browser.log").write_text(result.stdout + result.stderr, encoding="utf-8")
        print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        assert before == protected_files(), "Original database/research files changed"
        with store._connection() as connection:
            counts = {table: connection.execute(f"SELECT count(*) FROM {table}").fetchone()[0]
                      for table in ("writing_sessions", "writing_revisions", "submissions")}
        assert all(count == 0 for count in counts.values()), counts
        print("Protected data unchanged; isolated writing/revision/submission counts:", json.dumps(counts))
        if result.returncode != 0:
            return result.returncode
        summary = {"browser_status": "PASS", "protected_data_unchanged": True,
                   "protected_files_sha256": before, "isolated_persistence_counts": counts}
        (artifacts / "verification-summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

        images = ROOT / "docs" / "screenshots" / "conclusion-feedback-correction"
        evidence = ROOT / "docs" / "conclusion_feedback_correction_evidence"
        images.mkdir(parents=True, exist_ok=True)
        evidence.mkdir(exist_ok=True)
        for name in sorted(artifacts.glob("after-*.png")):
            shutil.copyfile(name, images / name.name)
        shutil.copyfile(artifacts / "after-outputs.json", evidence / "after-outputs.json")
        shutil.copyfile(artifacts / "browser.log", evidence / "browser.log")
        shutil.copyfile(artifacts / "verification-summary.json", evidence / "verification-summary.json")
        print("Published evidence:", evidence)
        return 0
    finally:
        server.shutdown()


if __name__ == "__main__":
    raise SystemExit(main())
