from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, text
from sqlalchemy.orm import relationship

from bot.config.database import Base


class OwoDonateHistory(Base):
    __tablename__ = "owo_donate_history"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    sender_user_id = Column(
        BigInteger,
        ForeignKey("member.user_id"),
        nullable=False,
    )
    receiver_user_id = Column(
        BigInteger,
        ForeignKey("member.user_id"),
        nullable=False,
    )
    cowoncy_amount = Column(
        BigInteger,
        nullable=False,
    )
    created_at = Column(
        DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )

    senderMember = relationship("Member", foreign_keys=[sender_user_id])
    receiverMember = relationship("Member", foreign_keys=[receiver_user_id])