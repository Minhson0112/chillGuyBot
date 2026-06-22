from bot.config.database import getDbSession
from bot.config.emoji import FARM_GAME_EMOJI
from bot.helper.farmItemHelper import buildItemText
from bot.repository.farmMarketListingRepository import FarmMarketListingRepository
from bot.repository.itemRepository import ItemRepository
from bot.repository.memberRepository import MemberRepository


class FarmMarketSearchService:
    SEARCH_COST = 5

    def findItemByName(self, itemName: str):
        if itemName is None or itemName.strip() == "":
            return {
                "success": False,
                "message": "Vui lòng nhập tên món đồ muốn tìm.",
            }

        with getDbSession() as session:
            itemRepository = ItemRepository(session)

            item = itemRepository.findActiveByNameKeyword(itemName)

            if item is None:
                return {
                    "success": False,
                    "message": f"Không tìm thấy món đồ gần giống với **{itemName}**.",
                }

            return {
                "success": True,
                "item": {
                    "id": item.id,
                    "name": item.name,
                    "code": item.code,
                    "iconImageKey": item.icon_image_key,
                },
                "itemText": buildItemText(item),
                "searchCost": self.SEARCH_COST,
            }

    def searchFirstListing(
        self,
        searcherUserId: int,
        itemId: int,
    ):
        with getDbSession() as session:
            memberRepository = MemberRepository(session)
            farmMarketListingRepository = FarmMarketListingRepository(session)

            searcher = memberRepository.findByUserId(searcherUserId)

            if searcher is None:
                return {
                    "success": False,
                    "message": "Không tìm thấy dữ liệu member của bạn.",
                }

            marketListing = farmMarketListingRepository.findFirstOpenListingByItemId(itemId)

            if marketListing is None or marketListing.item is None:
                return {
                    "success": False,
                    "message": "Hiện tại chưa có farm nào đang bán món đồ này. Bạn không mất phí tìm kiếm.",
                    "notFound": True,
                }

            chillCoinEmoji = FARM_GAME_EMOJI["chill_coin"]

            if searcher.chill_coin < self.SEARCH_COST:
                return {
                    "success": False,
                    "message": (
                        f"Bạn cần **{self.formatNumber(self.SEARCH_COST)}** {chillCoinEmoji} "
                        f"để tìm kiếm, hiện bạn có **{self.formatNumber(searcher.chill_coin)}** {chillCoinEmoji}."
                    ),
                }

            searcher.chill_coin -= self.SEARCH_COST

            seller = marketListing.seller
            item = marketListing.item

            result = {
                "listingId": marketListing.id,
                "sellerUserId": marketListing.seller_user_id,
                "sellerDisplayName": self.getSellerDisplayName(seller),
                "itemName": item.name,
                "itemIconImageKey": item.icon_image_key,
                "itemText": buildItemText(item),
                "quantity": marketListing.quantity,
                "price": marketListing.price,
                "searchCost": self.SEARCH_COST,
            }

            session.commit()

            return {
                "success": True,
                "result": result,
                "message": "Đã tìm thấy shop đang bán món đồ này.",
            }

    def getSellerDisplayName(self, seller):
        if seller is None:
            return "Không rõ"

        if seller.nick:
            return seller.nick

        if seller.global_name:
            return seller.global_name

        return seller.username

    def formatNumber(self, number: int):
        return f"{number:,}"
