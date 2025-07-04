"""Add enterprise URL discovery features

Revision ID: 002
Revises: 001
Create Date: 2025-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add URL discovery metadata to pages table
    op.add_column('pages', sa.Column('discovery_source', sa.String(length=50), nullable=True))
    op.add_column('pages', sa.Column('discovery_priority', sa.Float(), nullable=True))
    op.add_column('pages', sa.Column('sitemap_priority', sa.Float(), nullable=True))
    op.add_column('pages', sa.Column('sitemap_changefreq', sa.String(length=20), nullable=True))
    op.add_column('pages', sa.Column('sitemap_lastmod', sa.DateTime(timezone=True), nullable=True))
    op.add_column('pages', sa.Column('source_sitemap_url', sa.Text(), nullable=True))
    op.add_column('pages', sa.Column('parent_url', sa.Text(), nullable=True))
    op.add_column('pages', sa.Column('crawl_depth', sa.Integer(), nullable=True, default=0))
    
    # Add processing metadata to pages table
    op.add_column('pages', sa.Column('queue_priority', sa.String(length=20), nullable=True))
    op.add_column('pages', sa.Column('processing_started', sa.DateTime(timezone=True), nullable=True))
    op.add_column('pages', sa.Column('processing_completed', sa.DateTime(timezone=True), nullable=True))
    op.add_column('pages', sa.Column('estimated_processing_time', sa.Integer(), nullable=True))
    op.add_column('pages', sa.Column('actual_processing_time', sa.Integer(), nullable=True))
    op.add_column('pages', sa.Column('retry_count', sa.Integer(), nullable=True, default=0))
    op.add_column('pages', sa.Column('last_error', sa.Text(), nullable=True))
    op.add_column('pages', sa.Column('processing_status', sa.String(length=20), nullable=True, default='pending'))
    
    # Add indexes for efficient querying
    op.create_index('ix_pages_discovery_source', 'pages', ['discovery_source'])
    op.create_index('ix_pages_queue_priority', 'pages', ['queue_priority'])
    op.create_index('ix_pages_processing_status', 'pages', ['processing_status'])
    
    # Add enterprise sitemap features to sitemap_snapshots table
    op.add_column('sitemap_snapshots', sa.Column('sitemap_type', sa.String(length=20), nullable=True, default='regular'))
    op.add_column('sitemap_snapshots', sa.Column('is_sitemap_index', sa.Boolean(), nullable=True, default=False))
    op.add_column('sitemap_snapshots', sa.Column('parent_sitemap_url', sa.Text(), nullable=True))
    op.add_column('sitemap_snapshots', sa.Column('child_sitemaps_count', sa.Integer(), nullable=True, default=0))
    op.add_column('sitemap_snapshots', sa.Column('urls_with_metadata', sa.JSON(), nullable=True))
    op.add_column('sitemap_snapshots', sa.Column('priority_distribution', sa.JSON(), nullable=True))
    op.add_column('sitemap_snapshots', sa.Column('changefreq_distribution', sa.JSON(), nullable=True))
    op.add_column('sitemap_snapshots', sa.Column('image_urls_count', sa.Integer(), nullable=True, default=0))
    op.add_column('sitemap_snapshots', sa.Column('parsing_time', sa.Integer(), nullable=True))
    op.add_column('sitemap_snapshots', sa.Column('parsing_errors', sa.JSON(), nullable=True))
    op.add_column('sitemap_snapshots', sa.Column('compressed_size', sa.Integer(), nullable=True))
    op.add_column('sitemap_snapshots', sa.Column('uncompressed_size', sa.Integer(), nullable=True))


def downgrade() -> None:
    # Remove indexes
    op.drop_index('ix_pages_processing_status', 'pages')
    op.drop_index('ix_pages_queue_priority', 'pages')
    op.drop_index('ix_pages_discovery_source', 'pages')
    
    # Remove URL discovery metadata from pages table
    op.drop_column('pages', 'processing_status')
    op.drop_column('pages', 'last_error')
    op.drop_column('pages', 'retry_count')
    op.drop_column('pages', 'actual_processing_time')
    op.drop_column('pages', 'estimated_processing_time')
    op.drop_column('pages', 'processing_completed')
    op.drop_column('pages', 'processing_started')
    op.drop_column('pages', 'queue_priority')
    op.drop_column('pages', 'crawl_depth')
    op.drop_column('pages', 'parent_url')
    op.drop_column('pages', 'source_sitemap_url')
    op.drop_column('pages', 'sitemap_lastmod')
    op.drop_column('pages', 'sitemap_changefreq')
    op.drop_column('pages', 'sitemap_priority')
    op.drop_column('pages', 'discovery_priority')
    op.drop_column('pages', 'discovery_source')
    
    # Remove enterprise sitemap features from sitemap_snapshots table
    op.drop_column('sitemap_snapshots', 'uncompressed_size')
    op.drop_column('sitemap_snapshots', 'compressed_size')
    op.drop_column('sitemap_snapshots', 'parsing_errors')
    op.drop_column('sitemap_snapshots', 'parsing_time')
    op.drop_column('sitemap_snapshots', 'image_urls_count')
    op.drop_column('sitemap_snapshots', 'changefreq_distribution')
    op.drop_column('sitemap_snapshots', 'priority_distribution')
    op.drop_column('sitemap_snapshots', 'urls_with_metadata')
    op.drop_column('sitemap_snapshots', 'child_sitemaps_count')
    op.drop_column('sitemap_snapshots', 'parent_sitemap_url')
    op.drop_column('sitemap_snapshots', 'is_sitemap_index')
    op.drop_column('sitemap_snapshots', 'sitemap_type')