"""Tests for collaboration and concurrent edit handling."""

import pytest
from datetime import datetime, timedelta, timezone

from socratic_knowledge.collaboration.conflict import (
    Conflict,
    ConflictDetector,
    ConflictResolutionStrategy,
    ConflictType,
)
from socratic_knowledge.collaboration.locks import (
    LockToken,
    OptimisticLockManager,
)


class TestOptimisticLockManager:
    """Test optimistic locking for concurrent edits."""

    def test_acquire_lock(self):
        """Test acquiring a lock."""
        manager = OptimisticLockManager()
        token = manager.acquire_lock(
            item_id="item_1",
            user_id="user1",
            current_version=1,
        )

        assert token.item_id == "item_1"
        assert token.user_id == "user1"
        assert token.version == 1
        assert token.is_valid()

    def test_validate_lock_success(self):
        """Test validating a valid lock."""
        manager = OptimisticLockManager()
        manager.acquire_lock("item_1", "user1", 1)

        assert manager.validate_lock("item_1", "user1", 1)

    def test_validate_lock_no_lock(self):
        """Test validating when no lock exists."""
        manager = OptimisticLockManager()

        with pytest.raises(ValueError, match="No lock for item"):
            manager.validate_lock("item_1", "user1", 1)

    def test_validate_lock_wrong_user(self):
        """Test validating lock held by different user."""
        manager = OptimisticLockManager()
        manager.acquire_lock("item_1", "user1", 1)

        with pytest.raises(ValueError, match="Lock held by"):
            manager.validate_lock("item_1", "user2", 1)

    def test_validate_lock_version_conflict(self):
        """Test validating lock with version conflict."""
        manager = OptimisticLockManager()
        manager.acquire_lock("item_1", "user1", 1)

        with pytest.raises(ValueError, match="Version conflict"):
            manager.validate_lock("item_1", "user1", 2)

    def test_release_lock(self):
        """Test releasing a lock."""
        manager = OptimisticLockManager()
        manager.acquire_lock("item_1", "user1", 1)

        assert manager.release_lock("item_1")
        assert not manager.is_locked("item_1")

    def test_release_nonexistent_lock(self):
        """Test releasing lock that doesn't exist."""
        manager = OptimisticLockManager()

        assert not manager.release_lock("item_1")

    def test_is_locked(self):
        """Test checking if item is locked."""
        manager = OptimisticLockManager()
        assert not manager.is_locked("item_1")

        manager.acquire_lock("item_1", "user1", 1)
        assert manager.is_locked("item_1")

    def test_get_lock(self):
        """Test getting lock information."""
        manager = OptimisticLockManager()
        token = manager.acquire_lock("item_1", "user1", 1)

        retrieved = manager.get_lock("item_1")
        assert retrieved.item_id == token.item_id
        assert retrieved.user_id == token.user_id

    def test_get_nonexistent_lock(self):
        """Test getting lock that doesn't exist."""
        manager = OptimisticLockManager()

        assert manager.get_lock("item_1") is None

    def test_cleanup_expired_locks(self):
        """Test cleaning up expired locks."""
        manager = OptimisticLockManager(lock_duration_minutes=0)
        manager.acquire_lock("item_1", "user1", 1)

        # Wait for lock to expire
        import time
        time.sleep(0.1)

        count = manager.cleanup_expired_locks()
        assert count == 1
        assert not manager.is_locked("item_1")

    def test_clear_user_locks(self):
        """Test clearing all locks for a user."""
        manager = OptimisticLockManager()
        manager.acquire_lock("item_1", "user1", 1)
        manager.acquire_lock("item_2", "user1", 1)
        manager.acquire_lock("item_3", "user2", 1)

        count = manager.clear_user_locks("user1")
        assert count == 2
        assert manager.is_locked("item_3")

    def test_multiple_locks_different_items(self):
        """Test multiple locks on different items."""
        manager = OptimisticLockManager()
        token1 = manager.acquire_lock("item_1", "user1", 1)
        token2 = manager.acquire_lock("item_2", "user1", 1)

        assert manager.is_locked("item_1")
        assert manager.is_locked("item_2")
        assert token1.item_id == "item_1"
        assert token2.item_id == "item_2"

    def test_lock_token_expiry(self):
        """Test lock token expiration."""
        manager = OptimisticLockManager(lock_duration_minutes=0)
        token = manager.acquire_lock("item_1", "user1", 1)

        # Token should expire immediately
        import time
        time.sleep(0.1)

        assert not token.is_valid()


