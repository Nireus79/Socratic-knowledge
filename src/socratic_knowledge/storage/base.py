"""Abstract storage interface for knowledge management."""

from abc import ABC, abstractmethod
from typing import List, Optional

from ..core.collection import Collection
from ..core.knowledge_item import KnowledgeItem
from ..core.tenant import Tenant
from ..core.version import Version


class BaseKnowledgeStore(ABC):
    """
    Abstract interface for knowledge storage backends.

    Allows swapping SQLite, PostgreSQL, or custom implementations.
    """

    # ==================== Knowledge Item operations ====================

    @abstractmethod
    def create_item(self, item: KnowledgeItem) -> KnowledgeItem:
        """
        Create new knowledge item.

        Args:
            item: Knowledge item to create

        Returns:
            KnowledgeItem: Created item
        """
        pass

    @abstractmethod
    def get_item(self, item_id: str, tenant_id: str) -> Optional[KnowledgeItem]:
        """
        Get item by ID with tenant isolation.

        Args:
            item_id: Item ID
            tenant_id: Tenant ID (for security)

        Returns:
            Optional[KnowledgeItem]: Item if found and accessible
        """
        pass

    @abstractmethod
    def update_item(self, item: KnowledgeItem) -> KnowledgeItem:
        """
        Update existing item.

        Args:
            item: Updated item

        Returns:
            KnowledgeItem: Updated item
        """
        pass

    @abstractmethod
    def delete_item(self, item_id: str, tenant_id: str, soft: bool = True) -> bool:
        """
        Delete item.

        Args:
            item_id: Item ID
            tenant_id: Tenant ID
            soft: Soft delete (mark deleted) or hard delete

        Returns:
            bool: True if deleted successfully
        """
        pass

    @abstractmethod
    def list_items(
        self,
        tenant_id: str,
        collection_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[KnowledgeItem]:
        """
        List items with pagination.

        Args:
            tenant_id: Tenant ID (for security)
            collection_id: Filter by collection
            limit: Maximum items to return
            offset: Items to skip

        Returns:
            List[KnowledgeItem]: Items
        """
        pass

    # ==================== Collection operations ====================

    @abstractmethod
    def create_collection(self, collection: Collection) -> Collection:
        """
        Create collection.

        Args:
            collection: Collection to create

        Returns:
            Collection: Created collection
        """
        pass

    @abstractmethod
    def get_collection(self, collection_id: str) -> Optional[Collection]:
        """
        Get collection by ID.

        Args:
            collection_id: Collection ID

        Returns:
            Optional[Collection]: Collection if found
        """
        pass

    @abstractmethod
    def list_collections(
        self,
        tenant_id: str,
        parent_id: Optional[str] = None,
    ) -> List[Collection]:
        """
        List collections (hierarchical).

        Args:
            tenant_id: Tenant ID
            parent_id: Filter by parent (for hierarchy)

        Returns:
            List[Collection]: Collections
        """
        pass

    @abstractmethod
    def update_collection(self, collection: Collection) -> Collection:
        """
        Update collection.

        Args:
            collection: Updated collection

        Returns:
            Collection: Updated collection
        """
        pass

    # ==================== Tenant operations ====================

    @abstractmethod
    def create_tenant(self, tenant: Tenant) -> Tenant:
        """
        Create tenant.

        Args:
            tenant: Tenant to create

        Returns:
            Tenant: Created tenant
        """
        pass

    @abstractmethod
    def get_tenant(self, tenant_id: str) -> Optional[Tenant]:
        """
        Get tenant by ID.

        Args:
            tenant_id: Tenant ID

        Returns:
            Optional[Tenant]: Tenant if found
        """
        pass

    @abstractmethod
    def update_tenant(self, tenant: Tenant) -> Tenant:
        """
        Update tenant.

        Args:
            tenant: Updated tenant

        Returns:
            Tenant: Updated tenant
        """
        pass

    # ==================== Version operations ====================

    @abstractmethod
    def create_version(self, version: Version) -> Version:
        """
        Create version snapshot.

        Args:
            version: Version to create

        Returns:
            Version: Created version
        """
        pass

    @abstractmethod
    def get_version(self, version_id: str) -> Optional[Version]:
        """
        Get specific version.

        Args:
            version_id: Version ID

        Returns:
            Optional[Version]: Version if found
        """
        pass

    @abstractmethod
    def list_versions(
        self,
        item_id: str,
        limit: int = 10,
    ) -> List[Version]:
        """
        List version history for item.

        Args:
            item_id: Item ID
            limit: Maximum versions to return

        Returns:
            List[Version]: Versions in reverse chronological order
        """
        pass

    # ==================== Search operations ====================

    @abstractmethod
    def search(
        self,
        tenant_id: str,
        query: str,
        limit: int = 10,
    ) -> List[KnowledgeItem]:
        """
        Full-text search within tenant.

        Args:
            tenant_id: Tenant ID (for security)
            query: Search query
            limit: Maximum results to return

        Returns:
            List[KnowledgeItem]: Search results
        """
        pass
