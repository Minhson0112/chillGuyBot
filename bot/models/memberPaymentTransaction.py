from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, String, func
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import relationship

from bot.config.database import Base


class MemberPaymentTransaction(Base):
    __tablename__ = "member_payment_transaction"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="member payment transaction id")

    user_id = Column(BIGINT(unsigned=True), ForeignKey("member.user_id", ondelete="CASCADE"), nullable=False, comment="discord user id")

    payment_target_type = Column(
        String(50),
        nullable=False,
        comment="payment target type: role_shop, lotto_ticket, server_item, love_shop",
    )
    payment_target_id = Column(BigInteger, nullable=False, comment="target purchase record id")

    status = Column(String(50), nullable=False, comment="payment status: pending_payment, paid, cancelled, expired")

    required_cowoncy_amount = Column(BigInteger, nullable=True, comment="required cowoncy amount")
    required_chill_coin_amount = Column(BigInteger, nullable=True, comment="required chill coin amount")

    paid_payment_type = Column(String(50), nullable=True, comment="actual paid payment type")
    paid_amount = Column(BigInteger, nullable=True, comment="actual paid amount")

    registered_at = Column(DateTime, nullable=False, server_default=func.now(), comment="registered at")
    paid_at = Column(DateTime, nullable=True, comment="paid at")
    cancelled_at = Column(DateTime, nullable=True, comment="cancelled at")
    expired_at = Column(DateTime, nullable=True, comment="expired at")

    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="created at")
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now(), comment="updated at")

    member = relationship("Member")
