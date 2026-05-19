import random

from bot.config.database import getDbSession
from bot.config.emoji import FARM_GAME_EMOJI
from bot.repository.farmRepository import FarmRepository
from bot.repository.farmTrainEventRepository import FarmTrainEventRepository
from bot.repository.itemRepository import ItemRepository


class FarmTrainEventAutoService:
    CREATED_BY_USER_ID = 1479763866782142706

    BONUS_CHILL_COIN_MIN = 150
    BONUS_CHILL_COIN_MAX = 300

    def runAutoTrainEvent(self):
        with getDbSession() as session:
            itemRepository = ItemRepository(session)
            farmRepository = FarmRepository(session)
            farmTrainEventRepository = FarmTrainEventRepository(session)

            closedTrainEvent = farmTrainEventRepository.closeLatestEvent()
            farmRepository.updateAllTrainEventFlag(False)

            foodRow = itemRepository.findRandomFoodItemWithRecipe()

            if foodRow is None:
                session.commit()

                return {
                    "success": False,
                    "message": "Không tìm thấy item food có recipe để tạo sự kiện tàu hỏa.",
                }

            item, foodRecipe = foodRow

            requiredFarmLevel = foodRecipe.required_farm_level
            requiredQuantity = self.randomRequiredQuantity(requiredFarmLevel)

            rewardChillCoin = self.calculateRewardChillCoin(
                item=item,
                requiredQuantity=requiredQuantity,
            )

            rewardExp = self.randomRewardExp(requiredFarmLevel)

            farmTrainEvent = farmTrainEventRepository.create(
                requiredItemId=item.id,
                requiredQuantity=requiredQuantity,
                rewardChillCoin=rewardChillCoin,
                rewardExp=rewardExp,
                createdByUserId=self.CREATED_BY_USER_ID,
            )

            farmRepository.updateAllTrainEventFlag(True)

            session.commit()

            itemText = self.buildItemText(item)
            chillCoinEmoji = FARM_GAME_EMOJI["chill_coin"]

            message = (
                f"Đã tự động tạo sự kiện tàu hỏa **#{farmTrainEvent.id}**.\n"
                f"Yêu cầu: **{self.formatNumber(requiredQuantity)}** {itemText}\n"
                f"Thưởng: **{self.formatNumber(rewardChillCoin)}** {chillCoinEmoji} "
                f"và **{self.formatNumber(rewardExp)} EXP**."
            )

            if closedTrainEvent is not None:
                message = f"Đã đóng sự kiện tàu hỏa **#{closedTrainEvent.id}**.\n" + message

            return {
                "success": True,
                "message": message,
            }

    def randomRequiredQuantity(self, requiredFarmLevel: int):
        if requiredFarmLevel == 1:
            return random.randint(5, 15)

        if requiredFarmLevel == 2:
            return random.randint(3, 6)

        if requiredFarmLevel == 3:
            return random.randint(2, 4)

        if requiredFarmLevel == 4:
            return random.randint(1, 3)

        return random.randint(1, 3)

    def randomRewardExp(self, requiredFarmLevel: int):
        if requiredFarmLevel == 1:
            return random.randint(20, 30)

        if requiredFarmLevel == 2:
            return random.randint(30, 40)

        if requiredFarmLevel == 3:
            return random.randint(40, 50)

        if requiredFarmLevel == 4:
            return random.randint(50, 60)

        return random.randint(50, 60)

    def calculateRewardChillCoin(
        self,
        item,
        requiredQuantity: int,
    ):
        sellPrice = item.sell_price or 0
        bonusChillCoin = random.randint(
            self.BONUS_CHILL_COIN_MIN,
            self.BONUS_CHILL_COIN_MAX,
        )

        return sellPrice * requiredQuantity + bonusChillCoin

    def buildItemText(self, item):
        itemEmoji = FARM_GAME_EMOJI.get(item.icon_image_key)

        if itemEmoji is None:
            return f"**{item.name}**"

        return f"{itemEmoji} **{item.name}**"

    def formatNumber(self, number: int):
        return f"{number:,}"