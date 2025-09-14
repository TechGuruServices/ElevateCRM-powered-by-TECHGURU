"""Enable Row Level Security (RLS) for multi-tenant isolation

Revision ID: 0002
Revises: 0001
Create Date: 2025-09-08 23:15:00

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0002'
down_revision = '0001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create application roles
    op.execute("DO $$ BEGIN IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'app_user') THEN CREATE ROLE app_user; END IF; END $$")
    op.execute("DO $$ BEGIN IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'app_admin') THEN CREATE ROLE app_admin; END IF; END $$")
    
    # Grant basic permissions to app roles
    op.execute("GRANT USAGE ON SCHEMA public TO app_user, app_admin")
    op.execute("GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_user, app_admin")
    op.execute("GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO app_user, app_admin")
    
    # Enable RLS on all tenant-scoped tables
    tenant_tables = [
        'users', 'contacts', 'products', 'orders', 'order_line_items',
        'integrations', 'webhooks', 'stock_locations', 'stock_moves'
    ]
    
    for table in tenant_tables:
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
    
    # Create RLS policies for tenant isolation
    # Users table
    op.execute("""
        CREATE POLICY tenant_isolation_users ON users
        FOR ALL TO app_user, app_admin
        USING (company_id = current_setting('elevatecrm.tenant_id')::uuid)
    """)
    
    # Contacts table  
    op.execute("""
        CREATE POLICY tenant_isolation_contacts ON contacts
        FOR ALL TO app_user, app_admin
        USING (company_id = current_setting('elevatecrm.tenant_id')::uuid)
    """)
    
    # Products table
    op.execute("""
        CREATE POLICY tenant_isolation_products ON products
        FOR ALL TO app_user, app_admin
        USING (company_id = current_setting('elevatecrm.tenant_id')::uuid)
    """)
    
    # Stock locations table
    op.execute("""
        CREATE POLICY tenant_isolation_stock_locations ON stock_locations
        FOR ALL TO app_user, app_admin
        USING (company_id = current_setting('elevatecrm.tenant_id')::uuid)
    """)
    
    # Stock moves table
    op.execute("""
        CREATE POLICY tenant_isolation_stock_moves ON stock_moves
        FOR ALL TO app_user, app_admin
        USING (company_id = current_setting('elevatecrm.tenant_id')::uuid)
    """)
    
    # Orders table
    op.execute("""
        CREATE POLICY tenant_isolation_orders ON orders
        FOR ALL TO app_user, app_admin
        USING (company_id = current_setting('elevatecrm.tenant_id')::uuid)
    """)
    
    # Order line items table (inherits tenant from parent order)
    op.execute("""
        CREATE POLICY tenant_isolation_order_line_items ON order_line_items
        FOR ALL TO app_user, app_admin
        USING (EXISTS (
            SELECT 1 FROM orders 
            WHERE orders.id = order_line_items.order_id 
            AND orders.company_id = current_setting('elevatecrm.tenant_id')::uuid
        ))
    """)
    
    # Integrations table
    op.execute("""
        CREATE POLICY tenant_isolation_integrations ON integrations
        FOR ALL TO app_user, app_admin
        USING (company_id = current_setting('elevatecrm.tenant_id')::uuid)
    """)
    
    # Webhooks table (inherits tenant from parent integration)
    op.execute("""
        CREATE POLICY tenant_isolation_webhooks ON webhooks
        FOR ALL TO app_user, app_admin
        USING (EXISTS (
            SELECT 1 FROM integrations 
            WHERE integrations.id = webhooks.integration_id 
            AND integrations.company_id = current_setting('elevatecrm.tenant_id')::uuid
        ))
    """)
    
    # Companies table - users can only see their own company
    op.execute("ALTER TABLE companies ENABLE ROW LEVEL SECURITY")
    op.execute("""
        CREATE POLICY tenant_isolation_companies ON companies
        FOR ALL TO app_user, app_admin
        USING (id = current_setting('elevatecrm.tenant_id')::uuid)
    """)
    
    # Create function to set tenant context
    op.execute("""
        CREATE OR REPLACE FUNCTION set_tenant_context(tenant_uuid uuid)
        RETURNS void AS $$
        BEGIN
            PERFORM set_config('elevatecrm.tenant_id', tenant_uuid::text, true);
        END;
        $$ LANGUAGE plpgsql;
    """)
    
    # Grant execute permission on the function
    op.execute("GRANT EXECUTE ON FUNCTION set_tenant_context TO app_user, app_admin")


def downgrade() -> None:
    # Drop RLS policies
    tenant_tables = [
        'companies', 'users', 'contacts', 'products', 'orders', 'order_line_items',
        'integrations', 'webhooks', 'stock_locations', 'stock_moves'
    ]
    
    for table in tenant_tables:
        op.execute(f"DROP POLICY IF EXISTS tenant_isolation_{table} ON {table}")
        op.execute(f"ALTER TABLE {table} DISABLE ROW LEVEL SECURITY")
    
    # Drop function
    op.execute("DROP FUNCTION IF EXISTS set_tenant_context")
    
    # Note: We don't drop the roles as they might be in use
    # op.execute("DROP ROLE IF EXISTS app_user")
    # op.execute("DROP ROLE IF EXISTS app_admin")
