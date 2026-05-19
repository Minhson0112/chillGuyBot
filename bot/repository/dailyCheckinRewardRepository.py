from sqlalchemy.orm import joinedload

from bot.models.dailyCheckinReward import DailyCheckinReward


class DailyCheckinRewardRepository:
    def __init__(self, session):
        self.session = session

    def findActiveByStreakDayWithItem(self, streakDay: int):
        return (
            self.session.query(DailyCheckinReward)
            .options(joinedload(DailyCheckinReward.rewardItem))
            .filter(DailyCheckinReward.streak_day == streakDay)
            .filter(DailyCheckinReward.is_active.is_(True))
            .first()
        )