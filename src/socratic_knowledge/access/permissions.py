"""Permission checking and enforcement."""

from typing import Dict, List, Optional, Set

from ..core.collection import Collection
from ..core.knowledge_item import KnowledgeItem
from .rbac import Permission, Role, ROLE_PERMISSIONS


class AccessControl:
    """
    Role-based access control (RBAC) engine.

    Checks if user has permission to perform action on resource.
    """

    @staticmethod
    def check_permission(
        user_id: str,
        item: KnowledgeItem,
        permission: Permission,
    ) -> bool:
        """
        Check if user has permission on item.

        Args:
            user_id: User ID
            item: Knowledge item
            permission: Permission to check

        Returns:
            bool: True if user has permission
        """
        # Owner always has access
        if item.owner_id == user_id:
            return True

        # Check role-based permissions
        if not item.permissions:
            return False

        for role_str, user_ids in item.permissions.items():
            if user_id in user_ids:
                try:
                    role = Role[role_str.upper()]
                except KeyError:
                    continue

                role_permissions = ROLE_PERMISSIONS.get(role, set())
                if permission in role_permissions:
                    return True

        return False

    @staticmethod
    def check_collection_permission(
        user_id: str,
        collection: Collection,
        permission: Permission,
        storage: Optional[object] = None,
    ) -> bool:
        """
        Check permission with inheritance from parent collections.

        Args:
            user_id: User ID
            collection: Collection
            permission: Permission to check
            storage: Storage instance for fetching parents

        Returns:
            bool: True if user has permission
        """
        # Direct permission
        if AccessControl._has_collection_permission(
            user_id,
            collection,
            permission,
        ):
            return True

        # Check parent hierarchy if inheritance enabled
        if collection.inherit_permissions and collection.parent_id and storage:
            parent = storage.get_collection(collection.parent_id)
            if parent:
                return AccessControl.check_collection_permission(
                    user_id,
                    parent,
                    permission,
                    storage,
                )

        return False

    @staticmethod
    def _has_collection_permission(
        user_id: str,
        collection: Collection,
        permission: Permission,
    ) -> bool:
        """
        Check direct permission on collection.

        Args:
            user_id: User ID
            collection: Collection
            permission: Permission to check

        Returns:
            bool: True if user has permission
        """
        # Owner always has access
        if collection.owner_id == user_id:
            return True

        if not collection.permissions:
            return False

        for role_str, user_ids in collection.permissions.items():
            if user_id in user_ids:
                try:
                    role = Role[role_str.upper()]
                except KeyError:
                    continue

                role_permissions = ROLE_PERMISSIONS.get(role, set())
                if permission in role_permissions:
                    return True

        return False

    @staticmethod
    def grant_permission(
        item: KnowledgeItem,
        user_id: str,
        role: Role,
    ) -> None:
        """
        Grant permission to user.

        Args:
            item: Knowledge item
            user_id: User to grant permission to
            role: Role to grant
        """
        if item.permissions is None:
            item.permissions = {}

        role_str = role.value
        if role_str not in item.permissions:
            item.permissions[role_str] = []

        if user_id not in item.permissions[role_str]:
            item.permissions[role_str].append(user_id)

    @staticmethod
    def revoke_permission(
        item: KnowledgeItem,
        user_id: str,
        role: Optional[Role] = None,
    ) -> None:
        """
        Revoke permission from user.

        Args:
            item: Knowledge item
            user_id: User to revoke permission from
            role: Specific role to revoke, or None to revoke all
        """
        if not item.permissions:
            return

        if role:
            role_str = role.value
            if role_str in item.permissions:
                if user_id in item.permissions[role_str]:
                    item.permissions[role_str].remove(user_id)
        else:
            # Revoke all roles for user
            for role_str in item.permissions:
                if user_id in item.permissions[role_str]:
                    item.permissions[role_str].remove(user_id)

    @staticmethod
    def grant_collection_permission(
        collection: Collection,
        user_id: str,
        role: Role,
    ) -> None:
        """
        Grant permission on collection.

        Args:
            collection: Collection
            user_id: User to grant permission to
            role: Role to grant
        """
        if collection.permissions is None:
            collection.permissions = {}

        role_str = role.value
        if role_str not in collection.permissions:
            collection.permissions[role_str] = []

        if user_id not in collection.permissions[role_str]:
            collection.permissions[role_str].append(user_id)

    @staticmethod
    def revoke_collection_permission(
        collection: Collection,
        user_id: str,
        role: Optional[Role] = None,
    ) -> None:
        """
        Revoke permission on collection.

        Args:
            collection: Collection
            user_id: User to revoke permission from
            role: Specific role to revoke, or None to revoke all
        """
        if not collection.permissions:
            return

        if role:
            role_str = role.value
            if role_str in collection.permissions:
                if user_id in collection.permissions[role_str]:
                    collection.permissions[role_str].remove(user_id)
        else:
            # Revoke all roles for user
            for role_str in collection.permissions:
                if user_id in collection.permissions[role_str]:
                    collection.permissions[role_str].remove(user_id)
