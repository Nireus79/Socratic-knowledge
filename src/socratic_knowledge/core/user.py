"""User data model."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional


@dataclass
class User:
    """
    User identity model.

    Represents a user with identity and metadata.
    """

    user_id: str
    tenant_id: str
    username: str
    email: str

    # Status
    is_active: bool = True
    created_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Initialize datetime fields if not provided."""
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "user_id": self.user_id,
            "tenant_id": self.tenant_id,
            "username": self.username,
            "email": self.email,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "User":
        """Deserialize from dictionary."""
        # Parse datetime strings
        created_at = data.get("created_at")
        if isinstance(created_at, str):
            data = {**data, "created_at": datetime.fromisoformat(created_at)}

        return cls(**data)
