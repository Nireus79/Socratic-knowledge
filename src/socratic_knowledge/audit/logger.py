"""Audit logging for knowledge management operations."""

from typing import Any, Dict, List, Optional
from uuid import uuid4

from .events import AuditEvent, AuditEventType


class AuditLogger:
    """
    Audit logging system for tracking all operations.

    Maintains a complete audit trail for compliance and debugging.
    """

    def __init__(self):
        """Initialize audit logger."""
        self._events: List[AuditEvent] = []

    def log_event(
        self,
        event_type: AuditEventType,
        tenant_id: str,
        user_id: str,
        resource_type: str,
        resource_id: str,
        action: str,
        changes: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> AuditEvent:
        """
        Log an audit event.

        Args:
            event_type: Type of event
            tenant_id: Tenant ID
            user_id: User performing action
            resource_type: Type of resource (item, collection, etc.)
            resource_id: ID of resource
            action: Action performed (create, update, delete, etc.)
            changes: Dictionary of changes made
            metadata: Optional metadata
            ip_address: Optional IP address of user
            user_agent: Optional user agent string

        Returns:
            AuditEvent: Logged event
        """
        event = AuditEvent(
            event_id=str(uuid4()),
            event_type=event_type,
            tenant_id=tenant_id,
            user_id=user_id,
            resource_type=resource_type,
            resource_id=resource_id,
            action=action,
            changes=changes or {},
            metadata=metadata or {},
            ip_address=ip_address,
            user_agent=user_agent,
        )
        self._events.append(event)
        return event

    def get_events(
        self,
        tenant_id: Optional[str] = None,
        user_id: Optional[str] = None,
        resource_id: Optional[str] = None,
        event_type: Optional[AuditEventType] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[AuditEvent]:
        """
        Query audit events.

        Args:
            tenant_id: Filter by tenant
            user_id: Filter by user
            resource_id: Filter by resource
            event_type: Filter by event type
            limit: Maximum events to return
            offset: Number of events to skip

        Returns:
            List[AuditEvent]: Matching events
        """
        results = self._events

        if tenant_id:
            results = [e for e in results if e.tenant_id == tenant_id]

        if user_id:
            results = [e for e in results if e.user_id == user_id]

        if resource_id:
            results = [e for e in results if e.resource_id == resource_id]

        if event_type:
            results = [e for e in results if e.event_type == event_type]

        # Return in reverse chronological order
        results = list(reversed(results))

        return results[offset : offset + limit]

    def get_user_activity(
        self,
        tenant_id: str,
        user_id: str,
        limit: int = 50,
    ) -> List[AuditEvent]:
        """
        Get activity for specific user.

        Args:
            tenant_id: Tenant ID
            user_id: User ID
            limit: Maximum events to return

        Returns:
            List[AuditEvent]: User's recent actions
        """
        return self.get_events(
            tenant_id=tenant_id,
            user_id=user_id,
            limit=limit,
        )

    def get_resource_history(
        self,
        resource_id: str,
        limit: int = 50,
    ) -> List[AuditEvent]:
        """
        Get change history for specific resource.

        Args:
            resource_id: Resource ID
            limit: Maximum events to return

        Returns:
            List[AuditEvent]: Resource history
        """
        return self.get_events(
            resource_id=resource_id,
            limit=limit,
        )

    def get_tenant_audit_log(
        self,
        tenant_id: str,
        limit: int = 100,
    ) -> List[AuditEvent]:
        """
        Get complete audit log for tenant.

        Args:
            tenant_id: Tenant ID
            limit: Maximum events to return

        Returns:
            List[AuditEvent]: Tenant audit trail
        """
        return self.get_events(
            tenant_id=tenant_id,
            limit=limit,
        )

    def clear_events(self, tenant_id: Optional[str] = None) -> int:
        """
        Clear audit events.

        Args:
            tenant_id: If specified, only clear events for this tenant

        Returns:
            int: Number of events cleared
        """
        if not tenant_id:
            count = len(self._events)
            self._events = []
            return count

        original_count = len(self._events)
        self._events = [e for e in self._events if e.tenant_id != tenant_id]
        return original_count - len(self._events)

    def count_events(
        self,
        tenant_id: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> int:
        """
        Count audit events.

        Args:
            tenant_id: Optional tenant filter
            user_id: Optional user filter

        Returns:
            int: Number of matching events
        """
        count = len(self._events)

        if tenant_id:
            count = len([e for e in self._events if e.tenant_id == tenant_id])

        if user_id:
            count = len(
                [
                    e for e in self._events
                    if e.tenant_id == tenant_id and e.user_id == user_id
                ]
            )

        return count
