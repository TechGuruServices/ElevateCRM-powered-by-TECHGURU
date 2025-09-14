# Row Level Security (RLS) Setup Guide

## Overview
Row Level Security (RLS) is implemented to ensure multi-tenant data isolation in the ElevateCRM platform. Each tenant's data is automatically filtered based on the current session's tenant ID.

## Database Implementation

### RLS Policies
The RLS policies are implemented in migration `0002_enable_row_level_security_for_multi_tenant_isolation.py`:

```sql
-- Enable RLS on all tenant-scoped tables
ALTER TABLE companies ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE contacts ENABLE ROW LEVEL SECURITY;
ALTER TABLE products ENABLE ROW LEVEL SECURITY;
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE integrations ENABLE ROW LEVEL SECURITY;

-- Create policies using current_setting for tenant isolation
CREATE POLICY tenant_isolation_policy ON companies
FOR ALL USING (id::text = current_setting('elevatecrm.tenant_id', true));

CREATE POLICY tenant_isolation_policy ON users
FOR ALL USING (company_id::text = current_setting('elevatecrm.tenant_id', true));

CREATE POLICY tenant_isolation_policy ON contacts
FOR ALL USING (company_id::text = current_setting('elevatecrm.tenant_id', true));

CREATE POLICY tenant_isolation_policy ON products
FOR ALL USING (company_id::text = current_setting('elevatecrm.tenant_id', true));

CREATE POLICY tenant_isolation_policy ON orders
FOR ALL USING (company_id::text = current_setting('elevatecrm.tenant_id', true));

CREATE POLICY tenant_isolation_policy ON integrations
FOR ALL USING (company_id::text = current_setting('elevatecrm.tenant_id', true));
```

## Application Integration

### Setting Tenant Context
Before each database query, the application must set the tenant ID in the PostgreSQL session:

```sql
SET LOCAL elevatecrm.tenant_id = '<tenant_uuid>';
```

### Middleware Implementation
The tenant middleware (see `app/middleware/tenant.py`) automatically:

1. Extracts tenant ID from JWT token
2. Sets the session-level tenant ID using `SET LOCAL`
3. Ensures proper isolation for pooled connections

### Usage Example

```python
# In your API endpoint
@app.get("/api/v1/contacts")
async def get_contacts(
    db: AsyncSession = Depends(get_db),
    tenant: TenantInfo = Depends(get_current_tenant)
):
    # Tenant context is automatically set by middleware
    contacts = await db.execute(select(Contact))
    return contacts.scalars().all()  # Only returns tenant's contacts
```

## Security Verification

### Test RLS Isolation
```sql
-- Test 1: Set tenant A context
SET elevatecrm.tenant_id = 'tenant-a-uuid';
SELECT * FROM contacts;  -- Should only return tenant A's contacts

-- Test 2: Set tenant B context  
SET elevatecrm.tenant_id = 'tenant-b-uuid';
SELECT * FROM contacts;  -- Should only return tenant B's contacts

-- Test 3: No tenant context (should return no rows)
SET elevatecrm.tenant_id = '';
SELECT * FROM contacts;  -- Should return empty result
```

### Connection Pool Safety
- Uses `SET LOCAL` instead of `SET` to ensure tenant context is transaction-scoped
- Prevents cross-tenant data leaks in connection pools
- Middleware validates tenant ID on every request

## Troubleshooting

### Common Issues
1. **Empty Results**: Check if `elevatecrm.tenant_id` is set correctly
2. **Cross-Tenant Access**: Verify RLS policies are enabled and active
3. **Connection Pool Issues**: Ensure using `SET LOCAL` not `SET`

### Debug Commands
```sql
-- Check current tenant setting
SELECT current_setting('elevatecrm.tenant_id', true);

-- Check RLS status
SELECT tablename, rowsecurity FROM pg_tables WHERE schemaname = 'public';

-- Check policies
SELECT * FROM pg_policies WHERE tablename IN ('contacts', 'products', 'orders');
```
