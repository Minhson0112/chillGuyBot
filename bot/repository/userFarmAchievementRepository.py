from datetime import datetime

from bot.models.userFarmAchievement import UserFarmAchievement


class UserFarmAchievementRepository:
    def __init__(self, session):
        self.session = session

    def findByUserIdAndAchievementId(
        self,
        userId: int,
        achievementId: int,
    ):
        return (
            self.session.query(UserFarmAchievement)
            .filter(UserFarmAchievement.user_id == userId)
            .filter(UserFarmAchievement.achievement_id == achievementId)
            .first()
        )

    def findByUserIdAndAchievementIdForUpdate(
        self,
        userId: int,
        achievementId: int,
    ):
        return (
            self.session.query(UserFarmAchievement)
            .filter(UserFarmAchievement.user_id == userId)
            .filter(UserFarmAchievement.achievement_id == achievementId)
            .with_for_update()
            .first()
        )

    def create(
        self,
        userId: int,
        achievementId: int,
        progressValue: int,
        isCompleted: bool,
        completedAt,
    ):
        userFarmAchievement = UserFarmAchievement(
            user_id=userId,
            achievement_id=achievementId,
            progress_value=progressValue,
            is_completed=isCompleted,
            completed_at=completedAt,
            is_reward_claimed=False,
            reward_claimed_at=None,
        )

        self.session.add(userFarmAchievement)
        self.session.flush()

        return userFarmAchievement

    def upsertProgress(
        self,
        userId: int,
        achievementId: int,
        progressValue: int,
        isCompleted: bool,
        now: datetime,
    ):
        userFarmAchievement = self.findByUserIdAndAchievementId(
            userId=userId,
            achievementId=achievementId,
        )

        completedAt = now if isCompleted else None

        if userFarmAchievement is None:
            return self.create(
                userId=userId,
                achievementId=achievementId,
                progressValue=progressValue,
                isCompleted=isCompleted,
                completedAt=completedAt,
            )

        userFarmAchievement.progress_value = progressValue

        if isCompleted and not userFarmAchievement.is_completed:
            userFarmAchievement.is_completed = True
            userFarmAchievement.completed_at = now

        self.session.flush()

        return userFarmAchievement

    def markRewardClaimed(
        self,
        userFarmAchievement,
        now: datetime,
    ):
        userFarmAchievement.is_reward_claimed = True
        userFarmAchievement.reward_claimed_at = now

        self.session.flush()

        return userFarmAchievement
