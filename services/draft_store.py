"""Small SQLite store for one editable writing session per browser ID."""

import hashlib
import json
import sqlite3
import secrets
import string
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator
from uuid import uuid4


STAGE_PROGRESS_FIELDS = (
    ("Introduction", "introduction_text"),
    ("Body", "body_text"),
    ("Conclusion", "conclusion_text"),
)
STAGE_ACTIVITY_IDS = {
    "Introduction": "INTRODUCTION",
    "Body": "BODY",
    "Conclusion": "CONCLUSION",
}
WRITING_ACTIVITY_BUCKET_SECONDS = 5
WRITING_ACTIVITY_MAX_EVENT_SECONDS = 5
WRITING_ACTIVITY_MAX_AGE_SECONDS = 600
WRITING_ACTIVITY_FUTURE_TOLERANCE_SECONDS = 30
WRITING_ACTIVITY_MAX_EVENTS_PER_REQUEST = 24


class DraftNotFoundError(Exception):
    """Raised when an update or restore references an unknown session ID."""


class AssignmentNotFoundError(Exception):
    """Raised when a writing assignment cannot be found."""


class AssignmentDeletedError(Exception):
    """Raised when an archived assignment is used for new student work."""


class AssignmentLockedError(Exception):
    """Raised when task-defining fields are changed after student work exists."""


class ClassroomNotFoundError(Exception):
    """Raised when a classroom is missing or not owned/enrolled as requested."""


class DuplicateEnrollmentError(Exception):
    """Raised when a student has already joined a classroom."""


class IncompleteEssayError(Exception):
    """Raised when a saved essay is missing one or more writing sections."""


class AlreadySubmittedError(Exception):
    """Raised when a student attempts a second submission for an assignment."""


class SubmittedAssignmentError(Exception):
    """Raised when writing or revisions are changed after final submission."""


class UnsavedDraftError(Exception):
    """Raised when a submission request uses a stale saved-draft version."""


