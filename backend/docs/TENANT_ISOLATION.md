# Tenant Isolation with Row Level Security (RLS)

## Overview
ElevateCRM uses PostgreSQL Row Level Security (RLS) to ensure complete data isolation between tenants. Each tenant's data is identified by their `company_id` (UUID).

## Database Configuration

### RLS Policies
All tenant-scoped tables have RLS enabled with policies that filter by `company_id`:

```sql
-- Example policy for contacts table
CREATE POLICY tenant_isolation_contacts ON contacts
FOR ALL TO app_user, app_admin
USING (company_id = current_setting('elevatecrm.tenant_id')::uuid);
```

### Setting Tenant Context
Before executing any queries, the application must set the tenant context:

```sql
-- Set tenant context for the current session
SELECT set_config('elevatecrm.tenant_id', '550e8400-e29b-41d4-a716-446655440000', true);

-- Or using the helper function
SELECT set_tenant_context('550e8400-e29b-41d4-a716-446655440000'::uuid);
```

## API Implementation

### Per-Request Tenant Setting
The API middleware must set the tenant context at the beginning of each request:

```python
# In middleware or dependency
async def set_tenant_context(db: AsyncSession, tenant_id: str):
    """Set tenant context for the database session"""
    await db.execute(text("SELECT set_config('elevatecrm.tenant_id', :tenant_id, true)"), 
                     {"tenant_id": tenant_id})
```

### Connection Pooling Safety
For pooled connections, use session-local settings:
- Use `set_config('elevatecrm.tenant_id', value, true)` - the `true` parameter makes it session-local
- Reset the context at request end (optional, as session-local settings are automatically cleared)

## Testing Tenant Isolation

### SQL Test
```sql
-- Create test data for two tenants
INSERT INTO companies (id, name) VALUES 
  ('550e8400-e29b-41d4-a716-446655440000', 'Tenant A'),
  ('550e8400-e29b-41d4-a716-446655440001', 'Tenant B');

-- Set tenant A context
SELECT set_config('elevatecrm.tenant_id', '550e8400-e29b-41d4-a716-446655440000', true);
SELECT * FROM companies; -- Should only see Tenant A

-- Set tenant B context  
SELECT set_config('elevatecrm.tenant_id', '550e8400-e29b-41d4-a716-446655440001', true);
SELECT * FROM companies; -- Should only see Tenant B
```

### Python Test
```python
async def test_tenant_isolation():
    # Test that tenant A cannot see tenant B data
    await db.execute(text("SELECT set_config('elevatecrm.tenant_id', :tenant_id, true)"), 
                     {"tenant_id": str(tenant_a_id)})
    tenant_a_contacts = await db.execute(select(Contact))
    
    await db.execute(text("SELECT set_config('elevatecrm.tenant_id', :tenant_id, true)"), 
                     {"tenant_id": str(tenant_b_id)})
    tenant_b_contacts = await db.execute(select(Contact))
    
    # Verify no overlap
    assert len(set(tenant_a_contacts) & set(tenant_b_contacts)) == 0
```
