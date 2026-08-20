"""Tests for winidjango.core.db.setup module."""

from pathlib import Path

from pytest_mock import MockerFixture

from winidjango.core.db.setup import migrate_safely


def test_migrate_safely(tmp_path: Path, mocker: MockerFixture) -> None:
    """Test func for migrate_safely."""
    call_command = mocker.patch("winidjango.core.db.setup.call_command")
    db_path = tmp_path / "sub" / "db.sqlite3"

    migrate_safely(db_path)

    call_command.assert_called_once_with("migrate")
    lock_path = db_path.with_suffix(f"{db_path.suffix}.lock")
    assert lock_path.parent.is_dir()
