from bot.config.database import getDbSession
from bot.helper.numberFormatHelper import formatNumber
from bot.helper.serverItemHelper import buildServerItemText
from bot.repository.serverUserInventoryRepository import ServerUserInventoryRepository


class ServerUserInventoryService:
    def getInventoryMessage(self, userId: int):
        with getDbSession() as session:
            serverUserInventoryRepository = ServerUserInventoryRepository(session)
            inventoryItems = serverUserInventoryRepository.findByUserId(userId)

            if not inventoryItems:
                return {
                    "success": False,
                    "message": "Kho server item của bạn đang trống.",
                }

            lines = []

            for inventoryItem in inventoryItems:
                lines.append(self.buildInventoryItemLine(inventoryItem))

            return {
                "success": True,
                "message": "\n".join(lines),
            }

    def buildInventoryItemLine(self, inventoryItem):
        return (
            f"ID `{inventoryItem.id}` | "
            f"{buildServerItemText(inventoryItem.item)} | "
            f"Số lượng: **{formatNumber(inventoryItem.quantity)}**"
        )
