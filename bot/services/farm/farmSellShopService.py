from bot.config.database import getDbSession
from bot.config.farmMarket import (
    DAILY_MEMBER_SELLER_BONUS_LIMIT,
    MEMBER_SELLER_BONUS_RATE_PERCENT,
)
from bot.helper.farmItemHelper import buildItemText
from bot.repository.farmMarketListingRepository import FarmMarketListingRepository
from bot.repository.userInventoryRepository import UserInventoryRepository
from bot.services.farm.dailyTaskProgressService import DailyTaskProgressService


class FarmSellShopService:
    MAX_QUANTITY_PER_LISTING = 10

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

        if quantity > self.MAX_QUANTITY_PER_LISTING:
            return {
                "success": False,
                "message": (
                    f"Mỗi slot shop chỉ được đăng bán tối đa "
                    f"**{self.MAX_QUANTITY_PER_LISTING}** item."
                ),
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
            itemText = buildItemText(item)

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

            totalMarketPrice = item.sell_price * quantity

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

            memberSellerPayout = self.calculateMemberSellerPayout(totalMarketPrice)

            return {
                "success": True,
                "result": {
                    "quantity": quantity,
                    "itemText": itemText,
                    "totalMarketPrice": totalMarketPrice,
                    "memberSellerPayout": memberSellerPayout,
                    "dailyMemberSellerBonusLimit": DAILY_MEMBER_SELLER_BONUS_LIMIT,
                    "listingId": farmMarketListing.id,
                    "dailyTaskMessage": dailyTaskMessage,
                },
            }

    def calculateMemberSellerPayout(self, listingPrice: int):
        payoutRatePercent = 100 + MEMBER_SELLER_BONUS_RATE_PERCENT
        return (listingPrice * payoutRatePercent + 99) // 100
