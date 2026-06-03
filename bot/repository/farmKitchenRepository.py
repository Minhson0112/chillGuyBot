from sqlalchemy.orm import joinedload

from bot.models.farm import Farm
from bot.models.farmKitchen import FarmKitchen
from bot.models.foodRecipe import FoodRecipe


class FarmKitchenRepository:
    def __init__(self, session):
        self.session = session

    def findByFarmId(self, farmId: int):
        return (
            self.session.query(FarmKitchen)
            .filter(FarmKitchen.farm_id == farmId)
            .first()
        )

    def createDefaultKitchen(self, farmId: int):
        farmKitchen = FarmKitchen(
            farm_id=farmId,
            current_recipe_id=None,
            cooking_quantity=0,
            started_at=None,
            finished_at=None,
            total_cooking_seconds=0,
            status="idle",
        )

        self.session.add(farmKitchen)
        self.session.flush()

        return farmKitchen

    def createIfNotExists(self, farmId: int):
        farmKitchen = self.findByFarmId(farmId)

        if farmKitchen is not None:
            return farmKitchen

        return self.createDefaultKitchen(farmId)

    def resetKitchen(self, farmKitchen: FarmKitchen):
        farmKitchen.current_recipe_id = None
        farmKitchen.cooking_quantity = 0
        farmKitchen.started_at = None
        farmKitchen.finished_at = None
        farmKitchen.total_cooking_seconds = 0
        farmKitchen.status = "idle"

        self.session.flush()

        return farmKitchen
    
    def startCooking(
        self,
        farmKitchen,
        recipeId: int,
        cookingQuantity: int,
        startedAt,
        finishedAt,
        totalCookingSeconds: int,
    ):
        farmKitchen.current_recipe_id = recipeId
        farmKitchen.cooking_quantity = cookingQuantity
        farmKitchen.started_at = startedAt
        farmKitchen.finished_at = finishedAt
        farmKitchen.total_cooking_seconds = totalCookingSeconds
        farmKitchen.status = "cooking"

        self.session.flush()

        return farmKitchen
    
    def findByFarmIdWithCurrentRecipe(self, farmId: int):
        return (
            self.session.query(FarmKitchen)
            .options(
                joinedload(FarmKitchen.currentRecipe)
                .joinedload(FoodRecipe.resultItem)
            )
            .filter(FarmKitchen.farm_id == farmId)
            .first()
        )

    def findFinishedKitchensNeedNotification(self, now):
        return (
            self.session.query(FarmKitchen)
            .options(
                joinedload(FarmKitchen.farm).joinedload(Farm.member),
                joinedload(FarmKitchen.currentRecipe)
                .joinedload(FoodRecipe.resultItem),
            )
            .filter(FarmKitchen.current_recipe_id.isnot(None))
            .filter(FarmKitchen.cooking_quantity > 0)
            .filter(FarmKitchen.finished_at <= now)
            .filter(FarmKitchen.status == "cooking")
            .all()
        )

    def markCookedReadyNotified(self, farmKitchen: FarmKitchen):
        farmKitchen.status = "cooked_ready_notified"

        self.session.flush()

        return farmKitchen
