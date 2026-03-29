from bot.config.database import getDbSession
from bot.enums.moderationActionType import ModerationActionType
from bot.repository.memberModerationHistoryRepository import MemberModerationHistoryRepository


class UnmuteService:
    def createUnmuteHistory(self, actionByUserId, targetUserId):
        with getDbSession() as session:
            memberModerationHistoryRepository = MemberModerationHistoryRepository(session)

            memberModerationHistoryRepository.create({
                "action_by_user_id": actionByUserId,
                "target_user_id": targetUserId,
                "action_type": ModerationActionType.UNMUTE,
                "reason": "Unmute",
            })

            session.commit()