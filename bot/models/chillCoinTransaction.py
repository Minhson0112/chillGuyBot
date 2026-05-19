from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from bot.config.database import Base


class ChillCoinTransaction(Base):
    __tablename__ = "chill_coin_transactions"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="transaction id")

    from_user_id = Column(
        BigInteger,
        ForeignKey("member.user_id", ondelete="CASCADE"),
        nullable=False,
        comment="sender user id"
    )
    to_user_id = Column(
        BigInteger,
        ForeignKey("member.user_id", ondelete="CASCADE"),
        nullable=False,
        comment="receiver user id"
    )

    amount = Column(BigInteger, nullable=False, comment="amount of chill coin transferred")

    transaction_type = Column(String(50), nullable=False, default="transfer", comment="transaction type")
    note = Column(String(255), nullable=True, comment="optional note")

    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="transaction time")

    fromMember = relationship("Member", foreign_keys=[from_user_id])
    toMember = relationship("Member", foreign_keys=[to_user_id])