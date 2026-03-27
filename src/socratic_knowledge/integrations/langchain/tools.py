"""LangChain tool integrations for SocraticKnowledge."""

from typing import Any, Optional

try:
    from langchain.tools import tool

    HAS_LANGCHAIN = True
except ImportError:
    HAS_LANGCHAIN = False
    tool = None  # type: ignore

from ...manager import KnowledgeManager


class SocraticKnowledgeTools:
    """
    LangChain tools for Socratic Knowledge management.

    Provides LangChain-compatible tools for use in agents and chains.
    """

    def __init__(
        self,
        knowledge_manager: Optional[KnowledgeManager] = None,
        **km_kwargs: Any,
    ):
        """
        Initialize tools.

        Args:
            knowledge_manager: KnowledgeManager instance
            **km_kwargs: KnowledgeManager initialization args
        """
        if knowledge_manager:
            self.km = knowledge_manager
        else:
            self.km = KnowledgeManager(**km_kwargs)

        # Create tool instances
        self._setup_tools()

    def _setup_tools(self) -> None:
        """Set up all available tools."""
        # These will be dynamically created by the get_tools() method
        pass

    def get_tools(self) -> list:
        """
        Get all available tools for LangChain.

        Returns:
            list: LangChain tools
        """
        return [
            self._search_knowledge_tool(),
            self._semantic_search_tool(),
            self._get_item_tool(),
            self._check_permissions_tool(),
            self._get_audit_log_tool(),
        ]

    def _search_knowledge_tool(self):
        """Create knowledge search tool."""

        @tool
        def search_knowledge(
            tenant_id: str,
            query: str,
            top_k: int = 10,
        ) -> str:
            """
            Search knowledge base using hybrid search.

            Args:
                tenant_id: Tenant ID
                query: Search query
                top_k: Maximum results

            Returns:
                str: Formatted search results
            """
            results = self.km.hybrid_search(tenant_id, query, top_k=top_k)

            if not results:
                return f"No results found for query: {query}"

            output = f"Found {len(results)} results:\n\n"
            for i, item in enumerate(results, 1):
                output += (
                    f"{i}. **{item.title}** (ID: {item.item_id})\n"
                    f"   Content: {item.content[:200]}...\n"
                )

            return output

        return search_knowledge

    def _semantic_search_tool(self):
        """Create semantic search tool."""

        @tool
        def semantic_search(
            tenant_id: str,
            query: str,
            top_k: int = 5,
        ) -> str:
            """
            Semantic search using embeddings.

            Args:
                tenant_id: Tenant ID
                query: Search query
                top_k: Maximum results

            Returns:
                str: Formatted results
            """
            results = self.km.semantic_search(tenant_id, query, top_k=top_k)

            if not results:
                return f"No semantically similar results found for: {query}"

            output = f"Found {len(results)} semantically similar items:\n\n"
            for i, item in enumerate(results, 1):
                output += (
                    f"{i}. **{item.title}** (ID: {item.item_id})\n"
                    f"   Tags: {', '.join(item.tags or [])}\n"
                )

            return output

        return semantic_search

    def _get_item_tool(self):
        """Create get item tool."""

        @tool
        def get_knowledge_item(
            tenant_id: str,
            item_id: str,
        ) -> str:
            """
            Get a specific knowledge item.

            Args:
                tenant_id: Tenant ID
                item_id: Item ID

            Returns:
                str: Item details or error message
            """
            item = self.km.get_item(item_id, tenant_id)

            if not item:
                return f"Item {item_id} not found"

            assert item.created_at is not None, "Item.created_at must be set"
            return (
                f"**{item.title}**\n\n"
                f"Content: {item.content}\n\n"
                f"Version: {item.version}\n"
                f"Created: {item.created_at.isoformat()}\n"
                f"Tags: {', '.join(item.tags or [])}"
            )

        return get_knowledge_item

    def _check_permissions_tool(self):
        """Create permission checking tool."""

        @tool
        def check_permissions(
            tenant_id: str,
            user_id: str,
            item_id: str,
        ) -> str:
            """
            Check user permissions on item.

            Args:
                tenant_id: Tenant ID
                user_id: User ID
                item_id: Item ID

            Returns:
                str: Permission summary
            """
            can_read = self.km.can_user_read(user_id, item_id, tenant_id)
            can_edit = self.km.can_user_edit(user_id, item_id, tenant_id)
            can_delete = self.km.can_user_delete(user_id, item_id, tenant_id)

            return (
                f"Permissions for user {user_id} on item {item_id}:\n"
                f"  Read: {can_read}\n"
                f"  Edit: {can_edit}\n"
                f"  Delete: {can_delete}"
            )

        return check_permissions

    def _get_audit_log_tool(self):
        """Create audit log tool."""

        @tool
        def get_audit_log(
            tenant_id: str,
            limit: int = 10,
        ) -> str:
            """
            Get recent audit log for tenant.

            Args:
                tenant_id: Tenant ID
                limit: Maximum events

            Returns:
                str: Formatted audit log
            """
            events = self.km.get_audit_log(tenant_id, limit=limit)

            if not events:
                return "No audit events found"

            output = f"Recent {len(events)} events:\n\n"
            for event in events:
                output += (
                    f"- {event.timestamp.isoformat()}: "
                    f"{event.user_id} {event.action} {event.resource_type} "
                    f"{event.resource_id}\n"
                )

            return output

        return get_audit_log
