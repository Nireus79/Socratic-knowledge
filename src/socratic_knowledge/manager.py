"""Main KnowledgeManager interface for Socratic Knowledge."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from .access.permissions import AccessControl
from .access.rbac import Permission, Role
from .core.collection import Collection
from .core.knowledge_item import KnowledgeItem
from .core.tenant import Tenant
from .core.version import Version
from .storage.base import BaseKnowledgeStore
from .storage.sqlite_store import SQLiteKnowledgeStore
from .versioning.history import VersionHistory
from .versioning.version_model import VersionInfo


class KnowledgeManager:
    """
    Main interface for knowledge management operations.

    Provides a unified API for managing knowledge items, collections,
    tenants, access control, and versioning.
    """

    def __init__(
        self,
        storage: str = "sqlite",
        db_path: str = "knowledge.db",
        **storage_kwargs: Any,
    ):
        """
        Initialize KnowledgeManager.

        Args:
            storage: Storage backend ("sqlite" or custom)
            db_path: Path to SQLite database
            **storage_kwargs: Additional storage backend arguments
        """
        if storage == "sqlite":
            self.store: BaseKnowledgeStore = SQLiteKnowledgeStore(db_path=db_path)
        else:
            raise ValueError(f"Unknown storage backend: {storage}")

    # ==================== Tenant operations ====================

    def create_tenant(self, name: str, **kwargs: Any) -> Tenant:
        """
        Create new tenant.

        Args:
            name: Tenant name
            **kwargs: Additional tenant arguments

        Returns:
            Tenant: Created tenant
        """
        tenant = Tenant.create(name=name, **kwargs)
        return self.store.create_tenant(tenant)

    def get_tenant(self, tenant_id: str) -> Optional[Tenant]:
        """
        Get tenant by ID.

        Args:
            tenant_id: Tenant ID

        Returns:
            Optional[Tenant]: Tenant if found
        """
        return self.store.get_tenant(tenant_id)

    # ==================== Collection operations ====================

    def create_collection(
        self,
        tenant_id: str,
        name: str,
        created_by: str,
        parent_id: Optional[str] = None,
        **kwargs: Any,
    ) -> Collection:
        """
        Create collection (folder).

        Args:
            tenant_id: Tenant ID
            name: Collection name
            created_by: Creator user ID
            parent_id: Parent collection ID (for hierarchy)
            **kwargs: Additional arguments

        Returns:
            Collection: Created collection
        """
        collection = Collection.create(
            name=name,
            tenant_id=tenant_id,
            created_by=created_by,
            parent_id=parent_id,
            **kwargs,
        )
        return self.store.create_collection(collection)

    def get_collection(self, collection_id: str) -> Optional[Collection]:
        """
        Get collection by ID.

        Args:
            collection_id: Collection ID

        Returns:
            Optional[Collection]: Collection if found
        """
        return self.store.get_collection(collection_id)

    def list_collections(
        self,
        tenant_id: str,
        parent_id: Optional[str] = None,
    ) -> List[Collection]:
        """
        List collections.

        Args:
            tenant_id: Tenant ID
            parent_id: Filter by parent (for hierarchy)

        Returns:
            List[Collection]: Collections
        """
        return self.store.list_collections(tenant_id=tenant_id, parent_id=parent_id)

    # ==================== Knowledge item operations ====================

    def create_item(
        self,
        tenant_id: str,
        title: str,
        content: str,
        created_by: str,
        collection_id: Optional[str] = None,
        **kwargs: Any,
    ) -> KnowledgeItem:
        """
        Create knowledge item.

        Args:
            tenant_id: Tenant ID
            title: Item title
            content: Item content
            created_by: Creator user ID
            collection_id: Parent collection ID
            **kwargs: Additional arguments

        Returns:
            KnowledgeItem: Created item
        """
        item = KnowledgeItem.create(
            title=title,
            content=content,
            tenant_id=tenant_id,
            created_by=created_by,
            collection_id=collection_id,
            **kwargs,
        )
        return self.store.create_item(item)

    def get_item(self, item_id: str, tenant_id: str) -> Optional[KnowledgeItem]:
        """
        Get knowledge item.

        Args:
            item_id: Item ID
            tenant_id: Tenant ID (for security)

        Returns:
            Optional[KnowledgeItem]: Item if found and accessible
        """
        return self.store.get_item(item_id=item_id, tenant_id=tenant_id)

    def update_item(
        self,
        item: KnowledgeItem,
        change_message: str = "",
    ) -> KnowledgeItem:
        """
        Update knowledge item.

        Creates a version snapshot before updating.

        Args:
            item: Updated item
            change_message: Optional change message for version

        Returns:
            KnowledgeItem: Updated item
        """
        # Create version snapshot before updating
        old_item = self.get_item(item.item_id, item.tenant_id)
        if old_item:
            version = Version.create_from_item(
                old_item,
                change_message=change_message,
            )
            self.store.create_version(version)

        # Increment version and update
        item.increment_version()
        return self.store.update_item(item)

    def delete_item(
        self,
        item_id: str,
        tenant_id: str,
        soft: bool = True,
    ) -> bool:
        """
        Delete knowledge item.

        Args:
            item_id: Item ID
            tenant_id: Tenant ID
            soft: Soft delete (mark deleted) or hard delete

        Returns:
            bool: True if deleted
        """
        return self.store.delete_item(
            item_id=item_id,
            tenant_id=tenant_id,
            soft=soft,
        )

    def list_items(
        self,
        tenant_id: str,
        collection_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[KnowledgeItem]:
        """
        List knowledge items.

        Args:
            tenant_id: Tenant ID
            collection_id: Filter by collection
            limit: Maximum items to return
            offset: Items to skip

        Returns:
            List[KnowledgeItem]: Items
        """
        return self.store.list_items(
            tenant_id=tenant_id,
            collection_id=collection_id,
            limit=limit,
            offset=offset,
        )

    # ==================== Search operations ====================

    def search(
        self,
        tenant_id: str,
        query: str,
        limit: int = 10,
    ) -> List[KnowledgeItem]:
        """
        Full-text search.

        Args:
            tenant_id: Tenant ID
            query: Search query
            limit: Maximum results

        Returns:
            List[KnowledgeItem]: Search results
        """
        return self.store.search(tenant_id=tenant_id, query=query, limit=limit)

    # ==================== Versioning operations ====================

    def get_version_history(
        self,
        item_id: str,
        limit: int = 10,
    ) -> List[Version]:
        """
        Get version history for item.

        Args:
            item_id: Item ID
            limit: Maximum versions to return

        Returns:
            List[Version]: Version history
        """
        return self.store.list_versions(item_id=item_id, limit=limit)

    def get_version_info(
        self,
        item_id: str,
        limit: int = 10,
    ) -> List[VersionInfo]:
        """
        Get version info for item (lightweight).

        Args:
            item_id: Item ID
            limit: Maximum versions to return

        Returns:
            List[VersionInfo]: Version information
        """
        versions = self.get_version_history(item_id, limit)
        return VersionHistory.get_version_info_list(versions)

    def get_version_timeline(
        self,
        item_id: str,
        limit: int = 10,
    ) -> List[dict]:
        """
        Get timeline view of version history.

        Args:
            item_id: Item ID
            limit: Maximum versions to return

        Returns:
            List[dict]: Timeline events
        """
        versions = self.get_version_history(item_id, limit)
        return VersionHistory.get_version_timeline(versions)

    def rollback_item(
        self,
        item_id: str,
        tenant_id: str,
        version_number: int,
    ) -> KnowledgeItem:
        """
        Rollback item to previous version.

        Args:
            item_id: Item ID
            tenant_id: Tenant ID
            version_number: Version to rollback to

        Returns:
            KnowledgeItem: Updated item

        Raises:
            ValueError: If version not found
        """
        # Get version
        versions = self.get_version_history(item_id)
        version = None
        for v in versions:
            if v.version_number == version_number:
                version = v
                break

        if not version:
            raise ValueError(f"Version {version_number} not found for item {item_id}")

        # Get current item and update content
        item = self.get_item(item_id, tenant_id)
        if not item:
            raise ValueError(f"Item {item_id} not found")

        item.content = version.content
        item.title = version.title
        item.version = version.version_number

        # Update with rollback message
        return self.update_item(
            item,
            change_message=f"Rolled back to version {version_number}",
        )

    # ==================== Access control ====================

    def grant_permission(
        self,
        item_id: str,
        user_id: str,
        role: Role,
        tenant_id: str,
    ) -> None:
        """
        Grant permission to user.

        Args:
            item_id: Item ID
            user_id: User to grant permission to
            role: Role (viewer, editor, admin, owner)
            tenant_id: Tenant ID (for security)
        """
        item = self.get_item(item_id, tenant_id)
        if not item:
            raise ValueError(f"Item {item_id} not found")

        AccessControl.grant_permission(item, user_id, role)
        self.store.update_item(item)

    def revoke_permission(
        self,
        item_id: str,
        user_id: str,
        tenant_id: str,
        role: Optional[Role] = None,
    ) -> None:
        """
        Revoke permission from user.

        Args:
            item_id: Item ID
            user_id: User to revoke permission from
            tenant_id: Tenant ID (for security)
            role: Specific role to revoke, or None to revoke all
        """
        item = self.get_item(item_id, tenant_id)
        if not item:
            raise ValueError(f"Item {item_id} not found")

        AccessControl.revoke_permission(item, user_id, role)
        self.store.update_item(item)

    def can_user_read(
        self,
        user_id: str,
        item_id: str,
        tenant_id: str,
    ) -> bool:
        """
        Check if user can read item.

        Args:
            user_id: User ID
            item_id: Item ID
            tenant_id: Tenant ID

        Returns:
            bool: True if user can read
        """
        item = self.get_item(item_id, tenant_id)
        if not item:
            return False

        return AccessControl.check_permission(user_id, item, Permission.READ)

    def can_user_edit(
        self,
        user_id: str,
        item_id: str,
        tenant_id: str,
    ) -> bool:
        """
        Check if user can edit item.

        Args:
            user_id: User ID
            item_id: Item ID
            tenant_id: Tenant ID

        Returns:
            bool: True if user can edit
        """
        item = self.get_item(item_id, tenant_id)
        if not item:
            return False

        return AccessControl.check_permission(user_id, item, Permission.WRITE)

    def can_user_delete(
        self,
        user_id: str,
        item_id: str,
        tenant_id: str,
    ) -> bool:
        """
        Check if user can delete item.

        Args:
            user_id: User ID
            item_id: Item ID
            tenant_id: Tenant ID

        Returns:
            bool: True if user can delete
        """
        item = self.get_item(item_id, tenant_id)
        if not item:
            return False

        return AccessControl.check_permission(user_id, item, Permission.DELETE)
