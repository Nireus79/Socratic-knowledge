"""Tests for access control and RBAC."""

import pytest

from socratic_knowledge.access.permissions import AccessControl
from socratic_knowledge.access.rbac import Permission, Role
from socratic_knowledge.core.collection import Collection
from socratic_knowledge.core.knowledge_item import KnowledgeItem


class TestAccessControl:
    """Test AccessControl RBAC engine."""

    def test_owner_always_has_read_permission(self):
        """Test that owner always has READ permission."""
        item = KnowledgeItem.create(
            title="Test",
            content="Content",
            tenant_id="t1",
            created_by="user1",
        )

        assert AccessControl.check_permission(
            "user1", item, Permission.READ
        )

    def test_owner_always_has_write_permission(self):
        """Test that owner always has WRITE permission."""
        item = KnowledgeItem.create(
            title="Test",
            content="Content",
            tenant_id="t1",
            created_by="user1",
        )

        assert AccessControl.check_permission(
            "user1", item, Permission.WRITE
        )

    def test_owner_always_has_delete_permission(self):
        """Test that owner always has DELETE permission."""
        item = KnowledgeItem.create(
            title="Test",
            content="Content",
            tenant_id="t1",
            created_by="user1",
        )

        assert AccessControl.check_permission(
            "user1", item, Permission.DELETE
        )

    def test_non_owner_without_permission_cannot_read(self):
        """Test that non-owner without permission cannot READ."""
        item = KnowledgeItem.create(
            title="Test",
            content="Content",
            tenant_id="t1",
            created_by="user1",
        )

        assert not AccessControl.check_permission(
            "user2", item, Permission.READ
        )

    def test_viewer_can_read(self):
        """Test that viewer role can READ."""
        item = KnowledgeItem.create(
            title="Test",
            content="Content",
            tenant_id="t1",
            created_by="user1",
        )

        AccessControl.grant_permission(item, "user2", Role.VIEWER)

        assert AccessControl.check_permission(
            "user2", item, Permission.READ
        )

    def test_viewer_cannot_write(self):
        """Test that viewer role cannot WRITE."""
        item = KnowledgeItem.create(
            title="Test",
            content="Content",
            tenant_id="t1",
            created_by="user1",
        )

        AccessControl.grant_permission(item, "user2", Role.VIEWER)

        assert not AccessControl.check_permission(
            "user2", item, Permission.WRITE
        )

    def test_editor_can_read(self):
        """Test that editor role can READ."""
        item = KnowledgeItem.create(
            title="Test",
            content="Content",
            tenant_id="t1",
            created_by="user1",
        )

        AccessControl.grant_permission(item, "user2", Role.EDITOR)

        assert AccessControl.check_permission(
            "user2", item, Permission.READ
        )

    def test_editor_can_write(self):
        """Test that editor role can WRITE."""
        item = KnowledgeItem.create(
            title="Test",
            content="Content",
            tenant_id="t1",
            created_by="user1",
        )

        AccessControl.grant_permission(item, "user2", Role.EDITOR)

        assert AccessControl.check_permission(
            "user2", item, Permission.WRITE
        )

    def test_editor_cannot_delete(self):
        """Test that editor role cannot DELETE."""
        item = KnowledgeItem.create(
            title="Test",
            content="Content",
            tenant_id="t1",
            created_by="user1",
        )

        AccessControl.grant_permission(item, "user2", Role.EDITOR)

        assert not AccessControl.check_permission(
            "user2", item, Permission.DELETE
        )

    def test_admin_can_read(self):
        """Test that admin role can READ."""
        item = KnowledgeItem.create(
            title="Test",
            content="Content",
            tenant_id="t1",
            created_by="user1",
        )

        AccessControl.grant_permission(item, "user2", Role.ADMIN)

        assert AccessControl.check_permission(
            "user2", item, Permission.READ
        )

    def test_admin_can_write(self):
        """Test that admin role can WRITE."""
        item = KnowledgeItem.create(
            title="Test",
            content="Content",
            tenant_id="t1",
            created_by="user1",
        )

        AccessControl.grant_permission(item, "user2", Role.ADMIN)

        assert AccessControl.check_permission(
            "user2", item, Permission.WRITE
        )

    def test_admin_can_delete(self):
        """Test that admin role can DELETE."""
        item = KnowledgeItem.create(
            title="Test",
            content="Content",
            tenant_id="t1",
            created_by="user1",
        )

        AccessControl.grant_permission(item, "user2", Role.ADMIN)

        assert AccessControl.check_permission(
            "user2", item, Permission.DELETE
        )

    def test_admin_can_share(self):
        """Test that admin role can SHARE."""
        item = KnowledgeItem.create(
            title="Test",
            content="Content",
            tenant_id="t1",
            created_by="user1",
        )

        AccessControl.grant_permission(item, "user2", Role.ADMIN)

        assert AccessControl.check_permission(
            "user2", item, Permission.SHARE
        )

    def test_grant_permission_adds_user_to_role(self):
        """Test that grant_permission adds user to role."""
        item = KnowledgeItem.create(
            title="Test",
            content="Content",
            tenant_id="t1",
            created_by="user1",
        )

        AccessControl.grant_permission(item, "user2", Role.VIEWER)

        assert "viewer" in item.permissions
        assert "user2" in item.permissions["viewer"]

    def test_grant_permission_multiple_users(self):
        """Test granting permission to multiple users in same role."""
        item = KnowledgeItem.create(
            title="Test",
            content="Content",
            tenant_id="t1",
            created_by="user1",
        )

        AccessControl.grant_permission(item, "user2", Role.VIEWER)
        AccessControl.grant_permission(item, "user3", Role.VIEWER)

        assert "user2" in item.permissions["viewer"]
        assert "user3" in item.permissions["viewer"]

    def test_grant_permission_does_not_duplicate(self):
        """Test that granting same permission twice doesn't duplicate."""
        item = KnowledgeItem.create(
            title="Test",
            content="Content",
            tenant_id="t1",
            created_by="user1",
        )

        AccessControl.grant_permission(item, "user2", Role.VIEWER)
        AccessControl.grant_permission(item, "user2", Role.VIEWER)

        assert item.permissions["viewer"].count("user2") == 1

    def test_revoke_specific_role(self):
        """Test revoking a specific role from user."""
        item = KnowledgeItem.create(
            title="Test",
            content="Content",
            tenant_id="t1",
            created_by="user1",
        )

        AccessControl.grant_permission(item, "user2", Role.VIEWER)
        AccessControl.grant_permission(item, "user2", Role.EDITOR)

        AccessControl.revoke_permission(item, "user2", Role.VIEWER)

        assert "user2" not in item.permissions.get("viewer", [])
        assert "user2" in item.permissions["editor"]

    def test_revoke_all_roles(self):
        """Test revoking all roles from user."""
        item = KnowledgeItem.create(
            title="Test",
            content="Content",
            tenant_id="t1",
            created_by="user1",
        )

        AccessControl.grant_permission(item, "user2", Role.VIEWER)
        AccessControl.grant_permission(item, "user2", Role.EDITOR)

        AccessControl.revoke_permission(item, "user2")

        assert "user2" not in item.permissions.get("viewer", [])
        assert "user2" not in item.permissions.get("editor", [])

    def test_revoke_nonexistent_permission(self):
        """Test revoking permission that doesn't exist."""
        item = KnowledgeItem.create(
            title="Test",
            content="Content",
            tenant_id="t1",
            created_by="user1",
        )

        # Should not raise error
        AccessControl.revoke_permission(item, "user2", Role.VIEWER)

        assert item.permissions == {}

    def test_revoke_from_empty_permissions(self):
        """Test revoking from item with no permissions."""
        item = KnowledgeItem.create(
            title="Test",
            content="Content",
            tenant_id="t1",
            created_by="user1",
        )

        # Should not raise error
        AccessControl.revoke_permission(item, "user2")

        assert item.permissions == {}

    def test_multiple_roles_for_user(self):
        """Test user with multiple roles uses highest permission."""
        item = KnowledgeItem.create(
            title="Test",
            content="Content",
            tenant_id="t1",
            created_by="user1",
        )

        AccessControl.grant_permission(item, "user2", Role.VIEWER)
        AccessControl.grant_permission(item, "user2", Role.EDITOR)

        # User should have editor permissions (superset of viewer)
        assert AccessControl.check_permission(
            "user2", item, Permission.WRITE
        )
        assert AccessControl.check_permission(
            "user2", item, Permission.READ
        )

    def test_collection_permission_direct(self):
        """Test collection permission check."""
        collection = Collection.create(
            name="Test",
            tenant_id="t1",
            created_by="user1",
        )

        AccessControl.grant_collection_permission(
            collection, "user2", Role.VIEWER
        )

        assert AccessControl._has_collection_permission(
            "user2", collection, Permission.READ
        )

    def test_collection_owner_always_has_permission(self):
        """Test that collection owner always has permission."""
        collection = Collection.create(
            name="Test",
            tenant_id="t1",
            created_by="user1",
        )

        assert AccessControl._has_collection_permission(
            "user1", collection, Permission.READ
        )
        assert AccessControl._has_collection_permission(
            "user1", collection, Permission.WRITE
        )

    def test_collection_permission_revoke(self):
        """Test revoking collection permission."""
        collection = Collection.create(
            name="Test",
            tenant_id="t1",
            created_by="user1",
        )

        AccessControl.grant_collection_permission(
            collection, "user2", Role.VIEWER
        )
        AccessControl.revoke_collection_permission(
            collection, "user2", Role.VIEWER
        )

        assert not AccessControl._has_collection_permission(
            "user2", collection, Permission.READ
        )

    def test_permission_inheritance_enabled(self):
        """Test that permission inheritance works when enabled."""
        parent = Collection.create(
            name="Parent",
            tenant_id="t1",
            created_by="user1",
        )

        child = Collection.create(
            name="Child",
            tenant_id="t1",
            parent_id=parent.collection_id,
            created_by="user1",
            inherit_permissions=True,
        )

        AccessControl.grant_collection_permission(
            parent, "user2", Role.VIEWER
        )

        # Without storage, we can't test the full inheritance
        # But we can verify the structure is set up correctly
        assert child.inherit_permissions
        assert child.parent_id == parent.collection_id

    def test_no_permission_when_permissions_empty(self):
        """Test that user without entry in permissions has no access."""
        item = KnowledgeItem.create(
            title="Test",
            content="Content",
            tenant_id="t1",
            created_by="user1",
        )

        # Ensure item.permissions is empty
        assert item.permissions == {}

        assert not AccessControl.check_permission(
            "user2", item, Permission.READ
        )

    def test_invalid_role_in_permissions(self):
        """Test that invalid role in permissions is skipped."""
        item = KnowledgeItem.create(
            title="Test",
            content="Content",
            tenant_id="t1",
            created_by="user1",
        )

        # Manually add invalid role
        item.permissions["invalid_role"] = ["user2"]

        # Should not crash, just not grant permission
        assert not AccessControl.check_permission(
            "user2", item, Permission.READ
        )

    def test_empty_user_list_in_role(self):
        """Test permission check with empty user list in role."""
        item = KnowledgeItem.create(
            title="Test",
            content="Content",
            tenant_id="t1",
            created_by="user1",
        )

        item.permissions["viewer"] = []

        assert not AccessControl.check_permission(
            "user2", item, Permission.READ
        )

    def test_case_insensitive_role_lookup(self):
        """Test that role lookup is case insensitive."""
        item = KnowledgeItem.create(
            title="Test",
            content="Content",
            tenant_id="t1",
            created_by="user1",
        )

        # Manually add with uppercase (shouldn't happen normally)
        item.permissions["VIEWER"] = ["user2"]

        # The actual implementation converts to uppercase, so this should work
        assert AccessControl.check_permission(
            "user2", item, Permission.READ
        )

    def test_permission_share_admin_and_owner(self):
        """Test that owner and admin can have SHARE permission."""
        item = KnowledgeItem.create(
            title="Test",
            content="Content",
            tenant_id="t1",
            created_by="user1",
        )

        # Owner has all permissions
        assert AccessControl.check_permission(
            "user1", item, Permission.SHARE
        )

        # Admin role also has SHARE permission
        AccessControl.grant_permission(item, "user2", Role.ADMIN)
        assert AccessControl.check_permission(
            "user2", item, Permission.SHARE
        )

    def test_permission_admin_only_owner(self):
        """Test that only owner can have ADMIN permission."""
        item = KnowledgeItem.create(
            title="Test",
            content="Content",
            tenant_id="t1",
            created_by="user1",
        )

        # Owner has all permissions
        assert AccessControl.check_permission(
            "user1", item, Permission.ADMIN
        )

        # Non-owner with admin role doesn't have ADMIN permission
        AccessControl.grant_permission(item, "user2", Role.ADMIN)
        assert not AccessControl.check_permission(
            "user2", item, Permission.ADMIN
        )
