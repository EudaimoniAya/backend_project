"""
店铺内买家与卖家/助手的对话会话与消息（v1.0 可先仅 REST 人工消息）。
"""
from typing import TYPE_CHECKING, List, Optional
from datetime import datetime
import enum

from sqlalchemy import Integer, Text, DateTime, ForeignKey, func, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database.base import Base

if TYPE_CHECKING:
    from models.user import User
    from models.shop import Shop


class MessageSenderType(str, enum.Enum):
    """消息发送方类型"""
    USER = 'user'
    SELLER = 'seller'
    ASSISTANT = 'assistant'


class Conversation(Base):
    __tablename__ = 'conversations'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True,
                                    comment='会话ID')
    shop_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('shops.id', ondelete='CASCADE'),
        nullable=False, index=True,
        comment='店铺ID',
    )
    buyer_user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False, index=True,
        comment='买家用户ID',
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False, index=True,
        comment='创建时间',
    )

    shop: Mapped['Shop'] = relationship('Shop', back_populates='conversations')
    buyer: Mapped['User'] = relationship('User', back_populates='conversations_as_buyer')
    messages: Mapped[List['Message']] = relationship(
        'Message', back_populates='conversation', cascade='all, delete-orphan',
    )

    def __repr__(self) -> str:
        return f'<Conversation(id={self.id}, shop={self.shop_id}, buyer={self.buyer_user_id})>'


class Message(Base):
    __tablename__ = 'messages'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True,
                                    comment='消息ID')
    conversation_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('conversations.id', ondelete='CASCADE'),
        nullable=False, index=True,
        comment='会话ID',
    )
    sender_type: Mapped[MessageSenderType] = mapped_column(
        Enum(MessageSenderType, native_enum=False, length=32),
        nullable=False,
        comment='发送方：user/seller/assistant',
    )
    sender_user_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey('users.id', ondelete='SET NULL'),
        nullable=True, index=True,
        comment='发送用户ID，助手可为空',
    )
    content: Mapped[str] = mapped_column(Text, nullable=False, comment='消息正文')
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False, index=True,
        comment='发送时间',
    )

    conversation: Mapped['Conversation'] = relationship('Conversation', back_populates='messages')
    sender_user: Mapped[Optional['User']] = relationship(
        'User', back_populates='messages_sent',
    )

    def __repr__(self) -> str:
        return f'<Message(id={self.id}, conv={self.conversation_id}, type={self.sender_type})>'
