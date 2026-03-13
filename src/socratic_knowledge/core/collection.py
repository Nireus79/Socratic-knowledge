"""Collection data model for hierarchical organization."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4


@dataclass
class Collection:
    """
    Hierarchical container for organizing knowledge items.

    Similar to folders, with ACL inheritance and metadata.
    """

    collection_id: str
    tenant_id: str
    name: str

    # Hierarchy
    parent_id: Optional[str] = None

    # Ownership
    owner_id: str = "system"

    # Access control
    permissions: Dict[str, List[str]] = field(default_factory=dict)
    inherit_permissions: bool = True

    # Metadata
    description: str = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: str = "system"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Initialize datetime fields if not provided."""
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)
        if self.updated_at is None:
            self.updated_at = datetime.now(timezone.utc)

    @classmethod
    def create(
        cls,
        name: str,
        tenant_id: str,
        created_by: str,
        parent_id: Optional[str] = None,
        **kwargs: Any,
    ) -> "Collection":
        """
        Create collection with auto-generated ID.

        Args:
            name: Collection name
            tenant_id: Tenant ID
            created_by: Creator user ID
            parent_id: Parent collection ID (for hierarchy)
            **kwargs: Additional arguments

        Returns:
            Collection: New collection
        """
        return cls(
            collection_id=str(uuid4()),
            tenant_id=tenant_id,
            parent_id=parent_id,
            name=name,
            created_by=created_by,
            owner_id=created_by,
            **kwargs,
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize to dictionary.

        Returns:
            Dict[str, Any]: Serialized collection
        """
        return {
            "collection_id": self.collection_id,
            "tenant_id": self.tenant_id,
            "parent_id": self.parent_id,
            "name": self.name,
            "description": self.description,
            "owner_id": self.owner_id,
            "permissions": self.permissions,
            "inherit_permissions": self.inherit_permissions,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "created_by": self.created_by,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Collection":
        """
        Deserialize from dictionary.

        Args:
            data: Serialized data

        Returns:
            Collection: Deserialized collection
        """
        # Parse datetime strings
        created_at = data.get("created_at")
        if isinstance(created_at, str):
            data = {**data, "created_at": datetime.fromisoformat(created_at)}

        updated_at = data.get("updated_at")
        if isinstance(updated_at, str):
            data = {**data, "updated_at": datetime.fromisoformat(updated_at)}

        return cls(**data)

    def get_path(self, storage: Any) -> List[str]:
        """
        Get full hierarchical path.

        Args:
            storage: Storage instance to fetch parents

        Returns:
            List[str]: Path like ["Root", "Projects", "AI"]
        """
        path = [self.name]
        current = self
        while current.parent_id:
            parent = storage.get_collection(current.parent_id)
            if not parent:
                break
            path.insert(0, parent.name)
            current = parent
        return path
