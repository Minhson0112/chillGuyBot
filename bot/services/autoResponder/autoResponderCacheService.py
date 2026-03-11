from bot.cache.autoResponderCache import autoResponderKeyCache
from bot.config.database import getDbSession
from bot.repository.autoResponderRepository import AutoResponderRepository

class AutoResponderCacheService:
    def loadKeys(self):
        with getDbSession() as session:
            autoResponderRepository = AutoResponderRepository(session)
            keyRows = autoResponderRepository.getAll()

            autoResponderKeyCache.clear()

            for row in keyRows:
                autoResponderKeyCache.add(row[0].lower())