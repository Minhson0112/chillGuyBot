from bot.enums.toolStatus import ToolStatus
from bot.repository.toolTemplateRepository import ToolTemplateRepository
from bot.repository.userToolRepository import UserToolRepository


class FarmToolBuyService:
    ITEM_TYPE_TOOL = "tool"

    def canHandle(self, item):
        return item is not None and item.type_code == self.ITEM_TYPE_TOOL

    def buyTool(
        self,
        session,
        userId: int,
        item,
    ):
        toolTemplateRepository = ToolTemplateRepository(session)
        userToolRepository = UserToolRepository(session)

        toolTemplate = toolTemplateRepository.findActiveByItemId(item.id)

        if toolTemplate is None:
            return {
                "success": False,
                "message": f"Không tìm thấy dữ liệu tool template cho **{item.name}**.",
            }

        userTool = userToolRepository.create(
            userId=userId,
            itemId=item.id,
            toolTemplateId=toolTemplate.id,
            currentDurability=toolTemplate.max_durability,
            status=ToolStatus.AVAILABLE.value,
        )

        return {
            "success": True,
            "userTool": userTool,
            "toolTemplate": toolTemplate,
        }