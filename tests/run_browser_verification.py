"""Launch Flask and run real Chrome browser verification for reason clause highlighting."""
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


def run(output_dir: str | Path | None = None) -> int:
    if output_dir is None:
        output_dir = Path(r"C:\Users\My Pc\.gemini\antigravity\brain\0fc93177-b1ba-4575-a385-d2524318ca88")
    else:
        output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    db_path = output_dir / "isolated_browser_test.sqlite3"
    if db_path.exists():
        try:
            db_path.unlink()
        except OSError:
            pass

    app = create_app(analysis_service=EssayAnalysisService(), secret_key="isolated-browser-check")
    app.config.update(DRAFT_DATABASE_PATH=str(db_path), TESTING=True)
    store = DraftStore(str(db_path))
    store.create_user("student1", generate_password_hash("password123"))

    server = make_server("127.0.0.1", 0, app, threaded=True)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    origin = f"http://127.0.0.1:{server.server_port}"
    print(f"Flask test server started at {origin}", flush=True)

    try:
        result = subprocess.run(
            ["node", str(ROOT / "tests" / "browser_reason_verification.cjs"), origin, str(output_dir)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=180,
        )
        print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        return result.returncode
    finally:
        server.shutdown()


if __name__ == "__main__":
    sys.exit(run())
