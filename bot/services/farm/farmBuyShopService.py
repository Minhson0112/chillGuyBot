from bot.config.database import getDbSession
from bot.config.emoji import FARM_GAME_EMOJI
from bot.repository.farmMarketListingRepository import FarmMarketListingRepository
from bot.repository.memberRepository import MemberRepository
from bot.repository.userInventoryRepository import UserInventoryRepository
from bot.services.farm.dailyTaskProgressService import DailyTaskProgressService


class FarmBuyShopService:
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
            itemText = self.buildItemText(item)
            chillCoinEmoji = FARM_GAME_EMOJI["chill_coin"]

            if buyer.chill_coin < marketListing.price:
                return {
                    "success": False,
                    "message": (
                        f"Mua **{marketListing.quantity}** {itemText} cần "
                        f"**{self.formatNumber(marketListing.price)}** {chillCoinEmoji}, "
                        f"bạn chỉ có **{self.formatNumber(buyer.chill_coin)}** {chillCoinEmoji}."
                    ),
                }

            buyer.chill_coin -= marketListing.price
            seller.chill_coin += marketListing.price

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
                f"**{self.formatNumber(marketListing.price)}** {chillCoinEmoji}."
            )

            if dailyTaskMessage is not None:
                message += f"\n\n{dailyTaskMessage}"

            return {
                "success": True,
                "message": message,
            }

    def buildItemText(self, item):
        itemEmoji = FARM_GAME_EMOJI.get(item.icon_image_key)

        if itemEmoji is None:
            return f"**{item.name}**"

        return f"{itemEmoji} **{item.name}**"

    def getSellerDisplayName(self, seller):
        if seller.nick:
            return seller.nick

        if seller.global_name:
            return seller.global_name

        return seller.username

    def formatNumber(self, number: int):
        return f"{number:,}"