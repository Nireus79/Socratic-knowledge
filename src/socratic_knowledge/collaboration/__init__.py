"""Collaboration and concurrent edit management module."""

from .conflict import Conflict, ConflictDetector, ConflictResolutionStrategy, ConflictType
from .locks import LockToken, OptimisticLockManager

__all__ = [
    "LockToken",
    "OptimisticLockManager",
    "Conflict",
    "ConflictType",
    "ConflictDetector",
    "ConflictResolutionStrategy",
]
