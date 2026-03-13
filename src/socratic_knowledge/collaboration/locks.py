"""Optimistic locking for concurrent edit handling."""

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional


@dataclass
class LockToken:
    """Represents an optimistic lock token."""

    item_id: str
    user_id: str
    version: int
    acquired_at: datetime
    expires_at: datetime

    def is_valid(self) -> bool:
        """Check if lock is still valid (not expired)."""
        return datetime.now(timezone.utc) < self.expires_at


class OptimisticLockManager:
    """
    Optimistic locking manager for concurrent edits.

    Uses version numbers to detect conflicts.
    """

    def __init__(self, lock_duration_minutes: int = 15):
        """
        Initialize lock manager.

        Args:
            lock_duration_minutes: How long locks remain valid
        """
        self.lock_duration = timedelta(minutes=lock_duration_minutes)
        self._locks: Dict[str, LockToken] = {}

    def acquire_lock(
        self,
        item_id: str,
        user_id: str,
        current_version: int,
    ) -> LockToken:
        """
        Acquire a lock for editing.

        Args:
            item_id: Item to lock
            user_id: User acquiring lock
            current_version: Current version number

        Returns:
            LockToken: Lock token for later validation
        """
        now = datetime.now(timezone.utc)
        expires_at = now + self.lock_duration

        token = LockToken(
            item_id=item_id,
            user_id=user_id,
            version=current_version,
            acquired_at=now,
            expires_at=expires_at,
        )

        self._locks[item_id] = token
        return token

    def validate_lock(
        self,
        item_id: str,
        user_id: str,
        current_version: int,
    ) -> bool:
        """
        Validate lock before update.

        Checks that:
        1. Lock exists and is valid
        2. Same user holds the lock
        3. Version hasn't changed (no conflict)

        Args:
            item_id: Item being updated
            user_id: User performing update
            current_version: Current version

        Returns:
            bool: True if lock is valid

        Raises:
            ValueError: If conflict detected
        """
        if item_id not in self._locks:
            raise ValueError(f"No lock for item {item_id}")

        token = self._locks[item_id]

        if not token.is_valid():
            raise ValueError(f"Lock expired for item {item_id}")

        if token.user_id != user_id:
            raise ValueError(
                f"Lock held by {token.user_id}, not {user_id}"
            )

        if token.version != current_version:
            raise ValueError(
                f"Version conflict: expected {token.version}, "
                f"got {current_version}"
            )

        return True

    def release_lock(self, item_id: str) -> bool:
        """
        Release a lock.

        Args:
            item_id: Item to unlock

        Returns:
            bool: True if lock was released
        """
        if item_id in self._locks:
            del self._locks[item_id]
            return True
        return False

    def get_lock(self, item_id: str) -> Optional[LockToken]:
        """
        Get lock information for item.

        Args:
            item_id: Item ID

        Returns:
            Optional[LockToken]: Lock token if exists
        """
        return self._locks.get(item_id)

    def is_locked(self, item_id: str) -> bool:
        """
        Check if item is locked.

        Args:
            item_id: Item ID

        Returns:
            bool: True if currently locked
        """
        token = self._locks.get(item_id)
        if not token:
            return False
        return token.is_valid()

    def cleanup_expired_locks(self) -> int:
        """
        Remove expired locks.

        Returns:
            int: Number of locks cleaned up
        """
        now = datetime.now(timezone.utc)
        expired = [
            item_id
            for item_id, token in self._locks.items()
            if token.expires_at <= now
        ]

        for item_id in expired:
            del self._locks[item_id]

        return len(expired)

    def clear_user_locks(self, user_id: str) -> int:
        """
        Clear all locks held by user.

        Args:
            user_id: User ID

        Returns:
            int: Number of locks cleared
        """
        to_delete = [
            item_id
            for item_id, token in self._locks.items()
            if token.user_id == user_id
        ]

        for item_id in to_delete:
            del self._locks[item_id]

        return len(to_delete)
