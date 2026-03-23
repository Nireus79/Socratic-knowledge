"""
Version management for knowledge items.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class VersionRecord(BaseModel):
    """Record of a knowledge item version."""

    version: int = Field(..., description="Version number")
    content: str = Field(..., description="Content at this version")
    created_at: datetime = Field(..., description="When this version was created")
    created_by: str = Field(..., description="User who created this version")
    change_description: Optional[str] = Field(None, description="What changed")


class VersionManager:
    """
    Manage versions of knowledge items.

    Tracks changes to knowledge items over time with:
    - Full version history
    - Ability to revert to previous versions
    - Change tracking and annotations
    - Diff generation
    """

    def __init__(self):
        """Initialize version manager."""
        self.versions: Dict[str, List[VersionRecord]] = {}

    def create_version(
        self,
        item_id: str,
        version: int,
        content: str,
        created_by: str,
        change_description: Optional[str] = None,
    ) -> VersionRecord:
        """
        Create a new version record.

        Args:
            item_id: Knowledge item ID
            version: Version number
            content: Content at this version
            created_by: User who made the change
            change_description: Description of changes

        Returns:
            Version record
        """
        record = VersionRecord(
            version=version,
            content=content,
            created_at=datetime.utcnow(),
            created_by=created_by,
            change_description=change_description,
        )

        if item_id not in self.versions:
            self.versions[item_id] = []

        self.versions[item_id].append(record)
        logger.info(f"Created version {version} of {item_id}")
        return record

    def get_version(self, item_id: str, version: int) -> Optional[VersionRecord]:
        """
        Get a specific version of an item.

        Args:
            item_id: Knowledge item ID
            version: Version number

        Returns:
            Version record or None
        """
        if item_id not in self.versions:
            return None

        for record in self.versions[item_id]:
            if record.version == version:
                return record

        return None

    def get_version_history(self, item_id: str) -> List[VersionRecord]:
        """
        Get all versions of an item.

        Args:
            item_id: Knowledge item ID

        Returns:
            List of version records in order
        """
        return self.versions.get(item_id, [])

    def get_latest_version(self, item_id: str) -> Optional[VersionRecord]:
        """
        Get the latest version of an item.

        Args:
            item_id: Knowledge item ID

        Returns:
            Latest version record or None
        """
        history = self.get_version_history(item_id)
        return history[-1] if history else None

    def revert_to_version(self, item_id: str, version: int) -> Optional[VersionRecord]:
        """
        Create a new version by reverting to a previous version.

        Args:
            item_id: Knowledge item ID
            version: Version number to revert to

        Returns:
            New version record or None
        """
        old_version = self.get_version(item_id, version)
        if not old_version:
            return None

        history = self.get_version_history(item_id)
        latest_version = len(history)

        # Create new version with old content
        new_record = VersionRecord(
            version=latest_version + 1,
            content=old_version.content,
            created_at=datetime.utcnow(),
            created_by="system",
            change_description=f"Reverted to version {version}",
        )

        self.versions[item_id].append(new_record)
        logger.info(f"Reverted {item_id} to version {version} (new version: {latest_version + 1})")
        return new_record

    def get_diff(self, item_id: str, version_a: int, version_b: int) -> Optional[Dict]:
        """
        Get differences between two versions.

        Args:
            item_id: Knowledge item ID
            version_a: First version number
            version_b: Second version number

        Returns:
            Dictionary with differences or None
        """
        record_a = self.get_version(item_id, version_a)
        record_b = self.get_version(item_id, version_b)

        if not record_a or not record_b:
            return None

        # Simple line-based diff
        lines_a = record_a.content.split("\n")
        lines_b = record_b.content.split("\n")

        return {
            "version_a": version_a,
            "version_b": version_b,
            "lines_added": len([l for l in lines_b if l not in lines_a]),
            "lines_removed": len([l for l in lines_a if l not in lines_b]),
            "content_change_percent": abs(len(lines_b) - len(lines_a)) / max(len(lines_a), 1),
        }

    def cleanup_old_versions(self, item_id: str, keep_count: int = 10) -> int:
        """
        Remove old versions, keeping only the most recent.

        Args:
            item_id: Knowledge item ID
            keep_count: Number of versions to keep

        Returns:
            Number of versions removed
        """
        if item_id not in self.versions:
            return 0

        history = self.versions[item_id]
        if len(history) <= keep_count:
            return 0

        removed = len(history) - keep_count
        self.versions[item_id] = history[-keep_count:]
        logger.info(f"Cleaned up {removed} old versions of {item_id}")
        return removed
