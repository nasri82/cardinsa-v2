"""add_token_blacklist_table

Revision ID: a40bfa0084a1
Revises: a8702545e32a
Create Date: 2025-11-03 12:04:00.152721

SECURITY: Token blacklist for refresh token rotation and logout
Enables immediate token revocation and prevents token replay attacks
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'a40bfa0084a1'
down_revision: Union[str, None] = 'a8702545e32a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Create token_blacklist table for secure token rotation.

    SECURITY:
    - Enables refresh token rotation (old tokens are blacklisted when used)
    - Allows immediate logout (tokens blacklisted on logout)
    - Prevents token replay attacks
    - Essential for localStorage-based auth security
    """
    op.create_table(
        'token_blacklist',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False,
                  server_default=sa.text('gen_random_uuid()')),
        sa.Column('token_jti', sa.String(100), nullable=False, unique=True,
                  comment='JWT ID (jti claim) of blacklisted token'),
        sa.Column('token_type', sa.String(20), nullable=False,
                  comment='Token type: access or refresh'),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False,
                  comment='User who owns this token'),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False,
                  comment='When token expires (for cleanup)'),
        sa.Column('blacklisted_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text('now()'),
                  comment='When token was blacklisted'),
        sa.Column('reason', sa.String(100), nullable=True,
                  comment='Why token was blacklisted (logout, rotation, security)'),
    )

    # Indexes for efficient lookups
    op.create_index('ix_token_blacklist_token_jti', 'token_blacklist', ['token_jti'])
    op.create_index('ix_token_blacklist_user_id', 'token_blacklist', ['user_id'])
    op.create_index('ix_token_blacklist_expires_at', 'token_blacklist', ['expires_at'])


def downgrade() -> None:
    """Drop token_blacklist table and all indexes"""
    op.drop_index('ix_token_blacklist_expires_at', table_name='token_blacklist')
    op.drop_index('ix_token_blacklist_user_id', table_name='token_blacklist')
    op.drop_index('ix_token_blacklist_token_jti', table_name='token_blacklist')
    op.drop_table('token_blacklist')
