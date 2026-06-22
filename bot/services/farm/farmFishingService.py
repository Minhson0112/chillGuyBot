import random
from datetime import datetime, timedelta
from decimal import Decimal

from bot.config.database import getDbSession
from bot.helper.timeFormatHelper import formatMinutesSeconds
from bot.helper.farmItemHelper import buildItemText
from bot.enums.toolStatus import ToolStatus
from bot.enums.toolType import ToolType
from bot.repository.farmFishPondRepository import FarmFishPondRepository
from bot.repository.farmRepository import FarmRepository
from bot.repository.farmToolEquipmentRepository import FarmToolEquipmentRepository
from bot.repository.fishingHistoryRepository import FishingHistoryRepository
from bot.repository.itemRepository import ItemRepository
from bot.repository.userInventoryRepository import UserInventoryRepository
from bot.services.farm.dailyTaskProgressService import DailyTaskProgressService


class FarmFishingService:
    BUG_ITEM_CODE = "bug"
    SEAFOOD_TYPE_CODE = "seafood"

    BUG_COST_PER_FISHING = 1
    EXP_PER_FISHING = 1

    FISHING_COOLDOWN_SECONDS = 300
    DEFAULT_FISHING_SUCCESS_RATE = 0.50
    DEFAULT_FISHING_CATCH_QUANTITY = 1

    MIN_WEIGHT_KG = 1
    MAX_WEIGHT_KG = 100

    DAILY_TASK_TYPE_FISHING = "fishing"

    def fish(self, userId: int):
        with getDbSession() as session:
            farmRepository = FarmRepository(session)
            farmFishPondRepository = FarmFishPondRepository(session)
            farmToolEquipmentRepository = FarmToolEquipmentRepository(session)
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

            fishingRodEquipment = farmToolEquipmentRepository.findByFarmIdAndToolTypeWithToolData(
                farmId=farm.id,
                toolType=ToolType.FISHING_ROD.value,
            )

            fishingCooldownReductionSeconds = self.getFishingCooldownReductionSeconds(
                fishingRodEquipment,
            )

            cooldownResult = self.checkFishingCooldown(
                fishPond=fishPond,
                cooldownReductionSeconds=fishingCooldownReductionSeconds,
            )

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

            bugText = buildItemText(bugItem)

            if bugInventory is None or bugInventory.quantity < self.BUG_COST_PER_FISHING:
                currentQuantity = bugInventory.quantity if bugInventory is not None else 0

                return {
                    "success": False,
                    "message": (
                        f"Bạn cần **{self.BUG_COST_PER_FISHING}** {bugText} để câu cá. "
                        f"Hiện có **{currentQuantity}**."
                    ),
                }

            fishingCatchQuantity = min(
                self.getFishingCatchQuantity(fishingRodEquipment),
                bugInventory.quantity,
            )

            userInventoryRepository.decreaseQuantity(
                userInventory=bugInventory,
                quantity=fishingCatchQuantity,
            )

            farmFishPondRepository.markFished(fishPond)

            fishingSuccessRate = self.getFishingSuccessRate(fishingRodEquipment)
            fishingRodBroken = self.consumeFishingRodDurability(fishingRodEquipment)

            if not self.isFishingSuccess(fishingSuccessRate):
                completedDailyTasks = dailyTaskProgressService.addProgress(
                    userId=userId,
                    taskType=self.DAILY_TASK_TYPE_FISHING,
                    amount=1,
                    targetItemId=None,
                )

                dailyTaskMessage = dailyTaskProgressService.buildCompletedTaskMessage(
                    completedDailyTasks,
                )

                session.commit()

                message = (
                    f"Bạn bị đứt dây câu, câu được cái nịt. "
                    f"Đã dùng **{fishingCatchQuantity}** {bugText}."
                )

                if fishingRodEquipment is not None:
                    message += f"\nTỉ lệ câu thành công hiện tại là **{int(fishingSuccessRate * 100)}%**."

                if fishingRodBroken:
                    message += "\nCần câu đã hết độ bền và bị hỏng."

                if dailyTaskMessage is not None:
                    message += f"\n\n{dailyTaskMessage}"

                return {
                    "success": True,
                    "message": message,
                }

            seafoodItems = itemRepository.findActiveItemsByTypeCode(self.SEAFOOD_TYPE_CODE)

            if not seafoodItems:
                session.rollback()

                return {
                    "success": False,
                    "message": "Không tìm thấy dữ liệu cá trong hệ thống.",
                }

            caughtResults = []

            for _ in range(fishingCatchQuantity):
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

                caughtResults.append({
                    "item": caughtItem,
                    "weightKg": weightKg,
                })

            farmRepository.increaseFarmExp(farm, self.EXP_PER_FISHING)

            completedDailyTasks = dailyTaskProgressService.addProgress(
                userId=userId,
                taskType=self.DAILY_TASK_TYPE_FISHING,
                amount=1,
                targetItemId=caughtResults[0]["item"].id,
            )

            dailyTaskMessage = dailyTaskProgressService.buildCompletedTaskMessage(
                completedDailyTasks,
            )

            session.commit()

            caughtFishMessages = []

            for caughtResult in caughtResults:
                caughtItemText = buildItemText(caughtResult["item"])
                caughtFishMessages.append(
                    f"- {caughtItemText} nặng **{caughtResult['weightKg']}kg**"
                )

            caughtFishText = "\n".join(caughtFishMessages)

            message = (
                f"Bạn đã câu được **{fishingCatchQuantity}** con cá:\n"
                f"{caughtFishText}\n"
                f"Đã dùng **{fishingCatchQuantity}** {bugText}. "
                f"Farm EXP +{self.EXP_PER_FISHING}."
            )

            if fishingRodEquipment is not None:
                message += f"\nTỉ lệ câu thành công hiện tại là **{int(fishingSuccessRate * 100)}%**."

            if fishingRodBroken:
                message += "\nCần câu đã hết độ bền và bị hỏng."

            if dailyTaskMessage is not None:
                message += f"\n\n{dailyTaskMessage}"

            return {
                "success": True,
                "message": message,
            }

    def checkFishingCooldown(
        self,
        fishPond,
        cooldownReductionSeconds: int = 0,
    ):
        if fishPond.last_fished_at is None:
            return {
                "canFish": True,
                "remainingTimeText": None,
            }

        cooldownSeconds = max(
            self.FISHING_COOLDOWN_SECONDS - cooldownReductionSeconds,
            0,
        )

        now = datetime.now()
        nextFishAt = fishPond.last_fished_at + timedelta(seconds=cooldownSeconds)
        remainingSeconds = int((nextFishAt - now).total_seconds())

        if remainingSeconds <= 0:
            return {
                "canFish": True,
                "remainingTimeText": None,
            }

        return {
            "canFish": False,
            "remainingTimeText": formatMinutesSeconds(remainingSeconds),
        }

    def getFishingSuccessRate(self, fishingRodEquipment):
        if fishingRodEquipment is None:
            return self.DEFAULT_FISHING_SUCCESS_RATE

        userTool = fishingRodEquipment.user_tool

        if userTool is None:
            return self.DEFAULT_FISHING_SUCCESS_RATE

        if userTool.status == ToolStatus.BROKEN.value:
            return self.DEFAULT_FISHING_SUCCESS_RATE

        if userTool.current_durability <= 0:
            return self.DEFAULT_FISHING_SUCCESS_RATE

        toolTemplate = userTool.tool_template

        if toolTemplate is None:
            return self.DEFAULT_FISHING_SUCCESS_RATE

        fishingSuccessRate = float(toolTemplate.fishing_success_rate)

        if fishingSuccessRate <= 0:
            return self.DEFAULT_FISHING_SUCCESS_RATE

        return max(0, min(fishingSuccessRate, 1))

    def getFishingCooldownReductionSeconds(self, fishingRodEquipment):
        if fishingRodEquipment is None:
            return 0

        userTool = fishingRodEquipment.user_tool

        if userTool is None:
            return 0

        if userTool.status == ToolStatus.BROKEN.value:
            return 0

        if userTool.current_durability <= 0:
            return 0

        toolTemplate = userTool.tool_template

        if toolTemplate is None:
            return 0

        return max(toolTemplate.fishing_cooldown_reduction_seconds, 0)

    def getFishingCatchQuantity(self, fishingRodEquipment):
        if fishingRodEquipment is None:
            return self.DEFAULT_FISHING_CATCH_QUANTITY

        userTool = fishingRodEquipment.user_tool

        if userTool is None:
            return self.DEFAULT_FISHING_CATCH_QUANTITY

        if userTool.status == ToolStatus.BROKEN.value:
            return self.DEFAULT_FISHING_CATCH_QUANTITY

        if userTool.current_durability <= 0:
            return self.DEFAULT_FISHING_CATCH_QUANTITY

        toolTemplate = userTool.tool_template

        if toolTemplate is None:
            return self.DEFAULT_FISHING_CATCH_QUANTITY

        return max(
            toolTemplate.fishing_catch_quantity,
            self.DEFAULT_FISHING_CATCH_QUANTITY,
        )

    def consumeFishingRodDurability(self, fishingRodEquipment):
        if fishingRodEquipment is None:
            return False

        userTool = fishingRodEquipment.user_tool

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

    def isFishingSuccess(self, fishingSuccessRate: float):
        return random.random() < fishingSuccessRate

    def randomSeafoodItem(self, seafoodItems):
        return random.choice(seafoodItems)

    def randomWeightKg(self):
        randomRate = random.random()

        weight = self.MIN_WEIGHT_KG + (
            self.MAX_WEIGHT_KG - self.MIN_WEIGHT_KG
        ) * (randomRate ** 3)

        weight = round(weight, 2)

        return Decimal(str(weight))
