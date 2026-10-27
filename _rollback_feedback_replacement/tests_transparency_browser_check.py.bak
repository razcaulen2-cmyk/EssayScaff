"""Optional real-Chrome verification; only temporary, isolated records are used.

Run: .venv\Scripts\python.exe tests/transparency_browser_check.py
Requires installed Chrome and Node (built-in CDP WebSocket); installs nothing.
Screenshots and the result log remain in the printed temporary artifact folder.
"""

import json
import os
from pathlib import Path
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
    artifacts = Path(tempfile.mkdtemp(prefix="essayscaff-transparency-", dir=temp_parent))
    app = create_app(analysis_service=EssayAnalysisService(), secret_key="isolated-browser-check")
    database = artifacts / "isolated.sqlite3"
    app.config.update(DRAFT_DATABASE_PATH=str(database), TESTING=True)
    store = DraftStore(str(database))
    store.create_user("browser_student", generate_password_hash("browser-password-1"))
    store.create_teacher_user("browser_teacher", generate_password_hash("browser-password-1"))
    server = make_server("127.0.0.1", 0, app, threaded=True)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    print(f"Artifacts: {artifacts}", flush=True)
    try:
        result = subprocess.run(
            ["node", str(ROOT / "tests" / "transparency_browser_check.cjs"),
             f"http://127.0.0.1:{server.server_port}", str(artifacts)],
             cwd=ROOT, capture_output=True, text=True, encoding="utf-8", timeout=300,
        )
        print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        # Analysis/inspection must not create writing, revision or submission rows.
        import sqlite3
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
