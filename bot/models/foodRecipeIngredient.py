from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from bot.config.database import Base


class FoodRecipeIngredient(Base):
    __tablename__ = "food_recipe_ingredients"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="food recipe ingredient id")

    recipe_id = Column(
        BigInteger,
        ForeignKey("food_recipes.id", ondelete="CASCADE"),
        nullable=False,
        comment="food recipe id",
    )

    item_id = Column(
        BigInteger,
        ForeignKey("items.id", ondelete="RESTRICT"),
        nullable=False,
        comment="ingredient item id",
    )

    quantity = Column(Integer, nullable=False, comment="required ingredient quantity")

    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="created at")
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="updated at",
    )

    recipe = relationship("FoodRecipe", back_populates="ingredients")
    item = relationship("Item", back_populates="foodRecipeIngredients")