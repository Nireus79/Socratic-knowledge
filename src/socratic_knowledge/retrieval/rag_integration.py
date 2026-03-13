"""RAG integration for semantic search and retrieval."""

from typing import Any, Dict, List, Optional

try:
    from socratic_rag import RAGClient, RAGConfig, SearchResult
except ImportError:
    RAGClient = None  # type: ignore
    RAGConfig = None  # type: ignore
    SearchResult = None  # type: ignore

from ..core.knowledge_item import KnowledgeItem
from ..storage.base import BaseKnowledgeStore


class KnowledgeRAGIntegration:
    """
    Integration with Socratic RAG for semantic search.

    Manages indexing of knowledge items and semantic retrieval via
    RAG embeddings with tenant isolation.
    """

    def __init__(
        self,
        storage: BaseKnowledgeStore,
        rag_config: Optional[RAGConfig] = None,
    ):
        """
        Initialize RAG integration.

        Args:
            storage: Knowledge store for retrieving items
            rag_config: RAG configuration (uses defaults if None)
        """
        self.storage = storage
        self.rag = RAGClient(rag_config or RAGConfig())

    def index_item(self, item: KnowledgeItem) -> str:
        """
        Add knowledge item to RAG index.

        Args:
            item: Knowledge item to index

        Returns:
            str: Document ID in RAG index
        """
        content = f"Title: {item.title}\n\n{item.content}"
        metadata = {
            "item_id": item.item_id,
            "tenant_id": item.tenant_id,
            "collection_id": item.collection_id or "root",
            "tags": item.tags,
            "created_by": item.created_by,
            "version": item.version,
        }

        doc_id = self.rag.add_document(
            content=content,
            source=f"knowledge://{item.item_id}",
            metadata=metadata,
        )
        return doc_id

    def update_index(self, item: KnowledgeItem) -> str:
        """
        Update RAG index when item changes.

        Deletes old entry and re-indexes.

        Args:
            item: Updated knowledge item

        Returns:
            str: Document ID in RAG index
        """
        # Delete old entry
        self.rag.clear()

        # Re-index new version
        return self.index_item(item)

    def semantic_search(
        self,
        tenant_id: str,
        query: str,
        top_k: int = 5,
        collection_id: Optional[str] = None,
    ) -> List[KnowledgeItem]:
        """
        Semantic search using RAG embeddings.

        Respects tenant isolation and optional collection filtering.

        Args:
            tenant_id: Tenant ID for isolation
            query: Search query
            top_k: Maximum results to return
            collection_id: Optional collection filter

        Returns:
            List[KnowledgeItem]: Matching items ranked by relevance
        """
        filters = {"tenant_id": tenant_id}
        if collection_id:
            filters["collection_id"] = collection_id

        results = self.rag.search(query, top_k=top_k, filters=filters)

        items = []
        for result in results:
            if not hasattr(result, "metadata") or not result.metadata:
                continue

            item_id = result.metadata.get("item_id")
            if not item_id:
                continue

            item = self.storage.get_item(item_id, tenant_id)
            if item:
                items.append(item)

        return items

    def get_context(
        self,
        tenant_id: str,
        query: str,
        top_k: int = 5,
    ) -> str:
        """
        Get formatted context from semantic search.

        Useful for RAG applications needing formatted context.

        Args:
            tenant_id: Tenant ID for isolation
            query: Search query
            top_k: Maximum results to use

        Returns:
            str: Formatted context string
        """
        filters = {"tenant_id": tenant_id}
        return self.rag.retrieve_context(query, top_k=top_k)

    def clear_index(self) -> bool:
        """
        Clear all RAG indexes.

        Use with caution - will delete all indexed content.

        Returns:
            bool: True if cleared successfully
        """
        return self.rag.clear()
