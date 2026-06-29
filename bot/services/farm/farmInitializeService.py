from bot.repository.baseSkinMasterRepository import BaseSkinMasterRepository
from bot.repository.farmRepository import FarmRepository
from bot.repository.farmCropAreaRepository import FarmCropAreaRepository
from bot.repository.farmChickenCoopRepository import FarmChickenCoopRepository
from bot.repository.farmCowShedRepository import FarmCowShedRepository
from bot.repository.farmFishPondRepository import FarmFishPondRepository
from bot.repository.farmKitchenRepository import FarmKitchenRepository
from bot.repository.memberBaseSkinInventoryRepository import MemberBaseSkinInventoryRepository


class FarmInitializeService:
    DEFAULT_UNLOCKED_PLOT_COUNT = 1

    def initializeFarmForMember(self, session, userId: int, isBot: bool = False):
        if isBot:
            return None

        farmRepository = FarmRepository(session)
        farmCropAreaRepository = FarmCropAreaRepository(session)
        farmChickenCoopRepository = FarmChickenCoopRepository(session)
        farmCowShedRepository = FarmCowShedRepository(session)
        farmFishPondRepository = FarmFishPondRepository(session)
        farmKitchenRepository = FarmKitchenRepository(session)
        baseSkinMasterRepository = BaseSkinMasterRepository(session)
        memberBaseSkinInventoryRepository = MemberBaseSkinInventoryRepository(session)

        farm = farmRepository.findByUserId(userId)

        if farm is None:
            farm = farmRepository.createDefaultFarm(userId)

        baseSkin = baseSkinMasterRepository.findByCode("base")

        if baseSkin is None:
            raise ValueError("Default base skin not found")

        baseSkinInventory = memberBaseSkinInventoryRepository.findByUserIdAndBaseSkinId(
            userId=userId,
            baseSkinId=baseSkin.id,
        )

        if baseSkinInventory is None:
            memberBaseSkinInventoryRepository.create(
                userId=userId,
                baseSkinId=baseSkin.id,
                isUsing=True,
            )

        farmCropArea = farmCropAreaRepository.findByFarmId(farm.id)

        if farmCropArea is None:
            farmCropAreaRepository.createDefaultCropArea(
                farmId=farm.id,
                unlockedPlotCount=self.DEFAULT_UNLOCKED_PLOT_COUNT,
            )

        chickenCoop = farmChickenCoopRepository.findByFarmId(farm.id)

        if chickenCoop is None:
            farmChickenCoopRepository.createDefaultChickenCoop(farm.id)

        cowShed = farmCowShedRepository.findByFarmId(farm.id)

        if cowShed is None:
            farmCowShedRepository.createDefaultCowShed(farm.id)

        fishPond = farmFishPondRepository.findByFarmId(farm.id)

        if fishPond is None:
            farmFishPondRepository.createDefaultFishPond(farm.id)

        kitchen = farmKitchenRepository.findByFarmId(farm.id)

        if kitchen is None:
            farmKitchenRepository.createDefaultKitchen(farm.id)

        return farm
