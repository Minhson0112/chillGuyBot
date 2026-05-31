from bot.cache.anonymousMatchCache import anonymousMatchCache
from bot.config.database import getDbSession
from bot.repository.anonymousMatchSessionRepository import AnonymousMatchSessionRepository


class AnonymousMatchCacheService:
    def loadActiveMatches(self):
        with getDbSession() as session:
            sessionRepository = AnonymousMatchSessionRepository(session)
            anonymousMatchSessions = sessionRepository.findAllActive()

            anonymousMatchCache.clear()

            for anonymousMatchSession in anonymousMatchSessions:
                self.setMatch(anonymousMatchSession)

            return len(anonymousMatchSessions)

    def setMatch(self, anonymousMatchSession):
        anonymousMatchCache[anonymousMatchSession.user_a_id] = {
            "sessionId": anonymousMatchSession.id,
            "partnerUserId": anonymousMatchSession.user_b_id,
            "alias": anonymousMatchSession.user_a_alias,
        }
        anonymousMatchCache[anonymousMatchSession.user_b_id] = {
            "sessionId": anonymousMatchSession.id,
            "partnerUserId": anonymousMatchSession.user_a_id,
            "alias": anonymousMatchSession.user_b_alias,
        }

    def findByUserId(self, userId):
        return anonymousMatchCache.get(userId)

    def removeByUserId(self, userId):
        matchData = anonymousMatchCache.get(userId)
        if matchData is None:
            return

        partnerUserId = matchData["partnerUserId"]

        anonymousMatchCache.pop(userId, None)
        anonymousMatchCache.pop(partnerUserId, None)
