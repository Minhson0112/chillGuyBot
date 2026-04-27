import math

from bot.config.database import getDbSession
from bot.config.emoji import FARM_GAME_EMOJI
from bot.repository.farmMarketListingRepository import FarmMarketListingRepository
from bot.repository.userInventoryRepository import UserInventoryRepository


class FarmSellShopService:
    MARKET_PRICE_BONUS_RATE = 1.1

    def sellShopItem(
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
                "message": "Số lượng đăng bán phải lớn hơn 0.",
            }

        with getDbSession() as session:
            userInventoryRepository = UserInventoryRepository(session)
            farmMarketListingRepository = FarmMarketListingRepository(session)

            userInventory = userInventoryRepository.findByIdWithItem(inventoryId)

            if userInventory is None or userInventory.item is None:
                return {
                    "success": False,
                    "message": f"Không tìm thấy item trong kho với ID **{inventoryId}**.",
                }

            if userInventory.user_id != userId:
                return {
                    "success": False,
                    "message": "Bạn không thể đăng bán item trong kho của người khác.",
                }

            item = userInventory.item
            itemText = self.buildItemText(item)
            chillCoinEmoji = FARM_GAME_EMOJI["chill_coin"]

            if not item.is_sellable:
                return {
                    "success": False,
                    "message": f"{itemText} không thể đăng bán.",
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
                        f"Bạn không đủ {itemText} để đăng bán. "
                        f"Muốn đăng bán **{quantity}**, hiện có **{userInventory.quantity}**."
                    ),
                }

            unitMarketPrice = self.calculateMarketUnitPrice(item.sell_price)
            totalMarketPrice = unitMarketPrice * quantity

            userInventoryRepository.decreaseQuantity(
                userInventory=userInventory,
                quantity=quantity,
            )

            farmMarketListing = farmMarketListingRepository.create(
                sellerUserId=userId,
                itemId=item.id,
                quantity=quantity,
                price=totalMarketPrice,
            )

            session.commit()

            return {
                "success": True,
                "message": (
                    f"Bạn đã đăng bán **{quantity}** {itemText} lên shop riêng.\n"
                    f"Giá gốc mỗi món: {chillCoinEmoji} **{self.formatNumber(item.sell_price)}**\n"
                    f"Giá shop riêng mỗi món: {chillCoinEmoji} **{self.formatNumber(unitMarketPrice)}**\n"
                    f"Tổng giá bán: {chillCoinEmoji} **{self.formatNumber(totalMarketPrice)}**\n"
                    f"ID đăng bán: **{farmMarketListing.id}**"
                ),
            }

    def calculateMarketUnitPrice(self, sellPrice: int):
        return math.ceil(sellPrice * self.MARKET_PRICE_BONUS_RATE)

    def buildItemText(self, item):
        itemEmoji = FARM_GAME_EMOJI.get(item.icon_image_key)

        if itemEmoji is None:
            return f"**{item.name}**"

        return f"{itemEmoji} **{item.name}**"

    def formatNumber(self, number: int):
        return f"{number:,}"