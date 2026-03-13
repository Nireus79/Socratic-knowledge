"""Tests for knowledge indexer."""

from unittest.mock import MagicMock

from socratic_knowledge.core.knowledge_item import KnowledgeItem
from socratic_knowledge.retrieval.indexer import KnowledgeIndexer


class TestKnowledgeIndexer:
    """Test KnowledgeIndexer for automatic indexing."""

    def test_index_item(self):
        """Test indexing a single item."""
        rag = MagicMock()
        rag.index_item.return_value = "doc_123"

        item = KnowledgeItem.create(
            title="Test",
            content="Content",
            tenant_id="t1",
            created_by="user1",
        )

        indexer = KnowledgeIndexer(rag)
        doc_id = indexer.index_item(item)

        assert doc_id == "doc_123"
        rag.index_item.assert_called_once_with(item)

    def test_index_items(self):
        """Test indexing multiple items."""
        rag = MagicMock()
        rag.index_item.return_value = "doc_123"

        items = [
            KnowledgeItem.create(
                title=f"Item {i}",
                content="Content",
                tenant_id="t1",
                created_by="user1",
            )
            for i in range(3)
        ]

        indexer = KnowledgeIndexer(rag)
        count = indexer.index_items(items)

        assert count == 3
        assert rag.index_item.call_count == 3

    def test_index_items_handles_errors(self):
        """Test that indexing continues even if one fails."""
        rag = MagicMock()
        rag.index_item.side_effect = [
            "doc_1",
            Exception("Index error"),
            "doc_3",
        ]

        items = [
            KnowledgeItem.create(
                title=f"Item {i}",
                content="Content",
                tenant_id="t1",
                created_by="user1",
            )
            for i in range(3)
        ]

        indexer = KnowledgeIndexer(rag)
        count = indexer.index_items(items)

        # Should have indexed 2 items (first and third)
        assert count == 2
        assert rag.index_item.call_count == 3

    def test_re_index_item(self):
        """Test re-indexing an updated item."""
        rag = MagicMock()
        rag.update_index.return_value = "doc_456"

        item = KnowledgeItem.create(
            title="Updated",
            content="New content",
            tenant_id="t1",
            created_by="user1",
        )

        indexer = KnowledgeIndexer(rag)
        doc_id = indexer.re_index_item(item)

        assert doc_id == "doc_456"
        rag.update_index.assert_called_once_with(item)

    def test_clear_index(self):
        """Test clearing the index."""
        rag = MagicMock()
        rag.clear_index.return_value = True

        indexer = KnowledgeIndexer(rag)
        result = indexer.clear_index()

        assert result is True
        rag.clear_index.assert_called_once()

    def test_index_empty_list(self):
        """Test indexing empty list."""
        rag = MagicMock()

        indexer = KnowledgeIndexer(rag)
        count = indexer.index_items([])

        assert count == 0
        rag.index_item.assert_not_called()

    def test_index_all_items_fail(self):
        """Test when all items fail to index."""
        rag = MagicMock()
        rag.index_item.side_effect = Exception("Index error")

        items = [
            KnowledgeItem.create(
                title=f"Item {i}",
                content="Content",
                tenant_id="t1",
                created_by="user1",
            )
            for i in range(3)
        ]

        indexer = KnowledgeIndexer(rag)
        count = indexer.index_items(items)

        assert count == 0
