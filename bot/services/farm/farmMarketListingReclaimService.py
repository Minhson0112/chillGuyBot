from bot.config.database import getDbSession
from bot.helper.farmItemHelper import buildItemText
from bot.repository.farmMarketListingRepository import FarmMarketListingRepository
from bot.repository.userInventoryRepository import UserInventoryRepository


class FarmMarketListingReclaimService:
    def findReclaimOptions(
        self,
        sellerUserId: int,
        page: int,
        perPage: int,
    ):
        with getDbSession() as session:
            farmMarketListingRepository = FarmMarketListingRepository(session)
            marketListings = farmMarketListingRepository.findOpenListingsBySellerUserIdAndPage(
                sellerUserId=sellerUserId,
                page=page,
                perPage=perPage,
            )

            return [
                {
                    "listingId": marketListing.id,
                    "itemName": marketListing.item.name,
                    "iconImageKey": marketListing.item.icon_image_key,
                    "quantity": marketListing.quantity,
                }
                for marketListing in marketListings
                if marketListing.item is not None
            ]

    def reclaimListing(
        self,
        userId: int,
        listingId: int,
    ):
        with getDbSession() as session:
            farmMarketListingRepository = FarmMarketListingRepository(session)
            userInventoryRepository = UserInventoryRepository(session)
            marketListing = farmMarketListingRepository.findByIdWithItemAndSeller(listingId)

            if marketListing is None or marketListing.item is None:
                return {
                    "success": False,
                    "message": "Không tìm thấy món đồ đang bán này.",
                }

            if marketListing.seller_user_id != userId:
                return {
                    "success": False,
                    "message": "Bạn không thể lấy lại món đồ của shop khác.",
                }

            if marketListing.is_sold:
                return {
                    "success": False,
                    "message": "Món đồ này đã được bán và không thể lấy lại.",
                }

            itemText = buildItemText(marketListing.item)
            quantity = marketListing.quantity

            userInventoryRepository.addOrCreate(
                userId=userId,
                itemId=marketListing.item_id,
                quantity=quantity,
            )
            farmMarketListingRepository.delete(marketListing)
            session.commit()

            return {
                "success": True,
                "message": f"Đã lấy lại **{quantity}** {itemText} về kho.",
            }
