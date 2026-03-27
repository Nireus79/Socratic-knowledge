"""Utility functions for socratic-knowledge package."""

from datetime import datetime
from typing import Any, Dict, List, Optional


def parse_iso_datetime(value: Any) -> Optional[datetime]:
    """
    Parse ISO format datetime string to datetime object.

    Args:
        value: Value to parse (datetime or ISO string or None)

    Returns:
        datetime object or None

    Examples:
        >>> parse_iso_datetime("2024-03-27T10:30:00")
        datetime(2024, 3, 27, 10, 30, 0)
        >>> parse_iso_datetime(datetime(2024, 3, 27))
        datetime(2024, 3, 27)
        >>> parse_iso_datetime(None)
    """
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        return datetime.fromisoformat(value)
    return None


def ensure_iso_datetime(data: Dict[str, Any], *date_fields: str) -> Dict[str, Any]:
    """
    Convert ISO datetime strings in dict to datetime objects.

    Safely converts specified fields from ISO strings to datetime objects.
    Non-string values and missing fields are left unchanged.

    Args:
        data: Dictionary potentially containing datetime strings
        *date_fields: Field names to parse as datetimes

    Returns:
        Updated dictionary with parsed datetimes (doesn't modify original)

    Examples:
        >>> d = {"created_at": "2024-03-27T10:00:00", "name": "test"}
        >>> ensure_iso_datetime(d, "created_at")
        {"created_at": datetime(...), "name": "test"}
    """
    result = dict(data)
    for field in date_fields:
        if field in result:
            result[field] = parse_iso_datetime(result[field])
    return result
