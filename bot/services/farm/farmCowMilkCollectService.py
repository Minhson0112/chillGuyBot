from datetime import datetime, timedelta

from bot.config.database import getDbSession
from bot.config.emoji import FARM_GAME_EMOJI
from bot.enums.toolStatus import ToolStatus
from bot.enums.toolType import ToolType
from bot.repository.farmCowShedRepository import FarmCowShedRepository
from bot.repository.farmRepository import FarmRepository
from bot.repository.farmToolEquipmentRepository import FarmToolEquipmentRepository
from bot.repository.itemRepository import ItemRepository
from bot.repository.userInventoryRepository import UserInventoryRepository
from bot.services.farm.dailyTaskProgressService import DailyTaskProgressService


class FarmCowMilkCollectService:
    MILK_ITEM_CODE = "milk"
    HUNGRY_INTERVAL_MINUTES = 30
    MILK_COLLECT_INTERVAL_MINUTES = 15
    MILK_COLLECT_EXP = 1

    DAILY_TASK_TYPE_MILK_COLLECT = "milk_collect"

    def collectMilk(self, userId: int):
        with getDbSession() as session:
            farmRepository = FarmRepository(session)
            farmCowShedRepository = FarmCowShedRepository(session)
            farmToolEquipmentRepository = FarmToolEquipmentRepository(session)
            itemRepository = ItemRepository(session)
            userInventoryRepository = UserInventoryRepository(session)
            dailyTaskProgressService = DailyTaskProgressService(session)

            farm = farmRepository.findByUserId(userId)

            if farm is None:
                return {
                    "success": False,
                    "message": "Bạn chưa có nông trại.",
                }

            cowShed = farmCowShedRepository.findByFarmId(farm.id)

            if cowShed is None:
                return {
                    "success": False,
                    "message": "Nông trại của bạn chưa có chuồng bò.",
                }

            if cowShed.cow_count <= 0:
                return {
                    "success": False,
                    "message": "Bạn chưa nuôi con bò nào.",
                }

            now = datetime.now()

            if self.isCowHungry(cowShed, now):
                return {
                    "success": False,
                    "message": "Bò đang đói. Bạn cần cho bò ăn rồi mới vắt được sữa.",
                }

            if not self.canCollectMilk(cowShed, now):
                remainingSeconds = self.calculateMilkCollectRemainingSeconds(cowShed, now)

                return {
                    "success": False,
                    "message": f"Chưa thể vắt sữa. Có thể vắt sau **{self.formatRemainingTime(remainingSeconds)}**.",
                }

            milkItem = itemRepository.findByCode(self.MILK_ITEM_CODE)

            if milkItem is None:
                return {
                    "success": False,
                    "message": "Không tìm thấy item sữa bò trong hệ thống.",
                }

            milkPailEquipment = farmToolEquipmentRepository.findByFarmIdAndToolTypeWithToolData(
                farmId=farm.id,
                toolType=ToolType.MILK_PAIL.value,
            )

            milkBonusQuantity = self.getMilkPailBonusQuantity(milkPailEquipment)
            milkQuantity = cowShed.cow_count + milkBonusQuantity

            userInventoryRepository.addOrCreate(
                userId=userId,
                itemId=milkItem.id,
                quantity=milkQuantity,
            )

            milkPailBroken = self.consumeMilkPailDurability(milkPailEquipment)

            farmCowShedRepository.markMilkCollected(cowShed)
            farmRepository.increaseFarmExp(farm, self.MILK_COLLECT_EXP)

            completedDailyTasks = dailyTaskProgressService.addProgress(
                userId=userId,
                taskType=self.DAILY_TASK_TYPE_MILK_COLLECT,
                amount=milkQuantity,
                targetItemId=milkItem.id,
            )

            dailyTaskMessage = dailyTaskProgressService.buildCompletedTaskMessage(
                completedDailyTasks,
            )

            session.commit()

            milkText = self.buildItemText(milkItem)

            message = f"Bạn đã vắt được **{milkQuantity}** {milkText}."

            if milkBonusQuantity > 0:
                message += f"\nXô vắt sữa đã bonus thêm **{milkBonusQuantity}** {milkText}."

            if milkPailBroken:
                message += "\nXô vắt sữa đã hết độ bền và bị hỏng."

            if dailyTaskMessage is not None:
                message += f"\n\n{dailyTaskMessage}"

            return {
                "success": True,
                "message": message,
            }

    def getMilkPailBonusQuantity(self, milkPailEquipment):
        if milkPailEquipment is None:
            return 0

        userTool = milkPailEquipment.user_tool

        if userTool is None:
            return 0

        if userTool.status == ToolStatus.BROKEN.value:
            return 0

        if userTool.current_durability <= 0:
            return 0

        toolTemplate = userTool.tool_template

        if toolTemplate is None:
            return 0

        return max(toolTemplate.milk_bonus_quantity, 0)

    def consumeMilkPailDurability(self, milkPailEquipment):
        if milkPailEquipment is None:
            return False

        userTool = milkPailEquipment.user_tool

        if userTool is None:
            return False

        if userTool.status == ToolStatus.BROKEN.value:
            return False

        if userTool.current_durability <= 0:
            userTool.status = ToolStatus.BROKEN.value
            return True

        toolTemplate = userTool.tool_template

        if toolTemplate is None:
            return False

        userTool.current_durability -= toolTemplate.durability_cost_per_use

        if userTool.current_durability <= 0:
            userTool.current_durability = 0
            userTool.status = ToolStatus.BROKEN.value
            return True

        return False

    def isCowHungry(self, cowShed, now: datetime):
        if cowShed.last_fed_at is None:
            return True

        hungryAt = cowShed.last_fed_at + timedelta(minutes=self.HUNGRY_INTERVAL_MINUTES)

        return now >= hungryAt

    def canCollectMilk(self, cowShed, now: datetime):
        if cowShed.last_collected_milk_at is None:
            return True

        collectableAt = cowShed.last_collected_milk_at + timedelta(
            minutes=self.MILK_COLLECT_INTERVAL_MINUTES,
        )

        return now >= collectableAt

    def calculateMilkCollectRemainingSeconds(self, cowShed, now: datetime):
        collectableAt = cowShed.last_collected_milk_at + timedelta(
            minutes=self.MILK_COLLECT_INTERVAL_MINUTES,
        )
        remainingSeconds = int((collectableAt - now).total_seconds())

        return max(remainingSeconds, 0)

    def buildItemText(self, item):
        itemEmoji = FARM_GAME_EMOJI.get(item.icon_image_key)

        if itemEmoji is None:
            return f"**{item.name}**"

        return f"{itemEmoji} **{item.name}**"

    def formatRemainingTime(self, remainingSeconds: int):
        minutes = remainingSeconds // 60
        seconds = remainingSeconds % 60

        return f"{minutes}:{seconds:02d}"