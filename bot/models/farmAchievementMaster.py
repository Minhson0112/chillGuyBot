from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from bot.config.database import Base


class FarmAchievementMaster(Base):
    __tablename__ = "farm_achievement_masters"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="farm achievement master id")
    category_id = Column(
        BigInteger,
        ForeignKey("farm_achievement_categories.id", ondelete="CASCADE"),
        nullable=False,
        comment="farm achievement category id",
    )
    achievement_code = Column(String(100), nullable=False, unique=True, comment="unique achievement code")
    name = Column(String(255), nullable=False, comment="achievement display name")
    description = Column(String(500), nullable=True, comment="achievement description")
    condition_type = Column(String(100), nullable=False, comment="achievement condition type")
    target_item_id = Column(
        BigInteger,
        ForeignKey("items.id", ondelete="RESTRICT"),
        nullable=True,
        comment="target item id if condition targets an item",
    )
    target_item_type_code = Column(
        String(50),
        nullable=True,
        comment="target item type code if condition targets item type",
    )
    target_level = Column(Integer, nullable=True, comment="target farm level or recipe level")
    required_value = Column(BigInteger, nullable=True, comment="required progress value")
    required_weight_kg = Column(Numeric(6, 2), nullable=True, comment="required minimum fish weight in kg")
    sort_order = Column(Integer, nullable=False, default=0, comment="display sort order in category")
    is_active = Column(Boolean, nullable=False, default=True, comment="whether achievement is active")
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="created at")
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now(), comment="updated at")

    category = relationship("FarmAchievementCategory", back_populates="achievements")
    targetItem = relationship("Item", back_populates="targetAchievements")
    rewards = relationship(
        "FarmAchievementReward",
        back_populates="achievement",
        cascade="all, delete-orphan",
    )
    userAchievements = relationship(
        "UserFarmAchievement",
        back_populates="achievement",
        cascade="all, delete-orphan",
    )
