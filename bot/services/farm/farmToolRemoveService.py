from bot.config.database import getDbSession
from bot.config.emoji import FARM_GAME_EMOJI
from bot.enums.toolStatus import ToolStatus
from bot.repository.farmRepository import FarmRepository
from bot.repository.farmToolEquipmentRepository import FarmToolEquipmentRepository
from bot.repository.userToolRepository import UserToolRepository


class FarmToolRemoveService:
    def removeTool(
        self,
        userId: int,
        userToolId: int,
    ):
        with getDbSession() as session:
            farmRepository = FarmRepository(session)
            userToolRepository = UserToolRepository(session)
            farmToolEquipmentRepository = FarmToolEquipmentRepository(session)

            farm = farmRepository.findByUserId(userId)

            if farm is None:
                return {
                    "success": False,
                    "message": "Bạn chưa có nông trại.",
                }

            userTool = userToolRepository.findByIdWithRelations(userToolId)

            if userTool is None:
                return {
                    "success": False,
                    "message": f"Không tìm thấy dụng cụ với ID **{userToolId}**.",
                }

            if userTool.user_id != userId:
                return {
                    "success": False,
                    "message": "Bạn không thể gỡ dụng cụ của người khác.",
                }

            if userTool.farm_tool_equipment is None:
                return {
                    "success": False,
                    "message": f"{self.buildToolText(userTool.item)} hiện không được lắp trong farm.",
                }

            if userTool.farm_tool_equipment.farm_id != farm.id:
                return {
                    "success": False,
                    "message": "Dụng cụ này không được lắp trong farm của bạn.",
                }

            farmToolEquipmentRepository.delete(userTool.farm_tool_equipment)
            userTool.status = ToolStatus.AVAILABLE.value

            session.commit()

            return {
                "success": True,
                "message": f"Đã gỡ {self.buildToolText(userTool.item)} khỏi farm.",
            }

    def buildToolText(self, item):
        if item is None:
            return "**dụng cụ này**"

        itemEmoji = FARM_GAME_EMOJI.get(item.icon_image_key)

        if itemEmoji is None:
            return f"**{item.name}**"

        return f"{itemEmoji} **{item.name}**"
