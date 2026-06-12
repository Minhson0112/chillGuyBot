from datetime import datetime

from sqlalchemy import asc, case, desc, func

from bot.models.member import Member
from bot.models.mergeGamePlayHistory import MergeGamePlayHistory


class MergeGamePlayHistoryRepository:
    def __init__(self, session):
        self.session = session

    def findTopMembersByMonth(
        self,
        year: int,
        month: int,
        limit: int = 5,
    ):
        startAt, endAt = self.getMonthRange(year, month)

        bestScore = func.max(MergeGamePlayHistory.score).label("best_score")
        fastestSunTime = func.min(MergeGamePlayHistory.sun_time).label("fastest_sun_time")

        return (
            self.session.query(
                Member.user_id,
                Member.global_name,
                Member.username,
                Member.nick,
                bestScore,
                fastestSunTime,
            )
            .join(Member, Member.user_id == MergeGamePlayHistory.user_id)
            .filter(MergeGamePlayHistory.created_at >= startAt)
            .filter(MergeGamePlayHistory.created_at < endAt)
            .group_by(
                Member.user_id,
                Member.global_name,
                Member.username,
                Member.nick,
            )
            .order_by(
                desc(bestScore),
                asc(case((fastestSunTime.is_(None), 1), else_=0)),
                asc(fastestSunTime),
            )
            .limit(limit)
            .all()
        )

    def findTopSunMembersByMonth(
        self,
        year: int,
        month: int,
        limit: int = 5,
    ):
        startAt, endAt = self.getMonthRange(year, month)

        bestScore = func.max(MergeGamePlayHistory.score).label("best_score")
        fastestSunTime = func.min(MergeGamePlayHistory.sun_time).label("fastest_sun_time")

        return (
            self.session.query(
                Member.user_id,
                Member.global_name,
                Member.username,
                Member.nick,
                bestScore,
                fastestSunTime,
            )
            .join(Member, Member.user_id == MergeGamePlayHistory.user_id)
            .filter(MergeGamePlayHistory.created_at >= startAt)
            .filter(MergeGamePlayHistory.created_at < endAt)
            .filter(MergeGamePlayHistory.sun_time.isnot(None))
            .group_by(
                Member.user_id,
                Member.global_name,
                Member.username,
                Member.nick,
            )
            .order_by(
                asc(fastestSunTime),
                desc(bestScore),
            )
            .limit(limit)
            .all()
        )

    def findMemberStatsByMonth(
        self,
        userId: int,
        year: int,
        month: int,
    ):
        startAt, endAt = self.getMonthRange(year, month)

        bestScore = func.max(MergeGamePlayHistory.score).label("best_score")
        fastestSunTime = func.min(MergeGamePlayHistory.sun_time).label("fastest_sun_time")

        return (
            self.session.query(
                bestScore,
                fastestSunTime,
            )
            .filter(MergeGamePlayHistory.user_id == userId)
            .filter(MergeGamePlayHistory.created_at >= startAt)
            .filter(MergeGamePlayHistory.created_at < endAt)
            .one()
        )

    def getMonthRange(self, year: int, month: int):
        startAt = datetime(year, month, 1)

        if month == 12:
            endAt = datetime(year + 1, 1, 1)
        else:
            endAt = datetime(year, month + 1, 1)

        return startAt, endAt
