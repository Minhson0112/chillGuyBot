import random
from datetime import datetime, timedelta
from decimal import Decimal

from bot.config.database import getDbSession
from bot.config.emoji import FARM_GAME_EMOJI
from bot.repository.farmFishPondRepository import FarmFishPondRepository
from bot.repository.farmRepository import FarmRepository
from bot.repository.fishingHistoryRepository import FishingHistoryRepository
from bot.repository.itemRepository import ItemRepository
from bot.repository.userInventoryRepository import UserInventoryRepository


class FarmFishingService:
    BUG_ITEM_CODE = "bug"
    SEAFOOD_TYPE_CODE = "seafood"

    BUG_COST_PER_FISHING = 1
    EXP_PER_FISHING = 1

    FISHING_COOLDOWN_MINUTES = 5

    MIN_WEIGHT_KG = 1
    MAX_WEIGHT_KG = 100

    def fish(self, userId: int):
        with getDbSession() as session:
            farmRepository = FarmRepository(session)
            farmFishPondRepository = FarmFishPondRepository(session)
            itemRepository = ItemRepository(session)
            userInventoryRepository = UserInventoryRepository(session)
            fishingHistoryRepository = FishingHistoryRepository(session)

            farm = farmRepository.findByUserId(userId)

            if farm is None:
                return {
                    "success": False,
                    "message": "Bạn chưa có nông trại.",
                }

            fishPond = farmFishPondRepository.findByFarmId(farm.id)

            if fishPond is None:
                return {
                    "success": False,
                    "message": "Nông trại của bạn chưa có hồ câu cá.",
                }

            cooldownResult = self.checkFishingCooldown(fishPond)

            if not cooldownResult["canFish"]:
                return {
                    "success": False,
                    "message": (
                        f"Bạn vừa câu cá gần đây. "
                        f"Hãy chờ thêm **{cooldownResult['remainingTimeText']}** nữa."
                    ),
                }

            bugItem = itemRepository.findByCode(self.BUG_ITEM_CODE)

            if bugItem is None:
                return {
                    "success": False,
                    "message": "Không tìm thấy item mồi câu trong hệ thống.",
                }

            bugInventory = userInventoryRepository.findByUserIdAndItemId(
                userId=userId,
                itemId=bugItem.id,
            )

            bugText = self.buildItemText(bugItem)

            if bugInventory is None or bugInventory.quantity < self.BUG_COST_PER_FISHING:
                currentQuantity = bugInventory.quantity if bugInventory is not None else 0

                return {
                    "success": False,
                    "message": (
                        f"Bạn cần **{self.BUG_COST_PER_FISHING}** {bugText} để câu cá. "
                        f"Hiện có **{currentQuantity}**."
                    ),
                }

            seafoodItems = itemRepository.findActiveItemsByTypeCode(self.SEAFOOD_TYPE_CODE)

            if not seafoodItems:
                return {
                    "success": False,
                    "message": "Không tìm thấy dữ liệu cá trong hệ thống.",
                }

            caughtItem = self.randomSeafoodItem(seafoodItems)
            weightKg = self.randomWeightKg()

            userInventoryRepository.decreaseQuantity(
                userInventory=bugInventory,
                quantity=self.BUG_COST_PER_FISHING,
            )

            userInventoryRepository.addOrCreate(
                userId=userId,
                itemId=caughtItem.id,
                quantity=1,
            )

            fishingHistoryRepository.create(
                userId=userId,
                itemId=caughtItem.id,
                weightKg=weightKg,
            )

            farmFishPondRepository.markFished(fishPond)
            farmRepository.increaseFarmExp(farm, self.EXP_PER_FISHING)

            session.commit()

            caughtItemText = self.buildItemText(caughtItem)

            return {
                "success": True,
                "message": (
                    f"Bạn đã câu được {caughtItemText} nặng **{weightKg}kg**. "
                    f"Đã dùng **{self.BUG_COST_PER_FISHING}** {bugText}. "
                    f"Farm EXP +{self.EXP_PER_FISHING}."
                ),
            }

    def checkFishingCooldown(self, fishPond):
        if fishPond.last_fished_at is None:
            return {
                "canFish": True,
                "remainingTimeText": None,
            }

        now = datetime.now()
        nextFishAt = fishPond.last_fished_at + timedelta(minutes=self.FISHING_COOLDOWN_MINUTES)
        remainingSeconds = int((nextFishAt - now).total_seconds())

        if remainingSeconds <= 0:
            return {
                "canFish": True,
                "remainingTimeText": None,
            }

        return {
            "canFish": False,
            "remainingTimeText": self.formatRemainingTime(remainingSeconds),
        }

    def randomSeafoodItem(self, seafoodItems):
        return random.choice(seafoodItems)

    def randomWeightKg(self):
        randomRate = random.random()

        weight = self.MIN_WEIGHT_KG + (
            self.MAX_WEIGHT_KG - self.MIN_WEIGHT_KG
        ) * (randomRate ** 3)

        weight = round(weight, 2)

        return Decimal(str(weight))

    def buildItemText(self, item):
        itemEmoji = FARM_GAME_EMOJI.get(item.icon_image_key)

        if itemEmoji is None:
            return f"**{item.name}**"

        return f"{itemEmoji} **{item.name}**"

    def formatRemainingTime(self, remainingSeconds: int):
        minutes = remainingSeconds // 60
        seconds = remainingSeconds % 60

        return f"{minutes}:{seconds:02d}"