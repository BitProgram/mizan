"""Exception hierarchy for MizanZarb core."""
from __future__ import annotations


class MizanZarbError(Exception):
    """Base class for every error raised by mizan_zarb_core."""


class ValidationError(MizanZarbError):
    """Raised when input fails domain validation."""


class InvalidAmountError(ValidationError):
    """Raised when a monetary amount is malformed or out of range."""


class InvalidDateError(ValidationError):
    """Raised when a date string is malformed or out of range."""


class InvalidPercentError(ValidationError):
    """Raised when a percentage is outside [0, 1]."""


class DuplicateIDError(MizanZarbError):
    """Raised when an entity ID collides with an existing one."""


class ReferentialIntegrityError(MizanZarbError):
    """Raised when an operation would orphan a related entity."""


class NotFoundError(MizanZarbError):
    """Raised when a lookup by ID or key returns nothing."""


class StorageError(MizanZarbError):
    """Raised for file, serialization, or migration failures."""


class ConfigurationError(MizanZarbError):
    """Raised when settings are missing, corrupt, or contradictory."""

