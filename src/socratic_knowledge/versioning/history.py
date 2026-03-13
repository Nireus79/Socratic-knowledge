"""Version history tracking and management."""

from typing import List

from ..core.knowledge_item import KnowledgeItem
from ..core.version import Version
from .version_model import VersionInfo


class VersionHistory:
    """
    Version history tracking for knowledge items.

    Manages version snapshots, history queries, and rollback information.
    """

    @staticmethod
    def create_snapshot(
        item: KnowledgeItem,
        change_message: str = "",
    ) -> Version:
        """
        Create a version snapshot from current item state.

        Args:
            item: Knowledge item to snapshot
            change_message: Optional change message

        Returns:
            Version: New version snapshot
        """
        return Version.create_from_item(item, change_message=change_message)

    @staticmethod
    def get_version_info_list(
        versions: List[Version],
    ) -> List[VersionInfo]:
        """
        Get version info from version snapshots.

        Args:
            versions: List of Version objects

        Returns:
            List[VersionInfo]: Version information list
        """
        info_list = []
        for version in versions:
            preview = version.content[:100] if version.content else ""
            assert version.created_at is not None, "Version.created_at must be set"
            info = VersionInfo(
                version_number=version.version_number,
                created_at=version.created_at,
                created_by=version.created_by,
                change_message=version.change_message,
                content_preview=preview,
            )
            info_list.append(info)
        return info_list

    @staticmethod
    def can_rollback_to(
        current_version: int,
        target_version: int,
    ) -> bool:
        """
        Check if rollback to target version is possible.

        Args:
            current_version: Current version number
            target_version: Target version number

        Returns:
            bool: True if rollback is possible
        """
        return target_version > 0 and target_version < current_version

    @staticmethod
    def get_version_diff_summary(
        old_version: Version,
        new_version: Version,
    ) -> dict:
        """
        Get summary of differences between versions.

        Args:
            old_version: Previous version
            new_version: Current version

        Returns:
            dict: Differences summary
        """
        title_changed = old_version.title != new_version.title
        content_changed = old_version.content != new_version.content

        return {
            "title_changed": title_changed,
            "content_changed": content_changed,
            "content_length_old": len(old_version.content),
            "content_length_new": len(new_version.content),
        }

    @staticmethod
    def get_version_timeline(
        versions: List[Version],
    ) -> List[dict]:
        """
        Get timeline view of versions.

        Args:
            versions: List of Version objects (in reverse chronological order)

        Returns:
            List[dict]: Timeline events
        """
        timeline = []
        for version in versions:
            assert version.created_at is not None, "Version.created_at must be set"
            timeline.append(
                {
                    "version": version.version_number,
                    "timestamp": version.created_at.isoformat(),
                    "author": version.created_by,
                    "message": version.change_message,
                    "title": version.title,
                }
            )
        return timeline
