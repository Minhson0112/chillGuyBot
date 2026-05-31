from sqlalchemy import asc

from bot.enums.anonymousMatchQueueStatus import AnonymousMatchQueueStatus
from bot.models.anonymousMatchQueue import AnonymousMatchQueue


class AnonymousMatchQueueRepository:
    def __init__(self, session):
        self.session = session

    def create(self, userId):
        anonymousMatchQueue = AnonymousMatchQueue(
            user_id=userId,
            status=AnonymousMatchQueueStatus.WAITING.value,
        )
        self.session.add(anonymousMatchQueue)
        self.session.flush()
        return anonymousMatchQueue

    def findWaitingByUserId(self, userId):
        return (
            self.session.query(AnonymousMatchQueue)
            .filter(AnonymousMatchQueue.user_id == userId)
            .filter(AnonymousMatchQueue.status == AnonymousMatchQueueStatus.WAITING.value)
            .order_by(asc(AnonymousMatchQueue.id))
            .first()
        )

    def findWaitingCandidates(self, userId):
        return (
            self.session.query(AnonymousMatchQueue)
            .filter(AnonymousMatchQueue.user_id != userId)
            .filter(AnonymousMatchQueue.status == AnonymousMatchQueueStatus.WAITING.value)
            .order_by(asc(AnonymousMatchQueue.id))
            .all()
        )

    def markMatched(self, anonymousMatchQueue, matchedAt):
        anonymousMatchQueue.status = AnonymousMatchQueueStatus.MATCHED.value
        anonymousMatchQueue.matched_at = matchedAt
        self.session.flush()
        return anonymousMatchQueue
