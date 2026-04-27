from bot.config.database import getDbSession
from bot.config.emoji import FARM_GAME_EMOJI
from bot.repository.farmCropAreaRepository import FarmCropAreaRepository
from bot.repository.farmRepository import FarmRepository
from bot.repository.itemRepository import ItemRepository
from bot.repository.userInventoryRepository import UserInventoryRepository


class FarmPestRemoveService:
    BUG_ITEM_CODE = "bug"
    PEST_REMOVE_EXP = 1
    def removePest(self, userId: int):
        with getDbSession() as session:
            farmRepository = FarmRepository(session)
            farmCropAreaRepository = FarmCropAreaRepository(session)
            itemRepository = ItemRepository(session)
            userInventoryRepository = UserInventoryRepository(session)

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

            session.commit()

            bugText = self.buildItemText(bugItem)

            return {
                "success": True,
                "message": f"Bạn đã bắt được **{bugQuantity}** {bugText} và cây đã hết sâu bệnh.",
            }

    def buildItemText(self, item):
        itemEmoji = FARM_GAME_EMOJI.get(item.icon_image_key)

        if itemEmoji is None:
            return f"**{item.name}**"

        return f"{itemEmoji} **{item.name}**"