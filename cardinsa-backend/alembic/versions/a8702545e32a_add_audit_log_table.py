"""add_audit_log_table

Revision ID: a8702545e32a
Revises: 93cf1645dab5
Create Date: 2025-11-03 09:57:26.939394

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'a8702545e32a'
down_revision: Union[str, None] = '93cf1645dab5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Create audit_logs table for tracking all system changes.

    SECURITY: Essential for compliance, security audits, and debugging
    """
    op.create_table(
        'audit_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'), onupdate=sa.text('now()')),

        # What was changed
        sa.Column('entity_type', sa.String(length=100), nullable=False, comment='Type of entity (policy, claim, user, etc.)'),
        sa.Column('entity_id', postgresql.UUID(as_uuid=True), nullable=True, comment='ID of the affected entity'),

        # What action was performed
        sa.Column('action', sa.String(length=50), nullable=False, comment='Action performed (create, update, delete, view, etc.)'),

        # Who performed it
        sa.Column('performed_by', postgresql.UUID(as_uuid=True), nullable=True, comment='User who performed the action'),

        # What changed
        sa.Column('changes_made', postgresql.JSON(astext_type=sa.Text()), nullable=True, comment='JSON object with before/after values'),

        # Where it came from
        sa.Column('ip_address', sa.String(length=45), nullable=True, comment='IP address of the request'),
        sa.Column('user_agent', sa.Text(), nullable=True, comment='User agent string from the request'),

        # Additional context
        sa.Column('request_id', sa.String(length=100), nullable=True, comment='Request ID for correlation'),
        sa.Column('session_id', sa.String(length=100), nullable=True, comment='Session ID for user tracking'),
    )

    # Create indexes for efficient queries
    op.create_index('ix_audit_logs_entity_type', 'audit_logs', ['entity_type'])
    op.create_index('ix_audit_logs_entity_id', 'audit_logs', ['entity_id'])
    op.create_index('ix_audit_logs_action', 'audit_logs', ['action'])
    op.create_index('ix_audit_logs_performed_by', 'audit_logs', ['performed_by'])
    op.create_index('ix_audit_logs_created_at', 'audit_logs', ['created_at'])


def downgrade() -> None:
    """
    Drop audit_logs table and all indexes.
    """
    op.drop_index('ix_audit_logs_created_at', table_name='audit_logs')
    op.drop_index('ix_audit_logs_performed_by', table_name='audit_logs')
    op.drop_index('ix_audit_logs_action', table_name='audit_logs')
    op.drop_index('ix_audit_logs_entity_id', table_name='audit_logs')
    op.drop_index('ix_audit_logs_entity_type', table_name='audit_logs')
    op.drop_table('audit_logs')
