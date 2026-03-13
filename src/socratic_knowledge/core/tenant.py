"""Tenant data model for multi-tenancy support."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4


@dataclass
class Tenant:
    """
    Tenant for multi-tenancy support.

    Isolates knowledge, users, and permissions per organization.
    """

    tenant_id: str
    name: str

    # Configuration
    domain: Optional[str] = None
    max_storage_mb: int = 1000
    max_users: int = 100
    features: List[str] = field(default_factory=lambda: ["basic"])

    # Status
    is_active: bool = True
    created_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Initialize datetime fields if not provided."""
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)

    @classmethod
    def create(cls, name: str, **kwargs: Any) -> "Tenant":
        """
        Create tenant with auto-generated ID.

        Args:
            name: Tenant name
            **kwargs: Additional arguments

        Returns:
            Tenant: New tenant
        """
        return cls(
            tenant_id=str(uuid4()),
            name=name,
            **kwargs,
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize to dictionary.

        Returns:
            Dict[str, Any]: Serialized tenant
        """
        return {
            "tenant_id": self.tenant_id,
            "name": self.name,
            "domain": self.domain,
            "max_storage_mb": self.max_storage_mb,
            "max_users": self.max_users,
            "features": self.features,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Tenant":
        """
        Deserialize from dictionary.

        Args:
            data: Serialized data

        Returns:
            Tenant: Deserialized tenant
        """
        # Parse datetime strings
        created_at = data.get("created_at")
        if isinstance(created_at, str):
            data = {**data, "created_at": datetime.fromisoformat(created_at)}

        return cls(**data)
