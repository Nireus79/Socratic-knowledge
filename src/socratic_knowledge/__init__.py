"""
Socratic Knowledge - Multi-tenant knowledge management with RBAC and versioning

Provides secure, multi-tenant knowledge storage and management capabilities.
"""

__version__ = "0.1.0"

from .manager import KnowledgeManager
from .models import KnowledgeItem, AccessControl
from .versioning import VersionManager

__all__ = [
    "KnowledgeManager",
    "KnowledgeItem",
    "AccessControl",
    "VersionManager",
]
