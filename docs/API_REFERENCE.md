# Socratic Knowledge - API Reference

## KnowledgeManager

### Tenant Operations
- `create_tenant(name, domain=None)` - Create tenant
- `get_tenant(tenant_id)` - Get tenant

### Collection Operations
- `create_collection(tenant_id, name, created_by, parent_id=None)` - Create folder
- `get_collection(collection_id)` - Get folder
- `list_collections(tenant_id, parent_id=None)` - List folders

### Item Operations
- `create_item(tenant_id, title, content, created_by, ...)` - Add item
- `get_item(item_id, tenant_id)` - Get item
- `update_item(item, change_message="")` - Update item
- `delete_item(item_id, tenant_id, soft=True)` - Delete item
- `list_items(tenant_id, collection_id=None, limit=100)` - List items

### Search Operations
- `search(tenant_id, query, limit=10)` - Keyword search
- `semantic_search(tenant_id, query, top_k=5, collection_id=None)` - RAG search

### Access Control
- `grant_permission(item_id, user_id, role, granted_by)` - Set permission
- `can_user_edit(user_id, item_id)` - Check edit permission

### Versioning
- `get_version_history(item_id, limit=10)` - Get versions
- `rollback_item(item_id, version_number)` - Revert to version

### Audit
- `get_audit_log(tenant_id, limit=100)` - Get audit log
