"""Unit tests for the in-memory record repository.

These describe the behaviour a *real* storage backend must also satisfy. When
the Postgres implementation lands in Week 5, the same cases are run against it —
which is why they're written against behaviour, not implementation details.
"""

from __future__ import annotations

import pytest

from fieldbook.errors import RecordNotFoundError, ValidationError
from fieldbook.models import Status
from fieldbook.repository import InMemoryRecordRepository


def test_create_returns_record_with_defaults(repo: InMemoryRecordRepository) -> None:
    record = repo.create(title="write tests", owner_id="user-1")

    assert record.id
    assert record.title == "write tests"
    assert record.status is Status.TODO
    assert record.owner_id == "user-1"
    assert record.created_at is not None


def test_create_rejects_empty_title(repo: InMemoryRecordRepository) -> None:
    with pytest.raises(ValidationError):
        repo.create(title="   ", owner_id="user-1")


def test_get_returns_created_record(repo: InMemoryRecordRepository) -> None:
    created = repo.create(title="ship it", owner_id="user-1")

    assert repo.get(created.id) == created


def test_get_missing_raises(repo: InMemoryRecordRepository) -> None:
    with pytest.raises(RecordNotFoundError):
        repo.get("does-not-exist")


def test_list_is_scoped_to_owner(repo: InMemoryRecordRepository) -> None:
    repo.create(title="mine", owner_id="user-1")
    repo.create(title="also mine", owner_id="user-1")
    repo.create(title="theirs", owner_id="user-2")

    mine = repo.list(owner_id="user-1")

    assert len(mine) == 2
    assert all(r.owner_id == "user-1" for r in mine)

def test_count_is_scoped_to_owner(repo: InMemoryRecordRepository) -> None:
    repo.create(title="mine", owner_id="user-1")
    repo.create(title="also mine", owner_id="user-1")
    repo.create(title="theirs", owner_id="user-2")

    count = repo.count(owner_id="user-1")

    assert count == 2

def test_update_changes_fields(repo: InMemoryRecordRepository) -> None:
    created = repo.create(title="draft", owner_id="user-1")

    updated = repo.update(created.id, title="final", status=Status.DONE)

    assert updated.title == "final"
    assert updated.status is Status.DONE
    assert updated.id == created.id
    assert updated.created_at == created.created_at


def test_update_missing_raises(repo: InMemoryRecordRepository) -> None:
    with pytest.raises(RecordNotFoundError):
        repo.update("does-not-exist", title="nope")


def test_update_rejects_empty_title(repo: InMemoryRecordRepository) -> None:
    created = repo.create(title="draft", owner_id="user-1")

    with pytest.raises(ValidationError):
        repo.update(created.id, title="  ")


def test_delete_removes_record(repo: InMemoryRecordRepository) -> None:
    created = repo.create(title="temporary", owner_id="user-1")

    repo.delete(created.id)

    with pytest.raises(RecordNotFoundError):
        repo.get(created.id)


def test_delete_missing_raises(repo: InMemoryRecordRepository) -> None:
    with pytest.raises(RecordNotFoundError):
        repo.delete("does-not-exist")
