from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Integer, func
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import relationship

from bot.config.database import Base


class LottoTicket(Base):
    __tablename__ = "lotto_ticket"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="lotto ticket id")

    lotto_event_id = Column(BigInteger, ForeignKey("lotto_event.id", ondelete="CASCADE"), nullable=False, comment="lotto event id")
    lotto_ticket_purchase_id = Column(BigInteger, ForeignKey("lotto_ticket_purchase.id", ondelete="CASCADE"), nullable=False, comment="lotto ticket purchase id")
    user_id = Column(BIGINT(unsigned=True), ForeignKey("member.user_id", ondelete="CASCADE"), nullable=False, comment="discord user id")

    number_1 = Column(Integer, nullable=False, comment="first lotto number")
    number_2 = Column(Integer, nullable=False, comment="second lotto number")
    number_3 = Column(Integer, nullable=False, comment="third lotto number")
    number_4 = Column(Integer, nullable=False, comment="fourth lotto number")
    number_5 = Column(Integer, nullable=False, comment="fifth lotto number")

    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="created at")

    member = relationship("Member")
    lotto_event = relationship("LottoEvent", back_populates="tickets")
    ticket_purchase = relationship("LottoTicketPurchase", back_populates="tickets")
