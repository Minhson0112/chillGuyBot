from bot.cache.autoResponderCache import autoResponderCache
from bot.config.database import getDbSession
from bot.repository.autoResponderRepository import AutoResponderRepository

class AutoResponderCacheService:
    def loadKeys(self):
        with getDbSession() as session:
            autoResponderRepository = AutoResponderRepository(session)
            autoResponders = autoResponderRepository.getAllForCache()

            autoResponderCache.clear()

            for autoResponder in autoResponders:
                autoResponderCache.append({
                    "msg_key": autoResponder.msg_key.lower(),
                    "is_exact_match": autoResponder.is_exact_match,
                })