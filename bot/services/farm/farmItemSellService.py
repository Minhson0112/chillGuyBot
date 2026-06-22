from bot.helper.numberFormatHelper import formatNumber
from bot.config.database import getDbSession
from bot.config.emoji import FARM_GAME_EMOJI
from bot.helper.farmItemHelper import buildItemText
from bot.repository.memberRepository import MemberRepository
from bot.repository.userInventoryRepository import UserInventoryRepository


class FarmItemSellService:
    def sellItem(
        self,
        userId: int,
        inventoryId: int,
        quantity: int = 1,
    ):
        if quantity is None:
            quantity = 1

        if quantity <= 0:
            return {
                "success": False,
                "message": "Số lượng bán phải lớn hơn 0.",
            }

        with getDbSession() as session:
            memberRepository = MemberRepository(session)
            userInventoryRepository = UserInventoryRepository(session)

            member = memberRepository.findByUserId(userId)

            if member is None:
                return {
                    "success": False,
                    "message": "Không tìm thấy dữ liệu member của bạn.",
                }

            userInventory = userInventoryRepository.findByIdWithItem(inventoryId)

            if userInventory is None or userInventory.item is None:
                return {
                    "success": False,
                    "message": f"Không tìm thấy item trong kho với ID **{inventoryId}**.",
                }

            if userInventory.user_id != userId:
                return {
                    "success": False,
                    "message": "Bạn không thể bán item trong kho của người khác.",
                }

            item = userInventory.item
            itemText = buildItemText(item)
            chillCoinEmoji = FARM_GAME_EMOJI["chill_coin"]

            if not item.is_sellable:
                return {
                    "success": False,
                    "message": f"{itemText} không thể bán.",
                }

            if item.sell_price <= 0:
                return {
                    "success": False,
                    "message": f"{itemText} hiện không có giá bán.",
                }

            if userInventory.quantity < quantity:
                return {
                    "success": False,
                    "message": (
                        f"Bạn không đủ {itemText} để bán. "
                        f"Muốn bán **{quantity}**, hiện có **{userInventory.quantity}**."
                    ),
                }

            totalPrice = item.sell_price * quantity

            userInventoryRepository.decreaseQuantity(
                userInventory=userInventory,
                quantity=quantity,
            )

            member.chill_coin += totalPrice

            session.commit()

            return {
                "success": True,
                "message": (
                    f"Bạn đã bán **{quantity}** {itemText} và nhận được "
                    f"**{formatNumber(totalPrice)}** {chillCoinEmoji}."
                ),
            }
