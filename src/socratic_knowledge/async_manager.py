"""Async wrapper for KnowledgeManager - enables non-blocking knowledge operations."""

import asyncio
from typing import Any, Dict, List, Optional

from .core.collection import Collection
from .core.knowledge_item import KnowledgeItem
from .core.tenant import Tenant
from .core.version import Version
from .manager import KnowledgeManager
from .retrieval.search import SearchMode


class AsyncKnowledgeManager:
    """
    Asynchronous wrapper for KnowledgeManager.

    Provides non-blocking async operations for all knowledge management tasks
    using asyncio.to_thread() pattern for CPU-bound operations.

    Usage:
        manager = AsyncKnowledgeManager(db_path="knowledge.db")
        item = await manager.get_item(item_id)
        results = await manager.search("query")
    """

    def __init__(
        self,
        storage: str = "sqlite",
        db_path: str = "knowledge.db",
        enable_rag: bool = True,
        rag_config: Optional[Any] = None,
        **storage_kwargs: Any,
    ):
        """
        Initialize AsyncKnowledgeManager.

        Args:
            storage: Storage backend ("sqlite" or custom)
            db_path: Path to SQLite database
            enable_rag: Enable RAG integration for semantic search
            rag_config: RAG configuration (uses RAGConfig defaults if None)
            **storage_kwargs: Additional storage backend arguments
        """
        self._manager = KnowledgeManager(
            storage=storage,
            db_path=db_path,
            enable_rag=enable_rag,
            rag_config=rag_config,
            **storage_kwargs,
        )

    # ==================== Tenant operations ====================

    async def create_tenant(self, name: str, **kwargs: Any) -> Tenant:
        """Create new tenant asynchronously."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, self._manager.create_tenant, name, *kwargs.values()
        )

    async def get_tenant(self, tenant_id: str) -> Optional[Tenant]:
        """Get tenant by ID asynchronously."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._manager.get_tenant, tenant_id)

    # ==================== Collection operations ====================

    async def create_collection(
        self,
        tenant_id: str,
        name: str,
        description: Optional[str] = None,
        **kwargs: Any,
    ) -> Collection:
        """Create collection asynchronously."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self._manager.create_collection,
            tenant_id,
            name,
            description,
        )

    async def get_collection(self, collection_id: str) -> Optional[Collection]:
        """Get collection by ID asynchronously."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, self._manager.get_collection, collection_id
        )

    async def list_collections(
        self,
        tenant_id: str,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Collection]:
        """List collections asynchronously."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self._manager.list_collections,
            tenant_id,
            limit,
            offset,
        )

    # ==================== Knowledge Item operations ====================

    async def create_item(
        self,
        tenant_id: str,
        collection_id: str,
        title: str,
        content: str,
        **kwargs: Any,
    ) -> KnowledgeItem:
        """Create knowledge item asynchronously."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self._manager.create_item,
            tenant_id,
            collection_id,
            title,
            content,
        )

    async def get_item(self, item_id: str, tenant_id: str) -> Optional[KnowledgeItem]:
        """Get knowledge item by ID asynchronously."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, self._manager.get_item, item_id, tenant_id
        )

    async def update_item(
        self,
        item_id: str,
        tenant_id: str,
        title: Optional[str] = None,
        content: Optional[str] = None,
        **kwargs: Any,
    ) -> KnowledgeItem:
        """Update knowledge item asynchronously."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self._manager.update_item,
            item_id,
            tenant_id,
            title,
            content,
        )

    async def delete_item(self, item_id: str, tenant_id: str) -> bool:
        """Delete knowledge item asynchronously."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, self._manager.delete_item, item_id, tenant_id
        )

    async def list_items(
        self,
        collection_id: str,
        limit: int = 100,
        offset: int = 0,
    ) -> List[KnowledgeItem]:
        """List knowledge items asynchronously."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self._manager.list_items,
            collection_id,
            limit,
            offset,
        )

    # ==================== Search operations ====================

    async def search(
        self,
        query: str,
        collection_id: Optional[str] = None,
        limit: int = 10,
        search_mode: SearchMode = SearchMode.FULL_TEXT,
    ) -> List[KnowledgeItem]:
        """Search knowledge items asynchronously."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self._manager.search,
            query,
            collection_id,
            limit,
            search_mode,
        )

    async def semantic_search(
        self,
        query: str,
        collection_id: Optional[str] = None,
        limit: int = 10,
        threshold: float = 0.5,
    ) -> List[KnowledgeItem]:
        """Semantic search asynchronously."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self._manager.semantic_search,
            query,
            collection_id,
            limit,
            threshold,
        )

    async def hybrid_search(
        self,
        query: str,
        collection_id: Optional[str] = None,
        limit: int = 10,
        text_weight: float = 0.5,
        semantic_weight: float = 0.5,
    ) -> List[KnowledgeItem]:
        """Hybrid search asynchronously."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self._manager.hybrid_search,
            query,
            collection_id,
            limit,
            text_weight,
            semantic_weight,
        )

    # ==================== Indexing operations ====================

    async def index_item(self, item: KnowledgeItem) -> None:
        """Index knowledge item asynchronously."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._manager.index_item, item)

    async def re_index_item(self, item: KnowledgeItem) -> None:
        """Re-index knowledge item asynchronously."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._manager.re_index_item, item)

    # ==================== Version operations ====================

    async def get_version_history(
        self,
        item_id: str,
        limit: int = 100,
    ) -> List[Version]:
        """Get version history asynchronously."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, self._manager.get_version_history, item_id, limit
        )

    async def get_version_info(self, version_id: str) -> Optional[VersionInfo]:
        """Get version info asynchronously."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, self._manager.get_version_info, version_id
        )

    async def rollback_item(
        self,
        item_id: str,
        tenant_id: str,
        version_id: str,
    ) -> KnowledgeItem:
        """Rollback item to specific version asynchronously."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self._manager.rollback_item,
            item_id,
            tenant_id,
            version_id,
        )

    # ==================== Access control operations ====================

    async def grant_permission(
        self,
        user_id: str,
        resource_id: str,
        permission: str,
    ) -> bool:
        """Grant permission asynchronously."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self._manager.grant_permission,
            user_id,
            resource_id,
            permission,
        )

    async def revoke_permission(
        self,
        user_id: str,
        resource_id: str,
        permission: str,
    ) -> bool:
        """Revoke permission asynchronously."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self._manager.revoke_permission,
            user_id,
            resource_id,
            permission,
        )

    async def can_user_read(
        self,
        user_id: str,
        resource_id: str,
    ) -> bool:
        """Check if user can read resource asynchronously."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self._manager.can_user_read,
            user_id,
            resource_id,
        )

    async def can_user_edit(
        self,
        user_id: str,
        resource_id: str,
    ) -> bool:
        """Check if user can edit resource asynchronously."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self._manager.can_user_edit,
            user_id,
            resource_id,
        )

    async def can_user_delete(
        self,
        user_id: str,
        resource_id: str,
    ) -> bool:
        """Check if user can delete resource asynchronously."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self._manager.can_user_delete,
            user_id,
            resource_id,
        )

    # ==================== Audit operations ====================

    async def log_audit_event(
        self,
        event_type: str,
        resource_id: str,
        user_id: str,
        description: Optional[str] = None,
    ) -> bool:
        """Log audit event asynchronously."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self._manager.log_audit_event,
            event_type,
            resource_id,
            user_id,
            description,
        )

    async def get_audit_log(
        self,
        resource_id: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Get audit log asynchronously."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self._manager.get_audit_log,
            resource_id,
            limit,
        )

    async def get_user_activity(
        self,
        user_id: str,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Get user activity asynchronously."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self._manager.get_user_activity,
            user_id,
            limit,
        )

    async def get_resource_history(
        self,
        resource_id: str,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Get resource history asynchronously."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self._manager.get_resource_history,
            resource_id,
            limit,
        )
