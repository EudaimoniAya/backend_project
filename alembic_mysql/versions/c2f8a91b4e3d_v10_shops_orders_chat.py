"""v1.0 域扩展：店铺、商品 shop_id、订单、购物车、收藏、浏览、会话与消息、用户 last_seen_at

Revision ID: c2f8a91b4e3d
Revises: bd3ea4e044fc
Create Date: 2026-04-03

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision: str = 'c2f8a91b4e3d'
down_revision: Union[str, Sequence[str], None] = 'bd3ea4e044fc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'users',
        sa.Column('last_seen_at', sa.DateTime(), nullable=True, comment='最近活跃时间，可空'),
    )
    op.create_index(op.f('ix_users_last_seen_at'), 'users', ['last_seen_at'], unique=False)

    op.create_table(
        'shops',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False, comment='店铺ID'),
        sa.Column('owner_user_id', sa.Integer(), nullable=False, comment='店主用户ID（卖家）'),
        sa.Column('name', sa.String(length=200), nullable=False, comment='店铺名称'),
        sa.Column('slug', sa.String(length=100), nullable=True, comment='店铺短链标识，可选'),
        sa.Column('description', sa.Text(), nullable=True, comment='店铺描述'),
        sa.Column('manual_first', sa.Boolean(), server_default='1', nullable=False,
                    comment='是否优先人工接待'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False,
                    comment='创建时间'),
        sa.ForeignKeyConstraint(['owner_user_id'], ['users.id'], name=op.f('fk_shops_owner_user_id_users'),
                                ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_shops')),
        sa.UniqueConstraint('owner_user_id', name='uq_shops_owner_user_id'),
    )
    op.create_index(op.f('ix_shops_owner_user_id'), 'shops', ['owner_user_id'], unique=False)
    op.create_index(op.f('ix_shops_slug'), 'shops', ['slug'], unique=True)

    # 为角色为卖家的用户建店（MySQL 中 Enum 存 BUYER / SELLER）
    op.execute(text("""
        INSERT INTO shops (owner_user_id, name, manual_first, created_at)
        SELECT u.id, CONCAT(u.username, '的店铺'), 1, NOW()
        FROM users u
        WHERE u.role = 'SELLER'
          AND NOT EXISTS (SELECT 1 FROM shops s WHERE s.owner_user_id = u.id)
    """))
    # 为仅有商品但尚未有店的卖家补店（兼容历史或异常数据）
    op.execute(text("""
        INSERT INTO shops (owner_user_id, name, manual_first, created_at)
        SELECT DISTINCT p.seller_id, CONCAT(u.username, '的店铺'), 1, NOW()
        FROM products p
        INNER JOIN users u ON u.id = p.seller_id
        WHERE NOT EXISTS (SELECT 1 FROM shops s WHERE s.owner_user_id = p.seller_id)
    """))

    op.add_column(
        'products',
        sa.Column('shop_id', sa.Integer(), nullable=True, comment='商品所属店铺id'),
    )
    op.create_foreign_key(
        op.f('fk_products_shop_id_shops'),
        'products', 'shops',
        ['shop_id'], ['id'],
        ondelete='RESTRICT',
    )
    op.create_index(op.f('ix_products_shop_id'), 'products', ['shop_id'], unique=False)

    op.execute(text("""
        UPDATE products p
        INNER JOIN shops s ON s.owner_user_id = p.seller_id
        SET p.shop_id = s.id
    """))

    op.alter_column(
        'products', 'shop_id',
        existing_type=sa.Integer(),
        nullable=False,
    )

    op.create_table(
        'cart_items',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False, comment='购物车行ID'),
        sa.Column('user_id', sa.Integer(), nullable=False, comment='买家用户ID'),
        sa.Column('product_id', sa.Integer(), nullable=False, comment='商品ID'),
        sa.Column('quantity', sa.Integer(), nullable=False, comment='数量'),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False,
                    comment='更新时间'),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], name=op.f('fk_cart_items_product_id_products'),
                                ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_cart_items_user_id_users'),
                                ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_cart_items')),
        sa.UniqueConstraint('user_id', 'product_id', name='uq_cart_items_user_product'),
    )
    op.create_index(op.f('ix_cart_items_product_id'), 'cart_items', ['product_id'], unique=False)
    op.create_index(op.f('ix_cart_items_user_id'), 'cart_items', ['user_id'], unique=False)

    op.create_table(
        'user_favorites',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False, comment='收藏记录ID'),
        sa.Column('user_id', sa.Integer(), nullable=False, comment='用户ID'),
        sa.Column('product_id', sa.Integer(), nullable=False, comment='商品ID'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False,
                    comment='收藏时间'),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], name=op.f('fk_user_favorites_product_id_products'),
                                ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_user_favorites_user_id_users'),
                                ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_user_favorites')),
        sa.UniqueConstraint('user_id', 'product_id', name='uq_user_favorites_user_product'),
    )
    op.create_index(op.f('ix_user_favorites_product_id'), 'user_favorites', ['product_id'], unique=False)
    op.create_index(op.f('ix_user_favorites_user_id'), 'user_favorites', ['user_id'], unique=False)

    op.create_table(
        'product_views',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False, comment='浏览记录ID'),
        sa.Column('user_id', sa.Integer(), nullable=False, comment='用户ID'),
        sa.Column('product_id', sa.Integer(), nullable=False, comment='商品ID'),
        sa.Column('viewed_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False,
                    comment='浏览时间'),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], name=op.f('fk_product_views_product_id_products'),
                                ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_product_views_user_id_users'),
                                ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_product_views')),
    )
    op.create_index(op.f('ix_product_views_product_id'), 'product_views', ['product_id'], unique=False)
    op.create_index(op.f('ix_product_views_user_id'), 'product_views', ['user_id'], unique=False)
    op.create_index(op.f('ix_product_views_viewed_at'), 'product_views', ['viewed_at'], unique=False)

    op.create_table(
        'orders',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False, comment='订单ID'),
        sa.Column('user_id', sa.Integer(), nullable=False, comment='买家用户ID'),
        sa.Column('shop_id', sa.Integer(), nullable=False, comment='店铺ID'),
        sa.Column('status', sa.String(length=32), nullable=False, server_default='completed',
                    comment='订单状态'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False,
                    comment='创建时间'),
        sa.ForeignKeyConstraint(['shop_id'], ['shops.id'], name=op.f('fk_orders_shop_id_shops'),
                                ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_orders_user_id_users'),
                                ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_orders')),
    )
    op.create_index(op.f('ix_orders_created_at'), 'orders', ['created_at'], unique=False)
    op.create_index(op.f('ix_orders_shop_id'), 'orders', ['shop_id'], unique=False)
    op.create_index(op.f('ix_orders_user_id'), 'orders', ['user_id'], unique=False)

    op.create_table(
        'order_items',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False, comment='订单行ID'),
        sa.Column('order_id', sa.Integer(), nullable=False, comment='订单ID'),
        sa.Column('product_id', sa.Integer(), nullable=False, comment='商品ID'),
        sa.Column('quantity', sa.Integer(), nullable=False, comment='数量'),
        sa.Column('unit_price_snapshot', sa.Integer(), nullable=False, comment='成交单价快照，单位：分'),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id'], name=op.f('fk_order_items_order_id_orders'),
                                ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], name=op.f('fk_order_items_product_id_products'),
                                ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_order_items')),
    )
    op.create_index(op.f('ix_order_items_order_id'), 'order_items', ['order_id'], unique=False)
    op.create_index(op.f('ix_order_items_product_id'), 'order_items', ['product_id'], unique=False)

    op.create_table(
        'conversations',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False, comment='会话ID'),
        sa.Column('shop_id', sa.Integer(), nullable=False, comment='店铺ID'),
        sa.Column('buyer_user_id', sa.Integer(), nullable=False, comment='买家用户ID'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False,
                    comment='创建时间'),
        sa.ForeignKeyConstraint(['buyer_user_id'], ['users.id'], name=op.f('fk_conversations_buyer_user_id_users'),
                                ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['shop_id'], ['shops.id'], name=op.f('fk_conversations_shop_id_shops'),
                                ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_conversations')),
    )
    op.create_index(op.f('ix_conversations_buyer_user_id'), 'conversations', ['buyer_user_id'], unique=False)
    op.create_index(op.f('ix_conversations_created_at'), 'conversations', ['created_at'], unique=False)
    op.create_index(op.f('ix_conversations_shop_id'), 'conversations', ['shop_id'], unique=False)

    op.create_table(
        'messages',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False, comment='消息ID'),
        sa.Column('conversation_id', sa.Integer(), nullable=False, comment='会话ID'),
        sa.Column('sender_type', sa.String(length=32), nullable=False, comment='发送方类型'),
        sa.Column('sender_user_id', sa.Integer(), nullable=True, comment='发送用户ID'),
        sa.Column('content', sa.Text(), nullable=False, comment='消息正文'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False,
                    comment='发送时间'),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'],
                                name=op.f('fk_messages_conversation_id_conversations'),
                                ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['sender_user_id'], ['users.id'], name=op.f('fk_messages_sender_user_id_users'),
                                ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_messages')),
    )
    op.create_index(op.f('ix_messages_conversation_id'), 'messages', ['conversation_id'], unique=False)
    op.create_index(op.f('ix_messages_created_at'), 'messages', ['created_at'], unique=False)
    op.create_index(op.f('ix_messages_sender_user_id'), 'messages', ['sender_user_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_messages_sender_user_id'), table_name='messages')
    op.drop_index(op.f('ix_messages_created_at'), table_name='messages')
    op.drop_index(op.f('ix_messages_conversation_id'), table_name='messages')
    op.drop_table('messages')

    op.drop_index(op.f('ix_conversations_shop_id'), table_name='conversations')
    op.drop_index(op.f('ix_conversations_created_at'), table_name='conversations')
    op.drop_index(op.f('ix_conversations_buyer_user_id'), table_name='conversations')
    op.drop_table('conversations')

    op.drop_index(op.f('ix_order_items_product_id'), table_name='order_items')
    op.drop_index(op.f('ix_order_items_order_id'), table_name='order_items')
    op.drop_table('order_items')

    op.drop_index(op.f('ix_orders_user_id'), table_name='orders')
    op.drop_index(op.f('ix_orders_shop_id'), table_name='orders')
    op.drop_index(op.f('ix_orders_created_at'), table_name='orders')
    op.drop_table('orders')

    op.drop_index(op.f('ix_product_views_viewed_at'), table_name='product_views')
    op.drop_index(op.f('ix_product_views_user_id'), table_name='product_views')
    op.drop_index(op.f('ix_product_views_product_id'), table_name='product_views')
    op.drop_table('product_views')

    op.drop_index(op.f('ix_user_favorites_user_id'), table_name='user_favorites')
    op.drop_index(op.f('ix_user_favorites_product_id'), table_name='user_favorites')
    op.drop_table('user_favorites')

    op.drop_index(op.f('ix_cart_items_user_id'), table_name='cart_items')
    op.drop_index(op.f('ix_cart_items_product_id'), table_name='cart_items')
    op.drop_table('cart_items')

    op.drop_index(op.f('ix_products_shop_id'), table_name='products')
    op.drop_constraint(op.f('fk_products_shop_id_shops'), 'products', type_='foreignkey')
    op.drop_column('products', 'shop_id')

    op.drop_index(op.f('ix_shops_slug'), table_name='shops')
    op.drop_index(op.f('ix_shops_owner_user_id'), table_name='shops')
    op.drop_table('shops')

    op.drop_index(op.f('ix_users_last_seen_at'), table_name='users')
    op.drop_column('users', 'last_seen_at')
