"""Tests for LangChain tool integration."""

from unittest.mock import MagicMock

from socratic_knowledge.integrations.langchain import SocraticKnowledgeTools


class TestSocraticKnowledgeTools:
    """Test LangChain tool integration."""

    def test_tools_initialization(self):
        """Test tools initialization."""
        tools = SocraticKnowledgeTools(db_path=":memory:")

        assert tools.km is not None
        assert hasattr(tools, "get_tools")

    def test_tools_with_provided_manager(self):
        """Test tools with provided KnowledgeManager."""
        km = MagicMock()
        tools = SocraticKnowledgeTools(knowledge_manager=km)

        assert tools.km is km

    def test_get_tools(self):
        """Test getting tools list."""
        tools = SocraticKnowledgeTools(db_path=":memory:")
        tool_list = tools.get_tools()

        assert isinstance(tool_list, list)
        assert len(tool_list) > 0

    def test_search_knowledge_tool(self):
        """Test search knowledge tool."""
        km = MagicMock()
        item = MagicMock()
        item.item_id = "item_1"
        item.title = "Test"
        item.content = "This is test content"

        km.hybrid_search.return_value = [item]

        tools = SocraticKnowledgeTools(knowledge_manager=km)
        search_tool = tools._search_knowledge_tool()

        result = search_tool.invoke(
            {
                "tenant_id": "t1",
                "query": "test",
                "top_k": 10,
            }
        )

        assert isinstance(result, str)
        assert "Test" in result
        assert "item_1" in result

    def test_search_knowledge_tool_no_results(self):
        """Test search tool with no results."""
        km = MagicMock()
        km.hybrid_search.return_value = []

        tools = SocraticKnowledgeTools(knowledge_manager=km)
        search_tool = tools._search_knowledge_tool()

        result = search_tool.invoke(
            {
                "tenant_id": "t1",
                "query": "xyz",
                "top_k": 10,
            }
        )

        assert "No results found" in result

    def test_semantic_search_tool(self):
        """Test semantic search tool."""
        km = MagicMock()
        item = MagicMock()
        item.item_id = "item_1"
        item.title = "Test"
        item.tags = ["tag1", "tag2"]

        km.semantic_search.return_value = [item]

        tools = SocraticKnowledgeTools(knowledge_manager=km)
        search_tool = tools._semantic_search_tool()

        result = search_tool.invoke(
            {
                "tenant_id": "t1",
                "query": "test",
                "top_k": 5,
            }
        )

        assert isinstance(result, str)
        assert "Test" in result
        assert "semantically similar" in result.lower()

    def test_get_item_tool(self):
        """Test get item tool."""
        km = MagicMock()
        item = MagicMock()
        item.title = "Test"
        item.content = "Test content"
        item.version = 1
        item.created_at = MagicMock()
        item.created_at.isoformat.return_value = "2024-01-01T00:00:00"
        item.tags = ["tag1"]

        km.get_item.return_value = item

        tools = SocraticKnowledgeTools(knowledge_manager=km)
        get_tool = tools._get_item_tool()

        result = get_tool.invoke(
            {
                "tenant_id": "t1",
                "item_id": "item_1",
            }
        )

        assert isinstance(result, str)
        assert "Test" in result
        assert "Version: 1" in result

    def test_get_item_tool_not_found(self):
        """Test get item tool when item not found."""
        km = MagicMock()
        km.get_item.return_value = None

        tools = SocraticKnowledgeTools(knowledge_manager=km)
        get_tool = tools._get_item_tool()

        result = get_tool.invoke(
            {
                "tenant_id": "t1",
                "item_id": "nonexistent",
            }
        )

        assert "not found" in result

    def test_check_permissions_tool(self):
        """Test check permissions tool."""
        km = MagicMock()
        km.can_user_read.return_value = True
        km.can_user_edit.return_value = False
        km.can_user_delete.return_value = False

        tools = SocraticKnowledgeTools(knowledge_manager=km)
        perm_tool = tools._check_permissions_tool()

        result = perm_tool.invoke(
            {
                "tenant_id": "t1",
                "user_id": "user1",
                "item_id": "item_1",
            }
        )

        assert isinstance(result, str)
        assert "Permissions" in result
        assert "Read: True" in result
        assert "Edit: False" in result

    def test_get_audit_log_tool(self):
        """Test get audit log tool."""
        km = MagicMock()
        event = MagicMock()
        event.timestamp = MagicMock()
        event.timestamp.isoformat.return_value = "2024-01-01T00:00:00"
        event.user_id = "user1"
        event.action = "create"
        event.resource_type = "item"
        event.resource_id = "item_1"

        km.get_audit_log.return_value = [event]

        tools = SocraticKnowledgeTools(knowledge_manager=km)
        audit_tool = tools._get_audit_log_tool()

        result = audit_tool.invoke(
            {
                "tenant_id": "t1",
                "limit": 10,
            }
        )

        assert isinstance(result, str)
        assert "user1" in result
        assert "create" in result

    def test_get_audit_log_tool_empty(self):
        """Test audit log tool with no events."""
        km = MagicMock()
        km.get_audit_log.return_value = []

        tools = SocraticKnowledgeTools(knowledge_manager=km)
        audit_tool = tools._get_audit_log_tool()

        result = audit_tool.invoke(
            {
                "tenant_id": "t1",
                "limit": 10,
            }
        )

        assert "No audit events" in result

    def test_tool_descriptions(self):
        """Test that tools have descriptions."""
        tools = SocraticKnowledgeTools(db_path=":memory:")

        search_tool = tools._search_knowledge_tool()
        assert hasattr(search_tool, "description")
        assert search_tool.description is not None
        assert len(search_tool.description) > 0

    def test_tool_names(self):
        """Test that tools have names."""
        tools = SocraticKnowledgeTools(db_path=":memory:")

        search_tool = tools._search_knowledge_tool()
        assert hasattr(search_tool, "name")
        assert search_tool.name is not None

    def test_multiple_tools_independent(self):
        """Test that multiple tools can be used independently."""
        km = MagicMock()
        item = MagicMock()
        item.item_id = "item_1"
        item.title = "Test"
        item.content = "Content"

        km.hybrid_search.return_value = [item]
        km.get_item.return_value = item

        tools = SocraticKnowledgeTools(knowledge_manager=km)

        search_result = tools._search_knowledge_tool().invoke(
            {
                "tenant_id": "t1",
                "query": "test",
            }
        )
        get_result = tools._get_item_tool().invoke(
            {
                "tenant_id": "t1",
                "item_id": "item_1",
            }
        )

        assert "Test" in search_result
        assert "Test" in get_result
        assert km.hybrid_search.called
        assert km.get_item.called

    def test_tool_with_default_parameters(self):
        """Test tools with default parameters."""
        km = MagicMock()
        km.get_audit_log.return_value = []

        tools = SocraticKnowledgeTools(knowledge_manager=km)
        audit_tool = tools._get_audit_log_tool()

        # Call with only required parameter
        audit_tool.invoke(
            {
                "tenant_id": "t1",
            }
        )

        # Should use default limit
        call_args = km.get_audit_log.call_args
        assert call_args[1]["limit"] == 10  # Default limit

    def test_search_tool_formats_results(self):
        """Test that search tool formats results properly."""
        km = MagicMock()
        items = [
            MagicMock(
                item_id="item_1",
                title="First",
                content="This is the first item with some content",
            ),
            MagicMock(
                item_id="item_2",
                title="Second",
                content="This is the second item with different content",
            ),
        ]
        km.hybrid_search.return_value = items

        tools = SocraticKnowledgeTools(knowledge_manager=km)
        search_tool = tools._search_knowledge_tool()

        result = search_tool.invoke(
            {
                "tenant_id": "t1",
                "query": "test",
            }
        )

        # Check formatting
        assert "1. **First**" in result
        assert "2. **Second**" in result
        assert "(ID: item_1)" in result
        assert "(ID: item_2)" in result
        assert "Found 2 results" in result
