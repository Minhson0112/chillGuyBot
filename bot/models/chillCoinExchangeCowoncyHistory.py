from sqlalchemy import BigInteger, Column, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from bot.config.database import Base


class ChillCoinExchangeCowoncyHistory(Base):
    __tablename__ = "chill_coin_exchange_cowoncy_histories"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="chill coin exchange cowoncy history id")

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

    chill_coin_amount = Column(
        BigInteger,
        nullable=False,
        comment="exchanged chill coin amount",
    )

    cowoncy_amount = Column(
        BigInteger,
        nullable=False,
        comment="received cowoncy amount",
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
