from datetime import datetime

from bot.config.database import getDbSession
from bot.enums.toolStatus import ToolStatus
from bot.enums.toolType import ToolType
from bot.repository.farmCropAreaRepository import FarmCropAreaRepository
from bot.repository.farmRepository import FarmRepository
from bot.repository.farmToolEquipmentRepository import FarmToolEquipmentRepository


class FarmWaterService:
    WATER_EXP = 1

    def waterCrop(self, userId: int):
        with getDbSession() as session:
            farmRepository = FarmRepository(session)
            farmCropAreaRepository = FarmCropAreaRepository(session)
            farmToolEquipmentRepository = FarmToolEquipmentRepository(session)

            farm = farmRepository.findByUserId(userId)

            if farm is None:
                return {
                    "success": False,
                    "message": "Bạn chưa có nông trại.",
                }

            farmCropArea = farmCropAreaRepository.findByFarmId(farm.id)

            if farmCropArea is None:
                return {
                    "success": False,
                    "message": "Nông trại của bạn chưa có khu đất trồng.",
                }

            if farmCropArea.crop_id is None or farmCropArea.planted_at is None:
                return {
                    "success": False,
                    "message": "Bạn chưa trồng cây nào để tưới nước.",
                }

            now = datetime.now()

            if farmCropArea.harvestable_at is not None and now >= farmCropArea.harvestable_at:
                return {
                    "success": False,
                    "message": "Cây đã có thể thu hoạch rồi, không cần tưới nước nữa.",
                }

            if not farmCropArea.is_dry:
                return {
                    "success": False,
                    "message": "Đất vẫn đang ướt, chưa cần tưới nước.",
                }

            wateringCanEquipment = farmToolEquipmentRepository.findByFarmIdAndToolTypeWithToolData(
                farmId=farm.id,
                toolType=ToolType.WATERING_CAN.value,
            )

            growthReductionSeconds = self.getWateringCanGrowthReductionSeconds(
                wateringCanEquipment,
            )

            farmCropAreaRepository.markWatered(farmCropArea)

            if growthReductionSeconds > 0:
                farmCropAreaRepository.reduceGrowthTime(
                    farmCropArea=farmCropArea,
                    reductionSeconds=growthReductionSeconds,
                )

            wateringCanBroken = self.consumeWateringCanDurability(wateringCanEquipment)

            farmRepository.increaseFarmExp(farm, self.WATER_EXP)

            session.commit()

            message = "Bạn đã tưới nước cho cây. Đất đã ướt trở lại."

            if growthReductionSeconds > 0:
                message += (
                    f"\nBình tưới đã giúp cây phát triển nhanh hơn "
                    f"**{self.formatRemainingTime(growthReductionSeconds)}**."
                )

            if wateringCanBroken:
                message += "\nBình tưới đã hết độ bền và bị hỏng."

            return {
                "success": True,
                "message": message,
            }

    def getWateringCanGrowthReductionSeconds(self, wateringCanEquipment):
        if wateringCanEquipment is None:
            return 0

        userTool = wateringCanEquipment.user_tool

        if userTool is None:
            return 0

        if userTool.status == ToolStatus.BROKEN.value:
            return 0

        if userTool.current_durability <= 0:
            return 0

        toolTemplate = userTool.tool_template

        if toolTemplate is None:
            return 0

        return max(toolTemplate.crop_growth_reduction_seconds, 0)

    def consumeWateringCanDurability(self, wateringCanEquipment):
        if wateringCanEquipment is None:
            return False

        userTool = wateringCanEquipment.user_tool

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

    def formatRemainingTime(self, remainingSeconds: int):
        minutes = remainingSeconds // 60
        seconds = remainingSeconds % 60

        return f"{minutes}:{seconds:02d}"