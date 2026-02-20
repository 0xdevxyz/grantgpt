"""Initial migration - create all tables

Revision ID: 0001
Revises: 
Create Date: 2026-02-03 00:00:01

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '0001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create subscription tier enum
    subscription_tier = postgresql.ENUM('tier_1', 'tier_2', 'tier_3', name='subscriptiontier')
    subscription_tier.create(op.get_bind())
    
    # Create application status enum
    application_status = postgresql.ENUM(
        'draft', 'in_progress', 'review', 'submitted', 
        'approved', 'rejected', 'funded',
        name='applicationstatus'
    )
    application_status.create(op.get_bind())
    
    # Create document type enum
    document_type = postgresql.ENUM(
        'application', 'supporting_document', 'contract', 
        'invoice', 'report', 'other',
        name='documenttype'
    )
    document_type.create(op.get_bind())

    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(), nullable=False, unique=True, index=True),
        sa.Column('password_hash', sa.String(), nullable=False),
        sa.Column('full_name', sa.String(), nullable=True),
        sa.Column('company_name', sa.String(), nullable=False),
        sa.Column('company_size', sa.Integer(), nullable=True),
        sa.Column('industry', sa.String(), nullable=True),
        sa.Column('annual_revenue', sa.Integer(), nullable=True),
        sa.Column('location', sa.String(), nullable=True),
        sa.Column('technology_stack', sa.String(), nullable=True),
        sa.Column('subscription_tier', sa.Enum('tier_1', 'tier_2', 'tier_3', name='subscriptiontier'), nullable=False, default='tier_1'),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('is_verified', sa.Boolean(), nullable=False, default=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('last_login', sa.DateTime(), nullable=True),
    )

    # Create grants table
    op.create_table(
        'grants',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('external_id', sa.String(), nullable=True, index=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('anbieter', sa.String(), nullable=True),
        sa.Column('ebene', sa.String(), nullable=True),  # bund, land, eu
        sa.Column('beschreibung', sa.Text(), nullable=True),
        sa.Column('foerderhoehe_min', sa.Float(), nullable=True),
        sa.Column('foerderhoehe_max', sa.Float(), nullable=True),
        sa.Column('foerderquote', sa.Float(), nullable=True),
        sa.Column('foerderart', sa.String(), nullable=True),  # zuschuss, kredit, etc.
        sa.Column('zielgruppe', postgresql.JSONB(), nullable=True),
        sa.Column('foerdergegenstand', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('deadline', sa.DateTime(), nullable=True),
        sa.Column('is_continuous', sa.Boolean(), default=True),
        sa.Column('url_offiziell', sa.String(), nullable=True),
        sa.Column('source', sa.String(), nullable=True),
        sa.Column('status', sa.String(), nullable=True, default='active'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    
    # Create index for grant searching
    op.create_index('ix_grants_name', 'grants', ['name'])
    op.create_index('ix_grants_ebene', 'grants', ['ebene'])
    op.create_index('ix_grants_foerderart', 'grants', ['foerderart'])

    # Create applications table
    op.create_table(
        'applications',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('grant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('grants.id'), nullable=False),
        sa.Column('status', sa.Enum('draft', 'in_progress', 'review', 'submitted', 'approved', 'rejected', 'funded', name='applicationstatus'), nullable=False, default='draft'),
        sa.Column('project_name', sa.String(), nullable=False),
        sa.Column('project_description', sa.Text(), nullable=True),
        sa.Column('requested_amount', sa.Float(), nullable=True),
        sa.Column('approved_amount', sa.Float(), nullable=True),
        sa.Column('ai_generated_content', postgresql.JSONB(), nullable=True),
        sa.Column('ai_match_score', sa.Float(), nullable=True),
        sa.Column('submitted_at', sa.DateTime(), nullable=True),
        sa.Column('approved_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    
    op.create_index('ix_applications_user_id', 'applications', ['user_id'])
    op.create_index('ix_applications_grant_id', 'applications', ['grant_id'])
    op.create_index('ix_applications_status', 'applications', ['status'])

    # Create documents table
    op.create_table(
        'documents',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('application_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('applications.id', ondelete='CASCADE'), nullable=False),
        sa.Column('filename', sa.String(), nullable=False),
        sa.Column('file_path', sa.String(), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=True),
        sa.Column('mime_type', sa.String(), nullable=True),
        sa.Column('document_type', sa.Enum('application', 'supporting_document', 'contract', 'invoice', 'report', 'other', name='documenttype'), nullable=False, default='other'),
        sa.Column('ai_generated', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    
    op.create_index('ix_documents_application_id', 'documents', ['application_id'])

    # Create change_log table for tracking program changes
    op.create_table(
        'change_log',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('grant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('grants.id'), nullable=True),
        sa.Column('source_url', sa.String(), nullable=False),
        sa.Column('change_type', sa.String(), nullable=False),  # new_program, updated, expired, etc.
        sa.Column('old_hash', sa.String(), nullable=True),
        sa.Column('new_hash', sa.String(), nullable=False),
        sa.Column('changed_fields', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('requires_review', sa.Boolean(), default=True),
        sa.Column('reviewed', sa.Boolean(), default=False),
        sa.Column('reviewed_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(), nullable=True),
        sa.Column('detected_at', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    
    op.create_index('ix_change_log_source_url', 'change_log', ['source_url'])
    op.create_index('ix_change_log_change_type', 'change_log', ['change_type'])
    op.create_index('ix_change_log_requires_review', 'change_log', ['requires_review'])


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('change_log')
    op.drop_table('documents')
    op.drop_table('applications')
    op.drop_table('grants')
    op.drop_table('users')
    
    # Drop enums
    op.execute('DROP TYPE IF EXISTS documenttype')
    op.execute('DROP TYPE IF EXISTS applicationstatus')
    op.execute('DROP TYPE IF EXISTS subscriptiontier')
