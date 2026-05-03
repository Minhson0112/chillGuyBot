from bot.config.database import getDbSession
from bot.config.emoji import FARM_GAME_EMOJI
from bot.repository.cropRepository import CropRepository
from bot.repository.farmCropAreaRepository import FarmCropAreaRepository
from bot.repository.farmRepository import FarmRepository
from bot.repository.userInventoryRepository import UserInventoryRepository
from bot.services.farm.dailyTaskProgressService import DailyTaskProgressService


class FarmPlantService:
    DAILY_TASK_TYPE_PLANT_CROP = "plant_crop"

    def plantCrop(
        self,
        userId: int,
        userInventoryId: int,
    ):
        with getDbSession() as session:
            userInventoryRepository = UserInventoryRepository(session)
            farmRepository = FarmRepository(session)
            farmCropAreaRepository = FarmCropAreaRepository(session)
            cropRepository = CropRepository(session)
            dailyTaskProgressService = DailyTaskProgressService(session)

            userInventory = userInventoryRepository.findByIdWithItem(userInventoryId)

            if userInventory is None:
                return {
                    "success": False,
                    "message": f"Không tìm thấy item trong silo với ID **{userInventoryId}**.",
                }

            if userInventory.user_id != userId:
                return {
                    "success": False,
                    "message": "Item này không thuộc silo của bạn.",
                }

            item = userInventory.item

            if item is None:
                return {
                    "success": False,
                    "message": "Không tìm thấy thông tin item.",
                }

            itemText = self.buildItemText(item)

            if item.type_code != "seed":
                return {
                    "success": False,
                    "message": f"{itemText} không phải là hạt giống nên không thể trồng.",
                }

            crop = cropRepository.findBySeedItemIdWithItems(item.id)

            if crop is None:
                return {
                    "success": False,
                    "message": f"{itemText} chưa được liên kết với cây trồng nào.",
                }

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

            if farmCropArea.crop_id is not None:
                return {
                    "success": False,
                    "message": "Khu đất của bạn đang có cây trồng. Hãy thu hoạch trước khi trồng cây mới.",
                }

            requiredSeedQuantity = farmCropArea.unlocked_plot_count

            if userInventory.quantity < requiredSeedQuantity:
                return {
                    "success": False,
                    "message": (
                        f"Không đủ hạt giống {itemText} để trồng. "
                        f"Bạn cần ít nhất **{requiredSeedQuantity}** hạt giống, "
                        f"hiện có **{userInventory.quantity}**."
                    ),
                }

            userInventoryRepository.decreaseQuantity(
                userInventory=userInventory,
                quantity=requiredSeedQuantity,
            )

            farmCropAreaRepository.plantCrop(
                farmCropArea=farmCropArea,
                cropId=crop.id,
                totalGrowthSeconds=crop.total_growth_seconds,
            )

            completedDailyTasks = dailyTaskProgressService.addProgress(
                userId=userId,
                taskType=self.DAILY_TASK_TYPE_PLANT_CROP,
                amount=requiredSeedQuantity,
                targetCropId=crop.id,
            )

            dailyTaskMessage = dailyTaskProgressService.buildCompletedTaskMessage(
                completedDailyTasks,
            )

            session.commit()

            message = (
                f"Bạn đã trồng **{crop.name}** bằng "
                f"**{requiredSeedQuantity}** {itemText}."
            )

            if dailyTaskMessage is not None:
                message += f"\n\n{dailyTaskMessage}"

            return {
                "success": True,
                "message": message,
            }

    def buildItemText(self, item):
        itemEmoji = FARM_GAME_EMOJI.get(item.icon_image_key)

        if itemEmoji is None:
            return f"**{item.name}**"

        return f"{itemEmoji} **{item.name}**"