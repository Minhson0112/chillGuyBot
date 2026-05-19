from sqlalchemy import BigInteger, Column, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from bot.config.database import Base


class OwoExchangeCoinHistory(Base):
    __tablename__ = "owo_exchange_coin_histories"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="owo exchange coin history id")

    message_id = Column(
        BigInteger,
        nullable=False,
        unique=True,
        comment="owo bot message id",
    )

    channel_id = Column(
        BigInteger,
        nullable=False,
        comment="discord channel id",
    )

    sender_user_id = Column(
        BigInteger,
        ForeignKey("member.user_id", ondelete="CASCADE"),
        nullable=False,
        comment="discord user id who sent cowoncy",
    )

    receiver_user_id = Column(
        BigInteger,
        ForeignKey("member.user_id", ondelete="CASCADE"),
        nullable=False,
        comment="discord user id who received cowoncy",
    )

    cowoncy_amount = Column(
        BigInteger,
        nullable=False,
        comment="transferred cowoncy amount",
    )

    transferred_at = Column(
        DateTime,
        nullable=False,
        comment="transferred datetime in GMT+7",
    )

    created_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        comment="created at",
    )

    sender = relationship(
        "Member",
        foreign_keys=[sender_user_id],
    )

    receiver = relationship(
        "Member",
        foreign_keys=[receiver_user_id],
    )