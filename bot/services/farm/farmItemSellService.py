from bot.helper.numberFormatHelper import formatNumber
from bot.config.database import getDbSession
from bot.config.emoji import FARM_GAME_EMOJI
from bot.helper.farmItemHelper import buildItemText
from bot.repository.memberRepository import MemberRepository
from bot.repository.userInventoryRepository import UserInventoryRepository


class FarmItemSellService:
    SELL_PRICE_RATE_PERCENT = 80

    def getSellPreview(
        self,
        userId: int,
        inventoryId: int,
        quantity: int = 1,
    ):
        if quantity is None:
            quantity = 1

        with getDbSession() as session:
            validateResult = self.validateSellRequest(
                session=session,
                userId=userId,
                inventoryId=inventoryId,
                quantity=quantity,
            )

            if not validateResult["success"]:
                return validateResult

            item = validateResult["item"]

            return {
                "success": True,
                "itemText": validateResult["itemText"],
                "totalPrice": self.calculateTotalPrice(
                    sellPrice=item.sell_price,
                    quantity=quantity,
                ),
            }

    def sellItem(
        self,
        userId: int,
        inventoryId: int,
        quantity: int = 1,
    ):
        if quantity is None:
            quantity = 1

        with getDbSession() as session:
            validateResult = self.validateSellRequest(
                session=session,
                userId=userId,
                inventoryId=inventoryId,
                quantity=quantity,
            )

            if not validateResult["success"]:
                return validateResult

            member = validateResult["member"]
            userInventory = validateResult["userInventory"]
            item = validateResult["item"]
            itemText = validateResult["itemText"]
            totalPrice = self.calculateTotalPrice(
                sellPrice=item.sell_price,
                quantity=quantity,
            )
            chillCoinEmoji = FARM_GAME_EMOJI["chill_coin"]
            userInventoryRepository = UserInventoryRepository(session)

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

    def validateSellRequest(
        self,
        session,
        userId: int,
        inventoryId: int,
        quantity: int,
    ):
        if quantity <= 0:
            return {
                "success": False,
                "message": "Số lượng bán phải lớn hơn 0.",
            }

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

        return {
            "success": True,
            "member": member,
            "userInventory": userInventory,
            "item": item,
            "itemText": itemText,
        }

    def calculateTotalPrice(self, sellPrice: int, quantity: int):
        return sellPrice * quantity * self.SELL_PRICE_RATE_PERCENT // 100
