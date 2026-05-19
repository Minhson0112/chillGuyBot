from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from bot.config.database import Base


class FarmTrainEventHistory(Base):
    __tablename__ = "farm_train_event_histories"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="farm train event history id")

    train_event_id = Column(
        BigInteger,
        ForeignKey("farm_train_events.id", ondelete="CASCADE"),
        nullable=False,
        comment="farm train event id",
    )
    farm_id = Column(
        BigInteger,
        ForeignKey("farm.id", ondelete="CASCADE"),
        nullable=False,
        comment="farm id that loaded item",
    )
    user_id = Column(
        BigInteger,
        ForeignKey("member.user_id", ondelete="CASCADE"),
        nullable=False,
        comment="discord user id that loaded item",
    )

    delivered_item_id = Column(
        BigInteger,
        ForeignKey("items.id", ondelete="RESTRICT"),
        nullable=False,
        comment="delivered item id",
    )
    delivered_quantity = Column(BigInteger, nullable=False, comment="delivered item quantity")

    reward_chill_coin = Column(BigInteger, nullable=False, default=0, comment="reward chill coin snapshot")
    reward_exp = Column(Integer, nullable=False, default=0, comment="reward farm exp snapshot")

    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="created at")

    trainEvent = relationship("FarmTrainEvent", back_populates="histories")
    farm = relationship("Farm", foreign_keys=[farm_id])
    member = relationship("Member", foreign_keys=[user_id])
    deliveredItem = relationship("Item", foreign_keys=[delivered_item_id])