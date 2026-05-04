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
from bot.services.farm.dailyTaskProgressService import DailyTaskProgressService


class FarmFishingService:
    BUG_ITEM_CODE = "bug"
    SEAFOOD_TYPE_CODE = "seafood"

    BUG_COST_PER_FISHING = 1
    EXP_PER_FISHING = 1

    FISHING_COOLDOWN_MINUTES = 5
    FISH_LINE_BREAK_RATE = 0.3

    MIN_WEIGHT_KG = 1
    MAX_WEIGHT_KG = 100

    DAILY_TASK_TYPE_FISHING = "fishing"

    def fish(self, userId: int):
        with getDbSession() as session:
            farmRepository = FarmRepository(session)
            farmFishPondRepository = FarmFishPondRepository(session)
            itemRepository = ItemRepository(session)
            userInventoryRepository = UserInventoryRepository(session)
            fishingHistoryRepository = FishingHistoryRepository(session)
            dailyTaskProgressService = DailyTaskProgressService(session)

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

            userInventoryRepository.decreaseQuantity(
                userInventory=bugInventory,
                quantity=self.BUG_COST_PER_FISHING,
            )

            farmFishPondRepository.markFished(fishPond)

            if self.isFishingLineBroken():
                session.commit()

                return {
                    "success": True,
                    "message": (
                        f"Bạn bị đứt dây câu, câu được cái nịt. "
                        f"Đã dùng **{self.BUG_COST_PER_FISHING}** {bugText}."
                    ),
                }

            seafoodItems = itemRepository.findActiveItemsByTypeCode(self.SEAFOOD_TYPE_CODE)

            if not seafoodItems:
                session.rollback()

                return {
                    "success": False,
                    "message": "Không tìm thấy dữ liệu cá trong hệ thống.",
                }

            caughtItem = self.randomSeafoodItem(seafoodItems)
            weightKg = self.randomWeightKg()

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

            farmRepository.increaseFarmExp(farm, self.EXP_PER_FISHING)

            completedDailyTasks = dailyTaskProgressService.addProgress(
                userId=userId,
                taskType=self.DAILY_TASK_TYPE_FISHING,
                amount=1,
                targetItemId=caughtItem.id,
            )

            dailyTaskMessage = dailyTaskProgressService.buildCompletedTaskMessage(
                completedDailyTasks,
            )

            session.commit()

            caughtItemText = self.buildItemText(caughtItem)

            message = (
                f"Bạn đã câu được {caughtItemText} nặng **{weightKg}kg**. "
                f"Đã dùng **{self.BUG_COST_PER_FISHING}** {bugText}. "
                f"Farm EXP +{self.EXP_PER_FISHING}."
            )

            if dailyTaskMessage is not None:
                message += f"\n\n{dailyTaskMessage}"

            return {
                "success": True,
                "message": message,
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

    def isFishingLineBroken(self):
        return random.random() < self.FISH_LINE_BREAK_RATE

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