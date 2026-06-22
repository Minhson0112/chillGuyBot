from datetime import datetime, timedelta, timezone

from bot.helper.numberFormatHelper import formatNumber
from bot.config.database import getDbSession
from bot.enums.giveawayType import GiveawayType
from bot.repository.giveawayRepository import GiveawayRepository


class CreateGiveawayService:
    GMT7 = timezone(timedelta(hours=7))

    def createGiveaway(
        self,
        title: str,
        giveawayType: str,
        reward: int,
        winnerCount: int,
        durationSeconds: int,
        channelId: int,
        createdByUserId: int,
        limitRoleId: int | None = None,
    ):
        title = title.strip()

        if title == "":
            return {
                "success": False,
                "message": "Tiêu đề giveaway không được để trống.",
            }

        if giveawayType not in self.getAllowedGiveawayTypes():
            return {
                "success": False,
                "message": "Loại giveaway không hợp lệ.",
            }

        if reward <= 0:
            return {
                "success": False,
                "message": "Phần thưởng phải lớn hơn 0.",
            }

        if winnerCount <= 0:
            return {
                "success": False,
                "message": "Số người thắng phải lớn hơn 0.",
            }

        if durationSeconds <= 0:
            return {
                "success": False,
                "message": "Thời gian giveaway phải lớn hơn 0 giây.",
            }

        now = datetime.now(self.GMT7).replace(tzinfo=None)
        drawAt = now + timedelta(seconds=durationSeconds)
        rewardData = self.buildRewardData(giveawayType, reward)

        with getDbSession() as session:
            giveawayRepository = GiveawayRepository(session)
            giveaway = giveawayRepository.create(
                title=title,
                giveawayType=giveawayType,
                winnerCount=winnerCount,
                durationSeconds=durationSeconds,
                drawAt=drawAt,
                channelId=channelId,
                createdByUserId=createdByUserId,
                rewardChillCoin=rewardData["rewardChillCoin"],
                rewardCowoncy=rewardData["rewardCowoncy"],
                rewardVnd=rewardData["rewardVnd"],
                limitRoleId=limitRoleId,
            )

            session.commit()

            return {
                "success": True,
                "giveawayId": giveaway.id,
                "message": (
                    f"Đã tạo giveaway **#{giveaway.id}**.\n"
                    f"Đã gửi embed giveaway vào kênh hiện tại."
                ),
            }

    def updateGiveawayMessageId(self, giveawayId: int, messageId: int):
        with getDbSession() as session:
            giveawayRepository = GiveawayRepository(session)
            giveaway = giveawayRepository.updateMessageId(
                giveawayId=giveawayId,
                messageId=messageId,
            )

            if giveaway is None:
                return False

            session.commit()

            return True

    def getAllowedGiveawayTypes(self):
        return {
            GiveawayType.CHILL_COIN.value,
            GiveawayType.COWONCY.value,
            GiveawayType.VND.value,
        }

    def buildRewardData(self, giveawayType: str, reward: int):
        rewardData = {
            "rewardChillCoin": None,
            "rewardCowoncy": None,
            "rewardVnd": None,
        }

        if giveawayType == GiveawayType.CHILL_COIN.value:
            rewardData["rewardChillCoin"] = reward

        if giveawayType == GiveawayType.COWONCY.value:
            rewardData["rewardCowoncy"] = reward

        if giveawayType == GiveawayType.VND.value:
            rewardData["rewardVnd"] = reward

        return rewardData
