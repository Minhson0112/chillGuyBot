import math

from bot.config.database import getDbSession
from bot.config.emoji import FARM_GAME_EMOJI
from bot.repository.farmMarketListingRepository import FarmMarketListingRepository
from bot.repository.userInventoryRepository import UserInventoryRepository
from bot.services.farm.dailyTaskProgressService import DailyTaskProgressService


class FarmSellShopService:
    MARKET_PRICE_BONUS_RATE = 1.1

    DAILY_TASK_TYPE_SELL_MARKET_ITEM = "sell_market_item"

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
            dailyTaskProgressService = DailyTaskProgressService(session)

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

            completedDailyTasks = dailyTaskProgressService.addProgress(
                userId=userId,
                taskType=self.DAILY_TASK_TYPE_SELL_MARKET_ITEM,
                amount=quantity,
                targetItemId=item.id,
            )

            dailyTaskMessage = dailyTaskProgressService.buildCompletedTaskMessage(
                completedDailyTasks,
            )

            session.commit()

            message = (
                f"Bạn đã đăng bán **{quantity}** {itemText} lên shop riêng.\n"
                f"Giá gốc mỗi món: **{self.formatNumber(item.sell_price)}** {chillCoinEmoji}\n"
                f"Giá shop riêng mỗi món: **{self.formatNumber(unitMarketPrice)}** {chillCoinEmoji}\n"
                f"Tổng giá bán: **{self.formatNumber(totalMarketPrice)}** {chillCoinEmoji}\n"
                f"ID đăng bán: **{farmMarketListing.id}**"
            )

            if dailyTaskMessage is not None:
                message += f"\n\n{dailyTaskMessage}"

            return {
                "success": True,
                "message": message,
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