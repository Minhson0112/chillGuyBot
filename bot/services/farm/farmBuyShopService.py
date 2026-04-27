from bot.config.database import getDbSession
from bot.config.emoji import FARM_GAME_EMOJI
from bot.repository.farmMarketListingRepository import FarmMarketListingRepository
from bot.repository.memberRepository import MemberRepository
from bot.repository.userInventoryRepository import UserInventoryRepository


class FarmBuyShopService:
    def buyShopItem(
        self,
        buyerUserId: int,
        listingId: int,
    ):
        with getDbSession() as session:
            memberRepository = MemberRepository(session)
            farmMarketListingRepository = FarmMarketListingRepository(session)
            userInventoryRepository = UserInventoryRepository(session)

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
                        f"{chillCoinEmoji} **{self.formatNumber(marketListing.price)}**, "
                        f"bạn chỉ có {chillCoinEmoji} **{self.formatNumber(buyer.chill_coin)}**."
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

            session.commit()

            return {
                "success": True,
                "message": (
                    f"Bạn đã mua **{marketListing.quantity}** {itemText} "
                    f"từ shop của **{self.getSellerDisplayName(seller)}** với "
                    f"{chillCoinEmoji} **{self.formatNumber(marketListing.price)}**."
                ),
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