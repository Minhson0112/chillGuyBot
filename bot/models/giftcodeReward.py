from sqlalchemy import BigInteger, Column, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from bot.config.database import Base


class GiftcodeReward(Base):
    __tablename__ = "giftcode_rewards"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="giftcode reward id")

    giftcode_id = Column(
        BigInteger,
        ForeignKey("giftcodes.id", ondelete="CASCADE"),
        nullable=False,
        comment="giftcode id",
    )

    item_id = Column(
        BigInteger,
        ForeignKey("items.id", ondelete="RESTRICT"),
        nullable=False,
        comment="reward item id",
    )

    quantity = Column(BigInteger, nullable=False, comment="reward item quantity")
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="created at")

    giftcode = relationship("Giftcode", back_populates="rewards")
    item = relationship("Item")