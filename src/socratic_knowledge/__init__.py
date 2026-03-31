"""
Socratic Knowledge - Enterprise knowledge management system.

Provides multi-tenant knowledge management with access control, versioning,
and RAG integration.
"""

from .async_manager import AsyncKnowledgeManager
from .core.collection import Collection
from .core.knowledge_item import KnowledgeItem
from .core.tenant import Tenant
from .core.user import User
from .core.version import Version
from .manager import KnowledgeManager

# Alias for backward compatibility and consistent naming
KnowledgeBase = KnowledgeManager

__version__ = "0.1.0"

__all__ = [
    # Core models
    "KnowledgeItem",
    "Collection",
    "Tenant",
    "User",
    "Version",
    # Manager
    "KnowledgeBase",
    "KnowledgeManager",
    "AsyncKnowledgeManager",
]
