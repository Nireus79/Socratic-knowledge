"""
Data models for knowledge management.
"""

from datetime import datetime
from typing import Any, Dict, List

from pydantic import BaseModel, Field


class AccessControl(BaseModel):
    """Role-based access control for knowledge items."""

    read: List[str] = Field(default_factory=list, description="Roles with read access")
    write: List[str] = Field(default_factory=list, description="Roles with write access")
    delete: List[str] = Field(default_factory=list, description="Roles with delete access")
    owner: str = Field(..., description="Owner of the resource")


class KnowledgeItem(BaseModel):
    """Represents a knowledge item in the system."""

    id: str = Field(..., description="Unique identifier")
    tenant_id: str = Field(..., description="Tenant ID for multi-tenancy")
    title: str = Field(..., description="Knowledge item title")
    content: str = Field(..., description="Knowledge item content")
    category: str = Field(default="general", description="Category/tag")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Custom metadata")
    access_control: AccessControl = Field(..., description="Access control rules")
    version: int = Field(default=1, description="Current version")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Update timestamp")
    is_archived: bool = Field(default=False, description="Whether item is archived")


class KnowledgeIndex(BaseModel):
    """Index entry for knowledge items."""

    item_id: str = Field(..., description="Knowledge item ID")
    tenant_id: str = Field(..., description="Tenant ID")
    title: str = Field(..., description="Item title")
    category: str = Field(..., description="Item category")
    keywords: List[str] = Field(default_factory=list, description="Searchable keywords")
    created_at: datetime = Field(..., description="Creation timestamp")
