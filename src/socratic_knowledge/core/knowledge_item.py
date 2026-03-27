"""Knowledge Item data model."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

from ..utils import ensure_iso_datetime


@dataclass
class KnowledgeItem:
    """
    Core knowledge entity with versioning, access control, and metadata.

    Represents any knowledge artifact: document, note, snippet, etc.
    """

    item_id: str
    tenant_id: str
    title: str
    content: str
    content_type: str

    # Ownership and relationships
    collection_id: Optional[str] = None
    owner_id: str = "system"

    # Versioning
    version: int = 1
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: str = "system"
    updated_by: str = "system"

    # Access control
    permissions: Dict[str, List[str]] = field(default_factory=dict)

    # Metadata
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Status
    is_deleted: bool = False
    deleted_at: Optional[datetime] = None

    def __post_init__(self) -> None:
        """Initialize datetime fields if not provided."""
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)
        if self.updated_at is None:
            self.updated_at = datetime.now(timezone.utc)

    @classmethod
    def create(
        cls,
        title: str,
        content: str,
        tenant_id: str,
        created_by: str,
        content_type: str = "text",
        **kwargs: Any,
    ) -> "KnowledgeItem":
        """
        Factory method to create knowledge item with auto-generated ID.

        Args:
            title: Item title
            content: Item content
            tenant_id: Tenant ID for multi-tenancy
            created_by: Creator user ID
            content_type: Content type (text, markdown, json)
            **kwargs: Additional arguments

        Returns:
            KnowledgeItem: New knowledge item
        """
        return cls(
            item_id=str(uuid4()),
            tenant_id=tenant_id,
            title=title,
            content=content,
            content_type=content_type,
            created_by=created_by,
            updated_by=created_by,
            owner_id=created_by,
            **kwargs,
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize to dictionary for storage.

        Returns:
            Dict[str, Any]: Serialized knowledge item
        """
        return {
            "item_id": self.item_id,
            "tenant_id": self.tenant_id,
            "collection_id": self.collection_id,
            "title": self.title,
            "content": self.content,
            "content_type": self.content_type,
            "version": self.version,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "created_by": self.created_by,
            "updated_by": self.updated_by,
            "owner_id": self.owner_id,
            "permissions": self.permissions,
            "tags": self.tags,
            "metadata": self.metadata,
            "is_deleted": self.is_deleted,
            "deleted_at": self.deleted_at.isoformat() if self.deleted_at else None,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "KnowledgeItem":
        """
        Deserialize from dictionary.

        Args:
            data: Serialized data

        Returns:
            KnowledgeItem: Deserialized knowledge item
        """
        # Parse datetime strings to datetime objects
        data = ensure_iso_datetime(
            data, "created_at", "updated_at", "deleted_at"
        )
        return cls(**data)

    def increment_version(self) -> None:
        """Increment version number."""
        self.version += 1
        self.updated_at = datetime.now(timezone.utc)
