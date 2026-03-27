"""Version information model."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict

from ..utils import ensure_iso_datetime


@dataclass
class VersionInfo:
    """Information about a specific version."""

    version_number: int
    created_at: datetime
    created_by: str
    change_message: str = ""
    content_preview: str = ""  # First 100 chars of content

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "version_number": self.version_number,
            "created_at": self.created_at.isoformat(),
            "created_by": self.created_by,
            "change_message": self.change_message,
            "content_preview": self.content_preview,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "VersionInfo":
        """Deserialize from dictionary."""
        data = ensure_iso_datetime(data, "created_at")

        return cls(**data)