class DraftStore:
    """Persist current drafts and immutable revision snapshots in one database."""

    def __init__(
        self,
        database_path: str | Path,
        enable_activity_tracking: bool = False,
    ) -> None:
        self.database_path = str(database_path)
        self.activity_tracking_enabled = bool(enable_activity_tracking)
        Path(self.database_path).parent.mkdir(parents=True, exist_ok=True)
        with self._connection() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL COLLATE NOCASE UNIQUE,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL DEFAULT 'STUDENT',
                    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS classrooms (
                    classroom_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    teacher_user_id INTEGER NOT NULL REFERENCES users(user_id),
                    classroom_name TEXT NOT NULL,
                    subject TEXT NOT NULL,
                    section TEXT NOT NULL,
                    enrollment_code TEXT NOT NULL UNIQUE,
                    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS assignments (
                    assignment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    teacher_user_id INTEGER NOT NULL REFERENCES users(user_id),
                    classroom_id INTEGER REFERENCES classrooms(classroom_id),
                    title TEXT NOT NULL,
                    topic TEXT NOT NULL,
                    instructions TEXT NOT NULL,
                    focus_terms TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
                    deleted_at TEXT
                )
                """
            )
            assignment_columns = {
                row[1] for row in connection.execute("PRAGMA table_info(assignments)")
            }
            if "classroom_id" not in assignment_columns:
                # Phase 6B assignments stay teacher-owned but unassigned until explicitly reassigned.
                connection.execute(
                    "ALTER TABLE assignments ADD COLUMN classroom_id INTEGER REFERENCES classrooms(classroom_id)"
                )
            if "deleted_at" not in assignment_columns:
                connection.execute("ALTER TABLE assignments ADD COLUMN deleted_at TEXT")
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS classroom_enrollments (
                    classroom_id INTEGER NOT NULL REFERENCES classrooms(classroom_id),
                    student_user_id INTEGER NOT NULL REFERENCES users(user_id),
                    enrolled_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
                    PRIMARY KEY (classroom_id, student_user_id)
                )
                """
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS classroom_enrollments_student ON classroom_enrollments(student_user_id)"
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS writing_sessions (
                    session_id TEXT PRIMARY KEY,
                    user_id INTEGER REFERENCES users(user_id),
                    assignment_id INTEGER REFERENCES assignments(assignment_id),
                    assignment_topic TEXT NOT NULL,
                    focus_terms TEXT NOT NULL,
                    introduction_text TEXT NOT NULL,
                    body_text TEXT NOT NULL,
                    conclusion_text TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
                    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
                )
                """
            )
            session_columns = {
                row[1] for row in connection.execute("PRAGMA table_info(writing_sessions)")
            }
            if "user_id" not in session_columns:
                # Old browser-ID sessions remain NULL-owned; no student is assigned implicitly.
                connection.execute(
                    "ALTER TABLE writing_sessions ADD COLUMN user_id INTEGER REFERENCES users(user_id)"
                )
            if "assignment_id" not in session_columns:
                connection.execute(
                    "ALTER TABLE writing_sessions ADD COLUMN assignment_id INTEGER REFERENCES assignments(assignment_id)"
                )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS writing_sessions_user_id ON writing_sessions(user_id)"
            )
            connection.execute(
                """
                CREATE UNIQUE INDEX IF NOT EXISTS writing_sessions_unique_assignment_owner
                ON writing_sessions(user_id, assignment_id)
                WHERE user_id IS NOT NULL AND assignment_id IS NOT NULL
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS writing_revisions (
                    revision_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    revision_number INTEGER NOT NULL,
                    assignment_topic TEXT NOT NULL,
                    focus_terms TEXT NOT NULL,
                    introduction_text TEXT NOT NULL,
                    body_text TEXT NOT NULL,
                    conclusion_text TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
                    UNIQUE (session_id, revision_number),
                    FOREIGN KEY (session_id) REFERENCES writing_sessions(session_id)
                )
                """
            )
            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS writing_revisions_session_order
                ON writing_revisions(session_id, revision_number DESC)
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS submissions (
                    submission_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_user_id INTEGER NOT NULL REFERENCES users(user_id),
                    assignment_id INTEGER NOT NULL REFERENCES assignments(assignment_id),
                    session_id TEXT NOT NULL REFERENCES writing_sessions(session_id),
                    introduction_snapshot TEXT NOT NULL,
                    body_snapshot TEXT NOT NULL,
                    conclusion_snapshot TEXT NOT NULL,
                    submitted_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
                    UNIQUE (student_user_id, assignment_id)
                )
                """
            )
            connection.execute(
                """
                CREATE UNIQUE INDEX IF NOT EXISTS submissions_unique_student_assignment
                ON submissions(student_user_id, assignment_id)
                """
            )
            if self.activity_tracking_enabled:
                self._ensure_writing_activity_schema(connection)

    @staticmethod
    def _ensure_writing_activity_schema(connection: sqlite3.Connection) -> None:
        """Create the opt-in activity table only when tracking is explicitly enabled."""
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS writing_activity (
                activity_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL REFERENCES users(user_id),
                assignment_id INTEGER NOT NULL REFERENCES assignments(assignment_id),
                session_id TEXT NOT NULL REFERENCES writing_sessions(session_id),
                stage TEXT NOT NULL CHECK (stage IN ('INTRODUCTION', 'BODY', 'CONCLUSION')),
                bucket_start INTEGER NOT NULL,
                seconds INTEGER NOT NULL CHECK (seconds BETWEEN 1 AND 5),
                recorded_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
                UNIQUE (user_id, assignment_id, bucket_start)
            )
            """
        )
        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS writing_activity_assignment_student
            ON writing_activity(assignment_id, user_id)
            """
        )

    @contextmanager
    def _connection(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        try:
            connection.execute("PRAGMA foreign_keys = ON")
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def save(
        self,
        draft: dict[str, str],
        session_id: str | None = None,
        user_id: int | None = None,
        assignment_id: int | None = None,
    ) -> dict[str, Any]:
        if session_id is None:
            session_id = uuid4().hex
            with self._connection() as connection:
                self._ensure_assignment_active(connection, assignment_id)
                self._ensure_not_submitted(connection, user_id, assignment_id)
                connection.execute(
                    """
                    INSERT INTO writing_sessions (
                        session_id, user_id, assignment_id, assignment_topic, focus_terms,
                        introduction_text, body_text, conclusion_text
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        session_id,
                        user_id,
                        assignment_id,
                        draft["assignment_topic"],
                        draft["focus_terms"],
                        draft["introduction_text"],
                        draft["body_text"],
                        draft["conclusion_text"],
                    ),
                )
        else:
            with self._connection() as connection:
                self._ensure_assignment_active(connection, assignment_id)
                self._ensure_not_submitted(connection, user_id, assignment_id)
                cursor = connection.execute(
                    """
                    UPDATE writing_sessions
                    SET assignment_topic = ?, focus_terms = ?,
                        introduction_text = ?, body_text = ?, conclusion_text = ?,
                        updated_at = strftime('%Y-%m-%dT%H:%M:%fZ', 'now')
                    WHERE session_id = ? AND user_id IS ? AND assignment_id IS ?
                    """,
                    (
                        draft["assignment_topic"],
                        draft["focus_terms"],
                        draft["introduction_text"],
                        draft["body_text"],
                        draft["conclusion_text"],
                        session_id,
                        user_id,
                        assignment_id,
                    ),
                )
                if cursor.rowcount == 0:
                    raise DraftNotFoundError(session_id)

        restored = self.get(session_id, user_id, assignment_id)
        if restored is None:
            raise DraftNotFoundError(session_id)
        return restored

    def get(
        self,
        session_id: str,
        user_id: int | None = None,
        assignment_id: int | None = None,
    ) -> dict[str, Any] | None:
        with self._connection() as connection:
            row = connection.execute(
                """
                SELECT * FROM writing_sessions
                WHERE session_id = ? AND user_id IS ? AND assignment_id IS ?
                """,
                (session_id, user_id, assignment_id),
            ).fetchone()
        return dict(row) if row is not None else None

    def create_user(
        self, username: str, password_hash: str, role: str = "STUDENT"
    ) -> dict[str, Any]:
        if role not in {"STUDENT", "TEACHER"}:
            raise ValueError("Public accounts may only be Students or Teachers")
        with self._connection() as connection:
            cursor = connection.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                (username, password_hash, role),
            )
            user_id = cursor.lastrowid
        user = self.get_user(user_id)
        if user is None:
            raise RuntimeError("Created user could not be loaded")
        return user

    def create_teacher_user(self, username: str, password_hash: str) -> dict[str, Any]:
        """Create a teacher account for the local command-line setup tool."""
        with self._connection() as connection:
            cursor = connection.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (?, ?, 'TEACHER')",
                (username, password_hash),
            )
            user_id = cursor.lastrowid
        teacher = self.get_user(user_id)
        if teacher is None:
            raise RuntimeError("Created teacher account could not be loaded")
        return teacher

    def delete_user_and_linked_records(self, user_id: int) -> dict[str, int]:
        """Permanently delete one account and its directly associated writing records.

        Teacher deletion also removes their classrooms and assignments, along with
        student work associated with those assignments. All operations are explicit
        and ordered inside one transaction because the schema intentionally has no
        cascading delete constraints.
        """
        with self._connection() as connection:
            connection.execute("BEGIN IMMEDIATE")
            user = connection.execute(
                "SELECT role FROM users WHERE user_id = ?", (user_id,)
            ).fetchone()
            if user is None:
                raise KeyError(user_id)

            classroom_ids: list[int] = []
            assignment_ids: list[int] = []
            if user["role"] == "TEACHER":
                classroom_ids = [
                    row["classroom_id"]
                    for row in connection.execute(
                        "SELECT classroom_id FROM classrooms WHERE teacher_user_id = ?",
                        (user_id,),
                    )
                ]
                classroom_sql = ",".join("?" for _ in classroom_ids) or "NULL"
                assignment_ids = [
                    row["assignment_id"]
                    for row in connection.execute(
                        f"SELECT assignment_id FROM assignments WHERE teacher_user_id = ? OR classroom_id IN ({classroom_sql})",
                        (user_id, *classroom_ids),
                    )
                ]

            assignment_sql = ",".join("?" for _ in assignment_ids) or "NULL"
            session_ids = [
                row["session_id"]
                for row in connection.execute(
                    f"SELECT session_id FROM writing_sessions WHERE user_id = ? OR assignment_id IN ({assignment_sql})",
                    (user_id, *assignment_ids),
                )
            ]
            removed: dict[str, int] = {}

            session_sql = ",".join("?" for _ in session_ids) or "NULL"
            if session_ids:
                cursor = connection.execute(
                    f"DELETE FROM writing_revisions WHERE session_id IN ({session_sql})",
                    tuple(session_ids),
                )
                removed["revisions"] = cursor.rowcount
            else:
                removed["revisions"] = 0

            cursor = connection.execute(
                f"DELETE FROM submissions WHERE student_user_id = ? OR assignment_id IN ({assignment_sql})",
                (user_id, *assignment_ids),
            )
            removed["submissions"] = cursor.rowcount
            activity_table = connection.execute(
                "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'writing_activity'"
            ).fetchone()
            if activity_table is not None:
                cursor = connection.execute(
                    f"DELETE FROM writing_activity WHERE user_id = ? OR assignment_id IN ({assignment_sql})",
                    (user_id, *assignment_ids),
                )
                removed["activity"] = cursor.rowcount
            cursor = connection.execute(
                f"DELETE FROM writing_sessions WHERE user_id = ? OR assignment_id IN ({assignment_sql})",
                (user_id, *assignment_ids),
            )
            removed["writing_sessions"] = cursor.rowcount

            if classroom_ids:
                classroom_sql = ",".join("?" for _ in classroom_ids)
                cursor = connection.execute(
                    f"DELETE FROM classroom_enrollments WHERE student_user_id = ? OR classroom_id IN ({classroom_sql})",
                    (user_id, *classroom_ids),
                )
            else:
                cursor = connection.execute(
                    "DELETE FROM classroom_enrollments WHERE student_user_id = ?",
                    (user_id,),
                )
            removed["enrollments"] = cursor.rowcount

            cursor = connection.execute(
                f"DELETE FROM assignments WHERE teacher_user_id = ? OR assignment_id IN ({assignment_sql})",
                (user_id, *assignment_ids),
            )
            removed["assignments"] = cursor.rowcount
            cursor = connection.execute(
                "DELETE FROM classrooms WHERE teacher_user_id = ?", (user_id,)
            )
            removed["classrooms"] = cursor.rowcount
            cursor = connection.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
            if cursor.rowcount != 1:
                raise KeyError(user_id)
            removed["users"] = cursor.rowcount
        return removed

    def create_classroom(
        self, teacher_user_id: int, classroom_name: str, subject: str, section: str
    ) -> dict[str, Any]:
        teacher = self.get_user(teacher_user_id)
        if teacher is None or teacher["role"] != "TEACHER":
            raise ClassroomNotFoundError(teacher_user_id)
        alphabet = string.ascii_uppercase + "23456789"
        for _attempt in range(5):
            enrollment_code = "".join(secrets.choice(alphabet) for _ in range(10))
            try:
                with self._connection() as connection:
                    cursor = connection.execute(
                        """
                        INSERT INTO classrooms (
                            teacher_user_id, classroom_name, subject, section, enrollment_code
                        ) VALUES (?, ?, ?, ?, ?)
                        """,
                        (teacher_user_id, classroom_name, subject, section, enrollment_code),
                    )
                    row = connection.execute(
                        "SELECT * FROM classrooms WHERE classroom_id = ?", (cursor.lastrowid,)
                    ).fetchone()
                return dict(row)
            except sqlite3.IntegrityError:
                # A code collision is extraordinarily unlikely; try a new secure code.
                continue
        raise sqlite3.IntegrityError("Could not generate a unique classroom enrollment code")

    def list_teacher_classrooms(self, teacher_user_id: int) -> list[dict[str, Any]]:
        with self._connection() as connection:
            rows = connection.execute(
                """
                SELECT classrooms.*,
                    (SELECT COUNT(*) FROM classroom_enrollments AS enrollments
                     WHERE enrollments.classroom_id = classrooms.classroom_id) AS student_count,
                    (SELECT COUNT(*) FROM assignments
                     WHERE assignments.classroom_id = classrooms.classroom_id
                        AND assignments.deleted_at IS NULL) AS assignment_count
                FROM classrooms
                WHERE teacher_user_id = ?
                ORDER BY classroom_id DESC
                """,
                (teacher_user_id,),
            ).fetchall()
        return [dict(row) for row in rows]

    def list_teacher_classroom_students(
        self, teacher_user_id: int, classroom_id: int
    ) -> list[dict[str, Any]]:
        with self._connection() as connection:
            if connection.execute(
                "SELECT 1 FROM classrooms WHERE classroom_id = ? AND teacher_user_id = ?",
                (classroom_id, teacher_user_id),
            ).fetchone() is None:
                raise ClassroomNotFoundError(classroom_id)
            rows = connection.execute(
                """
                SELECT users.user_id, users.username, classroom_enrollments.enrolled_at
                FROM classroom_enrollments
                JOIN users ON users.user_id = classroom_enrollments.student_user_id
                WHERE classroom_enrollments.classroom_id = ?
                ORDER BY users.username COLLATE NOCASE
                """,
                (classroom_id,),
            ).fetchall()
        return [dict(row) for row in rows]

    def list_teacher_classroom_assignments(
        self, teacher_user_id: int, classroom_id: int
    ) -> list[dict[str, Any]]:
        with self._connection() as connection:
            if connection.execute(
                "SELECT 1 FROM classrooms WHERE classroom_id = ? AND teacher_user_id = ?",
                (classroom_id, teacher_user_id),
            ).fetchone() is None:
                raise ClassroomNotFoundError(classroom_id)
            rows = connection.execute(
                "SELECT * FROM assignments WHERE classroom_id = ? AND deleted_at IS NULL ORDER BY assignment_id DESC",
                (classroom_id,),
            ).fetchall()
        return [dict(row) for row in rows]

    def list_teacher_deleted_assignments(self, teacher_user_id: int) -> list[dict[str, Any]]:
        """Return archived assignments for their owning teacher only."""
        with self._connection() as connection:
            rows = connection.execute(
                """
                SELECT assignments.*, classrooms.classroom_name, classrooms.section
                FROM assignments
                LEFT JOIN classrooms ON classrooms.classroom_id = assignments.classroom_id
                WHERE assignments.teacher_user_id = ? AND assignments.deleted_at IS NOT NULL
                ORDER BY assignments.deleted_at DESC, assignments.assignment_id DESC
                """,
                (teacher_user_id,),
            ).fetchall()
        return [dict(row) for row in rows]

    def get_teacher_assignment_for_edit(
        self, teacher_user_id: int, assignment_id: int
    ) -> dict[str, Any] | None:
        with self._connection() as connection:
            row = connection.execute(
                """
                SELECT * FROM assignments
                WHERE assignment_id = ? AND teacher_user_id = ? AND deleted_at IS NULL
                """,
                (assignment_id, teacher_user_id),
            ).fetchone()
            if row is None:
                return None
            assignment = dict(row)
            assignment["has_student_work"] = self._assignment_has_student_work(
                connection, assignment_id
            )
        return assignment

    @staticmethod
    def _assignment_has_student_work(
        connection: sqlite3.Connection, assignment_id: int
    ) -> bool:
        row = connection.execute(
            """
            SELECT
                EXISTS(
                    SELECT 1 FROM writing_sessions
                    WHERE assignment_id = ? AND (
                        trim(introduction_text) <> '' OR
                        trim(body_text) <> '' OR
                        trim(conclusion_text) <> ''
                    )
                ) OR EXISTS(
                    SELECT 1 FROM writing_revisions
                    JOIN writing_sessions ON writing_sessions.session_id = writing_revisions.session_id
                    WHERE writing_sessions.assignment_id = ?
                ) OR EXISTS(
                    SELECT 1 FROM submissions WHERE assignment_id = ?
                ) AS has_student_work
            """,
            (assignment_id, assignment_id, assignment_id),
        ).fetchone()
        return bool(row["has_student_work"])

    def assignment_has_student_work(self, assignment_id: int) -> bool:
        with self._connection() as connection:
            return self._assignment_has_student_work(connection, assignment_id)

    def update_assignment(
        self,
        teacher_user_id: int,
        assignment_id: int,
        title: str,
        topic: str,
        instructions: str,
        focus_terms: str,
    ) -> dict[str, Any]:
        """Update one owned active assignment, locking task fields once work exists."""
        with self._connection() as connection:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute(
                """
                SELECT * FROM assignments
                WHERE assignment_id = ? AND teacher_user_id = ?
                """,
                (assignment_id, teacher_user_id),
            ).fetchone()
            if row is None:
                raise AssignmentNotFoundError(assignment_id)
            current = dict(row)
            if current["deleted_at"] is not None:
                raise AssignmentDeletedError(assignment_id)
            has_student_work = self._assignment_has_student_work(connection, assignment_id)
            task_fields = ("topic", "instructions", "focus_terms")
            if has_student_work and any(current[field] != value for field, value in zip(task_fields, (topic, instructions, focus_terms))):
                raise AssignmentLockedError(assignment_id)
            connection.execute(
                """
                UPDATE assignments
                SET title = ?, topic = ?, instructions = ?, focus_terms = ?
                WHERE assignment_id = ? AND teacher_user_id = ? AND deleted_at IS NULL
                """,
                (title, topic, instructions, focus_terms, assignment_id, teacher_user_id),
            )
            updated = connection.execute(
                "SELECT * FROM assignments WHERE assignment_id = ?", (assignment_id,)
            ).fetchone()
        return dict(updated)

    def soft_delete_assignment(self, teacher_user_id: int, assignment_id: int) -> None:
        """Archive an assignment without deleting its writing or related records."""
        with self._connection() as connection:
            cursor = connection.execute(
                """
                UPDATE assignments
                SET deleted_at = strftime('%Y-%m-%dT%H:%M:%fZ', 'now')
                WHERE assignment_id = ? AND teacher_user_id = ? AND deleted_at IS NULL
                """,
                (assignment_id, teacher_user_id),
            )
            if cursor.rowcount == 0:
                existing = connection.execute(
                    "SELECT 1 FROM assignments WHERE assignment_id = ? AND teacher_user_id = ?",
                    (assignment_id, teacher_user_id),
                ).fetchone()
                if existing is None:
                    raise AssignmentNotFoundError(assignment_id)

    def list_unassigned_teacher_assignments(self, teacher_user_id: int) -> list[dict[str, Any]]:
        with self._connection() as connection:
            rows = connection.execute(
                """
                SELECT * FROM assignments
                WHERE teacher_user_id = ? AND classroom_id IS NULL AND deleted_at IS NULL
                ORDER BY assignment_id DESC
                """,
                (teacher_user_id,),
            ).fetchall()
        return [dict(row) for row in rows]

    def assign_existing_assignment_to_classroom(
        self, teacher_user_id: int, assignment_id: int, classroom_id: int
    ) -> None:
        with self._connection() as connection:
            if connection.execute(
                "SELECT 1 FROM classrooms WHERE classroom_id = ? AND teacher_user_id = ?",
                (classroom_id, teacher_user_id),
            ).fetchone() is None:
                raise ClassroomNotFoundError(classroom_id)
            cursor = connection.execute(
                """
                UPDATE assignments SET classroom_id = ?
                WHERE assignment_id = ? AND teacher_user_id = ? AND classroom_id IS NULL
                """,
                (classroom_id, assignment_id, teacher_user_id),
            )
            if cursor.rowcount == 0:
                raise AssignmentNotFoundError(assignment_id)

    def list_student_classrooms(self, student_user_id: int) -> list[dict[str, Any]]:
        with self._connection() as connection:
            rows = connection.execute(
                """
                SELECT classrooms.classroom_id, classrooms.classroom_name, classrooms.subject,
                    classrooms.section, users.username AS teacher_username,
                    classroom_enrollments.enrolled_at,
                    (SELECT COUNT(*) FROM assignments
                     WHERE assignments.classroom_id = classrooms.classroom_id
                        AND assignments.deleted_at IS NULL) AS assignment_count
                FROM classroom_enrollments
                JOIN classrooms ON classrooms.classroom_id = classroom_enrollments.classroom_id
                JOIN users ON users.user_id = classrooms.teacher_user_id
                WHERE classroom_enrollments.student_user_id = ?
                ORDER BY classrooms.classroom_name COLLATE NOCASE
                """,
                (student_user_id,),
            ).fetchall()
        return [dict(row) for row in rows]

    def join_classroom(self, student_user_id: int, enrollment_code: str) -> dict[str, Any]:
        with self._connection() as connection:
            student = connection.execute(
                "SELECT role FROM users WHERE user_id = ?", (student_user_id,)
            ).fetchone()
            if student is None or student["role"] != "STUDENT":
                raise ClassroomNotFoundError(enrollment_code)
            classroom = connection.execute(
                "SELECT * FROM classrooms WHERE enrollment_code = ? COLLATE NOCASE",
                (enrollment_code.strip(),),
            ).fetchone()
            if classroom is None:
                raise ClassroomNotFoundError(enrollment_code)
            try:
                connection.execute(
                    "INSERT INTO classroom_enrollments (classroom_id, student_user_id) VALUES (?, ?)",
                    (classroom["classroom_id"], student_user_id),
                )
            except sqlite3.IntegrityError as error:
                if connection.execute(
                    "SELECT 1 FROM classroom_enrollments WHERE classroom_id = ? AND student_user_id = ?",
                    (classroom["classroom_id"], student_user_id),
                ).fetchone():
                    raise DuplicateEnrollmentError(enrollment_code) from error
                raise
        return dict(classroom)

    def list_classroom_assignments_for_student(
        self, student_user_id: int, classroom_id: int
    ) -> list[dict[str, Any]]:
        with self._connection() as connection:
            enrolled = connection.execute(
                "SELECT 1 FROM classroom_enrollments WHERE classroom_id = ? AND student_user_id = ?",
                (classroom_id, student_user_id),
            ).fetchone()
            if enrolled is None:
                raise ClassroomNotFoundError(classroom_id)
            rows = connection.execute(
                """
                SELECT assignments.assignment_id, assignments.title, assignments.topic,
                    assignments.instructions, assignments.focus_terms, assignments.created_at,
                    classrooms.classroom_id, classrooms.classroom_name, classrooms.section, classrooms.subject,
                    users.username AS teacher_username,
                    CASE
                        WHEN EXISTS(SELECT 1 FROM submissions WHERE submissions.assignment_id = assignments.assignment_id AND submissions.student_user_id = ?) THEN 'Submitted'
                        WHEN EXISTS(
                            SELECT 1 FROM writing_sessions
                            WHERE writing_sessions.assignment_id = assignments.assignment_id
                                AND writing_sessions.user_id = ? AND (
                                    trim(writing_sessions.introduction_text) <> '' OR
                                    trim(writing_sessions.body_text) <> '' OR
                                    trim(writing_sessions.conclusion_text) <> ''
                                )
                        ) OR EXISTS(
                            SELECT 1 FROM writing_revisions
                            JOIN writing_sessions ON writing_sessions.session_id = writing_revisions.session_id
                            WHERE writing_sessions.assignment_id = assignments.assignment_id
                                AND writing_sessions.user_id = ?
                        ) THEN 'In Progress' ELSE 'Not Started'
                    END AS progress
                FROM assignments
                JOIN classrooms ON classrooms.classroom_id = assignments.classroom_id
                JOIN users ON users.user_id = classrooms.teacher_user_id
                WHERE assignments.classroom_id = ? AND assignments.deleted_at IS NULL
                ORDER BY assignments.assignment_id DESC
                """,
                (student_user_id, student_user_id, student_user_id, classroom_id),
            ).fetchall()
        return [dict(row) for row in rows]

    def get_available_assignment(
        self, student_user_id: int, assignment_id: int
    ) -> dict[str, Any] | None:
        with self._connection() as connection:
            row = connection.execute(
                """
                SELECT assignments.*, classrooms.classroom_name, classrooms.subject, classrooms.section
                FROM assignments
                JOIN classrooms ON classrooms.classroom_id = assignments.classroom_id
                JOIN classroom_enrollments
                    ON classroom_enrollments.classroom_id = assignments.classroom_id
                WHERE assignments.assignment_id = ?
                    AND classroom_enrollments.student_user_id = ?
                    AND assignments.deleted_at IS NULL
                """,
                (assignment_id, student_user_id),
            ).fetchone()
        return dict(row) if row is not None else None

    def get_writing_activity_seconds(
        self, user_id: int, assignment_id: int
    ) -> int | None:
        """Return this student's recorded active seconds, or None if none exist."""
        with self._connection() as connection:
            enrolled = connection.execute(
                """
                SELECT 1 FROM assignments
                JOIN classroom_enrollments
                    ON classroom_enrollments.classroom_id = assignments.classroom_id
                WHERE assignments.assignment_id = ?
                    AND classroom_enrollments.student_user_id = ?
                """,
                (assignment_id, user_id),
            ).fetchone()
            if enrolled is None:
                raise AssignmentNotFoundError(assignment_id)
            if connection.execute(
                "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'writing_activity'"
            ).fetchone() is None:
                return None
            row = connection.execute(
                """
                SELECT SUM(seconds), COUNT(*) FROM writing_activity
                WHERE user_id = ? AND assignment_id = ?
                """,
                (user_id, assignment_id),
            ).fetchone()
        return int(row[0]) if row is not None and row[1] else None

    def record_writing_activity(
        self,
        user_id: int,
        assignment_id: int,
        session_id: str,
        events: list[dict[str, Any]],
        now: float | None = None,
    ) -> dict[str, int]:
        """Record validated five-second activity buckets idempotently."""
        if not self.activity_tracking_enabled:
            raise RuntimeError("Writing activity tracking is disabled.")
        if not isinstance(events, list) or not events:
            raise ValueError("At least one activity event is required.")
        if len(events) > WRITING_ACTIVITY_MAX_EVENTS_PER_REQUEST:
            raise ValueError("Too many activity events in one request.")
        current_time = int(time.time() if now is None else now)
        with self._connection() as connection:
            owned_session = connection.execute(
                """
                SELECT 1 FROM writing_sessions
                WHERE session_id = ? AND user_id = ? AND assignment_id = ?
                """,
                (session_id, user_id, assignment_id),
            ).fetchone()
            if owned_session is None:
                raise DraftNotFoundError(session_id)
            self._ensure_assignment_active(connection, assignment_id)
            self._ensure_not_submitted(connection, user_id, assignment_id)

            recorded = 0
            for event in events:
                if not isinstance(event, dict):
                    raise ValueError("Each activity event must be an object.")
                stage = event.get("stage")
                if stage not in STAGE_ACTIVITY_IDS.values():
                    raise ValueError("Choose Introduction, Body, or Conclusion.")
                bucket_start = event.get("bucket_start")
                if type(bucket_start) is not int:
                    raise ValueError("The activity interval is invalid.")
                bucket_start -= bucket_start % WRITING_ACTIVITY_BUCKET_SECONDS
                if (
                    bucket_start < current_time - WRITING_ACTIVITY_MAX_AGE_SECONDS
                    or bucket_start
                    > current_time + WRITING_ACTIVITY_FUTURE_TOLERANCE_SECONDS
                ):
                    raise ValueError("The activity interval is outside the accepted window.")
                seconds = event.get("seconds")
                if (
                    type(seconds) is not int
                    or seconds < 1
                    or seconds > WRITING_ACTIVITY_MAX_EVENT_SECONDS
                ):
                    raise ValueError("The activity duration is invalid.")
                # The conflict update leaves stage untouched: the first stage owns the bucket.
                connection.execute(
                    """
                    INSERT INTO writing_activity (
                        user_id, assignment_id, session_id, stage, bucket_start, seconds
                    ) VALUES (?, ?, ?, ?, ?, ?)
                    ON CONFLICT(user_id, assignment_id, bucket_start)
                    DO UPDATE SET seconds = MAX(writing_activity.seconds, excluded.seconds)
                    """,
                    (
                        user_id,
                        assignment_id,
                        session_id,
                        stage,
                        bucket_start,
                        seconds,
                    ),
                )
                recorded += 1
        return {"recorded": recorded}

    def assignment_progress(
        self, teacher_user_id: int, assignment_id: int
    ) -> list[dict[str, Any]]:
        with self._connection() as connection:
            rows = connection.execute(
                """
                SELECT users.username, users.user_id AS student_user_id,
                    CASE WHEN submissions.submission_id IS NOT NULL THEN 'Submitted'
                    WHEN sessions.session_id IS NULL OR (
                        trim(sessions.introduction_text) = '' AND
                        trim(sessions.body_text) = '' AND
                        trim(sessions.conclusion_text) = ''
                    ) THEN 'Not Started' ELSE 'In Progress' END AS progress,
                    sessions.session_id,
                    sessions.introduction_text AS draft_introduction_text,
                    sessions.body_text AS draft_body_text,
                    sessions.conclusion_text AS draft_conclusion_text,
                    submissions.submission_id,
                    submissions.introduction_snapshot AS submitted_introduction_text,
                    submissions.body_snapshot AS submitted_body_text,
                    submissions.conclusion_snapshot AS submitted_conclusion_text
                FROM assignments
                JOIN classrooms ON classrooms.classroom_id = assignments.classroom_id
                JOIN classroom_enrollments ON classroom_enrollments.classroom_id = classrooms.classroom_id
                JOIN users ON users.user_id = classroom_enrollments.student_user_id
                LEFT JOIN writing_sessions AS sessions
                    ON sessions.assignment_id = assignments.assignment_id
                    AND sessions.user_id = classroom_enrollments.student_user_id
                LEFT JOIN submissions
                    ON submissions.assignment_id = assignments.assignment_id
                    AND submissions.student_user_id = classroom_enrollments.student_user_id
                WHERE assignments.assignment_id = ? AND classrooms.teacher_user_id = ?
                ORDER BY users.username COLLATE NOCASE
                """,
                (assignment_id, teacher_user_id),
            ).fetchall()
            session_ids = [row["session_id"] for row in rows if row["session_id"]]
            revisions_by_session: dict[str, list[sqlite3.Row]] = {
                session_id: [] for session_id in session_ids
            }
            if session_ids:
                placeholders = ", ".join("?" for _ in session_ids)
                revision_rows = connection.execute(
                    f"""
                    SELECT session_id, revision_number,
                        introduction_text, body_text, conclusion_text
                    FROM writing_revisions
                    WHERE session_id IN ({placeholders})
                    ORDER BY session_id, revision_number
                    """,
                    session_ids,
                ).fetchall()
                for revision in revision_rows:
                    revisions_by_session[revision["session_id"]].append(revision)

            activity_by_student: dict[int, dict[str, int]] = {}
            student_ids = [row["student_user_id"] for row in rows]
            if self.activity_tracking_enabled and student_ids:
                placeholders = ", ".join("?" for _ in student_ids)
                activity_rows = connection.execute(
                    f"""
                    SELECT user_id, stage, SUM(seconds) AS seconds
                    FROM writing_activity
                    WHERE assignment_id = ? AND user_id IN ({placeholders})
                    GROUP BY user_id, stage
                    """,
                    [assignment_id, *student_ids],
                ).fetchall()
                for activity in activity_rows:
                    activity_by_student.setdefault(activity["user_id"], {})[
                        activity["stage"]
                    ] = activity["seconds"]

        progress_rows = []
        for row in rows:
            submitted = row["submission_id"] is not None
            if submitted:
                stage_texts = {
                    "introduction_text": row["submitted_introduction_text"],
                    "body_text": row["submitted_body_text"],
                    "conclusion_text": row["submitted_conclusion_text"],
                }
            else:
                stage_texts = {
                    "introduction_text": row["draft_introduction_text"] or "",
                    "body_text": row["draft_body_text"] or "",
                    "conclusion_text": row["draft_conclusion_text"] or "",
                }
            counts = self._stage_revision_counts(
                revisions_by_session.get(row["session_id"], [])
            )
            activity = activity_by_student.get(row["student_user_id"], {})
            progress_rows.append(
                {
                    "username": row["username"],
                    "progress": row["progress"],
                    "stages": [
                        {
                            "name": name,
                            "status": self._stage_status(stage_texts[field], submitted),
                            "revisions": counts[name],
                            "activity_seconds": activity.get(STAGE_ACTIVITY_IDS[name]),
                        }
                        for name, field in STAGE_PROGRESS_FIELDS
                    ],
                }
            )
        return progress_rows

    @staticmethod
    def _stage_status(stage_text: str | None, submitted: bool) -> str:
        if not stage_text or not stage_text.strip():
            return "Not Started"
        return "Submitted" if submitted else "In Progress"

    @staticmethod
    def _stage_revision_counts(
        revisions: list[sqlite3.Row],
    ) -> dict[str, int | None]:
        expected_numbers = list(range(1, len(revisions) + 1))
        if [revision["revision_number"] for revision in revisions] != expected_numbers:
            return {name: None for name, _field in STAGE_PROGRESS_FIELDS}
        counts: dict[str, int | None] = {}
        for name, field in STAGE_PROGRESS_FIELDS:
            count = 0
            has_saved_text = False
            previous_text = ""
            for revision in revisions:
                text = revision[field] or ""
                if text.strip():
                    if not has_saved_text:
                        # The first saved text is the stage's starting version.
                        has_saved_text = True
                        previous_text = text
                    elif text != previous_text:
                        count += 1
                        previous_text = text
                elif has_saved_text and previous_text != "":
                    # Clearing a previously saved stage is also a persisted change.
                    count += 1
                    previous_text = ""
            counts[name] = count
        return counts

    def get_user_for_login(self, username: str) -> dict[str, Any] | None:
        with self._connection() as connection:
            row = connection.execute(
                "SELECT user_id, username, password_hash, role FROM users WHERE username = ? COLLATE NOCASE",
                (username,),
            ).fetchone()
        return dict(row) if row is not None else None

    def get_user(self, user_id: int) -> dict[str, Any] | None:
        with self._connection() as connection:
            row = connection.execute(
                "SELECT user_id, username, role, created_at FROM users WHERE user_id = ?",
                (user_id,),
            ).fetchone()
        return dict(row) if row is not None else None

    @staticmethod
    def draft_version(draft: dict[str, Any]) -> str:
        """Return a stable token for the saved version, including all essay text."""
        values = [
            draft.get("session_id"),
            draft.get("user_id"),
            draft.get("assignment_id"),
            draft.get("assignment_topic"),
            draft.get("focus_terms"),
            draft.get("introduction_text"),
            draft.get("body_text"),
            draft.get("conclusion_text"),
            draft.get("updated_at"),
        ]
        serialized = json.dumps(values, ensure_ascii=False, separators=(",", ":"))
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    @staticmethod
    def _ensure_not_submitted(
        connection: sqlite3.Connection, user_id: int | None, assignment_id: int | None
    ) -> None:
        if user_id is None or assignment_id is None:
            return
        if connection.execute(
            "SELECT 1 FROM submissions WHERE student_user_id = ? AND assignment_id = ?",
            (user_id, assignment_id),
        ).fetchone() is not None:
            raise SubmittedAssignmentError(assignment_id)

    @staticmethod
    def _ensure_assignment_active(
        connection: sqlite3.Connection, assignment_id: int | None
    ) -> None:
        if assignment_id is None:
            return
        row = connection.execute(
            "SELECT deleted_at FROM assignments WHERE assignment_id = ?",
            (assignment_id,),
        ).fetchone()
        if row is None:
            raise AssignmentNotFoundError(assignment_id)
        if row["deleted_at"] is not None:
            raise AssignmentDeletedError(assignment_id)

    def create_assignment(
        self,
        teacher_user_id: int,
        classroom_id: int,
        title: str,
        topic: str,
        instructions: str,
        focus_terms: str,
    ) -> dict[str, Any]:
        with self._connection() as connection:
            owns_classroom = connection.execute(
                "SELECT 1 FROM classrooms WHERE classroom_id = ? AND teacher_user_id = ?",
                (classroom_id, teacher_user_id),
            ).fetchone()
            if owns_classroom is None:
                raise ClassroomNotFoundError(classroom_id)
            cursor = connection.execute(
                """
                INSERT INTO assignments (
                    teacher_user_id, classroom_id, title, topic, instructions, focus_terms
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (teacher_user_id, classroom_id, title, topic, instructions, focus_terms),
            )
            row = connection.execute(
                "SELECT * FROM assignments WHERE assignment_id = ?", (cursor.lastrowid,)
            ).fetchone()
        return dict(row)

    def list_teacher_assignments(self, teacher_user_id: int) -> list[dict[str, Any]]:
        with self._connection() as connection:
            rows = connection.execute(
                "SELECT * FROM assignments WHERE teacher_user_id = ? ORDER BY assignment_id DESC",
                (teacher_user_id,),
            ).fetchall()
        return [dict(row) for row in rows]

    def list_available_assignments(self, student_user_id: int) -> list[dict[str, Any]]:
        with self._connection() as connection:
            rows = connection.execute(
                """
                SELECT assignments.assignment_id, assignments.title, assignments.topic,
                    assignments.instructions, assignments.focus_terms, assignments.created_at,
                    classrooms.classroom_id, classrooms.classroom_name, classrooms.section, classrooms.subject,
                    users.username AS teacher_username,
                    CASE
                        WHEN EXISTS(SELECT 1 FROM submissions WHERE submissions.assignment_id = assignments.assignment_id AND submissions.student_user_id = ?) THEN 'Submitted'
                        WHEN EXISTS(
                            SELECT 1 FROM writing_sessions
                            WHERE writing_sessions.assignment_id = assignments.assignment_id
                                AND writing_sessions.user_id = ? AND (
                                    trim(writing_sessions.introduction_text) <> '' OR
                                    trim(writing_sessions.body_text) <> '' OR
                                    trim(writing_sessions.conclusion_text) <> ''
                                )
                        ) OR EXISTS(
                            SELECT 1 FROM writing_revisions
                            JOIN writing_sessions ON writing_sessions.session_id = writing_revisions.session_id
                            WHERE writing_sessions.assignment_id = assignments.assignment_id
                                AND writing_sessions.user_id = ?
                        ) THEN 'In Progress' ELSE 'Not Started'
                    END AS progress
                FROM assignments
                JOIN classroom_enrollments
                    ON classroom_enrollments.classroom_id = assignments.classroom_id
                JOIN classrooms ON classrooms.classroom_id = assignments.classroom_id
                JOIN users ON users.user_id = classrooms.teacher_user_id
                WHERE classroom_enrollments.student_user_id = ? AND assignments.deleted_at IS NULL
                ORDER BY assignments.assignment_id DESC
                """,
                (student_user_id, student_user_id, student_user_id, student_user_id),
            ).fetchall()
        return [dict(row) for row in rows]

    def list_student_history(self, student_user_id: int) -> list[dict[str, Any]]:
        """List submitted work and teacher-deleted work this student retains."""
        with self._connection() as connection:
            rows = connection.execute(
                """
                SELECT DISTINCT assignments.assignment_id, assignments.title, assignments.topic,
                    assignments.instructions, assignments.focus_terms, assignments.deleted_at,
                    classrooms.classroom_id, classrooms.classroom_name, classrooms.section,
                    classrooms.subject, submissions.submitted_at,
                    COALESCE(assignments.deleted_at, submissions.submitted_at) AS history_at,
                    CASE
                        WHEN assignments.deleted_at IS NOT NULL THEN 'Deleted'
                        ELSE 'Submitted'
                    END AS history_status
                FROM assignments
                JOIN classrooms ON classrooms.classroom_id = assignments.classroom_id
                JOIN classroom_enrollments
                    ON classroom_enrollments.classroom_id = assignments.classroom_id
                    AND classroom_enrollments.student_user_id = ?
                LEFT JOIN submissions
                    ON submissions.assignment_id = assignments.assignment_id
                    AND submissions.student_user_id = ?
                WHERE (
                    submissions.submission_id IS NOT NULL
                    OR (
                        assignments.deleted_at IS NOT NULL AND (
                            EXISTS(
                                SELECT 1 FROM writing_sessions
                                WHERE writing_sessions.assignment_id = assignments.assignment_id
                                    AND writing_sessions.user_id = ? AND (
                                        trim(writing_sessions.introduction_text) <> '' OR
                                        trim(writing_sessions.body_text) <> '' OR
                                        trim(writing_sessions.conclusion_text) <> ''
                                    )
                            ) OR EXISTS(
                                SELECT 1 FROM writing_revisions
                                JOIN writing_sessions
                                    ON writing_sessions.session_id = writing_revisions.session_id
                                WHERE writing_sessions.assignment_id = assignments.assignment_id
                                    AND writing_sessions.user_id = ?
                            )
                        )
                    )
                )
                ORDER BY history_at DESC, assignments.assignment_id DESC
                """,
                (student_user_id, student_user_id, student_user_id, student_user_id),
            ).fetchall()
        return [dict(row) for row in rows]

    def get_assignment(self, assignment_id: int) -> dict[str, Any] | None:
        with self._connection() as connection:
            row = connection.execute(
                "SELECT * FROM assignments WHERE assignment_id = ?", (assignment_id,)
            ).fetchone()
        return dict(row) if row is not None else None

    def get_or_create_assignment_workspace(
        self, student_user_id: int, assignment_id: int
    ) -> dict[str, Any]:
        """Return a student's unique writing session for an available assignment."""
        with self._connection() as connection:
            connection.execute("BEGIN IMMEDIATE")
            assignment = connection.execute(
                """
                SELECT assignments.*, classrooms.classroom_name, classrooms.subject, classrooms.section
                FROM assignments
                JOIN classrooms ON classrooms.classroom_id = assignments.classroom_id
                JOIN classroom_enrollments
                    ON classroom_enrollments.classroom_id = assignments.classroom_id
                WHERE assignments.assignment_id = ?
                    AND classroom_enrollments.student_user_id = ?
                """,
                (assignment_id, student_user_id),
            ).fetchone()
            if assignment is None:
                raise AssignmentNotFoundError(assignment_id)
            writing = connection.execute(
                "SELECT * FROM writing_sessions WHERE user_id = ? AND assignment_id = ?",
                (student_user_id, assignment_id),
            ).fetchone()
            if writing is None:
                if assignment["deleted_at"] is not None:
                    raise AssignmentDeletedError(assignment_id)
                session_id = uuid4().hex
                connection.execute(
                    """
                    INSERT INTO writing_sessions (
                        session_id, user_id, assignment_id, assignment_topic, focus_terms,
                        introduction_text, body_text, conclusion_text
                    ) VALUES (?, ?, ?, ?, ?, '', '', '')
                    """,
                    (
                        session_id,
                        student_user_id,
                        assignment_id,
                        assignment["topic"],
                        assignment["focus_terms"],
                    ),
                )
                writing = connection.execute(
                    "SELECT * FROM writing_sessions WHERE session_id = ?", (session_id,)
                ).fetchone()
            submission = connection.execute(
                """
                SELECT *
                FROM submissions
                WHERE student_user_id = ? AND assignment_id = ?
                """,
                (student_user_id, assignment_id),
            ).fetchone()
        return {
            "assignment": dict(assignment),
            "draft": dict(writing),
            "submission": dict(submission) if submission is not None else None,
        }

    def save_revision(
        self,
        draft: dict[str, str],
        session_id: str | None = None,
        user_id: int | None = None,
        assignment_id: int | None = None,
    ) -> dict[str, Any]:
        """Save the current draft and its next unique revision atomically."""
        new_session = session_id is None
        if new_session:
            session_id = uuid4().hex

        with self._connection() as connection:
            # Serializes revision-number allocation across concurrent requests.
            connection.execute("BEGIN IMMEDIATE")
            self._ensure_assignment_active(connection, assignment_id)
            self._ensure_not_submitted(connection, user_id, assignment_id)
            if new_session:
                connection.execute(
                    """
                    INSERT INTO writing_sessions (
                        session_id, user_id, assignment_id, assignment_topic, focus_terms,
                        introduction_text, body_text, conclusion_text
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (session_id, user_id, assignment_id, *self._draft_values(draft)),
                )
            else:
                cursor = connection.execute(
                    """
                    UPDATE writing_sessions
                    SET assignment_topic = ?, focus_terms = ?,
                        introduction_text = ?, body_text = ?, conclusion_text = ?,
                        updated_at = strftime('%Y-%m-%dT%H:%M:%fZ', 'now')
                        WHERE session_id = ? AND user_id IS ? AND assignment_id IS ?
                    """,
                    (*self._draft_values(draft), session_id, user_id, assignment_id),
                )
                if cursor.rowcount == 0:
                    raise DraftNotFoundError(session_id)

            previous = connection.execute(
                """
                SELECT * FROM writing_revisions
                WHERE session_id = ?
                ORDER BY revision_number DESC
                LIMIT 1
                """,
                (session_id,),
            ).fetchone()

            if previous is not None and self._revision_matches(previous, draft):
                revision = dict(previous)
                created = False
            else:
                revision_number = 1 if previous is None else previous["revision_number"] + 1
                cursor = connection.execute(
                    """
                    INSERT INTO writing_revisions (
                        session_id, revision_number, assignment_topic, focus_terms,
                        introduction_text, body_text, conclusion_text
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        session_id,
                        revision_number,
                        draft["assignment_topic"],
                        draft["focus_terms"],
                        draft["introduction_text"],
                        draft["body_text"],
                        draft["conclusion_text"],
                    ),
                )
                revision_row = connection.execute(
                    "SELECT * FROM writing_revisions WHERE revision_id = ?",
                    (cursor.lastrowid,),
                ).fetchone()
                revision = dict(revision_row)
                created = True

            session_row = connection.execute(
                """
                SELECT * FROM writing_sessions
                WHERE session_id = ? AND user_id IS ? AND assignment_id IS ?
                """,
                (session_id, user_id, assignment_id),
            ).fetchone()

        return {
            "session": dict(session_row),
            "revision": revision,
            "created": created,
        }

    @staticmethod
    def _draft_values(draft: dict[str, str]) -> tuple[str, ...]:
        return (
            draft["assignment_topic"],
            draft["focus_terms"],
            draft["introduction_text"],
            draft["body_text"],
            draft["conclusion_text"],
        )

    @staticmethod
    def _revision_matches(revision: sqlite3.Row, draft: dict[str, str]) -> bool:
        return all(
            revision[field] == draft[field]
            for field in (
                "assignment_topic",
                "focus_terms",
                "introduction_text",
                "body_text",
                "conclusion_text",
            )
        )

    def list_revisions(
        self, session_id: str, user_id: int | None = None
    ) -> list[dict[str, Any]]:
        with self._connection() as connection:
            if connection.execute(
                "SELECT 1 FROM writing_sessions WHERE session_id = ? AND user_id IS ?",
                (session_id, user_id),
            ).fetchone() is None:
                raise DraftNotFoundError(session_id)
            rows = connection.execute(
                """
                SELECT revision_id, session_id, revision_number, created_at
                FROM writing_revisions
                WHERE session_id = ?
                ORDER BY revision_number DESC
                """,
                (session_id,),
            ).fetchall()
        return [dict(row) for row in rows]

    def create_submission(
        self,
        student_user_id: int,
        assignment_id: int,
        session_id: str,
        expected_draft_version: str,
    ) -> dict[str, Any]:
        """Snapshot only the authenticated student's latest saved assigned draft."""
        with self._connection() as connection:
            connection.execute("BEGIN IMMEDIATE")
            self._ensure_assignment_active(connection, assignment_id)
            session_row = connection.execute(
                """
                SELECT sessions.* FROM writing_sessions AS sessions
                JOIN assignments ON assignments.assignment_id = sessions.assignment_id
                JOIN classroom_enrollments
                    ON classroom_enrollments.classroom_id = assignments.classroom_id
                    AND classroom_enrollments.student_user_id = sessions.user_id
                WHERE sessions.session_id = ?
                    AND sessions.user_id = ?
                    AND sessions.assignment_id = ?
                """,
                (session_id, student_user_id, assignment_id),
            ).fetchone()
            if session_row is None:
                raise DraftNotFoundError(session_id)

            existing = connection.execute(
                "SELECT * FROM submissions WHERE student_user_id = ? AND assignment_id = ?",
                (student_user_id, assignment_id),
            ).fetchone()
            if existing is not None:
                raise AlreadySubmittedError(assignment_id)
            saved_draft = dict(session_row)
            if expected_draft_version != self.draft_version(saved_draft):
                raise UnsavedDraftError(session_id)
            text_fields = ("introduction_text", "body_text", "conclusion_text")
            if any(not saved_draft[field].strip() for field in text_fields):
                raise IncompleteEssayError(assignment_id)

            cursor = connection.execute(
                """
                INSERT INTO submissions (
                    student_user_id, assignment_id, session_id,
                    introduction_snapshot, body_snapshot, conclusion_snapshot
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    student_user_id,
                    assignment_id,
                    session_id,
                    saved_draft["introduction_text"],
                    saved_draft["body_text"],
                    saved_draft["conclusion_text"],
                ),
            )
            submission = connection.execute(
                "SELECT * FROM submissions WHERE submission_id = ?",
                (cursor.lastrowid,),
            ).fetchone()
        return dict(submission)

    def get_student_submission(
        self, student_user_id: int, assignment_id: int
    ) -> dict[str, Any] | None:
        with self._connection() as connection:
            row = connection.execute(
                """
                SELECT submissions.* FROM submissions
                JOIN assignments ON assignments.assignment_id = submissions.assignment_id
                JOIN classroom_enrollments
                    ON classroom_enrollments.classroom_id = assignments.classroom_id
                    AND classroom_enrollments.student_user_id = submissions.student_user_id
                WHERE submissions.student_user_id = ? AND submissions.assignment_id = ?
                """,
                (student_user_id, assignment_id),
            ).fetchone()
        return dict(row) if row is not None else None

    def list_teacher_submissions(
        self, teacher_user_id: int, assignment_id: int
    ) -> list[dict[str, Any]]:
        with self._connection() as connection:
            assignment = connection.execute(
                """
                SELECT 1 FROM assignments
                JOIN classrooms ON classrooms.classroom_id = assignments.classroom_id
                WHERE assignments.assignment_id = ? AND classrooms.teacher_user_id = ?
                """,
                (assignment_id, teacher_user_id),
            ).fetchone()
            if assignment is None:
                raise AssignmentNotFoundError(assignment_id)
            rows = connection.execute(
                """
                SELECT submissions.submission_id, submissions.assignment_id,
                    submissions.submitted_at, users.username, assignments.title AS assignment_title
                FROM submissions
                JOIN users ON users.user_id = submissions.student_user_id
                JOIN assignments ON assignments.assignment_id = submissions.assignment_id
                JOIN classrooms ON classrooms.classroom_id = assignments.classroom_id
                WHERE submissions.assignment_id = ? AND classrooms.teacher_user_id = ?
                ORDER BY submissions.submitted_at DESC
                """,
                (assignment_id, teacher_user_id),
            ).fetchall()
        return [dict(row) for row in rows]

    def get_teacher_submission(
        self, teacher_user_id: int, submission_id: int
    ) -> dict[str, Any] | None:
        with self._connection() as connection:
            row = connection.execute(
                """
                SELECT submissions.*, users.username,
                    assignments.title AS assignment_title,
                    classrooms.classroom_name, classrooms.section
                FROM submissions
                JOIN users ON users.user_id = submissions.student_user_id
                JOIN assignments ON assignments.assignment_id = submissions.assignment_id
                JOIN classrooms ON classrooms.classroom_id = assignments.classroom_id
                WHERE submissions.submission_id = ? AND classrooms.teacher_user_id = ?
                """,
                (submission_id, teacher_user_id),
            ).fetchone()
        return dict(row) if row is not None else None

    def get_revision(
        self, session_id: str, revision_id: int, user_id: int | None = None
    ) -> dict[str, Any] | None:
        with self._connection() as connection:
            row = connection.execute(
                """
                SELECT revisions.* FROM writing_revisions AS revisions
                JOIN writing_sessions AS sessions ON sessions.session_id = revisions.session_id
                WHERE revisions.session_id = ? AND revisions.revision_id = ?
                    AND sessions.user_id IS ?
                """,
                (session_id, revision_id, user_id),
            ).fetchone()
        return dict(row) if row is not None else None
