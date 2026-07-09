from sqlalchemy import BigInteger, Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from bot.config.database import Base


class FarmAchievementCategory(Base):
    __tablename__ = "farm_achievement_categories"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="farm achievement category id")
    category_code = Column(String(100), nullable=False, unique=True, comment="unique category code")
    name = Column(String(255), nullable=False, comment="category display name")
    description = Column(String(500), nullable=True, comment="category description")
    sort_order = Column(Integer, nullable=False, default=0, comment="display sort order")
    is_active = Column(Boolean, nullable=False, default=True, comment="whether category is active")
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="created at")
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now(), comment="updated at")

    achievements = relationship(
        "FarmAchievementMaster",
        back_populates="category",
        cascade="all, delete-orphan",
    )
