# Socratic Knowledge - Troubleshooting

## Multi-Tenancy Issues

### Data leaking between tenants

Cause: Improper tenant isolation

Solution: Always include tenant_id in queries

### Tenant not found

Cause: Wrong tenant_id

Solution: Verify tenant exists first

## Access Control Issues

### User cannot access item

Cause: Missing permissions

Solution: Grant permission:
```python
km.grant_permission(item_id, user_id, "EDITOR", granted_by)
```

### Too many permissions to manage

Solution: Use group/role management

## Semantic Search Issues

### Search results not relevant

Cause: Embeddings not good quality

Solution: Ensure content is well-formatted

### Search is slow

Cause: Large knowledge base

Solution: Use external RAG with vector DB
