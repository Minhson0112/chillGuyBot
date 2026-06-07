from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import relationship

from bot.config.database import Base


class LottoTicketPurchase(Base):
    __tablename__ = "lotto_ticket_purchase"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="lotto ticket purchase id")

    user_id = Column(BIGINT(unsigned=True), ForeignKey("member.user_id", ondelete="CASCADE"), nullable=False, comment="discord user id")
    lotto_event_id = Column(BigInteger, ForeignKey("lotto_event.id", ondelete="CASCADE"), nullable=False, comment="lotto event id")

    ticket_quantity = Column(Integer, nullable=False, comment="ticket quantity")

    status = Column(String(50), nullable=False, comment="purchase status: pending_payment, paid, cancelled, expired")

    payment_type = Column(String(50), nullable=True, comment="payment type")
    payment_amount = Column(BigInteger, nullable=True, comment="payment amount")

    registered_at = Column(DateTime, nullable=False, server_default=func.now(), comment="registered at")
    paid_at = Column(DateTime, nullable=True, comment="paid at")
    expired_at = Column(DateTime, nullable=True, comment="expired at")

    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="created at")
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now(), comment="updated at")

    member = relationship("Member")
    lotto_event = relationship("LottoEvent", back_populates="ticket_purchases")
    tickets = relationship("LottoTicket", back_populates="ticket_purchase")
