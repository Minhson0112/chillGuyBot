from datetime import datetime, timedelta

from bot.config.database import getDbSession
from bot.helper.farmItemHelper import buildItemText
from bot.repository.farmChickenCoopRepository import FarmChickenCoopRepository
from bot.repository.farmRepository import FarmRepository
from bot.repository.itemRepository import ItemRepository
from bot.repository.userInventoryRepository import UserInventoryRepository
from bot.services.farm.dailyTaskProgressService import DailyTaskProgressService


class FarmChickenEggCollectService:
    EGG_ITEM_CODE = "egg"
    HUNGRY_INTERVAL_MINUTES = 30
    EGG_COLLECT_INTERVAL_MINUTES = 10
    EGG_COLLECT_EXP = 1

    DAILY_TASK_TYPE_EGG_COLLECT = "egg_collect"

    def collectEgg(self, userId: int):
        with getDbSession() as session:
            farmRepository = FarmRepository(session)
            farmChickenCoopRepository = FarmChickenCoopRepository(session)
            itemRepository = ItemRepository(session)
            userInventoryRepository = UserInventoryRepository(session)
            dailyTaskProgressService = DailyTaskProgressService(session)

            farm = farmRepository.findByUserId(userId)

            if farm is None:
                return {
                    "success": False,
                    "message": "Bạn chưa có nông trại.",
                }

            chickenCoop = farmChickenCoopRepository.findByFarmId(farm.id)

            if chickenCoop is None:
                return {
                    "success": False,
                    "message": "Nông trại của bạn chưa có chuồng gà.",
                }

            if chickenCoop.chicken_count <= 0:
                return {
                    "success": False,
                    "message": "Bạn chưa nuôi con gà nào.",
                }

            now = datetime.now()

            if self.isChickenHungry(chickenCoop, now):
                return {
                    "success": False,
                    "message": "Gà đang đói. Bạn cần cho gà ăn rồi mới lấy được trứng.",
                }

            if not self.canCollectEgg(chickenCoop, now):
                remainingSeconds = self.calculateEggCollectRemainingSeconds(chickenCoop, now)

                return {
                    "success": False,
                    "message": f"Chưa thể lấy trứng. Có thể lấy sau **{self.formatRemainingTime(remainingSeconds)}**.",
                }

            eggItem = itemRepository.findByCode(self.EGG_ITEM_CODE)

            if eggItem is None:
                return {
                    "success": False,
                    "message": "Không tìm thấy item trứng gà trong hệ thống.",
                }

            eggQuantity = chickenCoop.chicken_count

            userInventoryRepository.addOrCreate(
                userId=userId,
                itemId=eggItem.id,
                quantity=eggQuantity,
            )

            farmChickenCoopRepository.markEggCollected(chickenCoop)
            farmRepository.increaseFarmExp(farm, self.EGG_COLLECT_EXP)

            completedDailyTasks = dailyTaskProgressService.addProgress(
                userId=userId,
                taskType=self.DAILY_TASK_TYPE_EGG_COLLECT,
                amount=eggQuantity,
                targetItemId=eggItem.id,
            )

            dailyTaskMessage = dailyTaskProgressService.buildCompletedTaskMessage(
                completedDailyTasks,
            )

            session.commit()

            eggText = buildItemText(eggItem)

            message = f"Bạn đã lấy được **{eggQuantity}** {eggText}."

            if dailyTaskMessage is not None:
                message += f"\n\n{dailyTaskMessage}"

            return {
                "success": True,
                "message": message,
            }

    def isChickenHungry(self, chickenCoop, now: datetime):
        if chickenCoop.last_fed_at is None:
            return True

        hungryAt = chickenCoop.last_fed_at + timedelta(minutes=self.HUNGRY_INTERVAL_MINUTES)

        return now >= hungryAt

    def canCollectEgg(self, chickenCoop, now: datetime):
        if chickenCoop.last_collected_egg_at is None:
            return True

        collectableAt = chickenCoop.last_collected_egg_at + timedelta(
            minutes=self.EGG_COLLECT_INTERVAL_MINUTES,
        )

        return now >= collectableAt

    def calculateEggCollectRemainingSeconds(self, chickenCoop, now: datetime):
        collectableAt = chickenCoop.last_collected_egg_at + timedelta(
            minutes=self.EGG_COLLECT_INTERVAL_MINUTES,
        )
        remainingSeconds = int((collectableAt - now).total_seconds())

        return max(remainingSeconds, 0)

    def formatRemainingTime(self, remainingSeconds: int):
        minutes = remainingSeconds // 60
        seconds = remainingSeconds % 60

        return f"{minutes}:{seconds:02d}"
