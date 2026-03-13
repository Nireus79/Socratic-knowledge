"""
Example 4: RAG Integration & Semantic Search

This example demonstrates semantic search using RAG embeddings
for intelligent knowledge retrieval.
"""

from socratic_knowledge import KnowledgeManager


def main():
    """Run RAG integration example."""
    print("=" * 60)
    print("Example 4: RAG Integration & Semantic Search")
    print("=" * 60)

    # Initialize with RAG enabled
    km = KnowledgeManager(
        storage="sqlite",
        db_path="knowledge_demo.db",
        enable_rag=True,
    )

    # Create tenant
    tenant = km.create_tenant(name="AIResearch")

    # ==================== Add Knowledge Items ====================
    print("\n" + "=" * 60)
    print("1. Building Knowledge Base")
    print("=" * 60)

    documents = [
        {
            "title": "Large Language Models Overview",
            "content": """
# Large Language Models (LLMs)

Large Language Models are neural networks trained on vast amounts of text data.
They can understand and generate human-like text.

## Key Characteristics
- Transformer-based architecture
- Self-attention mechanisms
- Trained on billions of parameters
- Pre-trained on internet-scale text

## Applications
- Text generation
- Question answering
- Text summarization
- Language translation
            """,
        },
        {
            "title": "Fine-tuning Strategies",
            "content": """
# Fine-tuning Language Models

Fine-tuning is the process of adapting a pre-trained model
to specific tasks or domains.

## Methods
- Supervised fine-tuning (SFT)
- Reinforcement learning from human feedback (RLHF)
- Parameter-efficient fine-tuning (PEFT)
- LoRA (Low-Rank Adaptation)

## Best Practices
- Use domain-specific data
- Monitor overfitting
- Adjust learning rates carefully
- Validate on test set
            """,
        },
        {
            "title": "Prompt Engineering Techniques",
            "content": """
# Prompt Engineering

Prompt engineering is the art of crafting inputs to get
desired outputs from language models.

## Techniques
- Few-shot prompting
- Zero-shot prompting
- Chain-of-thought prompting
- Role-based prompting

## Tips
- Be specific in your instructions
- Use examples to guide the model
- Break complex tasks into steps
- Iterate and refine prompts
            """,
        },
        {
            "title": "RAG Systems",
            "content": """
# Retrieval-Augmented Generation

RAG combines retrieval and generation for better responses.

## How RAG Works
1. Retrieve relevant documents
2. Augment prompt with retrieved content
3. Generate response using context

## Advantages
- Better factuality
- Access to current information
- Reduced hallucinations
- Explainable answers

## Implementation
- Embedding-based retrieval
- Vector databases
- Semantic similarity search
            """,
        },
    ]

    print(f"\nAdding {len(documents)} knowledge items...")
    items = []
    for doc in documents:
        item = km.create_item(
            tenant_id=tenant.tenant_id,
            title=doc["title"],
            content=doc["content"],
            created_by="researcher",
            tags=["ai", "nlp", "llm"],
        )
        items.append(item)
        print(f"  ✓ {item.title}")
        # Index for semantic search
        km.index_item(item)

    # ==================== Keyword Search ====================
    print("\n" + "=" * 60)
    print("2. Full-Text Search (Keyword-based)")
    print("=" * 60)

    keyword_query = "fine-tuning"
    print(f"\nSearching for: '{keyword_query}'")

    results = km.search(
        tenant_id=tenant.tenant_id,
        query=keyword_query,
        limit=5,
    )

    print(f"Found {len(results)} results:")
    for i, item in enumerate(results, 1):
        print(f"  {i}. {item.title}")

    # ==================== Semantic Search ====================
    print("\n" + "=" * 60)
    print("3. Semantic Search (Embeddings-based)")
    print("=" * 60)

    semantic_query = "How do I adapt a model to my specific domain?"
    print(f"\nQuery: '{semantic_query}'")
    print("(Searching by semantic meaning, not exact keywords)")

    try:
        semantic_results = km.semantic_search(
            tenant_id=tenant.tenant_id,
            query=semantic_query,
            top_k=3,
        )

        print("\nSemantically similar documents:")
        for i, item in enumerate(semantic_results, 1):
            print(f"  {i}. {item.title}")
            print(f"     Tags: {', '.join(item.tags)}")
    except ValueError as e:
        print(f"Note: {e}")
        print("(RAG may not be available in this environment)")

    # ==================== Hybrid Search ====================
    print("\n" + "=" * 60)
    print("4. Hybrid Search (Keyword + Semantic)")
    print("=" * 60)

    hybrid_query = "best ways to improve model performance"
    print(f"\nQuery: '{hybrid_query}'")

    try:
        hybrid_results = km.hybrid_search(
            tenant_id=tenant.tenant_id,
            query=hybrid_query,
            top_k=5,
        )

        print("\nHybrid search results (combined ranking):")
        for i, item in enumerate(hybrid_results, 1):
            print(f"  {i}. {item.title}")
    except Exception:
        # Fallback to keyword search
        hybrid_results = km.search(
            tenant_id=tenant.tenant_id,
            query=hybrid_query,
            limit=5,
        )
        print("\nFull-text search results:")
        for i, item in enumerate(hybrid_results, 1):
            print(f"  {i}. {item.title}")

    # ==================== Search Comparison ====================
    print("\n" + "=" * 60)
    print("5. Search Comparison")
    print("=" * 60)

    comparison_query = "prompt engineering"

    keyword_results = km.search(
        tenant_id=tenant.tenant_id,
        query=comparison_query,
        limit=5,
    )

    print(f"\nQuery: '{comparison_query}'")
    print("\nKeyword Search Results:")
    for i, item in enumerate(keyword_results, 1):
        print(f"  {i}. {item.title}")

    try:
        semantic_results = km.semantic_search(
            tenant_id=tenant.tenant_id,
            query=comparison_query,
            top_k=5,
        )

        print("\nSemantic Search Results:")
        for i, item in enumerate(semantic_results, 1):
            print(f"  {i}. {item.title}")

        # Show differences
        keyword_ids = {item.item_id for item in keyword_results}
        semantic_ids = {item.item_id for item in semantic_results}

        only_keyword = keyword_ids - semantic_ids
        only_semantic = semantic_ids - keyword_ids
        both = keyword_ids & semantic_ids

        print("\nAnalysis:")
        print(f"  Both methods found: {len(both)} items")
        print(f"  Only in keyword search: {len(only_keyword)} items")
        print(f"  Only in semantic search: {len(only_semantic)} items")
    except ValueError:
        print("\nSemantic search not available")

    # ==================== Collection-based Search ====================
    print("\n" + "=" * 60)
    print("6. Filtered Search (by Collection)")
    print("=" * 60)

    # Create collection
    ai_collection = km.create_collection(
        tenant_id=tenant.tenant_id,
        name="AI Research",
        created_by="researcher",
    )

    # Move items to collection
    for item in items[:2]:
        item.collection_id = ai_collection.collection_id
        km.update_item(item)

    print(f"\nSearching within '{ai_collection.name}' collection...")

    collection_results = km.search(
        tenant_id=tenant.tenant_id,
        query="model",
        limit=10,
    )

    collection_filtered = [
        item for item in collection_results if item.collection_id == ai_collection.collection_id
    ]

    print(f"Total results: {len(collection_results)}")
    print(f"In AI Research collection: {len(collection_filtered)}")

    # ==================== Summary ====================
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)

    print("\nKnowledge Base Statistics:")
    print(f"  Total items: {len(items)}")
    print(f"  Tenant: {tenant.name}")
    print("  Search modes available:")
    print("    ✓ Full-text search (FTS5)")
    print("    ✓ Semantic search (RAG embeddings)")
    print("    ✓ Hybrid search (combined)")

    print("\nSearch Features:")
    print("  ✓ Keyword-based retrieval")
    print("  ✓ Semantic similarity matching")
    print("  ✓ Collection filtering")
    print("  ✓ Configurable result limits")
    print("  ✓ Graceful fallback modes")

    print("\n✅ RAG integration example completed!")


if __name__ == "__main__":
    main()
