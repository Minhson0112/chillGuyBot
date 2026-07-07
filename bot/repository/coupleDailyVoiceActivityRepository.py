from sqlalchemy import func

from bot.models.coupleDailyVoiceActivity import CoupleDailyVoiceActivity


class CoupleDailyVoiceActivityRepository:
    def __init__(self, session):
        self.session = session

    def findByCoupleIdAndActivityDate(self, coupleId: int, activityDate):
        return (
            self.session.query(CoupleDailyVoiceActivity)
            .filter(
                CoupleDailyVoiceActivity.couple_id == coupleId,
                CoupleDailyVoiceActivity.activity_date == activityDate,
            )
            .first()
        )

    def incrementVoiceSeconds(
        self,
        coupleId: int,
        activityDate,
        voiceSecondsIncrement: int,
    ):
        activity = self.findByCoupleIdAndActivityDate(
            coupleId=coupleId,
            activityDate=activityDate,
        )

        if activity is None:
            activity = CoupleDailyVoiceActivity(
                couple_id=coupleId,
                activity_date=activityDate,
                voice_seconds=0,
            )
            self.session.add(activity)
            self.session.flush()

        previousVoiceSeconds = activity.voice_seconds
        activity.voice_seconds += voiceSecondsIncrement
        self.session.flush()

        return activity, previousVoiceSeconds

    def getTotalVoiceSecondsByCoupleId(self, coupleId: int):
        return (
            self.session.query(func.coalesce(func.sum(CoupleDailyVoiceActivity.voice_seconds), 0))
            .filter(CoupleDailyVoiceActivity.couple_id == coupleId)
            .scalar()
            or 0
        )
