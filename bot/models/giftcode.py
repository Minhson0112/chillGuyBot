from sqlalchemy import BigInteger, Column, Date, DateTime, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from bot.config.database import Base


class Giftcode(Base):
    __tablename__ = "giftcodes"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="giftcode id")
    code = Column(String(100), nullable=False, unique=True, comment="giftcode code")
    reward_chill_coin = Column(BigInteger, nullable=False, default=0, comment="reward chill coin")
    expired_at = Column(Date, nullable=False, comment="giftcode expiration date")
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="created at")

    rewards = relationship(
        "GiftcodeReward",
        back_populates="giftcode",
        cascade="all, delete-orphan",
    )