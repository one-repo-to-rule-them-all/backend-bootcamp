"""Domain models for Fieldbook.

Pure data — no I/O, no framework, no persistence. This is the core the rest of
the service is built around. Keeping it free of infrastructure is what makes it
trivially unit-testable (see the tests) and is the seed of the clean
architecture introduced in Week 11.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class Status(StrEnum):
    """Lifecycle state of a record."""

    TODO = "todo"
    DOING = "doing"
    DONE = "done"


@dataclass(frozen=True)
class Record:
    """A single task/record owned by a user.

    Frozen (immutable) on purpose: an ``update`` produces a *new* ``Record``
    rather than mutating one in place, which keeps the store easy to reason
    about and rules out a whole class of aliasing bugs.
    """

    id: str
    title: str
    status: Status
    owner_id: str
    created_at: datetime
