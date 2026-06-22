from bot.config.database import getDbSession
from bot.helper.farmItemHelper import buildItemText
from bot.enums.toolStatus import ToolStatus
from bot.enums.toolType import ToolType
from bot.repository.farmRepository import FarmRepository
from bot.repository.farmToolEquipmentRepository import FarmToolEquipmentRepository
from bot.repository.userToolRepository import UserToolRepository


class FarmToolUseService:
    def useTool(
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
                    "message": "Bạn không thể dùng dụng cụ của người khác.",
                }

            if userTool.item is None:
                return {
                    "success": False,
                    "message": "Dụng cụ này không có dữ liệu item.",
                }

            if userTool.tool_template is None:
                return {
                    "success": False,
                    "message": "Dụng cụ này không có dữ liệu tool template.",
                }

            if userTool.current_durability <= 0:
                userTool.status = ToolStatus.BROKEN.value
                session.commit()

                return {
                    "success": False,
                    "message": "Dụng cụ này đã hỏng, không thể lắp vào farm.",
                }

            if userTool.status == ToolStatus.BROKEN.value:
                return {
                    "success": False,
                    "message": "Dụng cụ này đã hỏng, không thể lắp vào farm.",
                }

            toolType = userTool.tool_template.tool_type

            if not self.isValidToolType(toolType):
                return {
                    "success": False,
                    "message": f"Loại dụng cụ **{toolType}** không hợp lệ.",
                }

            existingEquipment = farmToolEquipmentRepository.findByFarmIdAndToolType(
                farmId=farm.id,
                toolType=toolType,
            )

            if existingEquipment is not None and existingEquipment.user_tool_id == userTool.id:
                return {
                    "success": False,
                    "message": f"{buildItemText(userTool.item)} đang được lắp trong farm rồi.",
                }

            oldUserTool = None

            if existingEquipment is not None:
                oldUserTool = existingEquipment.user_tool

                if oldUserTool is not None:
                    oldUserTool.status = ToolStatus.AVAILABLE.value

                farmToolEquipmentRepository.updateUserTool(
                    farmToolEquipment=existingEquipment,
                    userToolId=userTool.id,
                )
            else:
                farmToolEquipmentRepository.create(
                    farmId=farm.id,
                    toolType=toolType,
                    userToolId=userTool.id,
                )

            userTool.status = ToolStatus.EQUIPPED.value

            session.commit()

            if oldUserTool is not None and oldUserTool.item is not None:
                return {
                    "success": True,
                    "message": (
                        f"Đã tháo {buildItemText(oldUserTool.item)} và lắp "
                        f"{buildItemText(userTool.item)} vào farm."
                    ),
                }

            return {
                "success": True,
                "message": f"Đã lắp {buildItemText(userTool.item)} vào farm.",
            }

    def isValidToolType(self, toolType: str):
        return toolType in [toolTypeItem.value for toolTypeItem in ToolType]
