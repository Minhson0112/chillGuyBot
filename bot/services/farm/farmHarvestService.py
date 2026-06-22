from datetime import datetime

from bot.helper.numberFormatHelper import formatNumber
from bot.config.database import getDbSession
from bot.helper.timeFormatHelper import formatMinutesSeconds
from bot.helper.farmItemHelper import buildItemText
from bot.enums.toolStatus import ToolStatus
from bot.enums.toolType import ToolType
from bot.repository.farmCropAreaRepository import FarmCropAreaRepository
from bot.repository.farmRepository import FarmRepository
from bot.repository.farmToolEquipmentRepository import FarmToolEquipmentRepository
from bot.repository.userInventoryRepository import UserInventoryRepository


class FarmHarvestService:
    DRY_REDUCTION_SECONDS_PER_QUANTITY = 900
    PEST_REDUCTION_SECONDS_PER_QUANTITY = 1020
    HARVEST_EXP_PER_CROP = 1

    def harvestCrop(self, userId: int):
        with getDbSession() as session:
            farmRepository = FarmRepository(session)
            farmCropAreaRepository = FarmCropAreaRepository(session)
            farmToolEquipmentRepository = FarmToolEquipmentRepository(session)
            userInventoryRepository = UserInventoryRepository(session)

            farm = farmRepository.findByUserIdWithRenderData(userId)

            if farm is None:
                return {
                    "success": False,
                    "message": "Bạn chưa có nông trại.",
                }

            farmCropArea = farm.cropArea

            if farmCropArea is None:
                return {
                    "success": False,
                    "message": "Nông trại của bạn chưa có khu đất trồng.",
                }

            if farmCropArea.crop_id is None or farmCropArea.crop is None:
                return {
                    "success": False,
                    "message": "Hiện tại bạn chưa trồng cây nào.",
                }

            if farmCropArea.planted_at is None or farmCropArea.harvestable_at is None:
                return {
                    "success": False,
                    "message": "Dữ liệu cây trồng chưa hợp lệ.",
                }

            now = datetime.now()

            if now < farmCropArea.harvestable_at:
                remainingSeconds = int((farmCropArea.harvestable_at - now).total_seconds())

                return {
                    "success": False,
                    "message": f"Cây chưa thể thu hoạch. Còn **{formatMinutesSeconds(remainingSeconds)}**.",
                }

            crop = farmCropArea.crop
            cropItem = crop.cropItem

            if cropItem is None:
                return {
                    "success": False,
                    "message": "Không tìm thấy item thu hoạch của cây này.",
                }

            baseHarvestQuantity = farmCropArea.unlocked_plot_count * crop.harvest_quantity_per_plot
            drySeconds = self.calculateTotalDrySeconds(farmCropArea, now)
            pestSeconds = self.calculateTotalPestSeconds(farmCropArea, now)

            reducedHarvestQuantity = self.calculateHarvestQuantity(
                baseHarvestQuantity=baseHarvestQuantity,
                drySeconds=drySeconds,
                pestSeconds=pestSeconds,
            )

            sickleEquipment = farmToolEquipmentRepository.findByFarmIdAndToolTypeWithToolData(
                farmId=farm.id,
                toolType=ToolType.SICKLE.value,
            )

            sickleBonusQuantity = self.calculateSickleBonusQuantity(
                sickleEquipment=sickleEquipment,
                harvestQuantity=reducedHarvestQuantity,
            )

            harvestQuantity = reducedHarvestQuantity + sickleBonusQuantity
            sickleBroken = self.consumeSickleDurability(sickleEquipment)

            userInventoryRepository.addOrCreate(
                userId=userId,
                itemId=crop.crop_item_id,
                quantity=harvestQuantity,
            )

            farmCropAreaRepository.clearCrop(farmCropArea)
            farmRepository.increaseFarmExp(
                farm,
                self.HARVEST_EXP_PER_CROP * farmCropArea.unlocked_plot_count,
            )

            session.commit()

            cropItemText = buildItemText(cropItem)

            message = f"Bạn đã thu hoạch **{harvestQuantity}** {cropItemText}."

            if reducedHarvestQuantity < baseHarvestQuantity:
                message += (
                    f"\nSản lượng gốc là **{baseHarvestQuantity}**, "
                    f"nhưng bị giảm còn **{reducedHarvestQuantity}** do đất khô hoặc sâu bệnh."
                )

            if sickleBonusQuantity > 0:
                message += f"\nLiềm đã bonus thêm **{sickleBonusQuantity}** {cropItemText}."

            if sickleBroken:
                message += "\nLiềm đã hết độ bền và bị hỏng."

            return {
                "success": True,
                "message": message,
            }

    def calculateHarvestQuantity(
        self,
        baseHarvestQuantity: int,
        drySeconds: int,
        pestSeconds: int,
    ):
        dryReduction = drySeconds // self.DRY_REDUCTION_SECONDS_PER_QUANTITY
        pestReduction = pestSeconds // self.PEST_REDUCTION_SECONDS_PER_QUANTITY

        harvestQuantity = baseHarvestQuantity - dryReduction - pestReduction

        if baseHarvestQuantity <= 0:
            return 0

        return max(harvestQuantity, 1)

    def calculateSickleBonusQuantity(
        self,
        sickleEquipment,
        harvestQuantity: int,
    ):
        if sickleEquipment is None:
            return 0

        userTool = sickleEquipment.user_tool

        if userTool is None:
            return 0

        if userTool.status == ToolStatus.BROKEN.value:
            return 0

        if userTool.current_durability <= 0:
            return 0

        toolTemplate = userTool.tool_template

        if toolTemplate is None:
            return 0

        harvestBonusPercent = max(toolTemplate.harvest_bonus_percent, 0)

        if harvestBonusPercent <= 0:
            return 0

        return harvestQuantity * harvestBonusPercent // 100

    def consumeSickleDurability(self, sickleEquipment):
        if sickleEquipment is None:
            return False

        userTool = sickleEquipment.user_tool

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

    def calculateTotalDrySeconds(self, farmCropArea, now: datetime):
        totalDrySeconds = farmCropArea.total_dry_seconds

        if farmCropArea.is_dry and farmCropArea.dryness_started_at is not None:
            currentDrySeconds = int((now - farmCropArea.dryness_started_at).total_seconds())
            totalDrySeconds += max(currentDrySeconds, 0)

        return max(totalDrySeconds, 0)

    def calculateTotalPestSeconds(self, farmCropArea, now: datetime):
        totalPestSeconds = farmCropArea.total_pest_seconds

        if farmCropArea.is_pest_infected and farmCropArea.pest_started_at is not None:
            currentPestSeconds = int((now - farmCropArea.pest_started_at).total_seconds())
            totalPestSeconds += max(currentPestSeconds, 0)

        return max(totalPestSeconds, 0)
