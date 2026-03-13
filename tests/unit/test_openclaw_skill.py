"""Tests for Openclaw skill integration."""

import pytest
from unittest.mock import MagicMock, patch

from socratic_knowledge.integrations.openclaw import SocraticKnowledgeSkill


class TestSocraticKnowledgeSkill:
    """Test Openclaw skill integration."""

    def test_skill_initialization(self):
        """Test skill initialization."""
        skill = SocraticKnowledgeSkill(db_path=":memory:")

        assert skill.km is not None
        assert hasattr(skill, "search_knowledge")

    def test_skill_with_provided_manager(self):
        """Test skill with provided KnowledgeManager."""
        km = MagicMock()
        skill = SocraticKnowledgeSkill(knowledge_manager=km)

        assert skill.km is km

    def test_search_knowledge(self):
        """Test searching knowledge."""
        km = MagicMock()
        item = MagicMock()
        item.item_id = "item_1"
        item.title = "Test"
        item.content = "Content"
        item.collection_id = "coll_1"
        item.tags = ["tag1"]

        km.hybrid_search.return_value = [item]

        skill = SocraticKnowledgeSkill(knowledge_manager=km)
        results = skill.search_knowledge(
            tenant_id="t1",
            query="test",
            top_k=10,
        )

        assert len(results) == 1
        assert results[0]["title"] == "Test"
        assert results[0]["item_id"] == "item_1"

    def test_semantic_search(self):
        """Test semantic search."""
        km = MagicMock()
        item = MagicMock()
        item.item_id = "item_1"
        item.title = "Test"
        item.content = "Content"
        item.tags = ["tag1"]

        km.semantic_search.return_value = [item]

        skill = SocraticKnowledgeSkill(knowledge_manager=km)
        results = skill.semantic_search(
            tenant_id="t1",
            query="test",
            top_k=5,
        )

        assert len(results) == 1
        km.semantic_search.assert_called_once()

    def test_get_item(self):
        """Test getting item."""
        km = MagicMock()
        item = MagicMock()
        item.item_id = "item_1"
        item.title = "Test"
        item.content = "Content"
        item.collection_id = "coll_1"
        item.version = 1
        item.created_at = MagicMock()
        item.updated_at = MagicMock()
        item.tags = ["tag1"]
        item.metadata = {"key": "value"}

        km.get_item.return_value = item

        skill = SocraticKnowledgeSkill(knowledge_manager=km)
        result = skill.get_item("t1", "item_1")

        assert result["title"] == "Test"
        assert result["version"] == 1

    def test_get_item_not_found(self):
        """Test getting non-existent item."""
        km = MagicMock()
        km.get_item.return_value = None

        skill = SocraticKnowledgeSkill(knowledge_manager=km)
        result = skill.get_item("t1", "nonexistent")

        assert result is None

    def test_create_item(self):
        """Test creating item."""
        km = MagicMock()
        item = MagicMock()
        item.item_id = "item_1"
        item.title = "New"
        item.content = "Content"
        item.version = 1

        km.create_item.return_value = item
        km.log_audit_event.return_value = MagicMock()

        skill = SocraticKnowledgeSkill(knowledge_manager=km)
        result = skill.create_item(
            tenant_id="t1",
            title="New",
            content="Content",
            user_id="user1",
        )

        assert result["item_id"] == "item_1"
        km.log_audit_event.assert_called_once()

    def test_get_audit_log(self):
        """Test getting audit log."""
        km = MagicMock()
        event = MagicMock()
        event.event_type = MagicMock()
        event.event_type.value = "item_created"
        event.user_id = "user1"
        event.resource_type = "item"
        event.action = "create"
        event.timestamp = MagicMock()
        event.changes = {}

        km.get_audit_log.return_value = [event]

        skill = SocraticKnowledgeSkill(knowledge_manager=km)
        results = skill.get_audit_log("t1", limit=50)

        assert len(results) == 1
        assert results[0]["user_id"] == "user1"

    def test_get_user_activity(self):
        """Test getting user activity."""
        km = MagicMock()
        event = MagicMock()
        event.event_type = MagicMock()
        event.event_type.value = "item_created"
        event.action = "create"
        event.resource_type = "item"
        event.resource_id = "item_1"
        event.timestamp = MagicMock()

        km.get_user_activity.return_value = [event]

        skill = SocraticKnowledgeSkill(knowledge_manager=km)
        results = skill.get_user_activity("t1", "user1", limit=20)

        assert len(results) == 1
        assert results[0]["action"] == "create"

    def test_can_user_read(self):
        """Test checking read permission."""
        km = MagicMock()
        km.can_user_read.return_value = True

        skill = SocraticKnowledgeSkill(knowledge_manager=km)
        result = skill.can_user_read("t1", "user1", "item_1")

        assert result is True
        km.can_user_read.assert_called_once_with("user1", "item_1", "t1")

    def test_can_user_edit(self):
        """Test checking edit permission."""
        km = MagicMock()
        km.can_user_edit.return_value = False

        skill = SocraticKnowledgeSkill(knowledge_manager=km)
        result = skill.can_user_edit("t1", "user1", "item_1")

        assert result is False

    def test_grant_permission(self):
        """Test granting permission."""
        km = MagicMock()

        skill = SocraticKnowledgeSkill(knowledge_manager=km)
        result = skill.grant_permission(
            tenant_id="t1",
            item_id="item_1",
            user_id="user1",
            role="editor",
        )

        assert result is True
        km.grant_permission.assert_called_once()

    def test_grant_permission_invalid_role(self):
        """Test granting invalid permission."""
        km = MagicMock()
        km.grant_permission.side_effect = ValueError("Invalid role")

        skill = SocraticKnowledgeSkill(knowledge_manager=km)
        result = skill.grant_permission(
            tenant_id="t1",
            item_id="item_1",
            user_id="user1",
            role="invalid",
        )

        # Should handle error gracefully
        assert isinstance(result, bool)

    def test_get_skill_info(self):
        """Test getting skill info."""
        skill = SocraticKnowledgeSkill(db_path=":memory:")
        info = skill.get_skill_info()

        assert info["name"] == "SocraticKnowledge"
        assert "capabilities" in info
        assert "search_knowledge" in info["capabilities"]

    def test_skill_with_default_kg_initialization(self):
        """Test skill initializes KnowledgeManager with defaults."""
        skill = SocraticKnowledgeSkill()

        assert skill.km is not None
        # Default should work
        assert hasattr(skill.km, "store")

    def test_create_item_with_defaults(self):
        """Test creating item with optional parameters as defaults."""
        km = MagicMock()
        item = MagicMock()
        item.item_id = "item_1"
        item.title = "Test"
        item.content = "Content"
        item.version = 1

        km.create_item.return_value = item

        skill = SocraticKnowledgeSkill(knowledge_manager=km)
        result = skill.create_item(
            tenant_id="t1",
            title="Test",
            content="Content",
            user_id="user1",
        )

        # Check that tags and metadata defaulted to empty
        call_args = km.create_item.call_args
        assert call_args[1]["tags"] == []
        assert call_args[1]["metadata"] == {}

    def test_search_knowledge_empty_results(self):
        """Test search with no results."""
        km = MagicMock()
        km.hybrid_search.return_value = []

        skill = SocraticKnowledgeSkill(knowledge_manager=km)
        results = skill.search_knowledge("t1", "xyz", top_k=10)

        assert results == []

    def test_search_knowledge_multiple_results(self):
        """Test search with multiple results."""
        km = MagicMock()
        items = [
            MagicMock(
                item_id=f"item_{i}",
                title=f"Item {i}",
                content=f"Content {i}",
                collection_id="coll_1",
                tags=[],
            )
            for i in range(3)
        ]
        km.hybrid_search.return_value = items

        skill = SocraticKnowledgeSkill(knowledge_manager=km)
        results = skill.search_knowledge("t1", "test", top_k=10)

        assert len(results) == 3
        for i, result in enumerate(results):
            assert result["item_id"] == f"item_{i}"
