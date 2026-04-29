from sqlalchemy.orm import joinedload

from bot.models.farm import Farm
from bot.models.farmCropArea import FarmCropArea
from bot.models.crop import Crop
from bot.models.farmKitchen import FarmKitchen
from bot.models.foodRecipe import FoodRecipe
from bot.config.farmLevel import FARM_MAX_LEVEL, FARM_LEVEL_REQUIRED_EXP


class FarmRepository:
    def __init__(self, session):
        self.session = session

    def createDefaultFarm(self, userId: int):
        farm = Farm(
            user_id=userId,
            farm_level=1,
            farm_exp=0,
            base_image_key="farm_base",
            is_train_event=False,
        )

        self.session.add(farm)
        self.session.flush()

        return farm

    def findById(self, farmId: int):
        return (
            self.session.query(Farm)
            .filter(Farm.id == farmId)
            .first()
        )

    def findByUserId(self, userId: int):
        return (
            self.session.query(Farm)
            .filter(Farm.user_id == userId)
            .first()
        )

    def findByUserIdWithRenderData(self, userId: int):
        return (
            self.session.query(Farm)
            .options(
                joinedload(Farm.member),
                joinedload(Farm.cropArea)
                .joinedload(FarmCropArea.crop)
                .joinedload(Crop.growthStages),
                joinedload(Farm.cropArea)
                .joinedload(FarmCropArea.crop)
                .joinedload(Crop.cropItem),
                joinedload(Farm.chickenCoop),
                joinedload(Farm.cowShed),
                joinedload(Farm.fishPond),
                joinedload(Farm.kitchen)
                .joinedload(FarmKitchen.currentRecipe)
                .joinedload(FoodRecipe.resultItem),
            )
            .filter(Farm.user_id == userId)
            .first()
        )

    def findOrCreateDefaultFarm(self, userId: int):
        farm = self.findByUserId(userId)

        if farm is not None:
            return farm

        return self.createDefaultFarm(userId)

    def updateFarmExp(self, farm: Farm, farmExp: int):
        farm.farm_exp = farmExp
        self.session.flush()

        return farm

    def increaseFarmExp(self, farm: Farm, exp: int):
        farm.farm_exp += exp
        self.session.flush()

        return farm

    def updateFarmLevel(self, farm: Farm, farmLevel: int):
        farm.farm_level = farmLevel
        self.session.flush()

        return farm

    def activateTrainEvent(self, farm: Farm):
        farm.is_train_event = True
        self.session.flush()

        return farm

    def deactivateTrainEvent(self, farm: Farm):
        farm.is_train_event = False
        self.session.flush()

        return farm

    def updateBaseImageKey(self, farm: Farm, baseImageKey: str):
        farm.base_image_key = baseImageKey
        self.session.flush()

        return farm
    
    def increaseFarmExp(self, farm, exp: int):
        if exp <= 0:
            return farm

        if farm.farm_level >= FARM_MAX_LEVEL:
            farm.farm_exp = 0
            self.session.flush()
            return farm

        farm.farm_exp += exp

        while farm.farm_level < FARM_MAX_LEVEL:
            requiredExp = self.getRequiredExpToNextLevel(farm.farm_level)

            if requiredExp is None:
                break

            if farm.farm_exp < requiredExp:
                break

            farm.farm_exp -= requiredExp
            farm.farm_level += 1

            if farm.farm_level >= FARM_MAX_LEVEL:
                farm.farm_exp = 0
                break

        self.session.flush()

        return farm

    def getRequiredExpToNextLevel(self, currentLevel: int):
        if currentLevel >= FARM_MAX_LEVEL:
            return None

        nextLevel = currentLevel + 1

        currentLevelTotalExp = FARM_LEVEL_REQUIRED_EXP.get(currentLevel)
        nextLevelTotalExp = FARM_LEVEL_REQUIRED_EXP.get(nextLevel)

        if currentLevelTotalExp is None or nextLevelTotalExp is None:
            return None

        return nextLevelTotalExp - currentLevelTotalExp
    
    def updateAllTrainEventFlag(self, isTrainEvent: bool):
        self.session.query(Farm).update(
            {
                Farm.is_train_event: isTrainEvent,
            },
            synchronize_session=False,
        )

        self.session.flush()

    def updateTrainEventFlag(self, farm, isTrainEvent: bool):
        farm.is_train_event = isTrainEvent

        self.session.flush()

        return farm