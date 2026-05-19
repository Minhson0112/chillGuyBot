from sqlalchemy import desc

from bot.models.dailyCheckinHistory import DailyCheckinHistory


class DailyCheckinHistoryRepository:
    def __init__(self, session):
        self.session = session

    def findByUserIdAndCheckinDate(
        self,
        userId: int,
        checkinDate,
    ):
        return (
            self.session.query(DailyCheckinHistory)
            .filter(DailyCheckinHistory.user_id == userId)
            .filter(DailyCheckinHistory.checkin_date == checkinDate)
            .first()
        )

    def findLatestByUserId(self, userId: int):
        return (
            self.session.query(DailyCheckinHistory)
            .filter(DailyCheckinHistory.user_id == userId)
            .order_by(
                desc(DailyCheckinHistory.checkin_date),
                desc(DailyCheckinHistory.id),
            )
            .first()
        )

    def create(
        self,
        userId: int,
        checkinDate,
        streakDay: int,
        rewardChillCoin: int,
        rewardItemId: int = None,
        rewardItemQuantity: int = 0,
    ):
        dailyCheckinHistory = DailyCheckinHistory(
            user_id=userId,
            checkin_date=checkinDate,
            streak_day=streakDay,
            reward_chill_coin=rewardChillCoin,
            reward_item_id=rewardItemId,
            reward_item_quantity=rewardItemQuantity,
        )

        self.session.add(dailyCheckinHistory)
        self.session.flush()

        return dailyCheckinHistory