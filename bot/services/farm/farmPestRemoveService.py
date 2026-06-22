from bot.config.database import getDbSession
from bot.helper.farmItemHelper import buildItemText
from bot.repository.farmCropAreaRepository import FarmCropAreaRepository
from bot.repository.farmRepository import FarmRepository
from bot.repository.itemRepository import ItemRepository
from bot.repository.userInventoryRepository import UserInventoryRepository
from bot.services.farm.dailyTaskProgressService import DailyTaskProgressService


class FarmPestRemoveService:
    BUG_ITEM_CODE = "bug"
    PEST_REMOVE_EXP = 1

    DAILY_TASK_TYPE_PEST_REMOVE = "pest_remove"

    def removePest(self, userId: int):
        with getDbSession() as session:
            farmRepository = FarmRepository(session)
            farmCropAreaRepository = FarmCropAreaRepository(session)
            itemRepository = ItemRepository(session)
            userInventoryRepository = UserInventoryRepository(session)
            dailyTaskProgressService = DailyTaskProgressService(session)

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
                    "message": "Bạn chưa trồng cây nào để bắt sâu.",
                }

            if not farmCropArea.is_pest_infected:
                return {
                    "success": False,
                    "message": "Cây trồng hiện không bị sâu bệnh.",
                }

            bugItem = itemRepository.findByCode(self.BUG_ITEM_CODE)

            if bugItem is None:
                return {
                    "success": False,
                    "message": "Không tìm thấy item con sâu trong hệ thống.",
                }

            bugQuantity = farmCropArea.unlocked_plot_count

            userInventoryRepository.addOrCreate(
                userId=userId,
                itemId=bugItem.id,
                quantity=bugQuantity,
            )

            farmCropAreaRepository.markPestRemoved(farmCropArea)
            farmRepository.increaseFarmExp(farm, self.PEST_REMOVE_EXP)

            completedDailyTasks = dailyTaskProgressService.addProgress(
                userId=userId,
                taskType=self.DAILY_TASK_TYPE_PEST_REMOVE,
                amount=1,
                targetCropId=farmCropArea.crop_id,
            )

            dailyTaskMessage = dailyTaskProgressService.buildCompletedTaskMessage(
                completedDailyTasks,
            )

            session.commit()

            bugText = buildItemText(bugItem)

            message = f"Bạn đã bắt được **{bugQuantity}** {bugText} và cây đã hết sâu bệnh."

            if dailyTaskMessage is not None:
                message += f"\n\n{dailyTaskMessage}"

            return {
                "success": True,
                "message": message,
            }
