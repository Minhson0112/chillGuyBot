from bot.config.database import getDbSession
from bot.repository.autoResponderRepository import AutoResponderRepository
from bot.services.autoResponder.autoResponderCacheService import AutoResponderCacheService


class SetAutoResponseService:
    def __init__(self):
        self.autoResponderCacheService = AutoResponderCacheService()

    def createAutoResponder(self, userId, msgKey, isGlobal, isExactMatch, msgLink):
        with getDbSession() as session:
            autoResponderRepository = AutoResponderRepository(session)

            existedAutoResponder = autoResponderRepository.findByMsgKey(msgKey)
            if existedAutoResponder is not None:
                return None

            autoResponder = autoResponderRepository.create({
                "user_id": userId,
                "msg_key": msgKey,
                "is_global": isGlobal,
                "is_exact_match": isExactMatch,
                "msg_link": msgLink,
            })

            session.commit()

        self.autoResponderCacheService.loadKeys()
        return autoResponder