"""In-memory record storage.

Week 1 deliberately uses an in-memory ``dict`` so the domain logic can be built
and tested with zero infrastructure. A real Postgres-backed implementation
arrives in Week 5, at which point a shared ``RecordRepository`` *Protocol*
(interface) is introduced so the two are interchangeable. The method surface
below is already the shape that Protocol will describe.

Note: the curriculum sketches ``update(record_id, **changes)``. This reference
tightens that into explicit, typed keyword arguments — ``**changes`` is
effectively untyped and ``mypy --strict`` (rightly) can't check it. Prefer the
explicit signature.
"""

from __future__ import annotations

import uuid
from dataclasses import replace
from datetime import UTC, datetime

from fieldbook.errors import RecordNotFoundError, ValidationError
from fieldbook.models import Record, Status


class InMemoryRecordRepository:
    """Stores records in a dict keyed by id — O(1) lookup, not an O(n) scan."""

    def __init__(self) -> None:
        self._records: dict[str, Record] = {}

    def create(self, title: str, owner_id: str) -> Record:
        if not title.strip():
            raise ValidationError("title must not be empty")
        record = Record(
            id=str(uuid.uuid4()),
            title=title,
            status=Status.TODO,
            owner_id=owner_id,
            created_at=datetime.now(UTC),
        )
        self._records[record.id] = record
        return record

    def get(self, record_id: str) -> Record:
        try:
            return self._records[record_id]
        except KeyError:
            raise RecordNotFoundError(record_id) from None

    def list(self, owner_id: str) -> list[Record]:
        return [r for r in self._records.values() if r.owner_id == owner_id]

    def update(
        self,
        record_id: str,
        *,
        title: str | None = None,
        status: Status | None = None,
    ) -> Record:
        record = self.get(record_id)  # raises RecordNotFoundError if missing
        if title is not None and not title.strip():
            raise ValidationError("title must not be empty")
        updated = replace(
            record,
            title=record.title if title is None else title,
            status=record.status if status is None else status,
        )
        self._records[record_id] = updated
        return updated

    def delete(self, record_id: str) -> None:
        if record_id not in self._records:
            raise RecordNotFoundError(record_id)
        del self._records[record_id]
