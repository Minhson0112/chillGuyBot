from datetime import datetime, timedelta, timezone

from bot.config.database import getDbSession
from bot.config.emoji import FARM_GAME_EMOJI
from bot.repository.dailyCheckinHistoryRepository import DailyCheckinHistoryRepository
from bot.repository.dailyCheckinRewardRepository import DailyCheckinRewardRepository
from bot.repository.memberRepository import MemberRepository
from bot.repository.userInventoryRepository import UserInventoryRepository


class DailyCheckinService:
    MAX_STREAK_DAY = 7
    GMT7 = timezone(timedelta(hours=7))

    def checkin(self, userId: int):
        today = self.getTodayDate()
        yesterday = today - timedelta(days=1)

        with getDbSession() as session:
            memberRepository = MemberRepository(session)
            userInventoryRepository = UserInventoryRepository(session)
            dailyCheckinHistoryRepository = DailyCheckinHistoryRepository(session)
            dailyCheckinRewardRepository = DailyCheckinRewardRepository(session)

            member = memberRepository.findByUserId(userId)

            if member is None:
                return {
                    "success": False,
                    "message": "Không tìm thấy dữ liệu member của bạn.",
                }

            todayCheckin = dailyCheckinHistoryRepository.findByUserIdAndCheckinDate(
                userId=userId,
                checkinDate=today,
            )

            if todayCheckin is not None:
                return {
                    "success": False,
                    "message": (
                        f"Hôm nay bạn đã điểm danh rồi.\n"
                        f"Chuỗi điểm danh hiện tại: ngày **{todayCheckin.streak_day}**."
                    ),
                }

            latestCheckin = dailyCheckinHistoryRepository.findLatestByUserId(userId)
            streakDay = self.calculateStreakDay(latestCheckin, yesterday)

            reward = dailyCheckinRewardRepository.findActiveByStreakDayWithItem(streakDay)

            if reward is None:
                return {
                    "success": False,
                    "message": f"Không tìm thấy phần thưởng điểm danh ngày **{streakDay}**.",
                }

            member.chill_coin += reward.reward_chill_coin

            rewardItemId = None
            rewardItemQuantity = 0

            if reward.reward_item_id is not None and reward.reward_item_quantity > 0:
                rewardItemId = reward.reward_item_id
                rewardItemQuantity = reward.reward_item_quantity

                userInventoryRepository.addOrCreate(
                    userId=userId,
                    itemId=rewardItemId,
                    quantity=rewardItemQuantity,
                )

            dailyCheckinHistoryRepository.create(
                userId=userId,
                checkinDate=today,
                streakDay=streakDay,
                rewardChillCoin=reward.reward_chill_coin,
                rewardItemId=rewardItemId,
                rewardItemQuantity=rewardItemQuantity,
            )

            session.commit()

            return {
                "success": True,
                "message": self.buildSuccessMessage(
                    streakDay=streakDay,
                    reward=reward,
                ),
            }

    def calculateStreakDay(self, latestCheckin, yesterday):
        if latestCheckin is None:
            return 1

        if latestCheckin.checkin_date != yesterday:
            return 1

        nextStreakDay = latestCheckin.streak_day + 1

        if nextStreakDay > self.MAX_STREAK_DAY:
            return 1

        return nextStreakDay

    def buildSuccessMessage(self, streakDay: int, reward):
        chillCoinEmoji = FARM_GAME_EMOJI["chill_coin"]

        rewardMessages = [
            f"**{self.formatNumber(reward.reward_chill_coin)}** {chillCoinEmoji}",
        ]

        if reward.rewardItem is not None and reward.reward_item_quantity > 0:
            rewardMessages.append(
                f"**{self.formatNumber(reward.reward_item_quantity)}** {self.buildItemText(reward.rewardItem)}"
            )

        return (
            f"Điểm danh thành công ngày **{streakDay}**.\n"
            f"Bạn nhận được: " + " và ".join(rewardMessages)
        )

    def buildItemText(self, item):
        itemEmoji = FARM_GAME_EMOJI.get(item.icon_image_key)

        if itemEmoji is None:
            return f"**{item.name}**"

        return f"{itemEmoji} **{item.name}**"

    def getTodayDate(self):
        return datetime.now(self.GMT7).date()

    def formatNumber(self, number: int):
        return f"{number:,}"