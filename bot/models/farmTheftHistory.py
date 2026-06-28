from sqlalchemy import BigInteger, Column, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from bot.config.database import Base


class FarmTheftHistory(Base):
    __tablename__ = "farm_theft_histories"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="farm theft history id")
    thief_user_id = Column(
        BigInteger,
        ForeignKey("member.user_id", ondelete="CASCADE"),
        nullable=False,
        comment="discord user id of the thief",
    )
    victim_user_id = Column(
        BigInteger,
        ForeignKey("member.user_id", ondelete="CASCADE"),
        nullable=False,
        comment="discord user id of the victim",
    )
    item_id = Column(
        BigInteger,
        ForeignKey("items.id", ondelete="RESTRICT"),
        nullable=False,
        comment="stolen item id",
    )
    stolen_at = Column(DateTime, nullable=False, server_default=func.now(), comment="stolen at")

    thief = relationship("Member", foreign_keys=[thief_user_id])
    victim = relationship("Member", foreign_keys=[victim_user_id])
    item = relationship("Item", foreign_keys=[item_id])
