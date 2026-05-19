from datetime import datetime

from bot.config.database import getDbSession
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

            session.commit()

            return {
                "success": True,
                "soldCount": soldCount,
                "totalPaid": totalPaid,
                "message": f"Auto buy completed. Sold {soldCount} listings.",
            }