"""Framework integrations for Socratic Knowledge."""

from .langchain import HAS_LANGCHAIN, SocraticKnowledgeTools
from .openclaw import SocraticKnowledgeSkill

__all__ = [
    "SocraticKnowledgeSkill",
    "SocraticKnowledgeTools",
    "HAS_LANGCHAIN",
]
