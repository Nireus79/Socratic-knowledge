"""Tests for SQLite storage backend."""

import tempfile
from pathlib import Path

import pytest

from socratic_knowledge.core.knowledge_item import KnowledgeItem
from socratic_knowledge.core.collection import Collection
from socratic_knowledge.core.tenant import Tenant
from socratic_knowledge.storage.sqlite_store import SQLiteKnowledgeStore


@pytest.fixture
def temp_db():
    """Create a temporary database."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        yield str(db_path)


@pytest.fixture
def store(temp_db):
    """Create a store with temporary database."""
    return SQLiteKnowledgeStore(db_path=temp_db)


@pytest.fixture
def tenant(store):
    """Create a test tenant."""
    t = Tenant.create(name="Test Tenant")
    return store.create_tenant(t)


class TestSQLiteKnowledgeStore:
    """Test SQLite storage backend."""

    # ==================== Tenant tests ====================

    def test_create_tenant(self, store):
        """Test creating a tenant."""
        tenant = Tenant.create(name="Test Corp")
        created = store.create_tenant(tenant)

        assert created.tenant_id == tenant.tenant_id
        assert created.name == "Test Corp"

    def test_get_tenant(self, store, tenant):
        """Test retrieving a tenant."""
        retrieved = store.get_tenant(tenant.tenant_id)

        assert retrieved is not None
        assert retrieved.name == "Test Tenant"

    def test_get_nonexistent_tenant(self, store):
        """Test retrieving nonexistent tenant."""
        result = store.get_tenant("nonexistent")
        assert result is None

    # ==================== Collection tests ====================

    def test_create_collection(self, store, tenant):
        """Test creating a collection."""
        coll = Collection.create(
            name="Test Collection",
            tenant_id=tenant.tenant_id,
            created_by="user1",
        )
        created = store.create_collection(coll)

        assert created.name == "Test Collection"
        assert created.tenant_id == tenant.tenant_id

    def test_get_collection(self, store, tenant):
        """Test retrieving a collection."""
        coll = Collection.create(
            name="Test",
            tenant_id=tenant.tenant_id,
            created_by="user1",
        )
        store.create_collection(coll)
        retrieved = store.get_collection(coll.collection_id)

        assert retrieved is not None
        assert retrieved.name == "Test"

    def test_list_collections(self, store, tenant):
        """Test listing collections."""
        coll1 = Collection.create("Root", tenant.tenant_id, "user1")
        coll2 = Collection.create("Projects", tenant.tenant_id, "user1")
        store.create_collection(coll1)
        store.create_collection(coll2)

        collections = store.list_collections(tenant.tenant_id)

        assert len(collections) == 2
        assert any(c.name == "Root" for c in collections)

    def test_hierarchical_collections(self, store, tenant):
        """Test hierarchical collection structure."""
        root = Collection.create("Root", tenant.tenant_id, "user1")
        root = store.create_collection(root)

        sub = Collection.create(
            "Projects",
            tenant.tenant_id,
            "user1",
            parent_id=root.collection_id,
        )
        store.create_collection(sub)

        # List root-level collections
        root_colls = store.list_collections(tenant.tenant_id, parent_id=None)
        assert len(root_colls) == 1

        # List sub-collections
        sub_colls = store.list_collections(
            tenant.tenant_id,
            parent_id=root.collection_id,
        )
        assert len(sub_colls) == 1

    # ==================== Knowledge Item tests ====================

    def test_create_item(self, store, tenant):
        """Test creating a knowledge item."""
        item = KnowledgeItem.create(
            title="Test Doc",
            content="Test content",
            tenant_id=tenant.tenant_id,
            created_by="user1",
        )
        created = store.create_item(item)

        assert created.title == "Test Doc"
        assert created.content == "Test content"

    def test_get_item(self, store, tenant):
        """Test retrieving an item."""
        item = KnowledgeItem.create(
            title="Test",
            content="Content",
            tenant_id=tenant.tenant_id,
            created_by="user1",
        )
        store.create_item(item)
        retrieved = store.get_item(item.item_id, tenant.tenant_id)

        assert retrieved is not None
        assert retrieved.title == "Test"

    def test_get_item_different_tenant(self, store, tenant):
        """Test tenant isolation in get_item."""
        item = KnowledgeItem.create(
            title="Test",
            content="Content",
            tenant_id=tenant.tenant_id,
            created_by="user1",
        )
        store.create_item(item)

        # Try to get with different tenant
        retrieved = store.get_item(item.item_id, "other_tenant")
        assert retrieved is None

    def test_update_item(self, store, tenant):
        """Test updating an item."""
        item = KnowledgeItem.create(
            title="Original",
            content="Content",
            tenant_id=tenant.tenant_id,
            created_by="user1",
        )
        store.create_item(item)

        item.title = "Updated"
        item.content = "New content"
        store.update_item(item)

        retrieved = store.get_item(item.item_id, tenant.tenant_id)
        assert retrieved.title == "Updated"
        assert retrieved.content == "New content"

    def test_delete_item_soft(self, store, tenant):
        """Test soft delete."""
        item = KnowledgeItem.create(
            title="Test",
            content="Content",
            tenant_id=tenant.tenant_id,
            created_by="user1",
        )
        store.create_item(item)
        store.delete_item(item.item_id, tenant.tenant_id, soft=True)

        # Should not be retrievable
        retrieved = store.get_item(item.item_id, tenant.tenant_id)
        assert retrieved is None

    def test_list_items(self, store, tenant):
        """Test listing items."""
        item1 = KnowledgeItem.create("Item 1", "Content", tenant.tenant_id, "user1")
        item2 = KnowledgeItem.create("Item 2", "Content", tenant.tenant_id, "user1")
        store.create_item(item1)
        store.create_item(item2)

        items = store.list_items(tenant.tenant_id)

        assert len(items) >= 2

    def test_list_items_with_limit(self, store, tenant):
        """Test listing items with pagination."""
        for i in range(5):
            item = KnowledgeItem.create(
                f"Item {i}",
                "Content",
                tenant.tenant_id,
                "user1",
            )
            store.create_item(item)

        items = store.list_items(tenant.tenant_id, limit=2)
        assert len(items) == 2

    def test_search_items(self, store, tenant):
        """Test searching items."""
        item = KnowledgeItem.create(
            title="Python Tutorial",
            content="Learn Python programming",
            tenant_id=tenant.tenant_id,
            created_by="user1",
        )
        store.create_item(item)

        # Search
        results = store.search(tenant.tenant_id, "Python")
        assert len(results) > 0
        assert any(r.title == "Python Tutorial" for r in results)

    def test_search_tenant_isolation(self, store):
        """Test search respects tenant isolation."""
        t1 = Tenant.create("Tenant 1")
        t2 = Tenant.create("Tenant 2")
        store.create_tenant(t1)
        store.create_tenant(t2)

        item1 = KnowledgeItem.create(
            "Python",
            "Content",
            t1.tenant_id,
            "user1",
        )
        store.create_item(item1)

        # Search in tenant 2 should find nothing
        results = store.search(t2.tenant_id, "Python")
        assert len(results) == 0

    # ==================== Version tests ====================

    def test_create_version(self, store, tenant):
        """Test creating a version."""
        from socratic_knowledge.core.version import Version

        item = KnowledgeItem.create(
            "Test",
            "Content",
            tenant.tenant_id,
            "user1",
        )
        version = Version.create_from_item(item, change_message="Initial")
        created = store.create_version(version)

        assert created.title == "Test"
        assert created.version_number == 1

    def test_list_versions(self, store, tenant):
        """Test listing versions."""
        from socratic_knowledge.core.version import Version

        item = KnowledgeItem.create(
            "Test",
            "Content",
            tenant.tenant_id,
            "user1",
        )
        store.create_item(item)

        v1 = Version.create_from_item(item, change_message="v1")
        v2 = Version.create_from_item(item, change_message="v2")
        store.create_version(v1)
        store.create_version(v2)

        versions = store.list_versions(item.item_id)
        assert len(versions) >= 2
