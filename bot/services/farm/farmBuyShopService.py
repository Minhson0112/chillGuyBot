from bot.helper.numberFormatHelper import formatNumber
from bot.config.database import getDbSession
from bot.config.emoji import FARM_GAME_EMOJI
from bot.helper.farmItemHelper import buildItemText
from bot.repository.farmMarketListingRepository import FarmMarketListingRepository
from bot.repository.memberRepository import MemberRepository
from bot.repository.userInventoryRepository import UserInventoryRepository
from bot.services.farm.dailyTaskProgressService import DailyTaskProgressService


class FarmBuyShopService:
    SELLER_BONUS_RATE_PERCENT = 20

    DAILY_TASK_TYPE_BUY_MARKET_ITEM = "buy_market_item"

    def buyShopItem(
        self,
        buyerUserId: int,
        listingId: int,
    ):
        with getDbSession() as session:
            memberRepository = MemberRepository(session)
            farmMarketListingRepository = FarmMarketListingRepository(session)
            userInventoryRepository = UserInventoryRepository(session)
            dailyTaskProgressService = DailyTaskProgressService(session)

            buyer = memberRepository.findByUserId(buyerUserId)

            if buyer is None:
                return {
                    "success": False,
                    "message": "Không tìm thấy dữ liệu member của bạn.",
                }

            marketListing = farmMarketListingRepository.findByIdWithItemAndSeller(listingId)

            if marketListing is None or marketListing.item is None:
                return {
                    "success": False,
                    "message": f"Không tìm thấy món hàng với ID **{listingId}**.",
                }

            if marketListing.is_sold:
                return {
                    "success": False,
                    "message": "Món hàng này đã được bán.",
                }

            if marketListing.seller_user_id == buyerUserId:
                return {
                    "success": False,
                    "message": "Bạn không thể mua món hàng do chính mình đăng bán.",
                }

            seller = marketListing.seller

            if seller is None:
                return {
                    "success": False,
                    "message": "Không tìm thấy dữ liệu người bán.",
                }

            item = marketListing.item
            itemText = buildItemText(item)
            chillCoinEmoji = FARM_GAME_EMOJI["chill_coin"]

            if buyer.chill_coin < marketListing.price:
                return {
                    "success": False,
                    "message": (
                        f"Mua **{marketListing.quantity}** {itemText} cần "
                        f"**{formatNumber(marketListing.price)}** {chillCoinEmoji}, "
                        f"bạn chỉ có **{formatNumber(buyer.chill_coin)}** {chillCoinEmoji}."
                    ),
                }

            sellerPayout = self.calculateSellerPayout(marketListing.price)

            buyer.chill_coin -= marketListing.price
            seller.chill_coin += sellerPayout

            userInventoryRepository.addOrCreate(
                userId=buyerUserId,
                itemId=marketListing.item_id,
                quantity=marketListing.quantity,
            )

            farmMarketListingRepository.markSold(
                farmMarketListing=marketListing,
                buyerUserId=buyerUserId,
            )

            completedDailyTasks = dailyTaskProgressService.addProgress(
                userId=buyerUserId,
                taskType=self.DAILY_TASK_TYPE_BUY_MARKET_ITEM,
                amount=marketListing.quantity,
                targetItemId=marketListing.item_id,
            )

            dailyTaskMessage = dailyTaskProgressService.buildCompletedTaskMessage(
                completedDailyTasks,
            )

            session.commit()

            message = (
                f"Bạn đã mua **{marketListing.quantity}** {itemText} "
                f"từ shop của **{self.getSellerDisplayName(seller)}** với "
                f"**{formatNumber(marketListing.price)}** {chillCoinEmoji}."
            )

            if dailyTaskMessage is not None:
                message += f"\n\n{dailyTaskMessage}"

            notificationData = None

            if seller.is_allow_notifications:
                notificationData = {
                    "sellerUserId": seller.user_id,
                    "buyerDisplayName": self.getSellerDisplayName(buyer),
                    "quantity": marketListing.quantity,
                    "itemText": itemText,
                    "listingPrice": marketListing.price,
                    "sellerPayout": sellerPayout,
                }

            return {
                "success": True,
                "message": message,
                "notificationData": notificationData,
            }

    def calculateSellerPayout(self, listingPrice: int):
        payoutRatePercent = 100 + self.SELLER_BONUS_RATE_PERCENT
        return (listingPrice * payoutRatePercent + 99) // 100

    def getSellerDisplayName(self, seller):
        if seller.nick:
            return seller.nick

        if seller.global_name:
            return seller.global_name

        return seller.username
