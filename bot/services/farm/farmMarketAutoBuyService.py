from datetime import datetime

from bot.config.database import getDbSession
from bot.config.emoji import FARM_GAME_EMOJI
from bot.repository.farmMarketListingRepository import FarmMarketListingRepository
from bot.repository.memberRepository import MemberRepository


class FarmMarketAutoBuyService:
    EXPIRED_HOURS = 47

    def autoBuyExpiredListings(self, botUserId: int):
        with getDbSession() as session:
            memberRepository = MemberRepository(session)
            farmMarketListingRepository = FarmMarketListingRepository(session)

            botMember = memberRepository.findByUserId(botUserId)

            if botMember is None:
                return {
                    "success": False,
                    "soldCount": 0,
                    "message": "Không tìm thấy dữ liệu member của bot. Không thể auto buy vì buyer_user_id cần tồn tại.",
                }

            now = datetime.now()

            expiredListings = farmMarketListingRepository.findExpiredOpenListings(
                now=now,
                expiredHours=self.EXPIRED_HOURS,
            )

            soldCount = 0
            totalPaid = 0
            notificationSummaries = {}

            for listing in expiredListings:
                seller = listing.seller

                if seller is None:
                    continue

                seller.chill_coin += listing.price

                farmMarketListingRepository.markSold(
                    farmMarketListing=listing,
                    buyerUserId=botUserId,
                )

                soldCount += 1
                totalPaid += listing.price

                if seller.is_allow_notifications:
                    self.addNotificationSummary(
                        notificationSummaries=notificationSummaries,
                        sellerUserId=seller.user_id,
                        listing=listing,
                    )

            session.commit()

            return {
                "success": True,
                "soldCount": soldCount,
                "totalPaid": totalPaid,
                "notificationSummaries": list(notificationSummaries.values()),
                "message": f"Auto buy completed. Sold {soldCount} listings.",
            }

    def addNotificationSummary(
        self,
        notificationSummaries,
        sellerUserId: int,
        listing,
    ):
        if sellerUserId not in notificationSummaries:
            notificationSummaries[sellerUserId] = {
                "sellerUserId": sellerUserId,
                "totalPaid": 0,
                "items": [],
            }

        notificationSummaries[sellerUserId]["totalPaid"] += listing.price
        notificationSummaries[sellerUserId]["items"].append({
            "itemText": self.buildItemText(listing.item),
            "quantity": listing.quantity,
            "price": listing.price,
        })

    def buildItemText(self, item):
        if item is None:
            return "**item không xác định**"

        itemEmoji = FARM_GAME_EMOJI.get(item.icon_image_key)

        if itemEmoji is None:
            return f"**{item.name}**"

        return f"{itemEmoji} **{item.name}**"
