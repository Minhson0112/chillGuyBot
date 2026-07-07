from bot.config.database import getDbSession
from bot.helper.serverItemHelper import getServerItemEmoji
from bot.repository.coupleRepository import CoupleRepository
from bot.repository.serverUserInventoryRepository import ServerUserInventoryRepository


class ProposalService:
    RING_ITEM_TYPE = "ring"

    def validateProposalMembers(
        self,
        proposerUserId: int,
        targetUserId: int,
    ):
        if proposerUserId == targetUserId:
            return {
                "success": False,
                "message": "Bạn không thể tự cầu hôn chính mình.",
            }

        with getDbSession() as session:
            coupleRepository = CoupleRepository(session)
            proposerActiveCouple = coupleRepository.findActiveByUserId(proposerUserId)

            if proposerActiveCouple is not None:
                return {
                    "success": False,
                    "message": "Bạn đang trong một mối quan hệ rồi.",
                }

            targetActiveCouple = coupleRepository.findActiveByUserId(targetUserId)

            if targetActiveCouple is not None:
                return {
                    "success": False,
                    "message": "Người này đang trong một mối quan hệ rồi.",
                }

            return {
                "success": True,
            }

    def findAvailableRingOptions(self, userId: int):
        with getDbSession() as session:
            serverUserInventoryRepository = ServerUserInventoryRepository(session)
            ringInventoryItems = serverUserInventoryRepository.findAvailableRingsByUserId(userId)

            return [
                {
                    "inventoryId": ringInventoryItem.id,
                    "itemId": ringInventoryItem.item_id,
                    "itemName": ringInventoryItem.item.name,
                    "itemEmoji": getServerItemEmoji(ringInventoryItem.item),
                    "quantity": ringInventoryItem.quantity,
                    "intimacyPoints": ringInventoryItem.item.intimacy_points,
                }
                for ringInventoryItem in ringInventoryItems
                if ringInventoryItem.item is not None
            ]

    def acceptProposal(
        self,
        proposerUserId: int,
        targetUserId: int,
        ringInventoryId: int,
    ):
        if proposerUserId == targetUserId:
            return {
                "success": False,
                "message": "Bạn không thể tự cầu hôn chính mình.",
            }

        with getDbSession() as session:
            serverUserInventoryRepository = ServerUserInventoryRepository(session)
            coupleRepository = CoupleRepository(session)

            proposerActiveCouple = coupleRepository.findActiveByUserId(proposerUserId)

            if proposerActiveCouple is not None:
                return {
                    "success": False,
                    "message": "Người cầu hôn hiện đang có couple active.",
                }

            targetActiveCouple = coupleRepository.findActiveByUserId(targetUserId)

            if targetActiveCouple is not None:
                return {
                    "success": False,
                    "message": "Người được cầu hôn hiện đang có couple active.",
                }

            ringInventory = serverUserInventoryRepository.findById(ringInventoryId)

            if ringInventory is None or ringInventory.user_id != proposerUserId:
                return {
                    "success": False,
                    "message": "Không tìm thấy nhẫn trong kho của người cầu hôn.",
                }

            ringItem = ringInventory.item

            if ringItem is None or ringItem.type != self.RING_ITEM_TYPE:
                return {
                    "success": False,
                    "message": "Item được chọn không phải là nhẫn.",
                }

            if ringInventory.quantity <= 0:
                return {
                    "success": False,
                    "message": "Nhẫn này trong kho đã hết số lượng.",
                }

            couple = coupleRepository.createCouple(
                user1Id=proposerUserId,
                user2Id=targetUserId,
                intimacyPoints=ringItem.intimacy_points,
            )
            serverUserInventoryRepository.decreaseQuantity(ringInventory, 1)
            session.commit()

            return {
                "success": True,
                "coupleId": couple.id,
                "ringName": ringItem.name,
                "ringEmoji": getServerItemEmoji(ringItem),
                "intimacyPoints": ringItem.intimacy_points,
            }
