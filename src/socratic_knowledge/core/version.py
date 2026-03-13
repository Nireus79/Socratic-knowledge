"""Version data model for version control."""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from uuid import uuid4

from .knowledge_item import KnowledgeItem


@dataclass
class Version:
    """
    Version snapshot of a knowledge item.

    Stores complete state at a point in time for rollback.
    """

    version_id: str
    item_id: str
    version_number: int
    content: str
    title: str

    # Change tracking
    created_at: Optional[datetime] = None
    created_by: str = "system"
    change_message: str = ""

    # Delta tracking (optional)
    diff_from_previous: Optional[Dict[str, Any]] = None

    def __post_init__(self) -> None:
        """Initialize datetime fields if not provided."""
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)

    @classmethod
    def create_from_item(
        cls,
        item: KnowledgeItem,
        change_message: str = "",
    ) -> "Version":
        """
        Create version snapshot from current item state.

        Args:
            item: Knowledge item to snapshot
            change_message: Optional change message

        Returns:
            Version: New version snapshot
        """
        return cls(
            version_id=str(uuid4()),
            item_id=item.item_id,
            version_number=item.version,
            content=item.content,
            title=item.title,
            created_by=item.updated_by,
            change_message=change_message,
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize to dictionary.

        Returns:
            Dict[str, Any]: Serialized version
        """
        return {
            "version_id": self.version_id,
            "item_id": self.item_id,
            "version_number": self.version_number,
            "content": self.content,
            "title": self.title,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "created_by": self.created_by,
            "change_message": self.change_message,
            "diff_from_previous": self.diff_from_previous,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Version":
        """
        Deserialize from dictionary.

        Args:
            data: Serialized data

        Returns:
            Version: Deserialized version
        """
        # Parse datetime strings
        created_at = data.get("created_at")
        if isinstance(created_at, str):
            data = {**data, "created_at": datetime.fromisoformat(created_at)}

        return cls(**data)
