"""Audit event types and models."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional

from ..utils import ensure_iso_datetime


class AuditEventType(Enum):
    """Types of audit events."""

    # Item operations
    ITEM_CREATED = "item_created"
    ITEM_UPDATED = "item_updated"
    ITEM_DELETED = "item_deleted"
    ITEM_VIEWED = "item_viewed"

    # Collection operations
    COLLECTION_CREATED = "collection_created"
    COLLECTION_UPDATED = "collection_updated"
    COLLECTION_DELETED = "collection_deleted"

    # Tenant operations
    TENANT_CREATED = "tenant_created"
    TENANT_UPDATED = "tenant_updated"

    # Access control
    PERMISSION_GRANTED = "permission_granted"
    PERMISSION_REVOKED = "permission_revoked"

    # Version operations
    VERSION_CREATED = "version_created"
    ITEM_ROLLED_BACK = "item_rolled_back"

    # Search operations
    SEARCH_EXECUTED = "search_executed"

    # Conflict operations
    CONFLICT_DETECTED = "conflict_detected"
    CONFLICT_RESOLVED = "conflict_resolved"


@dataclass
class AuditEvent:
    """Represents a single audit event."""

    event_id: str
    event_type: AuditEventType
    tenant_id: str
    user_id: str
    resource_type: str  # "item", "collection", "tenant", etc.
    resource_id: str
    action: str  # "create", "update", "delete", etc.
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    changes: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "tenant_id": self.tenant_id,
            "user_id": self.user_id,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "action": self.action,
            "timestamp": self.timestamp.isoformat(),
            "changes": self.changes,
            "metadata": self.metadata,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AuditEvent":
        """Deserialize from dictionary."""
        event_type = data.get("event_type")
        if isinstance(event_type, str):
            data = {
                **data,
                "event_type": AuditEventType(event_type),
            }

        data = ensure_iso_datetime(data, "timestamp")

        return cls(**data)
