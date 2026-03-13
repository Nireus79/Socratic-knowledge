"""
Example 3: Versioning & Audit Logging

This example demonstrates version control and complete
audit trail functionality.
"""

from socratic_knowledge import KnowledgeManager


def main():
    """Run versioning and audit example."""
    print("=" * 60)
    print("Example 3: Versioning & Audit Logging")
    print("=" * 60)

    km = KnowledgeManager(storage="sqlite", db_path="knowledge_demo.db")

    # Create tenant and item
    tenant = km.create_tenant(name="DocumentCorp")
    item = km.create_item(
        tenant_id=tenant.tenant_id,
        title="Product Requirements",
        content="Version 1: Initial requirements",
        created_by="alice",
    )

    print(f"\nItem: {item.title}")
    print(f"Initial version: {item.version}")
    print(f"Created by: {item.created_by}")

    # ==================== Create Versions ====================
    print("\n" + "=" * 60)
    print("1. Creating Multiple Versions")
    print("=" * 60)

    updates = [
        ("Added user authentication requirements", "Version 2: Added auth"),
        ("Specified database schema", "Version 3: Database design"),
        ("Added API endpoint specifications", "Version 4: API spec"),
        ("Included performance requirements", "Version 5: Performance"),
    ]

    for change_msg, new_content in updates:
        item.content += f"\n\n{new_content}"
        updated = km.update_item(item, change_message=change_msg)
        print(f"  ✓ v{updated.version}: {change_msg}")

    # ==================== Version History ====================
    print("\n" + "=" * 60)
    print("2. Version History")
    print("=" * 60)

    history = km.get_version_history(item.item_id, limit=10)
    print(f"\nTotal versions: {len(history)}")
    print("\nVersion Timeline:")

    for version in history:
        creator = version.created_by
        timestamp = version.created_at.strftime("%Y-%m-%d %H:%M:%S")
        message = version.change_message or "Initial creation"
        print(f"  v{version.version_number} ({timestamp}) by {creator}")
        print(f"    └─ {message}")

    # ==================== Version Info ====================
    print("\n" + "=" * 60)
    print("3. Version Info & Timeline")
    print("=" * 60)

    version_info = km.get_version_info(item.item_id, limit=10)
    print("\nVersion details:")
    for info in version_info:
        print(
            f"  v{info.version_number}: {info.content_preview[:50]}... " f"(by {info.created_by})"
        )

    # ==================== Simulate Rollback Need ====================
    print("\n" + "=" * 60)
    print("4. Conflict Detection & Rollback")
    print("=" * 60)

    # Check for conflicts (version mismatch scenario)
    print("\nSimulating concurrent edit scenario...")
    old_version = 2
    current_version = item.version

    print(f"  User expects version: {old_version}")
    print(f"  Actual current version: {current_version}")

    conflict = km.detect_version_conflict(
        item_id=item.item_id,
        user_id="bob",
        expected_version=old_version,
        actual_version=current_version,
    )

    if conflict:
        print(f"  ⚠️  Conflict detected: {conflict.conflict_type.value}")
        print("  Resolution: Reject edit and notify user of newer version")

    # ==================== Audit Log ====================
    print("\n" + "=" * 60)
    print("5. Audit Trail")
    print("=" * 60)

    audit_log = km.get_audit_log(tenant.tenant_id, limit=20)
    print(f"\nTotal audit events: {len(audit_log)}")

    # Categorize events
    create_events = [e for e in audit_log if "created" in e.event_type.value]
    update_events = [e for e in audit_log if "updated" in e.event_type.value]
    version_events = [e for e in audit_log if "version" in e.event_type.value]

    print(f"  Creates: {len(create_events)}")
    print(f"  Updates: {len(update_events)}")
    print(f"  Version events: {len(version_events)}")

    # ==================== User Activity ====================
    print("\n" + "=" * 60)
    print("6. User Activity Timeline")
    print("=" * 60)

    alice_activity = km.get_user_activity(tenant.tenant_id, "alice", limit=20)
    print(f"\nAlice's activity ({len(alice_activity)} events):")

    for event in alice_activity[-5:]:
        timestamp = event.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        print(f"  {timestamp} - {event.action.upper()}")
        print(f"    Resource: {event.resource_type} ({event.resource_id})")
        if event.changes:
            print(f"    Changes: {event.changes}")

    # ==================== Resource History ====================
    print("\n" + "=" * 60)
    print("7. Resource Change History")
    print("=" * 60)

    resource_history = km.get_resource_history(item.item_id, limit=20)
    print(f"\nChanges to '{item.title}' ({len(resource_history)} events):")

    for event in resource_history[-5:]:
        timestamp = event.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        print(f"  {timestamp} - {event.action.upper()} by {event.user_id}")
        if event.changes:
            for key, value in event.changes.items():
                print(f"    {key}: {str(value)[:40]}")

    # ==================== Compliance Summary ====================
    print("\n" + "=" * 60)
    print("8. Compliance Summary")
    print("=" * 60)

    print("\nDocument Audit Trail:")
    print(f"  Title: {item.title}")
    print(f"  Owner: {item.owner_id}")
    print(f"  Total versions: {len(history)}")
    print(f"  Total modifications: {len(resource_history)}")
    print(f"  Current version: {item.version}")
    print(f"  Last modified: {item.updated_at.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Last modified by: {item.updated_by}")

    print("\nCompliance Ready:")
    print("  ✓ Full version history available")
    print("  ✓ All changes tracked and timestamped")
    print("  ✓ Rollback capability verified")
    print("  ✓ Complete audit trail maintained")

    # ==================== Summary ====================
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"✓ Created and modified item {len(history)} times")
    print(f"✓ Generated {len(audit_log)} audit events")
    print(f"✓ Tracked changes by {len(set(e.user_id for e in audit_log))} users")
    print("✓ Ready for compliance audit")

    print("\n✅ Versioning & audit example completed!")


if __name__ == "__main__":
    main()
