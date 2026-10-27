"""Capture screenshots for the end-to-end process walkthrough.

Run: .venv\\Scripts\\python.exe tests/process_walkthrough_capture.py
Uses a temporary SQLite database and a temporary Chrome profile. It never
opens the real application database and never saves student writing.
Screenshots and the recorded response JSON stay in the printed temp folder.
"""

import json
import os
from pathlib import Path
import sqlite3
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


def main():
    temp_parent = Path(os.environ["LOCALAPPDATA"]) / "Temp" / "opencode"
    if not temp_parent.is_dir():
        raise RuntimeError("The approved temporary parent directory must exist.")
    artifacts = Path(tempfile.mkdtemp(prefix="essayscaff-walkthrough-", dir=temp_parent))
    app = create_app(analysis_service=EssayAnalysisService(), secret_key="isolated-walkthrough")
    database = artifacts / "isolated.sqlite3"
    app.config.update(DRAFT_DATABASE_PATH=str(database), TESTING=True)
    store = DraftStore(str(database))
    store.create_user("walkthrough_student", generate_password_hash("walkthrough-password-1"))
    server = make_server("127.0.0.1", 0, app, threaded=True)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    print(f"Artifacts: {artifacts}", flush=True)
    try:
        result = subprocess.run(
            ["node", str(ROOT / "tests" / "process_walkthrough_capture.cjs"),
             f"http://127.0.0.1:{server.server_port}", str(artifacts)],
            cwd=ROOT, capture_output=True, text=True, encoding="utf-8", timeout=600,
        )
        print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        with sqlite3.connect(database) as connection:
            counts = {table: connection.execute(f"SELECT count(*) FROM {table}").fetchone()[0]
                      for table in ("writing_sessions", "writing_revisions", "submissions")}
        print("Isolated persistence counts:", json.dumps(counts))
        assert counts == {table: 0 for table in counts}
        return result.returncode
    finally:
        server.shutdown()


if __name__ == "__main__":
    raise SystemExit(main())
