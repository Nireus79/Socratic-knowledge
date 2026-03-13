"""
Example 1: Basic Knowledge Management

This example demonstrates the fundamental CRUD operations
for managing knowledge items, collections, and tenants.
"""

from socratic_knowledge import KnowledgeManager


def main():
    """Run basic knowledge management example."""
    print("=" * 60)
    print("Example 1: Basic Knowledge Management")
    print("=" * 60)

    # Initialize KnowledgeManager
    km = KnowledgeManager(storage="sqlite", db_path="knowledge_demo.db")

    # ==================== Create Tenant ====================
    print("\n1. Creating Tenant...")
    tenant = km.create_tenant(
        name="TechCorp",
        domain="techcorp.com",
    )
    print(f"   ✓ Created tenant: {tenant.name} (ID: {tenant.tenant_id})")

    # ==================== Create Collections ====================
    print("\n2. Creating Collections (Folders)...")

    # Root collection
    root = km.create_collection(
        tenant_id=tenant.tenant_id,
        name="Knowledge Base",
        created_by="admin",
    )
    print(f"   ✓ Created: {root.name}")

    # Sub-collections
    documentation = km.create_collection(
        tenant_id=tenant.tenant_id,
        name="Documentation",
        parent_id=root.collection_id,
        created_by="admin",
    )
    print(f"   ✓ Created: {documentation.name} (nested)")

    api_docs = km.create_collection(
        tenant_id=tenant.tenant_id,
        name="API Reference",
        parent_id=documentation.collection_id,
        created_by="admin",
    )
    print(f"   ✓ Created: {api_docs.name} (2-levels deep)")

    # ==================== Create Knowledge Items ====================
    print("\n3. Creating Knowledge Items...")

    item1 = km.create_item(
        tenant_id=tenant.tenant_id,
        collection_id=api_docs.collection_id,
        title="REST API Guide",
        content="""
# REST API Guide

## Authentication
Use Bearer tokens in the Authorization header:
```
Authorization: Bearer YOUR_TOKEN
```

## Endpoints
- GET /api/items - List all items
- POST /api/items - Create new item
- GET /api/items/{id} - Get specific item
- PUT /api/items/{id} - Update item
- DELETE /api/items/{id} - Delete item
        """,
        created_by="alice",
        tags=["api", "rest", "authentication"],
    )
    print(f"   ✓ Created: {item1.title} (v{item1.version})")

    item2 = km.create_item(
        tenant_id=tenant.tenant_id,
        collection_id=documentation.collection_id,
        title="Getting Started",
        content="""
# Getting Started with TechCorp

## Installation
```bash
pip install techcorp-sdk
```

## Quick Start
```python
from techcorp import Client
client = Client(api_key="your-key")
items = client.list_items()
```
        """,
        created_by="bob",
        tags=["guide", "quickstart"],
    )
    print(f"   ✓ Created: {item2.title} (v{item2.version})")

    # ==================== List Items ====================
    print("\n4. Listing Items...")
    all_items = km.list_items(tenant_id=tenant.tenant_id)
    print(f"   Total items in tenant: {len(all_items)}")

    items_in_api_docs = km.list_items(
        tenant_id=tenant.tenant_id,
        collection_id=api_docs.collection_id,
    )
    print(f"   Items in API Reference: {len(items_in_api_docs)}")

    # ==================== Search ====================
    print("\n5. Full-Text Search...")
    search_results = km.search(
        tenant_id=tenant.tenant_id,
        query="API",
        limit=10,
    )
    print(f"   Found {len(search_results)} items matching 'API':")
    for item in search_results:
        print(f"     - {item.title}")

    # ==================== Retrieve Item ====================
    print("\n6. Retrieving Item...")
    retrieved = km.get_item(item1.item_id, tenant.tenant_id)
    if retrieved:
        print(f"   ✓ Retrieved: {retrieved.title}")
        print(f"   Version: {retrieved.version}")
        print(f"   Tags: {', '.join(retrieved.tags)}")
        print(f"   Content preview: {retrieved.content[:100]}...")

    # ==================== Update Item ====================
    print("\n7. Updating Item...")
    item1.content += "\n\n## Rate Limiting\nAPI rate limit: 1000 requests/hour"
    item1.title = "REST API Guide (Updated)"
    updated = km.update_item(item1, change_message="Added rate limiting info")
    print(f"   ✓ Updated to version {updated.version}")

    # ==================== Version History ====================
    print("\n8. Checking Version History...")
    history = km.get_version_history(item1.item_id, limit=10)
    print(f"   Total versions: {len(history)}")
    for version in history:
        print(f"     - v{version.version_number}: {version.change_message or 'Initial creation'}")

    # ==================== Collection Hierarchy ====================
    print("\n9. Collection Hierarchy...")
    collections = km.list_collections(tenant_id=tenant.tenant_id)
    print(f"   Total collections: {len(collections)}")
    for coll in collections:
        indent = "  " if coll.parent_id else ""
        parent_info = f" (parent: {coll.parent_id})" if coll.parent_id else ""
        print(f"   {indent}- {coll.name}{parent_info}")

    # ==================== Summary ====================
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"Tenant: {tenant.name}")
    print(f"Collections: {len(collections)}")
    print(f"Items: {len(all_items)}")
    print(f"Largest item versions: {max(i.version for i in all_items) if all_items else 0}")
    print("\n✅ Basic usage example completed!")


if __name__ == "__main__":
    main()
