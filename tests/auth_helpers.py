"""Small helpers for authenticated Flask API tests."""

import re


def form_csrf_token(response) -> str:
    match = re.search(r'name="csrf_token" value="([^"]+)"', response.get_data(as_text=True))
    assert match, "CSRF form token was not rendered"
    return match.group(1)


def register_student(client, username: str = "student_one", password: str = "student-password-1"):
    page = client.get("/register")
    response = client.post(
        "/register",
        data={
            "csrf_token": form_csrf_token(page),
            "username": username,
            "password": password,
            "confirm_password": password,
        },
        follow_redirects=False,
    )
    if response.status_code == 302:
        with client.session_transaction() as flask_session:
            client.environ_base["HTTP_X_CSRF_TOKEN"] = flask_session["_csrf_token"]
    return response


def login_student(client, username: str = "student_one", password: str = "student-password-1"):
    page = client.get("/login")
    response = client.post(
        "/login",
        data={
            "csrf_token": form_csrf_token(page),
            "username": username,
            "password": password,
        },
        follow_redirects=False,
    )
    if response.status_code == 302:
        with client.session_transaction() as flask_session:
            client.environ_base["HTTP_X_CSRF_TOKEN"] = flask_session["_csrf_token"]
    return response
