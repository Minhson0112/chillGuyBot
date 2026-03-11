from bot.config.database import getDbSession
from bot.repository.autoResponderRepository import AutoResponderRepository
from bot.services.autoResponder.autoResponderCacheService import AutoResponderCacheService


class DeleteAutoResponseService:
    def __init__(self):
        self.autoResponderCacheService = AutoResponderCacheService()

    def deleteByMsgKey(self, msgKey):
        with getDbSession() as session:
            autoResponderRepository = AutoResponderRepository(session)

            autoResponder = autoResponderRepository.findByMsgKey(msgKey)
            if autoResponder is None:
                return None

            autoResponderRepository.delete(autoResponder)
            session.commit()

        self.autoResponderCacheService.loadKeys()
        return autoResponder