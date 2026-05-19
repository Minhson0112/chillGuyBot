from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from bot.config.database import Base


class FarmKitchen(Base):
    __tablename__ = "farm_kitchen"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="farm kitchen id")

    farm_id = Column(
        BigInteger,
        ForeignKey("farm.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        comment="farm id",
    )

    current_recipe_id = Column(
        BigInteger,
        ForeignKey("food_recipes.id", ondelete="SET NULL"),
        nullable=True,
        comment="current cooking recipe id",
    )

    cooking_quantity = Column(Integer, nullable=False, default=0, comment="cooking quantity")

    started_at = Column(DateTime, nullable=True, comment="cooking started at")
    finished_at = Column(DateTime, nullable=True, comment="cooking finished at")

    total_cooking_seconds = Column(
        Integer,
        nullable=False,
        default=0,
        comment="total cooking duration in seconds",
    )

    status = Column(String(50), nullable=False, default="idle", comment="kitchen status")

    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="created at")
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="updated at",
    )

    farm = relationship("Farm", back_populates="kitchen")
    currentRecipe = relationship("FoodRecipe", back_populates="farmKitchens")