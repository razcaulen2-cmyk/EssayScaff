"""Create a teacher account with the local, password-prompting setup tool."""

import re
import sqlite3
from getpass import getpass
from pathlib import Path

from werkzeug.security import generate_password_hash

from services.draft_store import DraftStore


USERNAME_PATTERN = re.compile(r"[A-Za-z0-9_]{3,32}\Z")
DATABASE_PATH = Path(__file__).resolve().parent / "instance" / "essay_scaff_drafts.sqlite3"


def main() -> int:
    username = input("Teacher username (3–32 letters, numbers, underscores): ").strip()
    if USERNAME_PATTERN.fullmatch(username) is None:
        print("Invalid username format.")
        return 1

    password = getpass("Teacher password (8–128 characters): ")
    confirmation = getpass("Confirm teacher password: ")
    if not 8 <= len(password) <= 128:
        print("Password must be between 8 and 128 characters.")
        return 1
    if password != confirmation:
        print("Passwords do not match.")
        return 1

    try:
        DraftStore(DATABASE_PATH).create_teacher_user(username, generate_password_hash(password))
    except sqlite3.IntegrityError:
        print("That username is already in use.")
        return 1
    except (OSError, sqlite3.Error):
        print("Teacher account could not be created. Check the local database and try again.")
        return 1

    print("Teacher account created.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
