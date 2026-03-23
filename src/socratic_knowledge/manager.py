"""
Knowledge management and storage.
"""

import logging
from typing import Any, Dict, List, Optional

from .models import KnowledgeItem, AccessControl, KnowledgeIndex

logger = logging.getLogger(__name__)


class KnowledgeManager:
    """
    Multi-tenant knowledge management system.

    Manages knowledge items with:
    - Multi-tenant isolation
    - Role-based access control (RBAC)
    - Versioning and history
    - Metadata and indexing
    """

    def __init__(self):
        """Initialize knowledge manager."""
        self.items: Dict[str, KnowledgeItem] = {}
        self.index: List[KnowledgeIndex] = []
        self.db = None
        self._initialize_db()

    def _initialize_db(self) -> None:
        """Initialize database connection if available."""
        try:
            import sqlalchemy
            logger.info("SQLAlchemy available for persistence")
        except ImportError:
            logger.warning("SQLAlchemy not available; using in-memory storage")

    def create_item(
        self,
        tenant_id: str,
        title: str,
        content: str,
        owner: str,
        category: str = "general",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> KnowledgeItem:
        """
        Create a new knowledge item.

        Args:
            tenant_id: Tenant identifier
            title: Item title
            content: Item content
            owner: Owner user ID
            category: Item category
            metadata: Custom metadata

        Returns:
            Created knowledge item
        """
        item_id = f"item_{len(self.items)}"

        access_control = AccessControl(
            read=[owner],
            write=[owner],
            delete=[owner],
            owner=owner
        )

        item = KnowledgeItem(
            id=item_id,
            tenant_id=tenant_id,
            title=title,
            content=content,
            category=category,
            metadata=metadata or {},
            access_control=access_control,
        )

        self.items[item_id] = item
        self._add_to_index(item)

        logger.info(f"Created knowledge item {item_id} for tenant {tenant_id}")
        return item

    def _add_to_index(self, item: KnowledgeItem) -> None:
        """Add item to search index."""
        keywords = self._extract_keywords(item.title + " " + item.content)
        index_entry = KnowledgeIndex(
            item_id=item.id,
            tenant_id=item.tenant_id,
            title=item.title,
            category=item.category,
            keywords=keywords,
            created_at=item.created_at,
        )
        self.index.append(index_entry)

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text."""
        # Simple implementation: split on spaces and filter
        words = text.lower().split()
        return [w for w in words if len(w) > 3]

    def get_item(self, item_id: str, tenant_id: str, user_id: str) -> Optional[KnowledgeItem]:
        """
        Get a knowledge item if user has access.

        Args:
            item_id: Item identifier
            tenant_id: Tenant identifier
            user_id: User identifier

        Returns:
            Knowledge item if accessible, None otherwise
        """
        item = self.items.get(item_id)
        if not item or item.tenant_id != tenant_id:
            return None

        # Check read permission
        if user_id not in item.access_control.read and user_id != item.access_control.owner:
            logger.warning(f"User {user_id} denied read access to {item_id}")
            return None

        return item

    def update_item(
        self,
        item_id: str,
        tenant_id: str,
        user_id: str,
        **updates
    ) -> Optional[KnowledgeItem]:
        """
        Update a knowledge item if user has permission.

        Args:
            item_id: Item identifier
            tenant_id: Tenant identifier
            user_id: User identifier
            **updates: Fields to update

        Returns:
            Updated item or None
        """
        item = self.items.get(item_id)
        if not item or item.tenant_id != tenant_id:
            return None

        # Check write permission
        if user_id not in item.access_control.write and user_id != item.access_control.owner:
            logger.warning(f"User {user_id} denied write access to {item_id}")
            return None

        # Update fields
        for key, value in updates.items():
            if hasattr(item, key):
                setattr(item, key, value)

        item.version += 1
        logger.info(f"Updated knowledge item {item_id} (v{item.version})")
        return item

    def search(
        self,
        tenant_id: str,
        query: str,
        user_id: str,
        category: Optional[str] = None,
    ) -> List[KnowledgeItem]:
        """
        Search for knowledge items.

        Args:
            tenant_id: Tenant identifier
            query: Search query
            user_id: User identifier
            category: Optional category filter

        Returns:
            List of accessible matching items
        """
        results = []

        for item in self.items.values():
            # Filter by tenant
            if item.tenant_id != tenant_id:
                continue

            # Filter by category
            if category and item.category != category:
                continue

            # Check read permission
            if user_id not in item.access_control.read and user_id != item.access_control.owner:
                continue

            # Search in title and content
            if query.lower() in item.title.lower() or query.lower() in item.content.lower():
                results.append(item)

        logger.info(f"Found {len(results)} items matching '{query}' for tenant {tenant_id}")
        return results

    def grant_access(
        self,
        item_id: str,
        user_id: str,
        permission_type: str,  # 'read', 'write', 'delete'
        grant_user: str,
    ) -> bool:
        """
        Grant access to a knowledge item.

        Args:
            item_id: Item identifier
            user_id: User identifier (requestor)
            permission_type: Type of permission to grant
            grant_user: User to grant access to

        Returns:
            True if access granted
        """
        item = self.items.get(item_id)
        if not item or user_id != item.access_control.owner:
            return False

        if permission_type == "read":
            if grant_user not in item.access_control.read:
                item.access_control.read.append(grant_user)
        elif permission_type == "write":
            if grant_user not in item.access_control.write:
                item.access_control.write.append(grant_user)
        elif permission_type == "delete":
            if grant_user not in item.access_control.delete:
                item.access_control.delete.append(grant_user)

        logger.info(f"Granted {permission_type} access to {item_id} for user {grant_user}")
        return True
