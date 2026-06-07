from sqlalchemy import BigInteger, Boolean, Column, DateTime, String, func
from sqlalchemy.orm import relationship

from bot.config.database import Base
from bot.enums.lottoEventStatus import LottoEventStatus


class LottoEvent(Base):
    __tablename__ = "lotto_event"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="lotto event id")

    name = Column(String(255), nullable=False, comment="lotto event name")
    ticket_price_cowoncy = Column(BigInteger, nullable=False, comment="ticket price in cowoncy")

    buy_deadline = Column(DateTime, nullable=False, comment="deadline to buy tickets")
    draw_at = Column(DateTime, nullable=True, comment="draw time")

    status = Column(String(50), nullable=False, default=LottoEventStatus.OPEN.value, comment="event status: open, closed, drawn, cancelled")
    is_active = Column(Boolean, nullable=False, default=True, comment="is active event")

    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="created at")
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now(), comment="updated at")

    ticket_purchases = relationship("LottoTicketPurchase", back_populates="lotto_event")
    tickets = relationship("LottoTicket", back_populates="lotto_event")
