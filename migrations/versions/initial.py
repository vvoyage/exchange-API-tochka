"""initial

Revision ID: initial
Create Date: 2024-02-09 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from app.schemas.user import UserRole
from app.schemas.order import OrderStatus, Direction

# revision identifiers, used by Alembic.
revision = 'initial'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Создаем enum типы
    op.execute("CREATE TYPE user_role AS ENUM ('USER', 'ADMIN')")
    op.execute("CREATE TYPE order_status AS ENUM ('NEW', 'EXECUTED', 'PARTIALLY_EXECUTED', 'CANCELLED')")
    op.execute("CREATE TYPE direction AS ENUM ('BUY', 'SELL')")
    
    # Создаем таблицу пользователей
    op.create_table(
        'users',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('role', sa.Enum('USER', 'ADMIN', name='user_role'), nullable=False),
        sa.Column('api_key', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('api_key')
    )
    
    # Создаем таблицу инструментов
    op.create_table(
        'instruments',
        sa.Column('ticker', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.PrimaryKeyConstraint('ticker')
    )
    
    # Создаем таблицу балансов
    op.create_table(
        'balances',
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('ticker', sa.String(), nullable=False),
        sa.Column('amount', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['ticker'], ['instruments.ticker'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('user_id', 'ticker')
    )
    
    # Создаем таблицу ордеров
    op.create_table(
        'orders',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('ticker', sa.String(), nullable=False),
        sa.Column('direction', sa.Enum('BUY', 'SELL', name='direction'), nullable=False),
        sa.Column('status', sa.Enum('NEW', 'EXECUTED', 'PARTIALLY_EXECUTED', 'CANCELLED', name='order_status'), nullable=False),
        sa.Column('qty', sa.Integer(), nullable=False),
        sa.Column('price', sa.Integer(), nullable=True),
        sa.Column('filled', sa.Integer(), nullable=False, default=0),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['ticker'], ['instruments.ticker'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Создаем таблицу транзакций
    op.create_table(
        'transactions',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('ticker', sa.String(), nullable=False),
        sa.Column('buyer_id', sa.String(), nullable=False),
        sa.Column('seller_id', sa.String(), nullable=False),
        sa.Column('amount', sa.Integer(), nullable=False),
        sa.Column('price', sa.Integer(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['buyer_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['seller_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['ticker'], ['instruments.ticker'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade() -> None:
    op.drop_table('transactions')
    op.drop_table('orders')
    op.drop_table('balances')
    op.drop_table('instruments')
    op.drop_table('users')
    op.execute('DROP TYPE direction')
    op.execute('DROP TYPE order_status')
    op.execute('DROP TYPE user_role') 