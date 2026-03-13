"""Tests for search engine."""

from unittest.mock import MagicMock

import pytest

from socratic_knowledge.core.knowledge_item import KnowledgeItem
from socratic_knowledge.retrieval.search import SearchEngine, SearchMode


class TestSearchEngine:
    """Test search engine combining keyword and semantic search."""

    def test_keyword_search(self):
        """Test keyword search mode."""
        storage = MagicMock()
        item = KnowledgeItem.create(
            title="Test",
            content="Content",
            tenant_id="t1",
            created_by="user1",
        )
        storage.search.return_value = [item]

        engine = SearchEngine(storage)
        results = engine.search(
            tenant_id="t1",
            query="test",
            mode=SearchMode.KEYWORD,
            top_k=10,
        )

        assert len(results) == 1
        assert results[0].item_id == item.item_id
        storage.search.assert_called_once()

    def test_keyword_search_with_collection_filter(self):
        """Test keyword search with collection filtering."""
        storage = MagicMock()
        item1 = KnowledgeItem.create(
            title="Test",
            content="Content",
            tenant_id="t1",
            created_by="user1",
            collection_id="coll1",
        )
        item2 = KnowledgeItem.create(
            title="Test",
            content="Content",
            tenant_id="t1",
            created_by="user1",
            collection_id="coll2",
        )
        storage.search.return_value = [item1, item2]

        engine = SearchEngine(storage)
        results = engine.search(
            tenant_id="t1",
            query="test",
            mode=SearchMode.KEYWORD,
            top_k=10,
            collection_id="coll1",
        )

        # Should filter to only coll1
        assert len(results) == 1
        assert results[0].collection_id == "coll1"

    def test_keyword_search_respects_top_k(self):
        """Test that keyword search respects top_k limit."""
        storage = MagicMock()
        items = [
            KnowledgeItem.create(
                title=f"Item {i}",
                content="Content",
                tenant_id="t1",
                created_by="user1",
            )
            for i in range(20)
        ]
        storage.search.return_value = items

        engine = SearchEngine(storage)
        results = engine.search(
            tenant_id="t1",
            query="test",
            mode=SearchMode.KEYWORD,
            top_k=5,
        )

        assert len(results) == 5

    def test_semantic_search_requires_rag(self):
        """Test that semantic search raises error without RAG."""
        storage = MagicMock()
        engine = SearchEngine(storage, rag=None)

        with pytest.raises(ValueError, match="Semantic search requires RAG"):
            engine.search(
                tenant_id="t1",
                query="test",
                mode=SearchMode.SEMANTIC,
            )

    def test_semantic_search_with_rag(self):
        """Test semantic search with RAG enabled."""
        storage = MagicMock()
        rag = MagicMock()
        item = KnowledgeItem.create(
            title="Test",
            content="Content",
            tenant_id="t1",
            created_by="user1",
        )
        rag.semantic_search.return_value = [item]

        engine = SearchEngine(storage, rag=rag)
        results = engine.search(
            tenant_id="t1",
            query="test",
            mode=SearchMode.SEMANTIC,
            top_k=5,
        )

        assert len(results) == 1
        rag.semantic_search.assert_called_once()

    def test_hybrid_search_without_rag_falls_back(self):
        """Test hybrid search falls back to keyword without RAG."""
        storage = MagicMock()
        item = KnowledgeItem.create(
            title="Test",
            content="Content",
            tenant_id="t1",
            created_by="user1",
        )
        storage.search.return_value = [item]

        engine = SearchEngine(storage, rag=None)
        results = engine.search(
            tenant_id="t1",
            query="test",
            mode=SearchMode.HYBRID,
            top_k=10,
        )

        assert len(results) == 1
        storage.search.assert_called_once()

    def test_hybrid_search_with_rag(self):
        """Test hybrid search combining both modes."""
        storage = MagicMock()
        rag = MagicMock()

        # Create different items for each search type
        item1 = KnowledgeItem.create(
            title="Semantic Result",
            content="Content 1",
            tenant_id="t1",
            created_by="user1",
        )
        item2 = KnowledgeItem.create(
            title="Keyword Result",
            content="Content 2",
            tenant_id="t1",
            created_by="user1",
        )

        storage.search.return_value = [item2, item2, item2]
        rag.semantic_search.return_value = [item1, item1, item1]

        engine = SearchEngine(storage, rag=rag)
        results = engine.search(
            tenant_id="t1",
            query="test",
            mode=SearchMode.HYBRID,
            top_k=5,
        )

        # Should have both items, interleaved
        assert len(results) == 2
        # First result should be semantic, second keyword
        assert results[0].item_id == item1.item_id
        assert results[1].item_id == item2.item_id

    def test_hybrid_search_deduplicates(self):
        """Test that hybrid search deduplicates results."""
        storage = MagicMock()
        rag = MagicMock()

        # Same item in both results
        item = KnowledgeItem.create(
            title="Test",
            content="Content",
            tenant_id="t1",
            created_by="user1",
        )

        storage.search.return_value = [item, item, item]
        rag.semantic_search.return_value = [item, item, item]

        engine = SearchEngine(storage, rag=rag)
        results = engine.search(
            tenant_id="t1",
            query="test",
            mode=SearchMode.HYBRID,
            top_k=10,
        )

        # Should only have one unique item
        assert len(results) == 1

    def test_hybrid_search_respects_top_k(self):
        """Test that hybrid search respects top_k limit."""
        storage = MagicMock()
        rag = MagicMock()

        items_keyword = [
            KnowledgeItem.create(
                title=f"Keyword {i}",
                content="Content",
                tenant_id="t1",
                created_by="user1",
            )
            for i in range(10)
        ]
        items_semantic = [
            KnowledgeItem.create(
                title=f"Semantic {i}",
                content="Content",
                tenant_id="t1",
                created_by="user1",
            )
            for i in range(10)
        ]

        storage.search.return_value = items_keyword
        rag.semantic_search.return_value = items_semantic

        engine = SearchEngine(storage, rag=rag)
        results = engine.search(
            tenant_id="t1",
            query="test",
            mode=SearchMode.HYBRID,
            top_k=5,
        )

        assert len(results) == 5

    def test_invalid_search_mode(self):
        """Test that invalid search mode raises error."""
        storage = MagicMock()
        engine = SearchEngine(storage)

        with pytest.raises(ValueError, match="Unknown search mode"):
            engine.search(
                tenant_id="t1",
                query="test",
                mode="invalid",  # Invalid mode
            )

    def test_hybrid_search_with_collection_filter(self):
        """Test hybrid search with collection filtering."""
        storage = MagicMock()
        rag = MagicMock()

        item = KnowledgeItem.create(
            title="Test",
            content="Content",
            tenant_id="t1",
            created_by="user1",
            collection_id="coll1",
        )

        storage.search.return_value = [item]
        rag.semantic_search.return_value = [item]

        engine = SearchEngine(storage, rag=rag)
        results = engine.search(
            tenant_id="t1",
            query="test",
            mode=SearchMode.HYBRID,
            top_k=10,
            collection_id="coll1",
        )

        assert len(results) == 1
        rag.semantic_search.assert_called_once_with(
            tenant_id="t1",
            query="test",
            top_k=20,
            collection_id="coll1",
        )

    def test_search_default_mode_is_hybrid(self):
        """Test that default search mode is hybrid."""
        storage = MagicMock()
        rag = MagicMock()
        item = KnowledgeItem.create(
            title="Test",
            content="Content",
            tenant_id="t1",
            created_by="user1",
        )
        storage.search.return_value = [item]
        rag.semantic_search.return_value = [item]

        engine = SearchEngine(storage, rag=rag)
        engine.search(
            tenant_id="t1",
            query="test",
        )

        # Both search methods should be called (hybrid mode)
        storage.search.assert_called()
        rag.semantic_search.assert_called()

    def test_empty_keyword_results(self):
        """Test hybrid search with no keyword results."""
        storage = MagicMock()
        rag = MagicMock()

        item_semantic = KnowledgeItem.create(
            title="Semantic",
            content="Content",
            tenant_id="t1",
            created_by="user1",
        )

        storage.search.return_value = []
        rag.semantic_search.return_value = [item_semantic]

        engine = SearchEngine(storage, rag=rag)
        results = engine.search(
            tenant_id="t1",
            query="test",
            mode=SearchMode.HYBRID,
            top_k=5,
        )

        assert len(results) == 1
        assert results[0].item_id == item_semantic.item_id

    def test_empty_semantic_results(self):
        """Test hybrid search with no semantic results."""
        storage = MagicMock()
        rag = MagicMock()

        item_keyword = KnowledgeItem.create(
            title="Keyword",
            content="Content",
            tenant_id="t1",
            created_by="user1",
        )

        storage.search.return_value = [item_keyword]
        rag.semantic_search.return_value = []

        engine = SearchEngine(storage, rag=rag)
        results = engine.search(
            tenant_id="t1",
            query="test",
            mode=SearchMode.HYBRID,
            top_k=5,
        )

        assert len(results) == 1
        assert results[0].item_id == item_keyword.item_id

    def test_empty_all_results(self):
        """Test hybrid search with no results."""
        storage = MagicMock()
        rag = MagicMock()

        storage.search.return_value = []
        rag.semantic_search.return_value = []

        engine = SearchEngine(storage, rag=rag)
        results = engine.search(
            tenant_id="t1",
            query="test",
            mode=SearchMode.HYBRID,
            top_k=5,
        )

        assert len(results) == 0
