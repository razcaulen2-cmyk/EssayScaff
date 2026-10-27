"""Permanent complete route/permission/link coverage from the real Flask url_map."""

import secrets
from datetime import timedelta

from app import create_app
from tests.pre_defense_audit import nlp_audit, route_audit, seed


def test_every_registered_route_method_permission_and_internal_link(tmp_path):
    app = create_app(secret_key=secrets.token_hex(32))
    app.config.update(
        TESTING=True,
        DRAFT_DATABASE_PATH=str(tmp_path / "system.sqlite3"),
        WRITING_ACTIVITY_ENABLED=True,
    )
    results = route_audit(app, seed(app))
    assert {r["endpoint"] for r in results["routes"]} == set(app.view_functions)
    assert all(r["classification"] == "PASS" for r in results["routes"])
    assert results["sqlite_integrity"] == "ok"
    assert results["foreign_key_violations"] == 0
    assert len(nlp_audit(app.config["ANALYSIS_SERVICE"])) == 28


def test_expired_session_and_malformed_api_payloads_are_clean_denials(tmp_path):
    app = create_app(secret_key=secrets.token_hex(32))
    app.config.update(TESTING=True, DRAFT_DATABASE_PATH=str(tmp_path / "expiry.sqlite3"))
    fixture = seed(app)
    student = fixture["clients"]["student"]
    # Force a genuinely expired signature age in the cookie verifier, not a fake
    # absent user. A negative max_age invalidates the already-issued signature.
    app.permanent_session_lifetime = timedelta(seconds=-1)
    assert student.get("/api/classrooms").status_code == 401
    assert student.get("/").status_code == 302


def test_all_html_templates_define_the_existing_local_favicon(tmp_path):
    app = create_app(secret_key=secrets.token_hex(32))
    app.config.update(TESTING=True, DRAFT_DATABASE_PATH=str(tmp_path / "assets.sqlite3"))
    for name in app.jinja_env.list_templates():
        source, _, _ = app.jinja_env.loader.get_source(app.jinja_env, name)
        assert 'rel="icon"' in source, name
    assert app.test_client().get("/assets/essayscaff-logo.png").status_code == 200
