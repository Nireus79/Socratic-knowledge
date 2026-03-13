"""Search engine combining full-text and semantic search."""

from enum import Enum
from typing import List, Optional

from ..core.knowledge_item import KnowledgeItem
from ..storage.base import BaseKnowledgeStore
from .rag_integration import KnowledgeRAGIntegration


class SearchMode(Enum):
    """Search modes for retrieval."""

    KEYWORD = "keyword"  # Full-text search only (FTS5)
    SEMANTIC = "semantic"  # Semantic search only (RAG)
    HYBRID = "hybrid"  # Combined keyword + semantic


class SearchEngine:
    """
    Unified search engine combining keyword and semantic search.

    Supports full-text search (FTS5), semantic search (RAG embeddings),
    and hybrid search combining both.
    """

    def __init__(
        self,
        storage: BaseKnowledgeStore,
        rag: Optional[KnowledgeRAGIntegration] = None,
    ):
        """
        Initialize search engine.

        Args:
            storage: Knowledge store for retrieval
            rag: Optional RAG integration for semantic search
        """
        self.storage = storage
        self.rag = rag

    def search(
        self,
        tenant_id: str,
        query: str,
        mode: SearchMode = SearchMode.HYBRID,
        top_k: int = 10,
        collection_id: Optional[str] = None,
    ) -> List[KnowledgeItem]:
        """
        Search for knowledge items.

        Args:
            tenant_id: Tenant ID for isolation
            query: Search query
            mode: Search mode (keyword, semantic, hybrid)
            top_k: Maximum results
            collection_id: Optional collection filter

        Returns:
            List[KnowledgeItem]: Matching items

        Raises:
            ValueError: If semantic search requested but RAG not available
        """
        if mode == SearchMode.KEYWORD:
            return self._keyword_search(tenant_id, query, top_k, collection_id)

        if mode == SearchMode.SEMANTIC:
            if not self.rag:
                raise ValueError("Semantic search requires RAG integration")
            return self._semantic_search(tenant_id, query, top_k, collection_id)

        if mode == SearchMode.HYBRID:
            if not self.rag:
                # Fall back to keyword search if RAG unavailable
                return self._keyword_search(tenant_id, query, top_k, collection_id)

            return self._hybrid_search(tenant_id, query, top_k, collection_id)

        raise ValueError(f"Unknown search mode: {mode}")

    def _keyword_search(
        self,
        tenant_id: str,
        query: str,
        top_k: int,
        collection_id: Optional[str],
    ) -> List[KnowledgeItem]:
        """
        Full-text search using FTS5.

        Args:
            tenant_id: Tenant ID
            query: Search query
            top_k: Maximum results
            collection_id: Optional collection filter

        Returns:
            List[KnowledgeItem]: Matching items
        """
        results = self.storage.search(
            tenant_id=tenant_id,
            query=query,
            limit=top_k,
        )

        # Filter by collection if specified
        if collection_id:
            results = [item for item in results if item.collection_id == collection_id]

        return results[:top_k]

    def _semantic_search(
        self,
        tenant_id: str,
        query: str,
        top_k: int,
        collection_id: Optional[str],
    ) -> List[KnowledgeItem]:
        """
        Semantic search using RAG embeddings.

        Args:
            tenant_id: Tenant ID
            query: Search query
            top_k: Maximum results
            collection_id: Optional collection filter

        Returns:
            List[KnowledgeItem]: Matching items
        """
        if self.rag is None:
            raise ValueError("Semantic search requires RAG integration")
        return self.rag.semantic_search(
            tenant_id=tenant_id,
            query=query,
            top_k=top_k,
            collection_id=collection_id,
        )

    def _hybrid_search(
        self,
        tenant_id: str,
        query: str,
        top_k: int,
        collection_id: Optional[str],
    ) -> List[KnowledgeItem]:
        """
        Hybrid search combining keyword and semantic.

        Returns top_k results from combined ranking.

        Args:
            tenant_id: Tenant ID
            query: Search query
            top_k: Maximum results
            collection_id: Optional collection filter

        Returns:
            List[KnowledgeItem]: Combined top results
        """
        # Get results from both search types
        keyword_results = self._keyword_search(tenant_id, query, top_k * 2, collection_id)
        semantic_results = self._semantic_search(tenant_id, query, top_k * 2, collection_id)

        # Combine and deduplicate by item ID
        seen = set()
        combined = []

        # Interleave results for better diversity
        for i in range(max(len(keyword_results), len(semantic_results))):
            if i < len(semantic_results):
                item = semantic_results[i]
                if item.item_id not in seen:
                    combined.append(item)
                    seen.add(item.item_id)

            if i < len(keyword_results):
                item = keyword_results[i]
                if item.item_id not in seen:
                    combined.append(item)
                    seen.add(item.item_id)

        return combined[:top_k]
