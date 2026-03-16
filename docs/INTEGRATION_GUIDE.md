# Socratic Knowledge - Integration Guide

## Socratic RAG Integration

Semantic search with embeddings:

```python
from socratic_knowledge import KnowledgeManager
from socratic_rag import RAGClient

km = KnowledgeManager()
rag = RAGClient()

# Add documents to both
item = km.create_item(...)
rag.add_document(item.content, source=item.title)

# Search with RAG
results = rag.search("query")
```

## Openclaw Integration

```python
from socratic_knowledge.integrations.openclaw import SocraticKnowledgeSkill

skill = SocraticKnowledgeSkill(storage="sqlite")
result = skill.search(tenant_id="org1", query="topic")
```

## LangChain Integration

```python
from socratic_knowledge.integrations.langchain import SocraticKnowledgeTool

tool = SocraticKnowledgeTool(enable_rag=True)
results = tool.semantic_search(tenant_id="org1", query="topic")
```
