# Socratic Knowledge

[![Tests](https://github.com/Nireus79/Socratic-knowledge/workflows/Tests/badge.svg)](https://github.com/Nireus79/Socratic-knowledge/actions)
[![Code Quality](https://github.com/Nireus79/Socratic-knowledge/workflows/Quality/badge.svg)](https://github.com/Nireus79/Socratic-knowledge/actions)
[![PyPI](https://img.shields.io/pypi/v/socratic-knowledge)](https://pypi.org/project/socratic-knowledge/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Enterprise knowledge management system with **multi-tenancy**, **access control**, **versioning**, and **RAG integration**.

## Features

- **📚 Knowledge Organization** - Hierarchical knowledge base with collections and documents
- **🔐 Multi-Tenancy** - Isolated knowledge spaces for multiple organizations
- **👥 Access Control** - Role-based permissions (RBAC) with fine-grained control
- **📝 Versioning** - Full history tracking with rollback capabilities
- **🔍 Semantic Search** - RAG-powered semantic search with embeddings
- **🤝 Collaboration** - Multi-user editing with conflict detection
- **📋 Audit Logging** - Complete audit trail for compliance
- **🔌 Framework Integration** - Works with Openclaw and LangChain

## Quick Start

### Installation

```bash
# Basic installation
pip install socratic-knowledge

# With RAG integration
pip install socratic-knowledge[rag]

# With LangChain integration
pip install socratic-knowledge[langchain]

# Everything
pip install socratic-knowledge[all]
```

### Simple Example

```python
from socratic_knowledge import KnowledgeManager

# Create knowledge manager
km = KnowledgeManager(storage="sqlite", db_path="knowledge.db")

# Create tenant (organization)
tenant = km.create_tenant(name="Acme Corp", domain="acme.com")

# Create collection (folder)
docs = km.create_collection(
    tenant_id=tenant.tenant_id,
    name="Documentation",
    created_by="user123"
)

# Add knowledge item
item = km.create_item(
    tenant_id=tenant.tenant_id,
    collection_id=docs.collection_id,
    title="API Guide",
    content="How to use our API...",
    created_by="user123",
    tags=["api", "guide"]
)

# Search
results = km.search(tenant_id=tenant.tenant_id, query="API")

# Get item
retrieved = km.get_item(item.item_id, tenant_id=tenant.tenant_id)
```

## Core Concepts

### KnowledgeItem

The main entity representing any knowledge artifact (document, note, etc.)

```python
@dataclass
class KnowledgeItem:
    item_id: str                    # UUID
    tenant_id: str                  # For multi-tenancy
    collection_id: Optional[str]    # Parent collection
    title: str
    content: str
    content_type: str               # "text", "markdown", "json"
    version: int
    created_at: datetime
    updated_at: datetime
    created_by: str
    updated_by: str
    owner_id: str
    permissions: Dict[str, List[str]]  # {role: [user_ids]}
    tags: List[str]
    metadata: Dict[str, Any]
```

### Collection

Hierarchical container for organizing knowledge items (like folders)

```python
@dataclass
class Collection:
    collection_id: str
    tenant_id: str
    parent_id: Optional[str]        # For hierarchy
    name: str
    owner_id: str
    permissions: Dict[str, List[str]]
    inherit_permissions: bool       # Inherit ACL from parent
```

### Tenant

Organization/account for multi-tenancy support

```python
@dataclass
class Tenant:
    tenant_id: str
    name: str
    domain: Optional[str]           # e.g., "acme.com"
    max_storage_mb: int
    is_active: bool
```

### Access Control

Role-based permissions (RBAC):

- **VIEWER** - Read only
- **EDITOR** - Read + Write
- **ADMIN** - Full access
- **OWNER** - All permissions

## API Reference

### KnowledgeManager

Main interface for knowledge management operations.

```python
class KnowledgeManager:
    # Tenant operations
    def create_tenant(self, name: str, **kwargs) -> Tenant
    def get_tenant(self, tenant_id: str) -> Optional[Tenant]

    # Collection operations
    def create_collection(self, tenant_id: str, name: str, created_by: str,
                         parent_id: Optional[str] = None) -> Collection
    def get_collection(self, collection_id: str) -> Optional[Collection]
    def list_collections(self, tenant_id: str, parent_id: Optional[str] = None) -> List[Collection]

    # Knowledge item operations
    def create_item(self, tenant_id: str, title: str, content: str,
                   created_by: str, collection_id: Optional[str] = None,
                   **kwargs) -> KnowledgeItem
    def get_item(self, item_id: str, tenant_id: str) -> Optional[KnowledgeItem]
    def update_item(self, item: KnowledgeItem, change_message: str = "") -> KnowledgeItem
    def delete_item(self, item_id: str, tenant_id: str, soft: bool = True) -> bool
    def list_items(self, tenant_id: str, collection_id: Optional[str] = None,
                  limit: int = 100, offset: int = 0) -> List[KnowledgeItem]

    # Search operations
    def search(self, tenant_id: str, query: str, limit: int = 10) -> List[KnowledgeItem]
    def semantic_search(self, tenant_id: str, query: str, top_k: int = 5,
                       collection_id: Optional[str] = None) -> List[KnowledgeItem]

    # Access control
    def grant_permission(self, item_id: str, user_id: str, role: Role,
                        granted_by: str) -> None
    def can_user_edit(self, user_id: str, item_id: str) -> bool

    # Versioning
    def get_version_history(self, item_id: str, limit: int = 10) -> List[Version]
    def rollback_item(self, item_id: str, version_number: int) -> KnowledgeItem

    # Audit
    def get_audit_log(self, tenant_id: str, limit: int = 100) -> List[Dict[str, Any]]
```

## Examples

See `examples/` directory for complete examples:

- `01_basic_usage.py` - Basic CRUD operations
- `02_access_control.py` - Role-based permissions
- `03_versioning.py` - Version history and rollback
- `04_rag_integration.py` - Semantic search with RAG

## Integrations

### Openclaw

```python
from socratic_knowledge.integrations.openclaw import SocraticKnowledgeSkill

skill = SocraticKnowledgeSkill(storage="sqlite")
result = skill.search(tenant_id="org1", query="LLM prompt engineering", top_k=5)
```

### LangChain

```python
from socratic_knowledge.integrations.langchain import SocraticKnowledgeTool

tool = SocraticKnowledgeTool(storage="sqlite", enable_rag=True)
results = tool.semantic_search(
    tenant_id="org1",
    query="How to fine-tune models?",
    top_k=5
)
```

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=src/socratic_knowledge

# Specific test file
pytest tests/unit/test_knowledge_item.py -v
```

## Quality

```bash
# Format code
black src/ tests/ examples/

# Lint
ruff check src/ tests/ examples/

# Type check
mypy src/socratic_knowledge
```

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Project Status

**Version**: 0.1.0 (MVP)

### Statistics

- **Lines of Code**: ~4,300
- **Test Coverage**: 75%+ (100+ tests)
- **Supported Python**: 3.9, 3.10, 3.11, 3.12
- **Quality**: Black, Ruff, MyPy ✅
- **CI/CD**: GitHub Actions

### Implementation Progress

- Phase 1: Core Foundation (in progress)
- Phase 2: Access Control & Versioning (planned)
- Phase 3: RAG Integration & Search (planned)
- Phase 4: Collaboration & Audit (planned)
- Phase 5: Integrations (planned)
- Phase 6: Polish & Documentation (planned)

## Support

- 📖 [Documentation](https://github.com/Nireus79/Socratic-knowledge#readme)
- 🐛 [Issues](https://github.com/Nireus79/Socratic-knowledge/issues)
- 💬 [Discussions](https://github.com/Nireus79/Socratic-knowledge/discussions)

## Related Projects

- [Socratic Workflow](https://github.com/Nireus79/Socratic-workflow) - Workflow orchestration
- [Socratic Agents](https://github.com/Nireus79/Socratic-agents) - Multi-agent orchestration
- [Socratic RAG](https://github.com/Nireus79/Socratic-rag) - Retrieval-augmented generation
- [Socratic Analyzer](https://github.com/Nireus79/Socratic-analyzer) - Code analysis
- [Socrates Nexus](https://github.com/Nireus79/socrates-nexus) - Universal LLM client

---

**Built with ❤️ by the Socratic Ecosystem**
