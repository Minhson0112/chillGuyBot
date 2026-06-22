from datetime import datetime, timedelta, timezone

from bot.config.database import getDbSession
from bot.config.emoji import FARM_GAME_EMOJI
from bot.helper.farmItemHelper import buildItemText
from bot.repository.giftcodeClaimHistoryRepository import GiftcodeClaimHistoryRepository
from bot.repository.giftcodeRepository import GiftcodeRepository
from bot.repository.memberRepository import MemberRepository
from bot.repository.userInventoryRepository import UserInventoryRepository


class GiftcodeService:
    GMT7 = timezone(timedelta(hours=7))

    def claimGiftcode(
        self,
        userId: int,
        code: str,
    ):
        if code is None or code.strip() == "":
            return {
                "success": False,
                "message": "Vui lòng nhập giftcode.",
            }

        normalizedCode = code.strip()

        with getDbSession() as session:
            memberRepository = MemberRepository(session)
            giftcodeRepository = GiftcodeRepository(session)
            giftcodeClaimHistoryRepository = GiftcodeClaimHistoryRepository(session)
            userInventoryRepository = UserInventoryRepository(session)

            member = memberRepository.findByUserId(userId)

            if member is None:
                return {
                    "success": False,
                    "message": "Không tìm thấy dữ liệu member của bạn.",
                }

            giftcode = giftcodeRepository.findByCodeWithRewards(normalizedCode)

            if giftcode is None:
                return {
                    "success": False,
                    "message": "Giftcode không tồn tại.",
                }

            today = self.getTodayDate()

            if giftcode.expired_at < today:
                return {
                    "success": False,
                    "message": "Giftcode này đã hết hạn.",
                }

            claimedHistory = giftcodeClaimHistoryRepository.findByUserIdAndGiftcodeId(
                userId=userId,
                giftcodeId=giftcode.id,
            )

            if claimedHistory is not None:
                return {
                    "success": False,
                    "message": "Bạn đã nhận giftcode này rồi.",
                }

            if giftcode.reward_chill_coin > 0:
                member.chill_coin += giftcode.reward_chill_coin

            rewardItemMessages = []

            for reward in giftcode.rewards:
                if reward.item is None:
                    continue

                if reward.quantity <= 0:
                    continue

                userInventoryRepository.addOrCreate(
                    userId=userId,
                    itemId=reward.item_id,
                    quantity=reward.quantity,
                )

                rewardItemMessages.append(
                    f"**{self.formatNumber(reward.quantity)}** {buildItemText(reward.item)}"
                )

            giftcodeClaimHistoryRepository.create(
                userId=userId,
                giftcodeId=giftcode.id,
            )

            session.commit()

            return {
                "success": True,
                "message": self.buildSuccessMessage(
                    giftcode=giftcode,
                    rewardItemMessages=rewardItemMessages,
                ),
            }

    def buildSuccessMessage(
        self,
        giftcode,
        rewardItemMessages,
    ):
        chillCoinEmoji = FARM_GAME_EMOJI["chill_coin"]

        rewardMessages = []

        if giftcode.reward_chill_coin > 0:
            rewardMessages.append(
                f"**{self.formatNumber(giftcode.reward_chill_coin)}** {chillCoinEmoji}"
            )

        rewardMessages.extend(rewardItemMessages)

        if not rewardMessages:
            rewardText = "Giftcode này không có phần thưởng."
        else:
            rewardText = "\n".join(f"- {message}" for message in rewardMessages)

        return (
            f"Nhận giftcode **{giftcode.code}** thành công.\n"
            f"Phần thưởng nhận được:\n"
            f"{rewardText}"
        )

    def getTodayDate(self):
        return datetime.now(self.GMT7).date()

    def formatNumber(self, number: int):
        return f"{number:,}"
