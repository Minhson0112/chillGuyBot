from bot.config.database import getDbSession
from bot.helper.numberFormatHelper import formatNumber
from bot.helper.serverItemHelper import getServerItemEmoji
from bot.repository.coupleRepository import CoupleRepository
from bot.repository.serverItemGiftHistoryRepository import ServerItemGiftHistoryRepository
from bot.repository.serverUserInventoryRepository import ServerUserInventoryRepository


class ServerItemGiftService:
    def giftItem(
        self,
        giverUserId: int,
        receiverUserId: int,
        inventoryId: int,
        quantity: int = 1,
    ):
        if giverUserId == receiverUserId:
            return {
                "success": False,
                "message": "Bạn không thể tự tặng item cho chính mình.",
            }

        if quantity <= 0:
            return {
                "success": False,
                "message": "Số lượng tặng phải lớn hơn 0.",
            }

        with getDbSession() as session:
            coupleRepository = CoupleRepository(session)
            serverUserInventoryRepository = ServerUserInventoryRepository(session)
            serverItemGiftHistoryRepository = ServerItemGiftHistoryRepository(session)

            couple = coupleRepository.findActiveByPair(
                user1Id=giverUserId,
                user2Id=receiverUserId,
            )

            if couple is None:
                return {
                    "success": False,
                    "message": "Bạn chỉ có thể tặng item cho người đang là couple của bạn.",
                }

            inventoryItem = serverUserInventoryRepository.findById(inventoryId)

            if inventoryItem is None or inventoryItem.user_id != giverUserId:
                return {
                    "success": False,
                    "message": "Không tìm thấy item này trong kho của bạn.",
                }

            if inventoryItem.item is None:
                return {
                    "success": False,
                    "message": "Không tìm thấy thông tin item.",
                }

            if inventoryItem.quantity < quantity:
                return {
                    "success": False,
                    "message": (
                        f"Bạn không đủ số lượng item để tặng. "
                        f"Hiện có **{formatNumber(inventoryItem.quantity)}**, "
                        f"muốn tặng **{formatNumber(quantity)}**."
                    ),
                }

            intimacyPointsGained = inventoryItem.item.intimacy_points * quantity
            serverUserInventoryRepository.decreaseQuantity(inventoryItem, quantity)
            coupleRepository.addIntimacyPoints(couple, intimacyPointsGained)
            serverItemGiftHistoryRepository.create(
                giverUserId=giverUserId,
                receiverUserId=receiverUserId,
                itemId=inventoryItem.item_id,
                quantity=quantity,
            )
            session.commit()

            return {
                "success": True,
                "itemName": inventoryItem.item.name,
                "itemEmoji": getServerItemEmoji(inventoryItem.item),
                "quantity": quantity,
                "intimacyPointsGained": intimacyPointsGained,
                "totalIntimacyPoints": couple.intimacy_points,
            }
