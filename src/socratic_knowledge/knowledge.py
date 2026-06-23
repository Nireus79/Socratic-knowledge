"""Knowledge entry model for Socrates AI"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional


@dataclass
class KnowledgeEntry:
    """Represents a single entry in the knowledge vector database"""

    id: str
    content: str
    category: str
    embedding: Optional[List[float]] = None
    metadata: Optional[Dict[str, Any]] = None

    @staticmethod
    def from_dict(data: dict) -> "KnowledgeEntry":
        """Deserialize from dictionary."""
        return KnowledgeEntry(**data)

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return asdict(self)
