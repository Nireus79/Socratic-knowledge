"""Openclaw skill integration for SocraticKnowledge."""

from typing import Any, Dict, List, Optional

from ...manager import KnowledgeManager


class SocraticKnowledgeSkill:
    """
    Openclaw skill for Socratic Knowledge management.

    Provides access to knowledge management operations through
    a skill interface compatible with Openclaw applications.
    """

    def __init__(
        self,
        knowledge_manager: Optional[KnowledgeManager] = None,
        **km_kwargs: Any,
    ):
        """
        Initialize SocraticKnowledgeSkill.

        Args:
            knowledge_manager: KnowledgeManager instance (creates if None)
            **km_kwargs: Arguments for KnowledgeManager initialization
        """
        if knowledge_manager:
            self.km = knowledge_manager
        else:
            self.km = KnowledgeManager(**km_kwargs)

    # ==================== Search operations ====================

    def search_knowledge(
        self,
        tenant_id: str,
        query: str,
        top_k: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Search knowledge base.

        Args:
            tenant_id: Tenant ID
            query: Search query
            top_k: Maximum results

        Returns:
            List[Dict]: Search results
        """
        results = self.km.hybrid_search(tenant_id, query, top_k=top_k)
        return [
            {
                "item_id": item.item_id,
                "title": item.title,
                "content": item.content,
                "collection_id": item.collection_id,
                "tags": item.tags,
            }
            for item in results
        ]

    def semantic_search(
        self,
        tenant_id: str,
        query: str,
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Semantic search using embeddings.

        Args:
            tenant_id: Tenant ID
            query: Search query
            top_k: Maximum results

        Returns:
            List[Dict]: Semantically relevant items
        """
        results = self.km.semantic_search(tenant_id, query, top_k=top_k)
        return [
            {
                "item_id": item.item_id,
                "title": item.title,
                "content": item.content,
                "tags": item.tags,
            }
            for item in results
        ]

    # ==================== Item operations ====================

    def get_item(
        self,
        tenant_id: str,
        item_id: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Get knowledge item.

        Args:
            tenant_id: Tenant ID
            item_id: Item ID

        Returns:
            Dict: Item details or None
        """
        item = self.km.get_item(item_id, tenant_id)
        if not item:
            return None

        return {
            "item_id": item.item_id,
            "title": item.title,
            "content": item.content,
            "collection_id": item.collection_id,
            "version": item.version,
            "created_at": item.created_at.isoformat(),
            "updated_at": item.updated_at.isoformat(),
            "tags": item.tags,
            "metadata": item.metadata,
        }

    def create_item(
        self,
        tenant_id: str,
        title: str,
        content: str,
        user_id: str,
        collection_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create knowledge item.

        Args:
            tenant_id: Tenant ID
            title: Item title
            content: Item content
            user_id: Creator user ID
            collection_id: Parent collection
            tags: Tags for item
            metadata: Additional metadata

        Returns:
            Dict: Created item
        """
        item = self.km.create_item(
            tenant_id=tenant_id,
            title=title,
            content=content,
            created_by=user_id,
            collection_id=collection_id,
            tags=tags or [],
            metadata=metadata or {},
        )

        self.km.log_audit_event(
            event_type="item_created",
            tenant_id=tenant_id,
            user_id=user_id,
            resource_type="item",
            resource_id=item.item_id,
            action="create",
        )

        return {
            "item_id": item.item_id,
            "title": item.title,
            "content": item.content,
            "version": item.version,
        }

    # ==================== Audit operations ====================

    def get_audit_log(
        self,
        tenant_id: str,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """
        Get audit log for tenant.

        Args:
            tenant_id: Tenant ID
            limit: Maximum events

        Returns:
            List[Dict]: Audit events
        """
        events = self.km.get_audit_log(tenant_id, limit=limit)
        return [
            {
                "event_type": event.event_type.value,
                "user_id": event.user_id,
                "resource_type": event.resource_type,
                "action": event.action,
                "timestamp": event.timestamp.isoformat(),
                "changes": event.changes,
            }
            for event in events
        ]

    def get_user_activity(
        self,
        tenant_id: str,
        user_id: str,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """
        Get user activity.

        Args:
            tenant_id: Tenant ID
            user_id: User ID
            limit: Maximum events

        Returns:
            List[Dict]: User activity
        """
        events = self.km.get_user_activity(tenant_id, user_id, limit=limit)
        return [
            {
                "event_type": event.event_type.value,
                "action": event.action,
                "resource_type": event.resource_type,
                "resource_id": event.resource_id,
                "timestamp": event.timestamp.isoformat(),
            }
            for event in events
        ]

    # ==================== Access control ====================

    def can_user_read(
        self,
        tenant_id: str,
        user_id: str,
        item_id: str,
    ) -> bool:
        """
        Check if user can read item.

        Args:
            tenant_id: Tenant ID
            user_id: User ID
            item_id: Item ID

        Returns:
            bool: True if readable
        """
        return self.km.can_user_read(user_id, item_id, tenant_id)

    def can_user_edit(
        self,
        tenant_id: str,
        user_id: str,
        item_id: str,
    ) -> bool:
        """
        Check if user can edit item.

        Args:
            tenant_id: Tenant ID
            user_id: User ID
            item_id: Item ID

        Returns:
            bool: True if editable
        """
        return self.km.can_user_edit(user_id, item_id, tenant_id)

    def grant_permission(
        self,
        tenant_id: str,
        item_id: str,
        user_id: str,
        role: str,
    ) -> bool:
        """
        Grant permission to user.

        Args:
            tenant_id: Tenant ID
            item_id: Item ID
            user_id: User to grant to
            role: Role (viewer, editor, admin, owner)

        Returns:
            bool: True if granted
        """
        try:
            from ...access.rbac import Role

            role_obj = Role[role.upper()]
            self.km.grant_permission(item_id, user_id, role_obj, tenant_id)
            return True
        except (KeyError, ValueError):
            return False

    # ==================== Utility ====================

    def get_skill_info(self) -> Dict[str, Any]:
        """
        Get skill information.

        Returns:
            Dict: Skill metadata
        """
        return {
            "name": "SocraticKnowledge",
            "version": "0.1.0",
            "description": "Enterprise knowledge management system",
            "capabilities": [
                "search_knowledge",
                "semantic_search",
                "create_item",
                "get_item",
                "get_audit_log",
                "get_user_activity",
                "can_user_read",
                "can_user_edit",
                "grant_permission",
            ],
        }