class TestConflictDetector:
    """Test conflict detection."""

    def test_detect_version_conflict(self):
        """Test detecting version conflict."""
        detector = ConflictDetector()
        conflict = detector.detect_version_conflict(
            item_id="item_1",
            user_id="user1",
            expected_version=1,
            actual_version=2,
        )

        assert conflict is not None
        assert conflict.conflict_type == ConflictType.VERSION_CONFLICT
        assert conflict.current_version == 1
        assert conflict.conflicting_version == 2

    def test_no_version_conflict(self):
        """Test when versions match."""
        detector = ConflictDetector()
        conflict = detector.detect_version_conflict(
            item_id="item_1",
            user_id="user1",
            expected_version=1,
            actual_version=1,
        )

        assert conflict is None

    def test_detect_content_conflict(self):
        """Test detecting content conflict."""
        detector = ConflictDetector()
        new_changes = {"title": "New Title"}
        existing_changes = {"title": "Other Title"}

        conflict = detector.detect_content_conflict(
            item_id="item_1",
            user_id="user1",
            new_changes=new_changes,
            existing_changes=existing_changes,
        )

        assert conflict is not None
        assert conflict.conflict_type == ConflictType.CONTENT_CONFLICT

    def test_no_content_conflict_non_overlapping(self):
        """Test no conflict when fields don't overlap."""
        detector = ConflictDetector()
        new_changes = {"title": "New Title"}
        existing_changes = {"content": "New Content"}

        conflict = detector.detect_content_conflict(
            item_id="item_1",
            user_id="user1",
            new_changes=new_changes,
            existing_changes=existing_changes,
        )

        assert conflict is None

    def test_no_content_conflict_same_values(self):
        """Test no conflict when same field has same value."""
        detector = ConflictDetector()
        new_changes = {"title": "Same Title"}
        existing_changes = {"title": "Same Title"}

        conflict = detector.detect_content_conflict(
            item_id="item_1",
            user_id="user1",
            new_changes=new_changes,
            existing_changes=existing_changes,
        )

        assert conflict is None

    def test_detect_lock_conflict(self):
        """Test detecting lock conflict."""
        detector = ConflictDetector()
        conflict = detector.detect_lock_conflict(
            item_id="item_1",
            user_id="user1",
            lock_holder="user2",
        )

        assert conflict is not None
        assert conflict.conflict_type == ConflictType.LOCK_CONFLICT
        assert conflict.metadata["lock_holder"] == "user2"

    def test_no_lock_conflict_same_user(self):
        """Test no conflict when same user holds lock."""
        detector = ConflictDetector()
        conflict = detector.detect_lock_conflict(
            item_id="item_1",
            user_id="user1",
            lock_holder="user1",
        )

        assert conflict is None

    def test_get_conflict(self):
        """Test retrieving a conflict."""
        detector = ConflictDetector()
        original = detector.detect_version_conflict(
            "item_1", "user1", 1, 2
        )

        retrieved = detector.get_conflict(original.conflict_id)
        assert retrieved.conflict_id == original.conflict_id

    def test_get_nonexistent_conflict(self):
        """Test getting conflict that doesn't exist."""
        detector = ConflictDetector()

        assert detector.get_conflict("nonexistent") is None

    def test_get_item_conflicts(self):
        """Test retrieving all conflicts for item."""
        detector = ConflictDetector()
        c1 = detector.detect_version_conflict("item_1", "user1", 1, 2)
        c2 = detector.detect_version_conflict("item_1", "user2", 1, 3)
        c3 = detector.detect_version_conflict("item_2", "user1", 1, 2)

        conflicts = detector.get_item_conflicts("item_1")
        assert len(conflicts) == 2

    def test_resolve_conflict(self):
        """Test resolving a conflict."""
        detector = ConflictDetector()
        conflict = detector.detect_version_conflict(
            "item_1", "user1", 1, 2
        )

        assert detector.resolve_conflict(
            conflict.conflict_id,
            ConflictResolutionStrategy.MANUAL,
        )
        assert detector.get_conflict(conflict.conflict_id) is None

    def test_resolve_nonexistent_conflict(self):
        """Test resolving conflict that doesn't exist."""
        detector = ConflictDetector()

        assert not detector.resolve_conflict(
            "nonexistent",
            ConflictResolutionStrategy.MANUAL,
        )

    def test_clear_conflicts(self):
        """Test clearing all conflicts."""
        detector = ConflictDetector()
        detector.detect_version_conflict("item_1", "user1", 1, 2)
        detector.detect_version_conflict("item_2", "user1", 1, 2)

        count = detector.clear_conflicts()
        assert count == 2
        assert not detector.has_conflicts()

    def test_clear_conflicts_by_item(self):
        """Test clearing conflicts for specific item."""
        detector = ConflictDetector()
        detector.detect_version_conflict("item_1", "user1", 1, 2)
        detector.detect_version_conflict("item_1", "user2", 1, 2)
        detector.detect_version_conflict("item_2", "user1", 1, 2)

        count = detector.clear_conflicts("item_1")
        assert count == 2

        remaining = detector.get_item_conflicts("item_2")
        assert len(remaining) == 1

    def test_has_conflicts(self):
        """Test checking if conflicts exist."""
        detector = ConflictDetector()
        assert not detector.has_conflicts()

        detector.detect_version_conflict("item_1", "user1", 1, 2)
        assert detector.has_conflicts()

    def test_has_conflicts_for_item(self):
        """Test checking conflicts for specific item."""
        detector = ConflictDetector()
        detector.detect_version_conflict("item_1", "user1", 1, 2)

        assert detector.has_conflicts("item_1")
        assert not detector.has_conflicts("item_2")

    def test_conflict_serialization(self):
        """Test conflict to_dict serialization."""
        detector = ConflictDetector()
        conflict = detector.detect_version_conflict(
            "item_1", "user1", 1, 2
        )

        data = conflict.to_dict()
        assert data["conflict_type"] == "version_conflict"
        assert data["item_id"] == "item_1"
        assert data["user_id"] == "user1"
