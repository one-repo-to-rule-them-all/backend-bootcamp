"""Shared pytest fixtures."""

from __future__ import annotations

import pytest

from fieldbook.repository import InMemoryRecordRepository


@pytest.fixture
def repo() -> InMemoryRecordRepository:
    """A fresh, empty repository for each test — no shared state between tests."""
    return InMemoryRecordRepository()
