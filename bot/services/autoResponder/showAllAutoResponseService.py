from bot.config.database import getDbSession
from bot.repository.autoResponderRepository import AutoResponderRepository
from bot.repository.memberRepository import MemberRepository


class ShowAllAutoResponseService:
    def canShowAllAutoResponse(self, userId):
        with getDbSession() as session:
            memberRepository = MemberRepository(session)

            return memberRepository.canCreateAutoResponse(userId)

    def getAllAutoResponders(self):
        with getDbSession() as session:
            autoResponderRepository = AutoResponderRepository(session)
            return autoResponderRepository.getAll()
