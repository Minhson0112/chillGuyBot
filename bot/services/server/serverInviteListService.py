from bot.config.database import getDbSession
from bot.repository.serverInviteRepository import ServerInviteRepository


class ServerInviteListService:
    def findAllInvites(self):
        with getDbSession() as session:
            serverInviteRepository = ServerInviteRepository(session)
            return serverInviteRepository.findAllForList()
