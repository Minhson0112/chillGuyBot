from sqlalchemy import func

from bot.models.farmCookingHistory import FarmCookingHistory
from bot.models.foodRecipe import FoodRecipe


class FarmCookingHistoryRepository:
    def __init__(self, session):
        self.session = session

    def create(
        self,
        userId: int,
        itemId: int,
        quantity: int,
    ):
        farmCookingHistory = FarmCookingHistory(
            user_id=userId,
            item_id=itemId,
            quantity=quantity,
        )

        self.session.add(farmCookingHistory)
        self.session.flush()

        return farmCookingHistory

    def countRequiredRecipesByLevel(
        self,
        level: int,
    ):
        return (
            self.session.query(func.count(FoodRecipe.id))
            .filter(FoodRecipe.required_farm_level == level)
            .filter(FoodRecipe.is_active.is_(True))
            .scalar()
            or 0
        )

    def countDistinctCookedRecipesByUserIdAndLevel(
        self,
        userId: int,
        level: int,
    ):
        return (
            self.session.query(func.count(func.distinct(FoodRecipe.id)))
            .join(FarmCookingHistory, FarmCookingHistory.item_id == FoodRecipe.result_item_id)
            .filter(FoodRecipe.required_farm_level == level)
            .filter(FoodRecipe.is_active.is_(True))
            .filter(FarmCookingHistory.user_id == userId)
            .scalar()
            or 0
        )
