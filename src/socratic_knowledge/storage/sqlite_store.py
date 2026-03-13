"""SQLite storage backend for production use."""

import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..core.collection import Collection
from ..core.knowledge_item import KnowledgeItem
from ..core.tenant import Tenant
from ..core.version import Version
from .base import BaseKnowledgeStore


class SQLiteKnowledgeStore(BaseKnowledgeStore):
    """
    SQLite-based storage for production use.

    Features:
    - Single-file database
    - ACID transactions
    - Full-text search via FTS5
    - Efficient for single-server deployments
    """

    def __init__(self, db_path: str = "knowledge.db"):
        """
        Initialize SQLite store.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self._init_database()

    def _init_database(self) -> None:
        """Create tables if they don't exist."""
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute("PRAGMA foreign_keys = ON")

            # Tenants table
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS tenants (
                    tenant_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    domain TEXT,
                    max_storage_mb INTEGER DEFAULT 1000,
                    max_users INTEGER DEFAULT 100,
                    features TEXT,
                    is_active INTEGER DEFAULT 1,
                    created_at TEXT NOT NULL,
                    metadata TEXT
                )
                """
            )

            # Collections table
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS collections (
                    collection_id TEXT PRIMARY KEY,
                    tenant_id TEXT NOT NULL,
                    parent_id TEXT,
                    name TEXT NOT NULL,
                    description TEXT,
                    owner_id TEXT NOT NULL,
                    permissions TEXT,
                    inherit_permissions INTEGER DEFAULT 1,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    created_by TEXT NOT NULL,
                    metadata TEXT,
                    FOREIGN KEY (tenant_id) REFERENCES tenants(tenant_id),
                    FOREIGN KEY (parent_id) REFERENCES collections(collection_id)
                )
                """
            )

            # Knowledge items table
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS knowledge_items (
                    item_id TEXT PRIMARY KEY,
                    tenant_id TEXT NOT NULL,
                    collection_id TEXT,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    content_type TEXT DEFAULT 'text',
                    version INTEGER DEFAULT 1,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    created_by TEXT NOT NULL,
                    updated_by TEXT NOT NULL,
                    owner_id TEXT NOT NULL,
                    permissions TEXT,
                    tags TEXT,
                    metadata TEXT,
                    is_deleted INTEGER DEFAULT 0,
                    deleted_at TEXT,
                    FOREIGN KEY (tenant_id) REFERENCES tenants(tenant_id),
                    FOREIGN KEY (collection_id) REFERENCES collections(collection_id)
                )
                """
            )

            # Versions table
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS versions (
                    version_id TEXT PRIMARY KEY,
                    item_id TEXT NOT NULL,
                    version_number INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    title TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    created_by TEXT NOT NULL,
                    change_message TEXT,
                    diff_from_previous TEXT,
                    FOREIGN KEY (item_id) REFERENCES knowledge_items(item_id)
                )
                """
            )

            # Create indexes for performance
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_items_tenant ON knowledge_items(tenant_id)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_items_collection ON knowledge_items(collection_id)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_items_deleted ON knowledge_items(is_deleted)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_collections_tenant ON collections(tenant_id)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_collections_parent ON collections(parent_id)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_versions_item ON versions(item_id)"
            )

            # Full-text search index using FTS5
            try:
                conn.execute(
                    """
                    CREATE VIRTUAL TABLE IF NOT EXISTS knowledge_items_fts USING fts5(
                        title, content, tags,
                        content=knowledge_items,
                        content_rowid=rowid
                    )
                    """
                )
            except sqlite3.OperationalError:
                # FTS5 might not be available in some SQLite builds
                pass

            conn.commit()

    # ==================== Knowledge Item operations ====================

    def create_item(self, item: KnowledgeItem) -> KnowledgeItem:
        """Create knowledge item with tenant isolation."""
        with sqlite3.connect(str(self.db_path)) as conn:
            data = item.to_dict()
            conn.execute(
                """
                INSERT INTO knowledge_items VALUES (
                    :item_id, :tenant_id, :collection_id, :title, :content,
                    :content_type, :version, :created_at, :updated_at,
                    :created_by, :updated_by, :owner_id,
                    :permissions, :tags, :metadata, :is_deleted, :deleted_at
                )
                """,
                {
                    **data,
                    "permissions": json.dumps(data["permissions"]),
                    "tags": json.dumps(data["tags"]),
                    "metadata": json.dumps(data["metadata"]),
                },
            )

            # Add to FTS index
            try:
                conn.execute(
                    """
                    INSERT INTO knowledge_items_fts(rowid, title, content, tags)
                    SELECT rowid, title, content, tags FROM knowledge_items WHERE item_id = ?
                    """,
                    (item.item_id,),
                )
            except sqlite3.OperationalError:
                # FTS5 might not be available
                pass

            conn.commit()

        return item

    def get_item(
        self, item_id: str, tenant_id: str
    ) -> Optional[KnowledgeItem]:
        """Get item with tenant isolation (security)."""
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                """
                SELECT * FROM knowledge_items
                WHERE item_id = ? AND tenant_id = ? AND is_deleted = 0
                """,
                (item_id, tenant_id),
            )
            row = cursor.fetchone()
            if not row:
                return None

            data = dict(row)
            data["permissions"] = json.loads(data["permissions"])
            data["tags"] = json.loads(data["tags"])
            data["metadata"] = json.loads(data["metadata"])
            return KnowledgeItem.from_dict(data)

    def update_item(self, item: KnowledgeItem) -> KnowledgeItem:
        """Update existing item."""
        with sqlite3.connect(str(self.db_path)) as conn:
            data = item.to_dict()
            conn.execute(
                """
                UPDATE knowledge_items SET
                    title = :title,
                    content = :content,
                    version = :version,
                    updated_at = :updated_at,
                    updated_by = :updated_by,
                    permissions = :permissions,
                    tags = :tags,
                    metadata = :metadata,
                    is_deleted = :is_deleted,
                    deleted_at = :deleted_at
                WHERE item_id = :item_id
                """,
                {
                    **data,
                    "permissions": json.dumps(data["permissions"]),
                    "tags": json.dumps(data["tags"]),
                    "metadata": json.dumps(data["metadata"]),
                },
            )

            # Update FTS index
            try:
                conn.execute(
                    """
                    UPDATE knowledge_items_fts SET title = ?, content = ?, tags = ?
                    WHERE rowid = (SELECT rowid FROM knowledge_items WHERE item_id = ?)
                    """,
                    (item.title, item.content, json.dumps(item.tags), item.item_id),
                )
            except sqlite3.OperationalError:
                pass

            conn.commit()

        return item

    def delete_item(
        self, item_id: str, tenant_id: str, soft: bool = True
    ) -> bool:
        """Delete item (soft delete by default)."""
        with sqlite3.connect(str(self.db_path)) as conn:
            if soft:
                conn.execute(
                    """
                    UPDATE knowledge_items SET is_deleted = 1, deleted_at = datetime('now')
                    WHERE item_id = ? AND tenant_id = ?
                    """,
                    (item_id, tenant_id),
                )
            else:
                conn.execute(
                    "DELETE FROM knowledge_items WHERE item_id = ? AND tenant_id = ?",
                    (item_id, tenant_id),
                )

            conn.commit()

        return True

    def list_items(
        self,
        tenant_id: str,
        collection_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[KnowledgeItem]:
        """List items with pagination (tenant-scoped)."""
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.row_factory = sqlite3.Row

            if collection_id:
                cursor = conn.execute(
                    """
                    SELECT * FROM knowledge_items
                    WHERE tenant_id = ? AND collection_id = ? AND is_deleted = 0
                    ORDER BY updated_at DESC LIMIT ? OFFSET ?
                    """,
                    (tenant_id, collection_id, limit, offset),
                )
            else:
                cursor = conn.execute(
                    """
                    SELECT * FROM knowledge_items
                    WHERE tenant_id = ? AND is_deleted = 0
                    ORDER BY updated_at DESC LIMIT ? OFFSET ?
                    """,
                    (tenant_id, limit, offset),
                )

            items = []
            for row in cursor:
                data = dict(row)
                data["permissions"] = json.loads(data["permissions"])
                data["tags"] = json.loads(data["tags"])
                data["metadata"] = json.loads(data["metadata"])
                items.append(KnowledgeItem.from_dict(data))

            return items

    # ==================== Collection operations ====================

    def create_collection(self, collection: Collection) -> Collection:
        """Create collection."""
        with sqlite3.connect(str(self.db_path)) as conn:
            data = collection.to_dict()
            conn.execute(
                """
                INSERT INTO collections VALUES (
                    :collection_id, :tenant_id, :parent_id, :name, :description,
                    :owner_id, :permissions, :inherit_permissions,
                    :created_at, :updated_at, :created_by, :metadata
                )
                """,
                {
                    **data,
                    "permissions": json.dumps(data["permissions"]),
                    "metadata": json.dumps(data["metadata"]),
                },
            )
            conn.commit()

        return collection

    def get_collection(self, collection_id: str) -> Optional[Collection]:
        """Get collection by ID."""
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM collections WHERE collection_id = ?",
                (collection_id,),
            )
            row = cursor.fetchone()
            if not row:
                return None

            data = dict(row)
            data["permissions"] = json.loads(data["permissions"])
            data["metadata"] = json.loads(data["metadata"])
            return Collection.from_dict(data)

    def list_collections(
        self,
        tenant_id: str,
        parent_id: Optional[str] = None,
    ) -> List[Collection]:
        """List collections (hierarchical)."""
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.row_factory = sqlite3.Row

            if parent_id:
                cursor = conn.execute(
                    """
                    SELECT * FROM collections
                    WHERE tenant_id = ? AND parent_id = ?
                    ORDER BY name
                    """,
                    (tenant_id, parent_id),
                )
            else:
                cursor = conn.execute(
                    """
                    SELECT * FROM collections
                    WHERE tenant_id = ? AND parent_id IS NULL
                    ORDER BY name
                    """,
                    (tenant_id,),
                )

            collections = []
            for row in cursor:
                data = dict(row)
                data["permissions"] = json.loads(data["permissions"])
                data["metadata"] = json.loads(data["metadata"])
                collections.append(Collection.from_dict(data))

            return collections

    def update_collection(self, collection: Collection) -> Collection:
        """Update collection."""
        with sqlite3.connect(str(self.db_path)) as conn:
            data = collection.to_dict()
            conn.execute(
                """
                UPDATE collections SET
                    name = :name,
                    description = :description,
                    permissions = :permissions,
                    inherit_permissions = :inherit_permissions,
                    updated_at = :updated_at,
                    metadata = :metadata
                WHERE collection_id = :collection_id
                """,
                {
                    **data,
                    "permissions": json.dumps(data["permissions"]),
                    "metadata": json.dumps(data["metadata"]),
                },
            )
            conn.commit()

        return collection

    # ==================== Tenant operations ====================

    def create_tenant(self, tenant: Tenant) -> Tenant:
        """Create tenant."""
        with sqlite3.connect(str(self.db_path)) as conn:
            data = tenant.to_dict()
            conn.execute(
                """
                INSERT INTO tenants VALUES (
                    :tenant_id, :name, :domain, :max_storage_mb, :max_users,
                    :features, :is_active, :created_at, :metadata
                )
                """,
                {
                    **data,
                    "features": json.dumps(data["features"]),
                    "metadata": json.dumps(data["metadata"]),
                },
            )
            conn.commit()

        return tenant

    def get_tenant(self, tenant_id: str) -> Optional[Tenant]:
        """Get tenant by ID."""
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM tenants WHERE tenant_id = ?",
                (tenant_id,),
            )
            row = cursor.fetchone()
            if not row:
                return None

            data = dict(row)
            data["features"] = json.loads(data["features"])
            data["metadata"] = json.loads(data["metadata"])
            return Tenant.from_dict(data)

    def update_tenant(self, tenant: Tenant) -> Tenant:
        """Update tenant."""
        with sqlite3.connect(str(self.db_path)) as conn:
            data = tenant.to_dict()
            conn.execute(
                """
                UPDATE tenants SET
                    name = :name,
                    domain = :domain,
                    max_storage_mb = :max_storage_mb,
                    max_users = :max_users,
                    features = :features,
                    is_active = :is_active,
                    metadata = :metadata
                WHERE tenant_id = :tenant_id
                """,
                {
                    **data,
                    "features": json.dumps(data["features"]),
                    "metadata": json.dumps(data["metadata"]),
                },
            )
            conn.commit()

        return tenant

    # ==================== Version operations ====================

    def create_version(self, version: Version) -> Version:
        """Create version snapshot."""
        with sqlite3.connect(str(self.db_path)) as conn:
            data = version.to_dict()
            conn.execute(
                """
                INSERT INTO versions VALUES (
                    :version_id, :item_id, :version_number, :content, :title,
                    :created_at, :created_by, :change_message, :diff_from_previous
                )
                """,
                {
                    **data,
                    "diff_from_previous": json.dumps(data["diff_from_previous"]),
                },
            )
            conn.commit()

        return version

    def get_version(self, version_id: str) -> Optional[Version]:
        """Get specific version."""
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM versions WHERE version_id = ?",
                (version_id,),
            )
            row = cursor.fetchone()
            if not row:
                return None

            data = dict(row)
            if data["diff_from_previous"]:
                data["diff_from_previous"] = json.loads(data["diff_from_previous"])
            return Version.from_dict(data)

    def list_versions(
        self,
        item_id: str,
        limit: int = 10,
    ) -> List[Version]:
        """List version history for item."""
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                """
                SELECT * FROM versions
                WHERE item_id = ?
                ORDER BY version_number DESC
                LIMIT ?
                """,
                (item_id, limit),
            )

            versions = []
            for row in cursor:
                data = dict(row)
                if data["diff_from_previous"]:
                    data["diff_from_previous"] = json.loads(data["diff_from_previous"])
                versions.append(Version.from_dict(data))

            return versions

    # ==================== Search operations ====================

    def search(
        self,
        tenant_id: str,
        query: str,
        limit: int = 10,
    ) -> List[KnowledgeItem]:
        """Full-text search using FTS5."""
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.row_factory = sqlite3.Row

            try:
                # Try FTS5 search
                cursor = conn.execute(
                    """
                    SELECT ki.* FROM knowledge_items ki
                    JOIN knowledge_items_fts fts ON ki.rowid = fts.rowid
                    WHERE fts MATCH ? AND ki.tenant_id = ? AND ki.is_deleted = 0
                    ORDER BY rank
                    LIMIT ?
                    """,
                    (query, tenant_id, limit),
                )
            except sqlite3.OperationalError:
                # Fallback to LIKE search if FTS5 unavailable
                like_query = f"%{query}%"
                cursor = conn.execute(
                    """
                    SELECT * FROM knowledge_items
                    WHERE tenant_id = ? AND is_deleted = 0
                    AND (title LIKE ? OR content LIKE ? OR tags LIKE ?)
                    ORDER BY updated_at DESC
                    LIMIT ?
                    """,
                    (tenant_id, like_query, like_query, like_query, limit),
                )

            items = []
            for row in cursor:
                data = dict(row)
                data["permissions"] = json.loads(data["permissions"])
                data["tags"] = json.loads(data["tags"])
                data["metadata"] = json.loads(data["metadata"])
                items.append(KnowledgeItem.from_dict(data))

            return items
