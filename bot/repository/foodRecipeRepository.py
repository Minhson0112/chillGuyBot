from sqlalchemy import asc, desc
from sqlalchemy.orm import joinedload

from bot.models.foodRecipe import FoodRecipe
from bot.models.foodRecipeIngredient import FoodRecipeIngredient


class FoodRecipeRepository:
    def __init__(self, session):
        self.session = session

    def countActiveRecipes(self):
        return (
            self.session.query(FoodRecipe)
            .filter(FoodRecipe.is_active.is_(True))
            .count()
        )

    def findActiveRecipesByPage(self, page: int, perPage: int):
        offset = (page - 1) * perPage

        return (
            self.session.query(FoodRecipe)
            .options(
                joinedload(FoodRecipe.resultItem),
                joinedload(FoodRecipe.ingredients).joinedload(FoodRecipeIngredient.item),
            )
            .filter(FoodRecipe.is_active.is_(True))
            .order_by(
                asc(FoodRecipe.required_farm_level),
                asc(FoodRecipe.id),
            )
            .offset(offset)
            .limit(perPage)
            .all()
        )

    def findByIdWithIngredients(self, recipeId: int):
        return (
            self.session.query(FoodRecipe)
            .options(
                joinedload(FoodRecipe.resultItem),
                joinedload(FoodRecipe.ingredients).joinedload(FoodRecipeIngredient.item),
            )
            .filter(FoodRecipe.id == recipeId)
            .first()
        )
    
    def findByResultItemIdWithIngredients(self, resultItemId: int):
        return (
            self.session.query(FoodRecipe)
            .options(
                joinedload(FoodRecipe.resultItem),
                joinedload(FoodRecipe.ingredients).joinedload(FoodRecipeIngredient.item),
            )
            .filter(FoodRecipe.result_item_id == resultItemId)
            .first()
        )