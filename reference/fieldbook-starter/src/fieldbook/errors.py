"""Exception hierarchy for Fieldbook.

Errors are modeled as exceptions rather than return codes or ``None``, so a
caller cannot silently ignore them. Everything derives from ``FieldbookError``,
so a caller can catch the whole family when that's what they want, or a specific
subclass when it isn't.
"""

from __future__ import annotations


class FieldbookError(Exception):
    """Base class for all Fieldbook domain errors."""


class RecordNotFoundError(FieldbookError):
    """Raised when a record is requested by an id that does not exist."""

    def __init__(self, record_id: str) -> None:
        super().__init__(f"record not found: {record_id}")
        self.record_id = record_id


class ValidationError(FieldbookError):
    """Raised when input fails a domain rule (e.g. an empty title)."""
