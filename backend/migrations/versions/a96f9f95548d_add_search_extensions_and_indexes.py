"""Add search extensions and indexes

Revision ID: a96f9f95548d
Revises: 0002
Create Date: 2025-09-12 19:23:24.929191

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'a96f9f95548d'
down_revision = '0002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add search indexes for search functionality"""
    
    # SQLite doesn't support PostgreSQL extensions, so we'll create basic indexes
    # The search service will handle fuzzy matching in application code
    
    # Add search indexes for contacts
    op.create_index('idx_contacts_name_search', 'contacts', ['name'])
    op.create_index('idx_contacts_email_search', 'contacts', ['email'])
    op.create_index('idx_contacts_company_search', 'contacts', ['company'])
    op.create_index('idx_contacts_title_search', 'contacts', ['title'])
    
    # Add search indexes for products  
    op.create_index('idx_products_name_search', 'products', ['name'])
    op.create_index('idx_products_sku_search', 'products', ['sku'])
    op.create_index('idx_products_description_search', 'products', ['description'])
    op.create_index('idx_products_category_search', 'products', ['category'])
    op.create_index('idx_products_barcode_search', 'products', ['barcode'])
    
    # Create compound indexes for common search patterns
    op.create_index('idx_contacts_name_company', 'contacts', ['name', 'company'])
    op.create_index('idx_products_name_sku', 'products', ['name', 'sku'])


def downgrade() -> None:
    """Remove search indexes"""
    
    # Drop compound indexes
    op.drop_index('idx_products_name_sku', 'products')
    op.drop_index('idx_contacts_name_company', 'contacts')
    
    # Drop product search indexes
    op.drop_index('idx_products_barcode_search', 'products')
    op.drop_index('idx_products_category_search', 'products')
    op.drop_index('idx_products_description_search', 'products')
    op.drop_index('idx_products_sku_search', 'products')
    op.drop_index('idx_products_name_search', 'products')
    
    # Drop contact search indexes
    op.drop_index('idx_contacts_title_search', 'contacts')
    op.drop_index('idx_contacts_company_search', 'contacts')
    op.drop_index('idx_contacts_email_search', 'contacts')
    op.drop_index('idx_contacts_name_search', 'contacts')
