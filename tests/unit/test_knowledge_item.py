"""Tests for KnowledgeItem model."""

import pytest

from socratic_knowledge.core.knowledge_item import KnowledgeItem


class TestKnowledgeItem:
    """Test KnowledgeItem model."""

    def test_create_knowledge_item(self):
        """Test creating a knowledge item."""
        item = KnowledgeItem.create(
            title="Test Item",
            content="Test content",
            tenant_id="tenant1",
            created_by="user1",
        )

        assert item.item_id is not None
        assert item.title == "Test Item"
        assert item.content == "Test content"
        assert item.tenant_id == "tenant1"
        assert item.created_by == "user1"
        assert item.version == 1
        assert item.is_deleted is False

    def test_knowledge_item_to_dict(self):
        """Test serialization."""
        item = KnowledgeItem.create(
            title="Test",
            content="Content",
            tenant_id="t1",
            created_by="u1",
            tags=["tag1", "tag2"],
        )

        data = item.to_dict()

        assert data["title"] == "Test"
        assert data["content"] == "Content"
        assert data["tenant_id"] == "t1"
        assert data["tags"] == ["tag1", "tag2"]

    def test_knowledge_item_from_dict(self):
        """Test deserialization."""
        original = KnowledgeItem.create(
            title="Test",
            content="Content",
            tenant_id="t1",
            created_by="u1",
        )

        data = original.to_dict()
        restored = KnowledgeItem.from_dict(data)

        assert restored.title == original.title
        assert restored.content == original.content
        assert restored.tenant_id == original.tenant_id

    def test_knowledge_item_increment_version(self):
        """Test version incrementing."""
        item = KnowledgeItem.create(
            title="Test",
            content="Content",
            tenant_id="t1",
            created_by="u1",
        )

        assert item.version == 1
        item.increment_version()
        assert item.version == 2

    def test_knowledge_item_with_collection(self):
        """Test knowledge item with collection."""
        item = KnowledgeItem.create(
            title="Test",
            content="Content",
            tenant_id="t1",
            created_by="u1",
            collection_id="coll1",
        )

        assert item.collection_id == "coll1"

    def test_knowledge_item_with_metadata(self):
        """Test knowledge item with metadata."""
        metadata = {"key": "value", "nested": {"field": "data"}}
        item = KnowledgeItem.create(
            title="Test",
            content="Content",
            tenant_id="t1",
            created_by="u1",
            metadata=metadata,
        )

        assert item.metadata == metadata
        data = item.to_dict()
        assert data["metadata"] == metadata
