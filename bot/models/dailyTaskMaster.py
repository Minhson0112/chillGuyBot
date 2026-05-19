from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from bot.config.database import Base


class DailyTaskMaster(Base):
    __tablename__ = "daily_task_masters"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="daily task master id")

    task_code = Column(String(100), nullable=False, unique=True, comment="unique task code")
    task_name = Column(String(255), nullable=False, comment="task display name")
    description = Column(String(500), nullable=True, comment="task description")

    task_type = Column(
        String(50),
        nullable=False,
        comment="task type: chat_message, voice_time, plant_crop, sell_market_item, fishing, cooking, train_delivery",
    )

    target_item_id = Column(
        BigInteger,
        ForeignKey("items.id", ondelete="RESTRICT"),
        nullable=True,
        comment="target item id if task requires an item",
    )

    target_crop_id = Column(
        BigInteger,
        ForeignKey("crops.id", ondelete="RESTRICT"),
        nullable=True,
        comment="target crop id if task requires a crop",
    )

    target_channel_id = Column(BigInteger, nullable=True, comment="discord channel id if task targets a channel")

    required_value = Column(
        BigInteger,
        nullable=False,
        default=1,
        comment="required progress value",
    )

    reward_chill_coin = Column(BigInteger, nullable=False, default=0, comment="reward chill coin")
    reward_exp = Column(Integer, nullable=False, default=0, comment="reward farm exp")

    min_farm_level = Column(Integer, nullable=False, default=1, comment="minimum farm level to receive this task")
    weight = Column(Integer, nullable=False, default=100, comment="random weight")

    is_active = Column(Boolean, nullable=False, default=True, comment="whether task is active")

    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="created at")
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="updated at",
    )

    targetItem = relationship("Item", foreign_keys=[target_item_id])
    targetCrop = relationship("Crop", foreign_keys=[target_crop_id])

    userDailyTasks = relationship(
        "UserDailyTask",
        back_populates="taskMaster",
    )