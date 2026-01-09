"""Initial schema with users, tasks, refresh_tokens and RLS

Revision ID: 001_initial
Revises:
Create Date: 2026-01-09

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Create user_role enum
    user_role_enum = postgresql.ENUM('user', 'admin', name='user_role', create_type=False)
    user_role_enum.create(op.get_bind(), checkfirst=True)

    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('role', postgresql.ENUM('user', 'admin', name='user_role', create_type=False), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)

    # Create tasks table
    op.create_table(
        'tasks',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_completed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_tasks_user_id', 'tasks', ['user_id'])
    op.create_index('ix_tasks_user_completed', 'tasks', ['user_id', 'is_completed'])

    # Create refresh_tokens table
    op.create_table(
        'refresh_tokens',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('token_hash', sa.String(255), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_refresh_tokens_user_id', 'refresh_tokens', ['user_id'])
    op.create_index('ix_refresh_tokens_token_hash', 'refresh_tokens', ['token_hash'])

    # Enable Row-Level Security on tasks table
    op.execute("ALTER TABLE tasks ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE tasks FORCE ROW LEVEL SECURITY")

    # Create RLS policy for tasks - users can only see their own tasks
    op.execute("""
        CREATE POLICY tasks_isolation_policy ON tasks
        FOR ALL
        USING (user_id = COALESCE(current_setting('app.current_user_id', true)::uuid, '00000000-0000-0000-0000-000000000000'::uuid))
    """)

    # Enable RLS on refresh_tokens
    op.execute("ALTER TABLE refresh_tokens ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE refresh_tokens FORCE ROW LEVEL SECURITY")

    op.execute("""
        CREATE POLICY refresh_tokens_isolation_policy ON refresh_tokens
        FOR ALL
        USING (user_id = COALESCE(current_setting('app.current_user_id', true)::uuid, '00000000-0000-0000-0000-000000000000'::uuid))
    """)

def downgrade() -> None:
    # Drop RLS policies
    op.execute("DROP POLICY IF EXISTS tasks_isolation_policy ON tasks")
    op.execute("DROP POLICY IF EXISTS refresh_tokens_isolation_policy ON refresh_tokens")

    # Drop tables
    op.drop_table('refresh_tokens')
    op.drop_table('tasks')
    op.drop_table('users')

    # Drop enum
    op.execute("DROP TYPE IF EXISTS user_role")
