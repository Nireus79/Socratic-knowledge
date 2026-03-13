"""Conflict detection and resolution for concurrent edits."""

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional


class ConflictType(Enum):
    """Types of conflicts."""

    VERSION_CONFLICT = "version_conflict"          # Version mismatch
    CONTENT_CONFLICT = "content_conflict"          # Simultaneous edits
    LOCK_CONFLICT = "lock_conflict"                # Lock held by another user
    PERMISSION_CONFLICT = "permission_conflict"    # Permission changed


class ConflictResolutionStrategy(Enum):
    """Strategies for resolving conflicts."""

    MANUAL = "manual"        # Require manual resolution
    LAST_WRITE_WINS = "last_write_wins"            # Latest change wins
    FIRST_WRITE_WINS = "first_write_wins"          # First change wins
    MERGE = "merge"          # Attempt to merge changes
    ABORT = "abort"          # Cancel the operation


@dataclass
class Conflict:
    """Represents a detected conflict."""

    conflict_id: str
    conflict_type: ConflictType
    item_id: str
    user_id: str
    current_version: int
    conflicting_version: int
    timestamp: datetime
    changes_new: Dict[str, Any]
    changes_existing: Dict[str, Any]
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "conflict_id": self.conflict_id,
            "conflict_type": self.conflict_type.value,
            "item_id": self.item_id,
            "user_id": self.user_id,
            "current_version": self.current_version,
            "conflicting_version": self.conflicting_version,
            "timestamp": self.timestamp.isoformat(),
            "changes_new": self.changes_new,
            "changes_existing": self.changes_existing,
            "metadata": self.metadata,
        }


class ConflictDetector:
    """
    Detects conflicts in concurrent edits.

    Identifies version mismatches and simultaneous changes.
    """

    def __init__(self):
        """Initialize conflict detector."""
        self._conflicts: Dict[str, Conflict] = {}

    def detect_version_conflict(
        self,
        item_id: str,
        user_id: str,
        expected_version: int,
        actual_version: int,
    ) -> Optional[Conflict]:
        """
        Detect version conflict.

        Args:
            item_id: Item being edited
            user_id: User making change
            expected_version: Version user expects
            actual_version: Actual current version

        Returns:
            Optional[Conflict]: Conflict if detected
        """
        if expected_version == actual_version:
            return None

        conflict = Conflict(
            conflict_id=f"conflict_{item_id}_{user_id}",
            conflict_type=ConflictType.VERSION_CONFLICT,
            item_id=item_id,
            user_id=user_id,
            current_version=expected_version,
            conflicting_version=actual_version,
            timestamp=datetime.now(timezone.utc),
            changes_new={},
            changes_existing={},
            metadata={},
        )

        self._conflicts[conflict.conflict_id] = conflict
        return conflict

    def detect_content_conflict(
        self,
        item_id: str,
        user_id: str,
        new_changes: Dict[str, Any],
        existing_changes: Dict[str, Any],
    ) -> Optional[Conflict]:
        """
        Detect content conflict from simultaneous edits.

        Args:
            item_id: Item being edited
            user_id: User making change
            new_changes: Changes proposed by user
            existing_changes: Changes already made

        Returns:
            Optional[Conflict]: Conflict if detected
        """
        # Check for overlapping field changes
        new_fields = set(new_changes.keys())
        existing_fields = set(existing_changes.keys())
        overlapping = new_fields & existing_fields

        if not overlapping:
            return None

        # Check if changes are to same fields with different values
        for field in overlapping:
            if new_changes[field] != existing_changes[field]:
                conflict = Conflict(
                    conflict_id=f"conflict_{item_id}_{user_id}",
                    conflict_type=ConflictType.CONTENT_CONFLICT,
                    item_id=item_id,
                    user_id=user_id,
                    current_version=0,
                    conflicting_version=0,
                    timestamp=datetime.now(timezone.utc),
                    changes_new=new_changes,
                    changes_existing=existing_changes,
                    metadata={"conflicting_field": field},
                )

                self._conflicts[conflict.conflict_id] = conflict
                return conflict

        return None

    def detect_lock_conflict(
        self,
        item_id: str,
        user_id: str,
        lock_holder: str,
    ) -> Optional[Conflict]:
        """
        Detect lock conflict (item locked by another user).

        Args:
            item_id: Item being edited
            user_id: User trying to edit
            lock_holder: User holding the lock

        Returns:
            Optional[Conflict]: Conflict if detected
        """
        if user_id == lock_holder:
            return None

        conflict = Conflict(
            conflict_id=f"conflict_{item_id}_{user_id}",
            conflict_type=ConflictType.LOCK_CONFLICT,
            item_id=item_id,
            user_id=user_id,
            current_version=0,
            conflicting_version=0,
            timestamp=datetime.now(timezone.utc),
            changes_new={},
            changes_existing={},
            metadata={"lock_holder": lock_holder},
        )

        self._conflicts[conflict.conflict_id] = conflict
        return conflict

    def get_conflict(self, conflict_id: str) -> Optional[Conflict]:
        """
        Get conflict by ID.

        Args:
            conflict_id: Conflict ID

        Returns:
            Optional[Conflict]: Conflict if exists
        """
        return self._conflicts.get(conflict_id)

    def get_item_conflicts(self, item_id: str) -> list:
        """
        Get all conflicts for item.

        Args:
            item_id: Item ID

        Returns:
            list: Conflicts for this item
        """
        return [c for c in self._conflicts.values() if c.item_id == item_id]

    def resolve_conflict(
        self,
        conflict_id: str,
        strategy: ConflictResolutionStrategy,
        resolution_data: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Resolve a conflict.

        Args:
            conflict_id: Conflict to resolve
            strategy: Resolution strategy
            resolution_data: Data for manual resolution

        Returns:
            bool: True if resolved
        """
        conflict = self._conflicts.get(conflict_id)
        if not conflict:
            return False

        # Mark as resolved by removing from tracking
        del self._conflicts[conflict_id]
        return True

    def clear_conflicts(self, item_id: Optional[str] = None) -> int:
        """
        Clear resolved conflicts.

        Args:
            item_id: If specified, only clear for this item

        Returns:
            int: Number cleared
        """
        if not item_id:
            count = len(self._conflicts)
            self._conflicts.clear()
            return count

        count = len(
            [c for c in self._conflicts.values() if c.item_id == item_id]
        )
        self._conflicts = {
            cid: c
            for cid, c in self._conflicts.items()
            if c.item_id != item_id
        }
        return count

    def has_conflicts(self, item_id: Optional[str] = None) -> bool:
        """
        Check if there are unresolved conflicts.

        Args:
            item_id: If specified, check only for this item

        Returns:
            bool: True if conflicts exist
        """
        if not item_id:
            return len(self._conflicts) > 0

        return any(c.item_id == item_id for c in self._conflicts.values())
