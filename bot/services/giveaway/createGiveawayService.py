from datetime import datetime, timedelta, timezone

from bot.config.database import getDbSession
from bot.enums.giveawayType import GiveawayType
from bot.repository.giveawayRepository import GiveawayRepository


class CreateGiveawayService:
    GMT7 = timezone(timedelta(hours=7))

    def createGiveaway(
        self,
        title: str,
        giveawayType: str,
        winnerCount: int,
        durationSeconds: int,
        channelId: int,
        createdByUserId: int,
        reward: int | None = None,
        rewardText: str | None = None,
        limitRoleId: int | None = None,
    ):
        title = title.strip()

        if title == "":
            return {
                "success": False,
                "message": "Tiêu đề giveaway không được để trống.",
            }

        try:
            giveawayTypeEnum = GiveawayType(giveawayType)
        except ValueError:
            return {
                "success": False,
                "message": "Loại giveaway không hợp lệ.",
            }

        if giveawayTypeEnum not in self.getAllowedGiveawayTypes():
            return {
                "success": False,
                "message": "Loại giveaway không hợp lệ.",
            }

        if giveawayTypeEnum.isMonetary and (reward is None or reward <= 0):
            return {
                "success": False,
                "message": "Phần thưởng phải lớn hơn 0.",
            }

        if giveawayTypeEnum.isSubscription:
            rewardText = rewardText.strip() if rewardText is not None else ""

            if rewardText == "":
                return {
                    "success": False,
                    "message": "Thời hạn phần thưởng subscription không được để trống.",
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
        rewardData = self.buildRewardData(giveawayTypeEnum, reward, rewardText)

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
                rewardText=rewardData["rewardText"],
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
            giveawayType
            for giveawayType in GiveawayType
            if giveawayType.isMonetary or giveawayType.isSubscription
        }

    def buildRewardData(
        self,
        giveawayType: GiveawayType,
        reward: int | None,
        rewardText: str | None,
    ):
        rewardData = {
            "rewardChillCoin": None,
            "rewardCowoncy": None,
            "rewardVnd": None,
            "rewardText": rewardText if giveawayType.isSubscription else None,
        }

        if giveawayType == GiveawayType.CHILL_COIN:
            rewardData["rewardChillCoin"] = reward

        if giveawayType == GiveawayType.COWONCY:
            rewardData["rewardCowoncy"] = reward

        if giveawayType == GiveawayType.VND:
            rewardData["rewardVnd"] = reward

        return rewardData
