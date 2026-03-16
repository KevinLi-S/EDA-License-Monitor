"""initial core schema

Revision ID: 001_initial
Revises:
Create Date: 2026-03-13
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'admin_users',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('username', sa.String(length=50), nullable=False, unique=True),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=100), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
    )

    op.create_table(
        'license_servers',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('vendor', sa.String(length=50), nullable=False),
        sa.Column('host', sa.String(length=255), nullable=False),
        sa.Column('port', sa.Integer(), nullable=False, server_default='27000'),
        sa.Column('lmutil_path', sa.String(length=255), nullable=True),
        sa.Column('ssh_host', sa.String(length=255), nullable=True),
        sa.Column('ssh_port', sa.Integer(), nullable=False, server_default='22'),
        sa.Column('ssh_user', sa.String(length=50), nullable=True),
        sa.Column('ssh_key_path', sa.String(length=255), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='active'),
        sa.Column('source_type', sa.String(length=20), nullable=False, server_default='lmutil'),
        sa.Column('lmstat_args', sa.String(length=500), nullable=True),
        sa.Column('sample_path', sa.String(length=500), nullable=True),
        sa.Column('last_check_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_status', sa.String(length=20), nullable=True),
        sa.Column('last_error', sa.String(length=1000), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
    )
    op.create_index('ix_license_servers_vendor', 'license_servers', ['vendor'])

    op.create_table(
        'license_features',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('server_id', sa.Integer(), sa.ForeignKey('license_servers.id', ondelete='CASCADE'), nullable=False),
        sa.Column('feature_name', sa.String(length=100), nullable=False),
        sa.Column('total_licenses', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('used_licenses', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('available_licenses', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('usage_percentage', sa.Numeric(5, 2), nullable=False, server_default='0'),
        sa.Column('vendor', sa.String(length=50), nullable=True),
        sa.Column('version', sa.String(length=50), nullable=True),
        sa.Column('raw_block', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.UniqueConstraint('server_id', 'feature_name', name='uq_server_feature_name'),
    )

    op.create_table(
        'license_usage_history',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('feature_id', sa.Integer(), sa.ForeignKey('license_features.id', ondelete='CASCADE'), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('used_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('available_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('usage_percentage', sa.Numeric(5, 2), nullable=False, server_default='0'),
    )

    op.create_table(
        'license_checkouts',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('feature_id', sa.Integer(), sa.ForeignKey('license_features.id', ondelete='CASCADE'), nullable=False),
        sa.Column('username', sa.String(length=100), nullable=False),
        sa.Column('hostname', sa.String(length=255), nullable=False),
        sa.Column('display', sa.String(length=100), nullable=True),
        sa.Column('process_info', sa.Text(), nullable=True),
        sa.Column('checkout_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('server_handle', sa.String(length=255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
    )


def downgrade() -> None:
    op.drop_table('license_checkouts')
    op.drop_table('license_usage_history')
    op.drop_table('license_features')
    op.drop_index('ix_license_servers_vendor', table_name='license_servers')
    op.drop_table('license_servers')
    op.drop_table('admin_users')
