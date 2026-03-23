# Socratic Knowledge

Multi-tenant knowledge management with RBAC and versioning for the Socratic AI platform.

## Features

- **Multi-Tenant Support**: Complete tenant isolation
- **Role-Based Access Control**: Fine-grained permissions (read, write, delete)
- **Full Versioning**: Complete change history with revert capability
- **Search & Discovery**: Full-text search with filtering
- **Metadata Support**: Custom metadata per knowledge item
- **Audit Trail**: Track who made changes and when

## Installation

```bash
pip install socratic-knowledge
```

With database support:

```bash
pip install socratic-knowledge[sqlalchemy]
```

## Quick Start

```python
from socratic_knowledge import KnowledgeManager

manager = KnowledgeManager()

# Create knowledge item
item = manager.create_item(
    tenant_id="org-1",
    title="Python Best Practices",
    content="# Best Practices...",
    owner="user-123",
    category="documentation"
)

# Search for items
results = manager.search(
    tenant_id="org-1",
    query="python",
    user_id="user-123"
)

# Manage access
manager.grant_access(
    item_id=item.id,
    user_id="user-123",
    permission_type="read",
    grant_user="user-456"
)
```

## Components

### KnowledgeManager

Manages knowledge items with multi-tenancy and RBAC.

```python
manager = KnowledgeManager()
item = manager.create_item(...)
result = manager.search(...)
manager.grant_access(...)
```

### VersionManager

Tracks item versions and enables reversion.

```python
from socratic_knowledge import VersionManager

version_mgr = VersionManager()
version_mgr.create_version(item_id, version_num, content, user)
history = version_mgr.get_version_history(item_id)
```

### AccessControl

Define granular permissions for knowledge items.

```python
from socratic_knowledge import AccessControl

ac = AccessControl(
    read=["user-1", "user-2"],
    write=["user-1"],
    delete=["user-1"],
    owner="user-1"
)
```

## License

MIT
