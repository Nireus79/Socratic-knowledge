"""Automatic indexing of knowledge items for RAG."""

from typing import List

from ..core.knowledge_item import KnowledgeItem
from .rag_integration import KnowledgeRAGIntegration


class KnowledgeIndexer:
    """
    Manages automatic indexing of knowledge items.

    Maintains RAG index in sync with knowledge items.
    """

    def __init__(self, rag: KnowledgeRAGIntegration):
        """
        Initialize indexer.

        Args:
            rag: RAG integration instance
        """
        self.rag = rag

    def index_items(
        self,
        items: List[KnowledgeItem],
    ) -> int:
        """
        Index multiple knowledge items.

        Args:
            items: List of items to index

        Returns:
            int: Number of items successfully indexed
        """
        indexed_count = 0
        for item in items:
            try:
                self.rag.index_item(item)
                indexed_count += 1
            except Exception:
                # Continue indexing others if one fails
                continue

        return indexed_count

    def index_item(self, item: KnowledgeItem) -> str:
        """
        Index a single knowledge item.

        Args:
            item: Item to index

        Returns:
            str: Document ID in RAG index
        """
        return self.rag.index_item(item)

    def re_index_item(self, item: KnowledgeItem) -> str:
        """
        Re-index a knowledge item (for updates).

        Args:
            item: Updated item

        Returns:
            str: Document ID in RAG index
        """
        return self.rag.update_index(item)

    def clear_index(self) -> bool:
        """
        Clear the RAG index.

        Returns:
            bool: True if successful
        """
        return self.rag.clear_index()
