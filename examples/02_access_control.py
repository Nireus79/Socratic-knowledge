"""
Example 2: Access Control & Permissions

This example demonstrates role-based access control (RBAC)
and permission management.
"""

from socratic_knowledge import KnowledgeManager
from socratic_knowledge.access.rbac import Role


def main():
    """Run access control example."""
    print("=" * 60)
    print("Example 2: Access Control & Permissions")
    print("=" * 60)

    km = KnowledgeManager(storage="sqlite", db_path="knowledge_demo.db")

    # Create tenant and item
    tenant = km.create_tenant(name="SecureCorp")
    item = km.create_item(
        tenant_id=tenant.tenant_id,
        title="Confidential Document",
        content="This is sensitive information...",
        created_by="alice",
    )

    print(f"\nItem: {item.title}")
    print(f"Owner: {item.owner_id}")

    # ==================== Permission Checks ====================
    print("\n" + "=" * 60)
    print("1. Initial Permission State")
    print("=" * 60)

    print(f"\nalice (owner) can read: {km.can_user_read('alice', item.item_id, tenant.tenant_id)}")
    print(f"alice (owner) can edit: {km.can_user_edit('alice', item.item_id, tenant.tenant_id)}")
    print(
        f"alice (owner) can delete: {km.can_user_delete('alice', item.item_id, tenant.tenant_id)}"
    )

    print(
        f"\nbob (no permissions) can read: {km.can_user_read('bob', item.item_id, tenant.tenant_id)}"
    )
    print(
        f"bob (no permissions) can edit: {km.can_user_edit('bob', item.item_id, tenant.tenant_id)}"
    )

    # ==================== Grant Permissions ====================
    print("\n" + "=" * 60)
    print("2. Granting Permissions")
    print("=" * 60)

    # Grant VIEWER role to bob
    print("\nGranting VIEWER role to bob...")
    km.grant_permission(
        item_id=item.item_id,
        user_id="bob",
        role=Role.VIEWER,
        tenant_id=tenant.tenant_id,
    )
    print(f"bob can now read: {km.can_user_read('bob', item.item_id, tenant.tenant_id)}")
    print(f"bob can edit: {km.can_user_edit('bob', item.item_id, tenant.tenant_id)}")

    # Grant EDITOR role to carol
    print("\nGranting EDITOR role to carol...")
    km.grant_permission(
        item_id=item.item_id,
        user_id="carol",
        role=Role.EDITOR,
        tenant_id=tenant.tenant_id,
    )
    print(f"carol can read: {km.can_user_read('carol', item.item_id, tenant.tenant_id)}")
    print(f"carol can edit: {km.can_user_edit('carol', item.item_id, tenant.tenant_id)}")
    print(f"carol can delete: {km.can_user_delete('carol', item.item_id, tenant.tenant_id)}")

    # Grant ADMIN role to dave
    print("\nGranting ADMIN role to dave...")
    km.grant_permission(
        item_id=item.item_id,
        user_id="dave",
        role=Role.ADMIN,
        tenant_id=tenant.tenant_id,
    )
    print(f"dave can read: {km.can_user_read('dave', item.item_id, tenant.tenant_id)}")
    print(f"dave can edit: {km.can_user_edit('dave', item.item_id, tenant.tenant_id)}")
    print(f"dave can delete: {km.can_user_delete('dave', item.item_id, tenant.tenant_id)}")

    # ==================== Demonstrate Access Control ====================
    print("\n" + "=" * 60)
    print("3. Access Control Workflow")
    print("=" * 60)

    # Simulate a user trying to perform actions
    users = [
        ("alice", "owner", "can do everything"),
        ("bob", "viewer", "can only read"),
        ("carol", "editor", "can read and edit"),
        ("dave", "admin", "can read, edit, delete"),
        ("eve", "no role", "cannot do anything"),
    ]

    print("\nAccess Summary:")
    print(f"{'User':<10} {'Role':<12} {'Read':<6} {'Edit':<6} {'Delete':<6}")
    print("-" * 50)

    for user_id, role, _ in users:
        can_read = km.can_user_read(user_id, item.item_id, tenant.tenant_id)
        can_edit = km.can_user_edit(user_id, item.item_id, tenant.tenant_id)
        can_delete = km.can_user_delete(user_id, item.item_id, tenant.tenant_id)

        print(
            f"{user_id:<10} {role:<12} "
            f"{'✓' if can_read else '✗':<6} "
            f"{'✓' if can_edit else '✗':<6} "
            f"{'✓' if can_delete else '✗':<6}"
        )

    # ==================== Role Hierarchy ====================
    print("\n" + "=" * 60)
    print("4. Role Permissions Hierarchy")
    print("=" * 60)

    roles_info = [
        (Role.VIEWER, "View knowledge items"),
        (Role.EDITOR, "View and edit knowledge items"),
        (Role.ADMIN, "View, edit, and manage items"),
        (Role.OWNER, "Full access and ownership control"),
    ]

    print("\nRole Permissions:")
    for role, description in roles_info:
        print(f"  {role.value.upper():<10} - {description}")

    # ==================== Revoke Permissions ====================
    print("\n" + "=" * 60)
    print("5. Revoking Permissions")
    print("=" * 60)

    print("\nRevoking bob's VIEWER role...")
    km.revoke_permission(
        item_id=item.item_id,
        user_id="bob",
        tenant_id=tenant.tenant_id,
        role=Role.VIEWER,
    )
    print(f"bob can now read: {km.can_user_read('bob', item.item_id, tenant.tenant_id)}")

    # ==================== Audit Trail ====================
    print("\n" + "=" * 60)
    print("6. Audit Trail")
    print("=" * 60)

    audit_log = km.get_audit_log(tenant.tenant_id, limit=20)
    print(f"\nTotal audit events: {len(audit_log)}")

    permission_events = [e for e in audit_log if "permission" in e.event_type.value.lower()]
    print(f"Permission events: {len(permission_events)}")

    if permission_events:
        print("\nRecent permission events:")
        for event in permission_events[-5:]:
            print(f"  - {event.user_id} {event.action}ed permission " f"for {event.resource_id}")

    # ==================== Summary ====================
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    print("✓ Users with access:")
    for user_id, _, _ in users:
        if km.can_user_read(user_id, item.item_id, tenant.tenant_id):
            print(f"  - {user_id}")

    print("\n✅ Access control example completed!")


if __name__ == "__main__":
    main()
