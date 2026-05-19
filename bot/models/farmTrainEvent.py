from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from bot.config.database import Base


class FarmTrainEvent(Base):
    __tablename__ = "farm_train_events"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="farm train event id")

    required_item_id = Column(
        BigInteger,
        ForeignKey("items.id", ondelete="RESTRICT"),
        nullable=False,
        comment="requested item id",
    )
    required_quantity = Column(BigInteger, nullable=False, comment="requested item quantity")

    reward_chill_coin = Column(BigInteger, nullable=False, default=0, comment="reward chill coin")
    reward_exp = Column(Integer, nullable=False, default=0, comment="reward farm exp")

    is_completed = Column(Boolean, nullable=False, default=False, comment="whether train event is completed")

    created_by_user_id = Column(
        BigInteger,
        ForeignKey("member.user_id", ondelete="SET NULL"),
        nullable=True,
        comment="admin user id who created event",
    )
    completed_by_farm_id = Column(
        BigInteger,
        ForeignKey("farm.id", ondelete="SET NULL"),
        nullable=True,
        comment="farm id that completed event",
    )
    completed_by_user_id = Column(
        BigInteger,
        ForeignKey("member.user_id", ondelete="SET NULL"),
        nullable=True,
        comment="user id that completed event",
    )

    completed_at = Column(DateTime, nullable=True, comment="completed at")
    closed_at = Column(DateTime, nullable=True, comment="closed at")

    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="created at")
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="updated at",
    )

    requiredItem = relationship("Item", foreign_keys=[required_item_id])
    createdByMember = relationship("Member", foreign_keys=[created_by_user_id])
    completedByFarm = relationship("Farm", foreign_keys=[completed_by_farm_id])
    completedByMember = relationship("Member", foreign_keys=[completed_by_user_id])

    histories = relationship(
        "FarmTrainEventHistory",
        back_populates="trainEvent",
        cascade="all, delete-orphan",
    )