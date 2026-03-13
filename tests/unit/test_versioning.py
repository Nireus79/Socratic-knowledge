"""Tests for versioning and history tracking."""

from datetime import datetime, timezone

from socratic_knowledge.core.knowledge_item import KnowledgeItem
from socratic_knowledge.core.version import Version
from socratic_knowledge.versioning.history import VersionHistory
from socratic_knowledge.versioning.version_model import VersionInfo


class TestVersionHistory:
    """Test VersionHistory tracking and analysis."""

    def test_create_snapshot(self):
        """Test creating a version snapshot."""
        item = KnowledgeItem.create(
            title="Test",
            content="Content",
            tenant_id="t1",
            created_by="user1",
        )

        snapshot = VersionHistory.create_snapshot(item)

        assert snapshot.item_id == item.item_id
        assert snapshot.content == item.content
        assert snapshot.title == item.title
        assert snapshot.created_by == item.created_by

    def test_create_snapshot_with_message(self):
        """Test creating snapshot with change message."""
        item = KnowledgeItem.create(
            title="Test",
            content="Content",
            tenant_id="t1",
            created_by="user1",
        )

        snapshot = VersionHistory.create_snapshot(item, change_message="Fixed typo")

        assert snapshot.change_message == "Fixed typo"

    def test_get_version_info_list(self):
        """Test converting versions to lightweight info."""
        item = KnowledgeItem.create(
            title="Test",
            content="Content",
            tenant_id="t1",
            created_by="user1",
        )

        versions = [
            VersionHistory.create_snapshot(item),
        ]

        info_list = VersionHistory.get_version_info_list(versions)

        assert len(info_list) == 1
        assert isinstance(info_list[0], VersionInfo)
        assert info_list[0].version_number == versions[0].version_number
        assert info_list[0].created_by == versions[0].created_by

    def test_version_info_content_preview(self):
        """Test that version info has content preview."""
        item = KnowledgeItem.create(
            title="Test",
            content="A" * 200,
            tenant_id="t1",
            created_by="user1",
        )

        versions = [
            VersionHistory.create_snapshot(item),
        ]

        info_list = VersionHistory.get_version_info_list(versions)

        assert len(info_list[0].content_preview) == 100
        assert info_list[0].content_preview == "A" * 100

    def test_can_rollback_to_valid_version(self):
        """Test that can rollback to valid previous version."""
        assert VersionHistory.can_rollback_to(current_version=5, target_version=3)

    def test_cannot_rollback_to_current(self):
        """Test that cannot rollback to current version."""
        assert not VersionHistory.can_rollback_to(current_version=5, target_version=5)

    def test_cannot_rollback_to_future(self):
        """Test that cannot rollback to future version."""
        assert not VersionHistory.can_rollback_to(current_version=5, target_version=10)

    def test_cannot_rollback_to_version_zero(self):
        """Test that cannot rollback to version 0."""
        assert not VersionHistory.can_rollback_to(current_version=5, target_version=0)

    def test_can_rollback_to_version_one(self):
        """Test that can rollback to version 1."""
        assert VersionHistory.can_rollback_to(current_version=2, target_version=1)

    def test_version_diff_summary_no_changes(self):
        """Test diff summary when content unchanged."""
        item = KnowledgeItem.create(
            title="Test",
            content="Content",
            tenant_id="t1",
            created_by="user1",
        )

        v1 = VersionHistory.create_snapshot(item)
        v2 = VersionHistory.create_snapshot(item)

        diff = VersionHistory.get_version_diff_summary(v1, v2)

        assert not diff["title_changed"]
        assert not diff["content_changed"]

    def test_version_diff_summary_title_changed(self):
        """Test diff summary when title changed."""
        item1 = KnowledgeItem.create(
            title="Old Title",
            content="Content",
            tenant_id="t1",
            created_by="user1",
        )

        v1 = VersionHistory.create_snapshot(item1)

        item2 = KnowledgeItem.create(
            title="New Title",
            content="Content",
            tenant_id="t1",
            created_by="user1",
        )

        v2 = VersionHistory.create_snapshot(item2)

        diff = VersionHistory.get_version_diff_summary(v1, v2)

        assert diff["title_changed"]
        assert not diff["content_changed"]

    def test_version_diff_summary_content_changed(self):
        """Test diff summary when content changed."""
        item1 = KnowledgeItem.create(
            title="Title",
            content="Old content",
            tenant_id="t1",
            created_by="user1",
        )

        v1 = VersionHistory.create_snapshot(item1)

        item2 = KnowledgeItem.create(
            title="Title",
            content="New content",
            tenant_id="t1",
            created_by="user1",
        )

        v2 = VersionHistory.create_snapshot(item2)

        diff = VersionHistory.get_version_diff_summary(v1, v2)

        assert not diff["title_changed"]
        assert diff["content_changed"]

    def test_version_diff_summary_both_changed(self):
        """Test diff summary when both changed."""
        item1 = KnowledgeItem.create(
            title="Old Title",
            content="Old content",
            tenant_id="t1",
            created_by="user1",
        )

        v1 = VersionHistory.create_snapshot(item1)

        item2 = KnowledgeItem.create(
            title="New Title",
            content="New content",
            tenant_id="t1",
            created_by="user1",
        )

        v2 = VersionHistory.create_snapshot(item2)

        diff = VersionHistory.get_version_diff_summary(v1, v2)

        assert diff["title_changed"]
        assert diff["content_changed"]

    def test_version_diff_summary_content_length(self):
        """Test diff summary includes content length."""
        item1 = KnowledgeItem.create(
            title="Title",
            content="A" * 50,
            tenant_id="t1",
            created_by="user1",
        )

        v1 = VersionHistory.create_snapshot(item1)

        item2 = KnowledgeItem.create(
            title="Title",
            content="B" * 100,
            tenant_id="t1",
            created_by="user1",
        )

        v2 = VersionHistory.create_snapshot(item2)

        diff = VersionHistory.get_version_diff_summary(v1, v2)

        assert diff["content_length_old"] == 50
        assert diff["content_length_new"] == 100

    def test_get_version_timeline_single(self):
        """Test timeline generation with single version."""
        item = KnowledgeItem.create(
            title="Test",
            content="Content",
            tenant_id="t1",
            created_by="user1",
        )

        versions = [
            VersionHistory.create_snapshot(item),
        ]

        timeline = VersionHistory.get_version_timeline(versions)

        assert len(timeline) == 1
        assert timeline[0]["version"] == versions[0].version_number
        assert timeline[0]["author"] == "user1"
        assert timeline[0]["title"] == "Test"

    def test_get_version_timeline_multiple(self):
        """Test timeline generation with multiple versions."""
        item1 = KnowledgeItem.create(
            title="Title 1",
            content="Content 1",
            tenant_id="t1",
            created_by="user1",
        )

        item2 = KnowledgeItem.create(
            title="Title 2",
            content="Content 2",
            tenant_id="t1",
            created_by="user2",
        )

        versions = [
            VersionHistory.create_snapshot(item1, change_message="Initial"),
            VersionHistory.create_snapshot(item2, change_message="Update"),
        ]

        timeline = VersionHistory.get_version_timeline(versions)

        assert len(timeline) == 2
        assert timeline[0]["message"] == "Initial"
        assert timeline[1]["message"] == "Update"

    def test_version_timeline_timestamp_format(self):
        """Test that timeline timestamps are ISO format."""
        item = KnowledgeItem.create(
            title="Test",
            content="Content",
            tenant_id="t1",
            created_by="user1",
        )

        versions = [
            VersionHistory.create_snapshot(item),
        ]

        timeline = VersionHistory.get_version_timeline(versions)

        # Should be ISO format string
        timestamp = timeline[0]["timestamp"]
        assert "T" in timestamp
        # Should be parseable
        parsed = datetime.fromisoformat(timestamp)
        assert parsed is not None

    def test_version_info_to_dict(self):
        """Test VersionInfo serialization."""
        info = VersionInfo(
            version_number=1,
            created_at=datetime.now(timezone.utc),
            created_by="user1",
            change_message="Initial",
            content_preview="Content...",
        )

        data = info.to_dict()

        assert data["version_number"] == 1
        assert data["created_by"] == "user1"
        assert data["change_message"] == "Initial"
        assert "T" in data["created_at"]  # ISO format

    def test_version_info_from_dict(self):
        """Test VersionInfo deserialization."""
        now = datetime.now(timezone.utc)
        data = {
            "version_number": 1,
            "created_at": now.isoformat(),
            "created_by": "user1",
            "change_message": "Initial",
            "content_preview": "Content...",
        }

        info = VersionInfo.from_dict(data)

        assert info.version_number == 1
        assert info.created_by == "user1"
        assert info.change_message == "Initial"

    def test_version_info_from_dict_with_datetime(self):
        """Test VersionInfo deserialization with datetime object."""
        now = datetime.now(timezone.utc)
        data = {
            "version_number": 1,
            "created_at": now,
            "created_by": "user1",
            "change_message": "Initial",
            "content_preview": "Content...",
        }

        info = VersionInfo.from_dict(data)

        assert info.version_number == 1
        assert isinstance(info.created_at, datetime)

    def test_version_create_from_item(self):
        """Test Version.create_from_item factory method."""
        item = KnowledgeItem.create(
            title="Test",
            content="Content",
            tenant_id="t1",
            created_by="user1",
        )

        version = Version.create_from_item(item, change_message="Initial commit")

        assert version.item_id == item.item_id
        assert version.content == item.content
        assert version.title == item.title
        assert version.created_by == item.created_by
        assert version.change_message == "Initial commit"

    def test_version_number_matches_item_version(self):
        """Test that version number matches item version."""
        item = KnowledgeItem.create(
            title="Test",
            content="Content",
            tenant_id="t1",
            created_by="user1",
        )

        item.increment_version()
        item.increment_version()

        version = Version.create_from_item(item)

        assert version.version_number == item.version

    def test_empty_version_list(self):
        """Test handling empty version list."""
        versions = []

        timeline = VersionHistory.get_version_timeline(versions)

        assert timeline == []

    def test_version_info_empty_preview(self):
        """Test version info with empty content."""
        item = KnowledgeItem.create(
            title="Test",
            content="",
            tenant_id="t1",
            created_by="user1",
        )

        versions = [
            VersionHistory.create_snapshot(item),
        ]

        info_list = VersionHistory.get_version_info_list(versions)

        assert info_list[0].content_preview == ""

    def test_version_info_short_content_preview(self):
        """Test version info with content shorter than preview."""
        item = KnowledgeItem.create(
            title="Test",
            content="Short",
            tenant_id="t1",
            created_by="user1",
        )

        versions = [
            VersionHistory.create_snapshot(item),
        ]

        info_list = VersionHistory.get_version_info_list(versions)

        assert info_list[0].content_preview == "Short"

    def test_version_diff_empty_content(self):
        """Test diff with empty content."""
        item1 = KnowledgeItem.create(
            title="Title",
            content="",
            tenant_id="t1",
            created_by="user1",
        )

        v1 = VersionHistory.create_snapshot(item1)

        item2 = KnowledgeItem.create(
            title="Title",
            content="",
            tenant_id="t1",
            created_by="user1",
        )

        v2 = VersionHistory.create_snapshot(item2)

        diff = VersionHistory.get_version_diff_summary(v1, v2)

        assert diff["content_length_old"] == 0
        assert diff["content_length_new"] == 0
        assert not diff["content_changed"]
