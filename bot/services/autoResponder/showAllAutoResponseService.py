from bot.config.database import getDbSession
from bot.repository.autoResponderRepository import AutoResponderRepository


class ShowAllAutoResponseService:
    def getAllAutoResponders(self):
        with getDbSession() as session:
            autoResponderRepository = AutoResponderRepository(session)
            return autoResponderRepository.getAll()