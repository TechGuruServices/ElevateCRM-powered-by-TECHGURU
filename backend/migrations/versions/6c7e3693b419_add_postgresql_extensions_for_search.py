"""add_postgresql_extensions_for_search

Revision ID: 6c7e3693b419
Revises: a96f9f95548d
Create Date: 2025-09-13 18:15:21.922459

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6c7e3693b419'
down_revision = 'a96f9f95548d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add PostgreSQL extensions required for advanced search functionality"""
    
    # Create PostgreSQL extensions for fuzzy search and full-text search
    # These extensions must be created with superuser privileges
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")
    op.execute("CREATE EXTENSION IF NOT EXISTS unaccent;")
    op.execute("CREATE EXTENSION IF NOT EXISTS btree_gin;")
    op.execute("CREATE EXTENSION IF NOT EXISTS fuzzystrmatch;")
    
    # Add GIN indexes for trigram search on text fields
    # Contacts search indexes
    op.execute("CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_contacts_name_gin_trgm ON contacts USING gin (name gin_trgm_ops);")
    op.execute("CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_contacts_email_gin_trgm ON contacts USING gin (email gin_trgm_ops);")
    op.execute("CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_contacts_company_gin_trgm ON contacts USING gin (company gin_trgm_ops);")
    
    # Products search indexes  
    op.execute("CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_products_name_gin_trgm ON products USING gin (name gin_trgm_ops);")
    op.execute("CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_products_description_gin_trgm ON products USING gin (description gin_trgm_ops);")
    op.execute("CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_products_sku_gin_trgm ON products USING gin (sku gin_trgm_ops);")


def downgrade() -> None:
    """Remove search indexes and extensions"""
    
    # Drop GIN indexes
    op.execute("DROP INDEX CONCURRENTLY IF EXISTS idx_contacts_name_gin_trgm;")
    op.execute("DROP INDEX CONCURRENTLY IF EXISTS idx_contacts_email_gin_trgm;")
    op.execute("DROP INDEX CONCURRENTLY IF EXISTS idx_contacts_company_gin_trgm;")
    op.execute("DROP INDEX CONCURRENTLY IF EXISTS idx_products_name_gin_trgm;")
    op.execute("DROP INDEX CONCURRENTLY IF EXISTS idx_products_description_gin_trgm;")
    op.execute("DROP INDEX CONCURRENTLY IF EXISTS idx_products_sku_gin_trgm;")
    
    # Note: We don't drop extensions as they might be used by other applications
    # Extensions: pg_trgm, unaccent, btree_gin, fuzzystrmatch remain
