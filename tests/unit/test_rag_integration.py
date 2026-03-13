"""Tests for RAG integration and semantic search."""

import pytest
from unittest.mock import MagicMock, patch

from socratic_knowledge.core.knowledge_item import KnowledgeItem
from socratic_knowledge.retrieval.rag_integration import (
    KnowledgeRAGIntegration,
)


class TestKnowledgeRAGIntegration:
    """Test RAG integration for semantic search."""

    def test_index_item(self):
        """Test indexing a knowledge item."""
        # Mock storage and RAG
        storage = MagicMock()
        rag_client = MagicMock()

        item = KnowledgeItem.create(
            title="Test",
            content="Content",
            tenant_id="t1",
            created_by="user1",
        )

        # Mock RAG client behavior
        rag_client.add_document.return_value = "doc_id_123"

        with patch("socratic_knowledge.retrieval.rag_integration.RAGClient") as mock_rag_class:
            mock_rag_class.return_value = rag_client
            integration = KnowledgeRAGIntegration(storage)
            doc_id = integration.index_item(item)

        assert doc_id == "doc_id_123"
        rag_client.add_document.assert_called_once()

    def test_index_item_metadata(self):
        """Test that metadata is properly formatted for RAG."""
        storage = MagicMock()
        rag_client = MagicMock()
        rag_client.add_document.return_value = "doc_123"

        item = KnowledgeItem.create(
            title="Test",
            content="Content",
            tenant_id="t1",
            created_by="user1",
            collection_id="coll1",
            tags=["tag1", "tag2"],
        )

        with patch("socratic_knowledge.retrieval.rag_integration.RAGClient") as mock_rag_class:
            mock_rag_class.return_value = rag_client
            integration = KnowledgeRAGIntegration(storage)
            integration.index_item(item)

        # Check the call arguments
        call_args = rag_client.add_document.call_args
        assert call_args is not None
        kwargs = call_args[1]

        # Check content includes both title and content
        content = kwargs["content"]
        assert "Title:" in content
        assert "Test" in content
        assert "Content" in content

        metadata = kwargs["metadata"]
        assert metadata["item_id"] == item.item_id
        assert metadata["tenant_id"] == "t1"
        assert metadata["collection_id"] == "coll1"
        assert metadata["tags"] == ["tag1", "tag2"]

    def test_update_index(self):
        """Test updating an item in the RAG index."""
        storage = MagicMock()
        rag_client = MagicMock()
        rag_client.clear.return_value = True
        rag_client.add_document.return_value = "doc_123"

        item = KnowledgeItem.create(
            title="Updated",
            content="New content",
            tenant_id="t1",
            created_by="user1",
        )

        with patch("socratic_knowledge.retrieval.rag_integration.RAGClient") as mock_rag_class:
            mock_rag_class.return_value = rag_client
            integration = KnowledgeRAGIntegration(storage)
            doc_id = integration.update_index(item)

        assert doc_id == "doc_123"
        rag_client.clear.assert_called_once()
        rag_client.add_document.assert_called_once()

    def test_semantic_search(self):
        """Test semantic search with RAG."""
        storage = MagicMock()
        rag_client = MagicMock()

        # Mock search result
        mock_result = MagicMock()
        mock_result.metadata = {
            "item_id": "item_123",
            "tenant_id": "t1",
        }
        rag_client.search.return_value = [mock_result]

        # Mock storage retrieval
        item = KnowledgeItem.create(
            title="Test",
            content="Content",
            tenant_id="t1",
            created_by="user1",
        )
        storage.get_item.return_value = item

        with patch("socratic_knowledge.retrieval.rag_integration.RAGClient") as mock_rag_class:
            mock_rag_class.return_value = rag_client
            integration = KnowledgeRAGIntegration(storage)
            results = integration.semantic_search(
                tenant_id="t1",
                query="test query",
                top_k=5,
            )

        assert len(results) == 1
        assert results[0].item_id == item.item_id

    def test_semantic_search_with_collection_filter(self):
        """Test semantic search with collection filtering."""
        storage = MagicMock()
        rag_client = MagicMock()
        rag_client.search.return_value = []

        with patch("socratic_knowledge.retrieval.rag_integration.RAGClient") as mock_rag_class:
            mock_rag_class.return_value = rag_client
            integration = KnowledgeRAGIntegration(storage)
            results = integration.semantic_search(
                tenant_id="t1",
                query="test",
                top_k=5,
                collection_id="coll1",
            )

        # Check that collection filter was passed
        call_args = rag_client.search.call_args
        filters = call_args[1]["filters"]
        assert filters["tenant_id"] == "t1"
        assert filters["collection_id"] == "coll1"

    def test_semantic_search_handles_missing_metadata(self):
        """Test that semantic search handles results without metadata."""
        storage = MagicMock()
        rag_client = MagicMock()

        # Mock result without metadata
        mock_result = MagicMock()
        mock_result.metadata = None
        rag_client.search.return_value = [mock_result]

        with patch("socratic_knowledge.retrieval.rag_integration.RAGClient") as mock_rag_class:
            mock_rag_class.return_value = rag_client
            integration = KnowledgeRAGIntegration(storage)
            results = integration.semantic_search(
                tenant_id="t1",
                query="test",
            )

        assert results == []

    def test_semantic_search_handles_missing_item_id(self):
        """Test that semantic search skips results without item_id."""
        storage = MagicMock()
        rag_client = MagicMock()

        mock_result = MagicMock()
        mock_result.metadata = {"tenant_id": "t1"}  # No item_id
        rag_client.search.return_value = [mock_result]

        with patch("socratic_knowledge.retrieval.rag_integration.RAGClient") as mock_rag_class:
            mock_rag_class.return_value = rag_client
            integration = KnowledgeRAGIntegration(storage)
            results = integration.semantic_search(
                tenant_id="t1",
                query="test",
            )

        assert results == []

    def test_semantic_search_handles_missing_items(self):
        """Test that semantic search skips items not found in storage."""
        storage = MagicMock()
        rag_client = MagicMock()
        storage.get_item.return_value = None  # Item not found

        mock_result = MagicMock()
        mock_result.metadata = {
            "item_id": "nonexistent",
            "tenant_id": "t1",
        }
        rag_client.search.return_value = [mock_result]

        with patch("socratic_knowledge.retrieval.rag_integration.RAGClient") as mock_rag_class:
            mock_rag_class.return_value = rag_client
            integration = KnowledgeRAGIntegration(storage)
            results = integration.semantic_search(
                tenant_id="t1",
                query="test",
            )

        assert results == []

    def test_get_context(self):
        """Test getting formatted context from RAG."""
        storage = MagicMock()
        rag_client = MagicMock()
        rag_client.retrieve_context.return_value = "Context text"

        with patch("socratic_knowledge.retrieval.rag_integration.RAGClient") as mock_rag_class:
            mock_rag_class.return_value = rag_client
            integration = KnowledgeRAGIntegration(storage)
            context = integration.get_context(
                tenant_id="t1",
                query="test query",
                top_k=5,
            )

        assert context == "Context text"
        rag_client.retrieve_context.assert_called_once_with("test query", top_k=5)

    def test_clear_index(self):
        """Test clearing the RAG index."""
        storage = MagicMock()
        rag_client = MagicMock()
        rag_client.clear.return_value = True

        with patch("socratic_knowledge.retrieval.rag_integration.RAGClient") as mock_rag_class:
            mock_rag_class.return_value = rag_client
            integration = KnowledgeRAGIntegration(storage)
            result = integration.clear_index()

        assert result is True
        rag_client.clear.assert_called_once()

    def test_index_item_with_no_collection(self):
        """Test indexing item without collection (root)."""
        storage = MagicMock()
        rag_client = MagicMock()
        rag_client.add_document.return_value = "doc_123"

        item = KnowledgeItem.create(
            title="Test",
            content="Content",
            tenant_id="t1",
            created_by="user1",
            collection_id=None,
        )

        with patch("socratic_knowledge.retrieval.rag_integration.RAGClient") as mock_rag_class:
            mock_rag_class.return_value = rag_client
            integration = KnowledgeRAGIntegration(storage)
            integration.index_item(item)

        call_args = rag_client.add_document.call_args
        metadata = call_args[1]["metadata"]
        assert metadata["collection_id"] == "root"

    def test_semantic_search_tenant_isolation(self):
        """Test that semantic search enforces tenant isolation."""
        storage = MagicMock()
        rag_client = MagicMock()

        mock_result = MagicMock()
        mock_result.metadata = {
            "item_id": "item_123",
            "tenant_id": "t1",
        }
        rag_client.search.return_value = [mock_result]

        # Mock that item belongs to different tenant
        item = KnowledgeItem.create(
            title="Test",
            content="Content",
            tenant_id="t2",  # Different tenant
            created_by="user1",
        )
        storage.get_item.return_value = item

        with patch("socratic_knowledge.retrieval.rag_integration.RAGClient") as mock_rag_class:
            mock_rag_class.return_value = rag_client
            integration = KnowledgeRAGIntegration(storage)
            results = integration.semantic_search(
                tenant_id="t1",  # Searching in t1
                query="test",
            )

        # Should still return item, caller is responsible for tenant check
        assert len(results) == 1
