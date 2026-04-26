"""
Socratic Knowledge - Knowledge Base Management

Extracted from Socrates v1.3.3
"""

from __future__ import annotations

from .code_parser import CodeParser
from .knowledge import KnowledgeEntry
from .knowledge_base import DEFAULT_KNOWLEDGE

__version__ = "0.1.6"
__all__ = ["KnowledgeEntry", "CodeParser", "DEFAULT_KNOWLEDGE"]
