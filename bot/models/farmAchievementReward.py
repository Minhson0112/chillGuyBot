from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from bot.config.database import Base


class FarmAchievementReward(Base):
    __tablename__ = "farm_achievement_rewards"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="farm achievement reward id")
    achievement_id = Column(
        BigInteger,
        ForeignKey("farm_achievement_masters.id", ondelete="CASCADE"),
        nullable=False,
        comment="farm achievement master id",
    )
    reward_type = Column(String(50), nullable=False, comment="reward type: chill_coin, farm_exp, discord_role")
    reward_amount = Column(BigInteger, nullable=True, comment="reward amount for chill coin or farm exp")
    discord_role_id = Column(BigInteger, nullable=True, comment="discord role id reward")
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="created at")

    achievement = relationship("FarmAchievementMaster", back_populates="rewards")
