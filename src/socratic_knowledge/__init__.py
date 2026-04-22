"""
Socratic Knowledge - Knowledge Base Management

Extracted from Socrates v1.3.3
"""

from .knowledge import KnowledgeEntry
from .knowledge_base import KnowledgeBase
from .code_parser import CodeParser

__version__ = "1.3.3"
__all__ = ["KnowledgeEntry", "KnowledgeBase", "CodeParser"]
