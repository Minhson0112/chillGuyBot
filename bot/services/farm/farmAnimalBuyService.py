from bot.repository.farmChickenCoopRepository import FarmChickenCoopRepository
from bot.repository.farmCowShedRepository import FarmCowShedRepository


class FarmAnimalBuyService:
    CHICKEN_CODE = "chicken"
    COW_CODE = "cow"

    MAX_CHICKEN_COUNT = 2
    MAX_COW_COUNT = 1

    def canHandle(self, itemCode: str):
        return itemCode in [
            self.CHICKEN_CODE,
            self.COW_CODE,
        ]

    def buyAnimal(self, session, farm, itemCode: str):
        if itemCode == self.CHICKEN_CODE:
            return self.buyChicken(session, farm)

        if itemCode == self.COW_CODE:
            return self.buyCow(session, farm)

        return {
            "success": False,
            "message": "Item này không phải vật nuôi.",
        }

    def buyChicken(self, session, farm):
        farmChickenCoopRepository = FarmChickenCoopRepository(session)
        chickenCoop = farmChickenCoopRepository.findByFarmId(farm.id)

        if chickenCoop is None:
            return {
                "success": False,
                "message": "Nông trại của bạn chưa có chuồng gà.",
            }

        if chickenCoop.chicken_count >= self.MAX_CHICKEN_COUNT:
            return {
                "success": False,
                "message": f"Chuồng gà đã đầy. Bạn chỉ có thể nuôi tối đa **{self.MAX_CHICKEN_COUNT}** con gà.",
            }

        farmChickenCoopRepository.increaseChickenCount(chickenCoop)

        return {
            "success": True,
            "message": "Bạn đã mua thêm **1** con gà.",
        }

    def buyCow(self, session, farm):
        farmCowShedRepository = FarmCowShedRepository(session)
        cowShed = farmCowShedRepository.findByFarmId(farm.id)

        if cowShed is None:
            return {
                "success": False,
                "message": "Nông trại của bạn chưa có chuồng bò.",
            }

        if cowShed.cow_count >= self.MAX_COW_COUNT:
            return {
                "success": False,
                "message": f"Chuồng bò đã đầy. Bạn chỉ có thể nuôi tối đa **{self.MAX_COW_COUNT}** con bò.",
            }

        farmCowShedRepository.increaseCowCount(cowShed)

        return {
            "success": True,
            "message": "Bạn đã mua thêm **1** con bò.",
        }