# Socratic Knowledge - FAQ by Scenario

## Creating Tenant

How do I set up a new organization?

```python
from socratic_knowledge import KnowledgeManager

km = KnowledgeManager(storage="sqlite")
tenant = km.create_tenant(
    name="Acme Corp",
    domain="acme.com"
)
```

## Adding Documents

How do I add knowledge?

```python
collection = km.create_collection(
    tenant_id=tenant.tenant_id,
    name="Documentation",
    created_by="user123"
)

item = km.create_item(
    tenant_id=tenant.tenant_id,
    collection_id=collection.collection_id,
    title="API Guide",
    content="How to use our API...",
    created_by="user123",
    tags=["api", "guide"]
)
```

## Searching

How do I find documents?

```python
results = km.search(
    tenant_id=tenant.tenant_id,
    query="API documentation"
)

results = km.semantic_search(
    tenant_id=tenant.tenant_id,
    query="How to authenticate?"
)
```

## Access Control

How do I set permissions?

```python
km.grant_permission(
    item_id=item.item_id,
    user_id="user456",
    role="EDITOR",
    granted_by="user123"
)

can_edit = km.can_user_edit("user456", item.item_id)
```

## Versioning

How do I track changes?

```python
history = km.get_version_history(
    item_id=item.item_id,
    limit=10
)

km.rollback_item(
    item_id=item.item_id,
    version_number=5
)
```
