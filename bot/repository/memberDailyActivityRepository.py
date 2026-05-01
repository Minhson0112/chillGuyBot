from datetime import date

from sqlalchemy import desc, func

from bot.models.member import Member
from bot.models.memberDailyActivity import MemberDailyActivity


class MemberDailyActivityRepository:
    def __init__(self, session):
        self.session = session

    def findByUserIdAndActivityDate(self, userId, activityDate):
        return (
            self.session.query(MemberDailyActivity)
            .filter(
                MemberDailyActivity.user_id == userId,
                MemberDailyActivity.activity_date == activityDate,
            )
            .first()
        )

    def create(self, activityData):
        activity = MemberDailyActivity(**activityData)
        self.session.add(activity)
        self.session.flush()
        return activity

    def incrementDailyActivity(
        self,
        userId,
        activityDate,
        totalChatIncrement=0,
        levelChatIncrement=0,
        voiceSecondsIncrement=0,
    ):
        activity = self.findByUserIdAndActivityDate(userId, activityDate)

        if activity is None:
            activity = self.create({
                "user_id": userId,
                "activity_date": activityDate,
                "total_chat_count": 0,
                "level_chat_count": 0,
                "voice_seconds": 0,
            })

        activity.total_chat_count += totalChatIncrement
        activity.level_chat_count += levelChatIncrement
        activity.voice_seconds += voiceSecondsIncrement

        self.session.flush()
        return activity

    def findTopChatMembersByMonth(self, year, month, limit=10):
        startDate, endDate = self.getMonthRange(year, month)

        totalChatCount = func.sum(MemberDailyActivity.total_chat_count).label("total_chat_count")
        levelChatCount = func.sum(MemberDailyActivity.level_chat_count).label("level_chat_count")
        voiceSeconds = func.sum(MemberDailyActivity.voice_seconds).label("voice_seconds")

        return (
            self.session.query(
                Member.user_id,
                Member.global_name,
                Member.username,
                Member.nick,
                totalChatCount,
                levelChatCount,
                voiceSeconds,
            )
            .join(Member, Member.user_id == MemberDailyActivity.user_id)
            .filter(
                MemberDailyActivity.activity_date >= startDate,
                MemberDailyActivity.activity_date < endDate,
            )
            .group_by(
                Member.user_id,
                Member.global_name,
                Member.username,
                Member.nick,
            )
            .order_by(desc(totalChatCount))
            .limit(limit)
            .all()
        )

    def findTopVoiceMembersByMonth(self, year, month, limit=10):
        startDate, endDate = self.getMonthRange(year, month)

        totalChatCount = func.sum(MemberDailyActivity.total_chat_count).label("total_chat_count")
        levelChatCount = func.sum(MemberDailyActivity.level_chat_count).label("level_chat_count")
        voiceSeconds = func.sum(MemberDailyActivity.voice_seconds).label("voice_seconds")

        return (
            self.session.query(
                Member.user_id,
                Member.global_name,
                Member.username,
                Member.nick,
                totalChatCount,
                levelChatCount,
                voiceSeconds,
            )
            .join(Member, Member.user_id == MemberDailyActivity.user_id)
            .filter(
                MemberDailyActivity.activity_date >= startDate,
                MemberDailyActivity.activity_date < endDate,
            )
            .group_by(
                Member.user_id,
                Member.global_name,
                Member.username,
                Member.nick,
            )
            .order_by(desc(voiceSeconds))
            .limit(limit)
            .all()
        )

    def getMonthRange(self, year, month):
        startDate = date(year, month, 1)

        if month == 12:
            endDate = date(year + 1, 1, 1)
        else:
            endDate = date(year, month + 1, 1)

        return startDate, endDate
    
    def findTopLevelChatMembersByMonth(self, year, month, limit=10):
        startDate, endDate = self.getMonthRange(year, month)

        levelChatCount = func.sum(MemberDailyActivity.level_chat_count).label("level_chat_count")

        return (
            self.session.query(
                Member.user_id,
                Member.global_name,
                Member.username,
                Member.nick,
                levelChatCount,
            )
            .join(Member, Member.user_id == MemberDailyActivity.user_id)
            .filter(
                MemberDailyActivity.activity_date >= startDate,
                MemberDailyActivity.activity_date < endDate,
            )
            .group_by(
                Member.user_id,
                Member.global_name,
                Member.username,
                Member.nick,
            )
            .having(levelChatCount > 0)
            .order_by(desc(levelChatCount))
            .limit(limit)
            .all()
        )

def getMonthRange(self, year, month):
    startDate = date(year, month, 1)

    if month == 12:
        endDate = date(year + 1, 1, 1)
    else:
        endDate = date(year, month + 1, 1)

    return startDate, endDate