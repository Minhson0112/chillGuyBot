from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from bot.config.database import Base


class FoodRecipe(Base):
    __tablename__ = "food_recipes"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="food recipe id")

    result_item_id = Column(
        BigInteger,
        ForeignKey("items.id", ondelete="RESTRICT"),
        nullable=False,
        unique=True,
        comment="crafted food item id",
    )

    result_quantity = Column(Integer, nullable=False, default=1, comment="crafted food quantity")
    cooking_seconds = Column(Integer, nullable=False, comment="cooking duration in seconds")
    required_farm_level = Column(Integer, nullable=False, default=1, comment="required farm level to cook")
    is_active = Column(Boolean, nullable=False, default=True, comment="whether recipe is active")

    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="created at")
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="updated at",
    )

    resultItem = relationship("Item", back_populates="foodRecipe")
    ingredients = relationship(
        "FoodRecipeIngredient",
        back_populates="recipe",
        cascade="all, delete-orphan",
    )
    farmKitchens = relationship("FarmKitchen", back_populates="currentRecipe")