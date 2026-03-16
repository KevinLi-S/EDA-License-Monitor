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
        sa.Column('license_file_path', sa.String(length=500), nullable=True),
        sa.Column('license_log_path', sa.String(length=500), nullable=True),
        sa.Column('last_check_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_status', sa.String(length=20), nullable=True),
        sa.Column('last_error', sa.String(length=1000), nullable=True),
        sa.Column('static_grants_last_parsed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('static_grants_parse_error', sa.String(length=1000), nullable=True),
        sa.Column('log_last_parsed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('log_parse_error', sa.String(length=1000), nullable=True),
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

    op.create_table(
        'license_file_assets',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('server_id', sa.Integer(), sa.ForeignKey('license_servers.id', ondelete='CASCADE'), nullable=False),
        sa.Column('source_path', sa.String(length=500), nullable=True),
        sa.Column('server_name', sa.String(length=255), nullable=True),
        sa.Column('server_hostid', sa.String(length=255), nullable=True),
        sa.Column('server_port', sa.String(length=50), nullable=True),
        sa.Column('daemon_name', sa.String(length=100), nullable=True),
        sa.Column('daemon_path', sa.String(length=500), nullable=True),
        sa.Column('options_path', sa.String(length=500), nullable=True),
        sa.Column('raw_header', sa.Text(), nullable=True),
        sa.Column('last_parsed_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.UniqueConstraint('server_id', name='uq_license_file_asset_server'),
    )

    op.create_table(
        'static_license_grants',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('server_id', sa.Integer(), sa.ForeignKey('license_servers.id', ondelete='CASCADE'), nullable=False),
        sa.Column('license_file_asset_id', sa.Integer(), sa.ForeignKey('license_file_assets.id', ondelete='CASCADE'), nullable=True),
        sa.Column('record_type', sa.String(length=20), nullable=False),
        sa.Column('vendor_name', sa.String(length=100), nullable=True),
        sa.Column('feature_name', sa.String(length=255), nullable=False),
        sa.Column('version', sa.String(length=50), nullable=True),
        sa.Column('quantity', sa.Integer(), nullable=True),
        sa.Column('issued_date', sa.Date(), nullable=True),
        sa.Column('start_date', sa.Date(), nullable=True),
        sa.Column('expiry_date', sa.Date(), nullable=True),
        sa.Column('expiry_text', sa.String(length=50), nullable=True),
        sa.Column('serial_number', sa.String(length=100), nullable=True),
        sa.Column('notice', sa.Text(), nullable=True),
        sa.Column('raw_record', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.UniqueConstraint('server_id', 'feature_name', 'record_type', 'version', 'expiry_date', 'serial_number', name='uq_static_license_grant_identity'),
    )

    op.create_table(
        'license_log_events',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('server_id', sa.Integer(), sa.ForeignKey('license_servers.id', ondelete='CASCADE'), nullable=False),
        sa.Column('event_type', sa.String(length=20), nullable=False),
        sa.Column('event_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('vendor_daemon', sa.String(length=100), nullable=True),
        sa.Column('feature_name', sa.String(length=255), nullable=True),
        sa.Column('username', sa.String(length=100), nullable=True),
        sa.Column('hostname', sa.String(length=255), nullable=True),
        sa.Column('display', sa.String(length=100), nullable=True),
        sa.Column('event_hash', sa.String(length=64), nullable=False),
        sa.Column('raw_line', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.UniqueConstraint('event_hash', name='uq_license_log_event_hash'),
    )


def downgrade() -> None:
    op.drop_table('license_log_events')
    op.drop_table('static_license_grants')
    op.drop_table('license_file_assets')
    op.drop_table('license_checkouts')
    op.drop_table('license_usage_history')
    op.drop_table('license_features')
    op.drop_index('ix_license_servers_vendor', table_name='license_servers')
    op.drop_table('license_servers')
    op.drop_table('admin_users')
