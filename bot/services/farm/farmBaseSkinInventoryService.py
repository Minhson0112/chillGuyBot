from bot.config.database import getDbSession
from bot.repository.memberBaseSkinInventoryRepository import MemberBaseSkinInventoryRepository


class FarmBaseSkinInventoryService:
    def getMemberBaseSkins(self, userId: int):
        with getDbSession() as session:
            memberBaseSkinInventoryRepository = MemberBaseSkinInventoryRepository(session)

            return memberBaseSkinInventoryRepository.findByUserId(userId)
