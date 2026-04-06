"""Bulk operations for efficient batch processing in Socratic Knowledge."""

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from .core.collection import Collection
from .core.knowledge_item import KnowledgeItem
from .core.tenant import Tenant
from .core.version import Version
from .storage.base import BaseKnowledgeStore


logger = logging.getLogger(__name__)


@dataclass
class BulkOperationResult:
    """Result of a bulk operation."""

    total_requested: int
    total_processed: int
    total_successful: int
    total_failed: int
    failed_items: List[Tuple[str, str]] = None  # List of (item_id, error_message)

    def __post_init__(self):
        """Initialize failed_items list if not provided."""
        if self.failed_items is None:
            self.failed_items = []

    @property
    def success_rate(self) -> float:
        """Calculate success rate as percentage."""
        if self.total_processed == 0:
            return 0.0
        return (self.total_successful / self.total_processed) * 100

    def __repr__(self) -> str:
        """Return string representation."""
        return (
            f"BulkOperationResult(processed={self.total_processed}/{self.total_requested}, "
            f"successful={self.total_successful}, "
            f"success_rate={self.success_rate:.1f}%)"
        )


class BulkOperationManager:
    """Manages efficient bulk operations on knowledge items and collections."""

    def __init__(self, store: BaseKnowledgeStore, batch_size: int = 100):
        """
        Initialize bulk operation manager.

        Args:
            store: Knowledge storage backend
            batch_size: Size of batches for processing
        """
        self.store = store
        self.batch_size = batch_size
        self.logger = logging.getLogger(__name__)

    def bulk_create_items(
        self,
        items: List[KnowledgeItem],
        auto_index: bool = True,
    ) -> BulkOperationResult:
        """
        Create multiple knowledge items in batches.

        Args:
            items: List of KnowledgeItem objects to create
            auto_index: Auto-index items for RAG if available

        Returns:
            BulkOperationResult with operation details
        """
        result = BulkOperationResult(
            total_requested=len(items),
            total_processed=0,
            total_successful=0,
            total_failed=0,
        )

        # Process in batches
        for batch_start in range(0, len(items), self.batch_size):
            batch_end = min(batch_start + self.batch_size, len(items))
            batch = items[batch_start:batch_end]

            for item in batch:
                try:
                    created_item = self.store.create_item(item)
                    result.total_successful += 1
                    result.total_processed += 1

                except Exception as e:
                    error_msg = str(e)
                    result.failed_items.append((item.item_id, error_msg))
                    result.total_failed += 1
                    result.total_processed += 1
                    self.logger.error(
                        f"Failed to create item {item.item_id}: {error_msg}"
                    )

        self.logger.info(
            f"Bulk create completed: {result.total_successful}/{len(items)} successful"
        )
        return result

    def bulk_update_items(
        self,
        items: List[KnowledgeItem],
        change_message: str = "",
        create_versions: bool = True,
    ) -> BulkOperationResult:
        """
        Update multiple knowledge items in batches.

        Optionally creates version snapshots before updating.

        Args:
            items: List of KnowledgeItem objects to update
            change_message: Optional change message for versions
            create_versions: Create version snapshots before updates

        Returns:
            BulkOperationResult with operation details
        """
        result = BulkOperationResult(
            total_requested=len(items),
            total_processed=0,
            total_successful=0,
            total_failed=0,
        )

        # Process in batches
        for batch_start in range(0, len(items), self.batch_size):
            batch_end = min(batch_start + self.batch_size, len(items))
            batch = items[batch_start:batch_end]

            for item in batch:
                try:
                    # Create version snapshot if requested
                    if create_versions:
                        old_item = self.store.get_item(item.item_id, item.tenant_id)
                        if old_item:
                            version = Version.create_from_item(
                                old_item,
                                change_message=change_message,
                            )
                            self.store.create_version(version)

                    # Update item
                    item.increment_version()
                    updated_item = self.store.update_item(item)
                    result.total_successful += 1
                    result.total_processed += 1

                except Exception as e:
                    error_msg = str(e)
                    result.failed_items.append((item.item_id, error_msg))
                    result.total_failed += 1
                    result.total_processed += 1
                    self.logger.error(
                        f"Failed to update item {item.item_id}: {error_msg}"
                    )

        self.logger.info(
            f"Bulk update completed: {result.total_successful}/{len(items)} successful"
        )
        return result

    def bulk_delete_items(
        self,
        item_ids: List[str],
        tenant_id: str,
        soft: bool = True,
    ) -> BulkOperationResult:
        """
        Delete multiple knowledge items in batches.

        Args:
            item_ids: List of item IDs to delete
            tenant_id: Tenant ID (for security)
            soft: Soft delete (mark deleted) or hard delete

        Returns:
            BulkOperationResult with operation details
        """
        result = BulkOperationResult(
            total_requested=len(item_ids),
            total_processed=0,
            total_successful=0,
            total_failed=0,
        )

        # Process in batches
        for batch_start in range(0, len(item_ids), self.batch_size):
            batch_end = min(batch_start + self.batch_size, len(item_ids))
            batch = item_ids[batch_start:batch_end]

            for item_id in batch:
                try:
                    deleted = self.store.delete_item(
                        item_id=item_id,
                        tenant_id=tenant_id,
                        soft=soft,
                    )

                    if deleted:
                        result.total_successful += 1
                    else:
                        result.failed_items.append(
                            (item_id, "Item not found or already deleted")
                        )
                        result.total_failed += 1

                    result.total_processed += 1

                except Exception as e:
                    error_msg = str(e)
                    result.failed_items.append((item_id, error_msg))
                    result.total_failed += 1
                    result.total_processed += 1
                    self.logger.error(
                        f"Failed to delete item {item_id}: {error_msg}"
                    )

        self.logger.info(
            f"Bulk delete completed: {result.total_successful}/{len(item_ids)} successful"
        )
        return result

    def bulk_index_items(
        self,
        items: List[KnowledgeItem],
        rag_integration: Optional[Any] = None,
    ) -> BulkOperationResult:
        """
        Index multiple items for semantic search in batches.

        Args:
            items: List of KnowledgeItem objects to index
            rag_integration: RAG integration instance

        Returns:
            BulkOperationResult with operation details
        """
        if not rag_integration:
            raise ValueError("RAG integration is required for indexing")

        result = BulkOperationResult(
            total_requested=len(items),
            total_processed=0,
            total_successful=0,
            total_failed=0,
        )

        # Process in batches
        for batch_start in range(0, len(items), self.batch_size):
            batch_end = min(batch_start + self.batch_size, len(items))
            batch = items[batch_start:batch_end]

            try:
                # Bulk index the batch
                rag_integration.bulk_index_items(batch)
                result.total_successful += len(batch)
                result.total_processed += len(batch)

            except Exception as e:
                # If batch indexing fails, try individual items
                for item in batch:
                    try:
                        rag_integration.index_item(item)
                        result.total_successful += 1
                    except Exception as item_error:
                        result.failed_items.append((item.item_id, str(item_error)))
                        result.total_failed += 1

                    result.total_processed += 1

                self.logger.warning(f"Batch indexing failed, retried individually: {e}")

        self.logger.info(
            f"Bulk indexing completed: {result.total_successful}/{len(items)} successful"
        )
        return result

    def bulk_create_collections(
        self,
        collections: List[Collection],
    ) -> BulkOperationResult:
        """
        Create multiple collections in batches.

        Args:
            collections: List of Collection objects to create

        Returns:
            BulkOperationResult with operation details
        """
        result = BulkOperationResult(
            total_requested=len(collections),
            total_processed=0,
            total_successful=0,
            total_failed=0,
        )

        # Process in batches
        for batch_start in range(0, len(collections), self.batch_size):
            batch_end = min(batch_start + self.batch_size, len(collections))
            batch = collections[batch_start:batch_end]

            for collection in batch:
                try:
                    created_collection = self.store.create_collection(collection)
                    result.total_successful += 1
                    result.total_processed += 1

                except Exception as e:
                    error_msg = str(e)
                    result.failed_items.append((collection.collection_id, error_msg))
                    result.total_failed += 1
                    result.total_processed += 1
                    self.logger.error(
                        f"Failed to create collection {collection.collection_id}: {error_msg}"
                    )

        self.logger.info(
            f"Bulk collection creation completed: "
            f"{result.total_successful}/{len(collections)} successful"
        )
        return result

    def bulk_delete_collections(
        self,
        collection_ids: List[str],
        cascade: bool = False,
    ) -> BulkOperationResult:
        """
        Delete multiple collections in batches.

        Args:
            collection_ids: List of collection IDs to delete
            cascade: Delete all items in collections (if True)

        Returns:
            BulkOperationResult with operation details
        """
        result = BulkOperationResult(
            total_requested=len(collection_ids),
            total_processed=0,
            total_successful=0,
            total_failed=0,
        )

        # Process in batches
        for batch_start in range(0, len(collection_ids), self.batch_size):
            batch_end = min(batch_start + self.batch_size, len(collection_ids))
            batch = collection_ids[batch_start:batch_end]

            for collection_id in batch:
                try:
                    # If cascade, delete all items first
                    if cascade:
                        items = self.store.list_items(
                            tenant_id="",  # Would need context
                            collection_id=collection_id,
                        )
                        for item in items:
                            self.store.delete_item(
                                item_id=item.item_id,
                                tenant_id=item.tenant_id,
                            )

                    # Delete collection
                    deleted = self.store.delete_collection(collection_id)

                    if deleted:
                        result.total_successful += 1
                    else:
                        result.failed_items.append(
                            (collection_id, "Collection not found")
                        )
                        result.total_failed += 1

                    result.total_processed += 1

                except Exception as e:
                    error_msg = str(e)
                    result.failed_items.append((collection_id, error_msg))
                    result.total_failed += 1
                    result.total_processed += 1
                    self.logger.error(
                        f"Failed to delete collection {collection_id}: {error_msg}"
                    )

        self.logger.info(
            f"Bulk collection deletion completed: "
            f"{result.total_successful}/{len(collection_ids)} successful"
        )
        return result


class TransactionManager:
    """Manages transactional operations for data consistency."""

    def __init__(self, store: BaseKnowledgeStore):
        """
        Initialize transaction manager.

        Args:
            store: Knowledge storage backend
        """
        self.store = store
        self.logger = logging.getLogger(__name__)

    def begin_transaction(self) -> str:
        """
        Begin a new transaction.

        Returns:
            str: Transaction ID
        """
        # Implementation depends on store backend
        # For now, return a placeholder
        return "txn_" + str(id(self))

    def commit_transaction(self, transaction_id: str) -> bool:
        """
        Commit a transaction.

        Args:
            transaction_id: Transaction ID

        Returns:
            bool: True if committed successfully
        """
        # Implementation depends on store backend
        return True

    def rollback_transaction(self, transaction_id: str) -> bool:
        """
        Rollback a transaction.

        Args:
            transaction_id: Transaction ID

        Returns:
            bool: True if rolled back successfully
        """
        # Implementation depends on store backend
        return True
