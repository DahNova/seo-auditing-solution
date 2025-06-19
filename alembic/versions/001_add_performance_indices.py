"""Add performance indices for foreign keys

Revision ID: 001
Revises: 
Create Date: 2025-01-19 14:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add performance indices for frequently queried foreign keys"""
    
    # Index on websites.client_id for faster client->websites lookups
    op.create_index('idx_websites_client_id', 'websites', ['client_id'])
    
    # Index on scans.website_id for faster website->scans lookups
    op.create_index('idx_scans_website_id', 'scans', ['website_id'])
    
    # Index on issues.scan_id for faster scan->issues lookups
    op.create_index('idx_issues_scan_id', 'issues', ['scan_id'])
    
    # Index on pages.scan_id for faster scan->pages lookups
    op.create_index('idx_pages_scan_id', 'pages', ['scan_id'])
    
    # Index on issues.page_id for faster page->issues lookups
    op.create_index('idx_issues_page_id', 'issues', ['page_id'])
    
    # Composite index for issues severity filtering
    op.create_index('idx_issues_scan_severity', 'issues', ['scan_id', 'severity'])
    
    # Index on scans.created_at for faster ordering
    op.create_index('idx_scans_created_at', 'scans', ['created_at'])
    
    # Index on scans.status for status filtering
    op.create_index('idx_scans_status', 'scans', ['status'])


def downgrade() -> None:
    """Remove performance indices"""
    
    op.drop_index('idx_scans_status', table_name='scans')
    op.drop_index('idx_scans_created_at', table_name='scans')
    op.drop_index('idx_issues_scan_severity', table_name='issues')
    op.drop_index('idx_issues_page_id', table_name='issues')
    op.drop_index('idx_pages_scan_id', table_name='pages')
    op.drop_index('idx_issues_scan_id', table_name='issues')
    op.drop_index('idx_scans_website_id', table_name='scans')
    op.drop_index('idx_websites_client_id', table_name='websites')