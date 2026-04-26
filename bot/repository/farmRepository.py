from sqlalchemy.orm import joinedload

from bot.models.farm import Farm
from bot.models.farmCropArea import FarmCropArea
from bot.models.crop import Crop


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
                joinedload(Farm.cropArea)
                .joinedload(FarmCropArea.crop)
                .joinedload(Crop.growthStages),
                joinedload(Farm.chickenCoop),
                joinedload(Farm.cowShed),
                joinedload(Farm.fishPond),
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