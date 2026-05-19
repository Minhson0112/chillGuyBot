from sqlalchemy import BigInteger, Column, Date, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from bot.config.database import Base


class UserDailyTask(Base):
    __tablename__ = "user_daily_tasks"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="user daily task id")

    user_id = Column(
        BigInteger,
        ForeignKey("member.user_id", ondelete="CASCADE"),
        nullable=False,
        comment="discord user id",
    )

    task_date = Column(Date, nullable=False, comment="daily task date")

    slot_no = Column(Integer, nullable=False, comment="task slot from 1 to 5")

    task_master_id = Column(
        BigInteger,
        ForeignKey("daily_task_masters.id", ondelete="RESTRICT"),
        nullable=False,
        comment="daily task master id",
    )

    task_code = Column(String(100), nullable=False, comment="snapshot task code")
    task_name = Column(String(255), nullable=False, comment="snapshot task name")
    description = Column(String(500), nullable=True, comment="snapshot task description")

    task_type = Column(String(50), nullable=False, comment="snapshot task type")

    target_item_id = Column(
        BigInteger,
        ForeignKey("items.id", ondelete="RESTRICT"),
        nullable=True,
        comment="snapshot target item id",
    )

    target_crop_id = Column(
        BigInteger,
        ForeignKey("crops.id", ondelete="RESTRICT"),
        nullable=True,
        comment="snapshot target crop id",
    )

    target_channel_id = Column(BigInteger, nullable=True, comment="snapshot target channel id")

    required_value = Column(BigInteger, nullable=False, comment="required progress value")
    progress_value = Column(BigInteger, nullable=False, default=0, comment="current progress value")

    reward_chill_coin = Column(BigInteger, nullable=False, default=0, comment="reward chill coin snapshot")
    reward_exp = Column(Integer, nullable=False, default=0, comment="reward farm exp snapshot")

    status = Column(
        String(50),
        nullable=False,
        default="in_progress",
        comment="task status: in_progress, completed",
    )

    completed_at = Column(DateTime, nullable=True, comment="completed at")
    reward_received_at = Column(DateTime, nullable=True, comment="reward received at")
    notified_at = Column(DateTime, nullable=True, comment="completion notification sent at")

    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="created at")
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="updated at",
    )

    member = relationship("Member", foreign_keys=[user_id])
    taskMaster = relationship("DailyTaskMaster", back_populates="userDailyTasks")
    targetItem = relationship("Item", foreign_keys=[target_item_id])
    targetCrop = relationship("Crop", foreign_keys=[target_crop_id])