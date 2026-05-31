from sqlalchemy import and_, desc, or_

from bot.enums.anonymousMatchSessionStatus import AnonymousMatchSessionStatus
from bot.models.anonymousMatchSession import AnonymousMatchSession


class AnonymousMatchSessionRepository:
    def __init__(self, session):
        self.session = session

    def create(self, sessionData):
        anonymousMatchSession = AnonymousMatchSession(**sessionData)
        self.session.add(anonymousMatchSession)
        self.session.flush()
        return anonymousMatchSession

    def findActiveByUserId(self, userId):
        activeStatuses = [
            AnonymousMatchSessionStatus.ACTIVE.value,
            AnonymousMatchSessionStatus.ENDING_REQUESTED.value,
        ]

        return (
            self.session.query(AnonymousMatchSession)
            .filter(AnonymousMatchSession.status.in_(activeStatuses))
            .filter(
                or_(
                    AnonymousMatchSession.user_a_id == userId,
                    AnonymousMatchSession.user_b_id == userId,
                )
            )
            .order_by(desc(AnonymousMatchSession.id))
            .first()
        )

    def findAllActive(self):
        activeStatuses = [
            AnonymousMatchSessionStatus.ACTIVE.value,
            AnonymousMatchSessionStatus.ENDING_REQUESTED.value,
        ]

        return (
            self.session.query(AnonymousMatchSession)
            .filter(AnonymousMatchSession.status.in_(activeStatuses))
            .all()
        )

    def findLatestByUserId(self, userId):
        return (
            self.session.query(AnonymousMatchSession)
            .filter(
                or_(
                    AnonymousMatchSession.user_a_id == userId,
                    AnonymousMatchSession.user_b_id == userId,
                )
            )
            .order_by(desc(AnonymousMatchSession.id))
            .first()
        )

    def findLatestBetweenUsers(self, firstUserId, secondUserId):
        return (
            self.session.query(AnonymousMatchSession)
            .filter(
                or_(
                    and_(
                        AnonymousMatchSession.user_a_id == firstUserId,
                        AnonymousMatchSession.user_b_id == secondUserId,
                    ),
                    and_(
                        AnonymousMatchSession.user_a_id == secondUserId,
                        AnonymousMatchSession.user_b_id == firstUserId,
                    ),
                )
            )
            .order_by(desc(AnonymousMatchSession.id))
            .first()
        )

    def requestEnd(self, anonymousMatchSession, userId):
        if anonymousMatchSession.user_a_id == userId:
            anonymousMatchSession.end_requested_by_a = True

        if anonymousMatchSession.user_b_id == userId:
            anonymousMatchSession.end_requested_by_b = True

        anonymousMatchSession.status = AnonymousMatchSessionStatus.ENDING_REQUESTED.value
        self.session.flush()
        return anonymousMatchSession

    def endSession(self, anonymousMatchSession, endedAt):
        anonymousMatchSession.status = AnonymousMatchSessionStatus.ENDED.value
        anonymousMatchSession.ended_at = endedAt
        self.session.flush()
        return anonymousMatchSession
