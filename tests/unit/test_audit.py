"""Tests for audit logging."""


from socratic_knowledge.audit.events import AuditEvent, AuditEventType
from socratic_knowledge.audit.logger import AuditLogger


class TestAuditLogger:
    """Test audit logging system."""

    def test_log_event(self):
        """Test logging an event."""
        logger = AuditLogger()
        event = logger.log_event(
            event_type=AuditEventType.ITEM_CREATED,
            tenant_id="t1",
            user_id="user1",
            resource_type="item",
            resource_id="item_123",
            action="create",
        )

        assert event.event_type == AuditEventType.ITEM_CREATED
        assert event.tenant_id == "t1"
        assert event.user_id == "user1"
        assert event.resource_id == "item_123"

    def test_log_event_with_changes(self):
        """Test logging event with change details."""
        logger = AuditLogger()
        changes = {"title": "New Title", "content": "New Content"}
        event = logger.log_event(
            event_type=AuditEventType.ITEM_UPDATED,
            tenant_id="t1",
            user_id="user1",
            resource_type="item",
            resource_id="item_123",
            action="update",
            changes=changes,
        )

        assert event.changes == changes

    def test_get_events_all(self):
        """Test retrieving all events."""
        logger = AuditLogger()
        logger.log_event(
            AuditEventType.ITEM_CREATED,
            "t1",
            "user1",
            "item",
            "item_1",
            "create",
        )
        logger.log_event(
            AuditEventType.ITEM_UPDATED,
            "t1",
            "user1",
            "item",
            "item_2",
            "update",
        )

        events = logger.get_events()
        assert len(events) == 2

    def test_get_events_by_tenant(self):
        """Test filtering events by tenant."""
        logger = AuditLogger()
        logger.log_event(
            AuditEventType.ITEM_CREATED,
            "t1",
            "user1",
            "item",
            "item_1",
            "create",
        )
        logger.log_event(
            AuditEventType.ITEM_CREATED,
            "t2",
            "user1",
            "item",
            "item_2",
            "create",
        )

        events = logger.get_events(tenant_id="t1")
        assert len(events) == 1
        assert events[0].tenant_id == "t1"

    def test_get_events_by_user(self):
        """Test filtering events by user."""
        logger = AuditLogger()
        logger.log_event(
            AuditEventType.ITEM_CREATED,
            "t1",
            "user1",
            "item",
            "item_1",
            "create",
        )
        logger.log_event(
            AuditEventType.ITEM_CREATED,
            "t1",
            "user2",
            "item",
            "item_2",
            "create",
        )

        events = logger.get_events(user_id="user1")
        assert len(events) == 1
        assert events[0].user_id == "user1"

    def test_get_events_by_resource_id(self):
        """Test filtering events by resource ID."""
        logger = AuditLogger()
        logger.log_event(
            AuditEventType.ITEM_CREATED,
            "t1",
            "user1",
            "item",
            "item_1",
            "create",
        )
        logger.log_event(
            AuditEventType.ITEM_UPDATED,
            "t1",
            "user1",
            "item",
            "item_1",
            "update",
        )
        logger.log_event(
            AuditEventType.ITEM_CREATED,
            "t1",
            "user1",
            "item",
            "item_2",
            "create",
        )

        events = logger.get_events(resource_id="item_1")
        assert len(events) == 2

    def test_get_events_by_type(self):
        """Test filtering events by type."""
        logger = AuditLogger()
        logger.log_event(
            AuditEventType.ITEM_CREATED,
            "t1",
            "user1",
            "item",
            "item_1",
            "create",
        )
        logger.log_event(
            AuditEventType.ITEM_UPDATED,
            "t1",
            "user1",
            "item",
            "item_1",
            "update",
        )

        events = logger.get_events(event_type=AuditEventType.ITEM_CREATED)
        assert len(events) == 1
        assert events[0].event_type == AuditEventType.ITEM_CREATED

    def test_get_user_activity(self):
        """Test getting user activity."""
        logger = AuditLogger()
        logger.log_event(
            AuditEventType.ITEM_CREATED,
            "t1",
            "user1",
            "item",
            "item_1",
            "create",
        )
        logger.log_event(
            AuditEventType.ITEM_CREATED,
            "t1",
            "user2",
            "item",
            "item_2",
            "create",
        )

        activity = logger.get_user_activity("t1", "user1")
        assert len(activity) == 1

    def test_get_resource_history(self):
        """Test getting resource history."""
        logger = AuditLogger()
        logger.log_event(
            AuditEventType.ITEM_CREATED,
            "t1",
            "user1",
            "item",
            "item_1",
            "create",
        )
        logger.log_event(
            AuditEventType.ITEM_UPDATED,
            "t1",
            "user1",
            "item",
            "item_1",
            "update",
        )

        history = logger.get_resource_history("item_1")
        assert len(history) == 2

    def test_get_tenant_audit_log(self):
        """Test getting complete audit log for tenant."""
        logger = AuditLogger()
        logger.log_event(
            AuditEventType.ITEM_CREATED,
            "t1",
            "user1",
            "item",
            "item_1",
            "create",
        )
        logger.log_event(
            AuditEventType.ITEM_CREATED,
            "t2",
            "user1",
            "item",
            "item_2",
            "create",
        )

        log = logger.get_tenant_audit_log("t1")
        assert len(log) == 1
        assert log[0].tenant_id == "t1"

    def test_clear_events_all(self):
        """Test clearing all events."""
        logger = AuditLogger()
        logger.log_event(
            AuditEventType.ITEM_CREATED,
            "t1",
            "user1",
            "item",
            "item_1",
            "create",
        )

        count = logger.clear_events()
        assert count == 1

        events = logger.get_events()
        assert len(events) == 0

    def test_clear_events_by_tenant(self):
        """Test clearing events for specific tenant."""
        logger = AuditLogger()
        logger.log_event(
            AuditEventType.ITEM_CREATED,
            "t1",
            "user1",
            "item",
            "item_1",
            "create",
        )
        logger.log_event(
            AuditEventType.ITEM_CREATED,
            "t2",
            "user1",
            "item",
            "item_2",
            "create",
        )

        count = logger.clear_events(tenant_id="t1")
        assert count == 1

        events = logger.get_events()
        assert len(events) == 1
        assert events[0].tenant_id == "t2"

    def test_count_events(self):
        """Test counting events."""
        logger = AuditLogger()
        logger.log_event(
            AuditEventType.ITEM_CREATED,
            "t1",
            "user1",
            "item",
            "item_1",
            "create",
        )
        logger.log_event(
            AuditEventType.ITEM_CREATED,
            "t1",
            "user1",
            "item",
            "item_2",
            "create",
        )

        count = logger.count_events()
        assert count == 2

    def test_count_events_by_tenant(self):
        """Test counting events by tenant."""
        logger = AuditLogger()
        logger.log_event(
            AuditEventType.ITEM_CREATED,
            "t1",
            "user1",
            "item",
            "item_1",
            "create",
        )
        logger.log_event(
            AuditEventType.ITEM_CREATED,
            "t2",
            "user1",
            "item",
            "item_2",
            "create",
        )

        count = logger.count_events(tenant_id="t1")
        assert count == 1

    def test_event_serialization(self):
        """Test event to_dict and from_dict."""
        logger = AuditLogger()
        event = logger.log_event(
            AuditEventType.ITEM_CREATED,
            "t1",
            "user1",
            "item",
            "item_1",
            "create",
        )

        data = event.to_dict()
        restored = AuditEvent.from_dict(data)

        assert restored.event_id == event.event_id
        assert restored.event_type == event.event_type
        assert restored.tenant_id == event.tenant_id

    def test_events_reverse_chronological(self):
        """Test that events are returned in reverse chronological order."""
        logger = AuditLogger()
        logger.log_event(
            AuditEventType.ITEM_CREATED,
            "t1",
            "user1",
            "item",
            "item_1",
            "create",
        )
        logger.log_event(
            AuditEventType.ITEM_UPDATED,
            "t1",
            "user1",
            "item",
            "item_1",
            "update",
        )

        events = logger.get_events()
        # Latest should be first
        assert events[0].event_type == AuditEventType.ITEM_UPDATED
        assert events[1].event_type == AuditEventType.ITEM_CREATED

    def test_pagination(self):
        """Test event pagination."""
        logger = AuditLogger()
        for i in range(15):
            logger.log_event(
                AuditEventType.ITEM_CREATED,
                "t1",
                "user1",
                "item",
                f"item_{i}",
                "create",
            )

        page1 = logger.get_events(limit=10, offset=0)
        page2 = logger.get_events(limit=10, offset=10)

        assert len(page1) == 10
        assert len(page2) == 5
