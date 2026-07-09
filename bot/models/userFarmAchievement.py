from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from bot.config.database import Base


class UserFarmAchievement(Base):
    __tablename__ = "user_farm_achievements"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="user farm achievement id")
    user_id = Column(
        BigInteger,
        ForeignKey("member.user_id", ondelete="CASCADE"),
        nullable=False,
        comment="discord user id",
    )
    achievement_id = Column(
        BigInteger,
        ForeignKey("farm_achievement_masters.id", ondelete="CASCADE"),
        nullable=False,
        comment="farm achievement master id",
    )
    progress_value = Column(BigInteger, nullable=False, default=0, comment="latest calculated progress value")
    is_completed = Column(Boolean, nullable=False, default=False, comment="whether achievement condition is completed")
    completed_at = Column(DateTime, nullable=True, comment="completed at")
    is_reward_claimed = Column(Boolean, nullable=False, default=False, comment="whether reward has been claimed")
    reward_claimed_at = Column(DateTime, nullable=True, comment="reward claimed at")
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="created at")
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now(), comment="updated at")

    member = relationship("Member", back_populates="farmAchievements")
    achievement = relationship("FarmAchievementMaster", back_populates="userAchievements")
