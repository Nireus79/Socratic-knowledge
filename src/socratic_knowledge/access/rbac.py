"""Role-Based Access Control (RBAC) implementation."""

from enum import Enum
from typing import Set


class Permission(Enum):
    """Fine-grained permissions."""

    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    SHARE = "share"
    ADMIN = "admin"


class Role(Enum):
    """Predefined roles with permission sets."""

    VIEWER = "viewer"
    EDITOR = "editor"
    ADMIN = "admin"
    OWNER = "owner"


ROLE_PERMISSIONS: dict[Role, Set[Permission]] = {
    Role.VIEWER: {Permission.READ},
    Role.EDITOR: {Permission.READ, Permission.WRITE},
    Role.ADMIN: {Permission.READ, Permission.WRITE, Permission.DELETE, Permission.SHARE},
    Role.OWNER: {
        Permission.READ,
        Permission.WRITE,
        Permission.DELETE,
        Permission.SHARE,
        Permission.ADMIN,
    },
}
