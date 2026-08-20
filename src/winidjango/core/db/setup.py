"""Concurrency-safe Django database setup helpers.

Django's migration recorder checks whether its bookkeeping table exists
and, if not, creates it. That check-then-create is not atomic, so when
multiple processes call ``migrate`` against the same database at once
(for example, several concurrent invocations of the same pre-commit
hook), more than one process can decide the table is missing and race
to create it, crashing with "table already exists". ``migrate_safely``
serializes migration across processes with a file lock so only one
process ever runs it at a time; the rest simply find the schema already
up to date once they acquire the lock.
"""

from pathlib import Path

from django.core.management import call_command
from filelock import FileLock


def migrate_safely(db_path: Path) -> None:
    """Apply Django migrations without racing other concurrent processes.

    Must be called after ``django.setup()``. Serializes access with a
    file lock next to ``db_path`` so concurrent processes targeting the
    same database apply migrations one at a time instead of racing to
    create the migration bookkeeping table.

    Args:
        db_path: Path to the database file the migrations apply to.
    """
    lock_path = db_path.with_suffix(f"{db_path.suffix}.lock")
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with FileLock(lock_path):
        call_command("migrate")
