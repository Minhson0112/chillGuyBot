from datetime import datetime

from bot.config.database import getDbSession
from bot.config.emoji import FARM_GAME_EMOJI
from bot.repository.farmCropAreaRepository import FarmCropAreaRepository
from bot.repository.farmRepository import FarmRepository
from bot.repository.userInventoryRepository import UserInventoryRepository

class FarmHarvestService:
    DRY_REDUCTION_SECONDS_PER_QUANTITY = 900
    PEST_REDUCTION_SECONDS_PER_QUANTITY = 1020
    HARVEST_EXP_PER_CROP = 1

    def harvestCrop(self, userId: int):
        with getDbSession() as session:
            farmRepository = FarmRepository(session)
            farmCropAreaRepository = FarmCropAreaRepository(session)
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
                    "message": f"Cây chưa thể thu hoạch. Còn **{self.formatRemainingTime(remainingSeconds)}**.",
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

            harvestQuantity = self.calculateHarvestQuantity(
                baseHarvestQuantity=baseHarvestQuantity,
                drySeconds=drySeconds,
                pestSeconds=pestSeconds,
            )

            userInventoryRepository.addOrCreate(
                userId=userId,
                itemId=crop.crop_item_id,
                quantity=harvestQuantity,
            )

            farmCropAreaRepository.clearCrop(farmCropArea)
            farmRepository.increaseFarmExp(farm, self.HARVEST_EXP_PER_CROP * farmCropArea.unlocked_plot_count)

            session.commit()

            cropItemText = self.buildItemText(cropItem)

            if harvestQuantity < baseHarvestQuantity:
                return {
                    "success": True,
                    "message": (
                        f"Bạn đã thu hoạch **{harvestQuantity}** {cropItemText}. "
                        f"Sản lượng gốc là **{baseHarvestQuantity}**, nhưng bị giảm do đất khô hoặc sâu bệnh."
                    ),
                }

            return {
                "success": True,
                "message": f"Bạn đã thu hoạch **{harvestQuantity}** {cropItemText}.",
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

    def buildItemText(self, item):
        itemEmoji = FARM_GAME_EMOJI.get(item.icon_image_key)

        if itemEmoji is None:
            return f"**{item.name}**"

        return f"{itemEmoji} **{item.name}**"

    def formatRemainingTime(self, remainingSeconds: int):
        minutes = remainingSeconds // 60
        seconds = remainingSeconds % 60

        return f"{minutes}:{seconds:02d}"

    def formatNumber(self, number: int):
        return f"{number:,}"