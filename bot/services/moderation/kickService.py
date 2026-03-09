from bot.config.database import getDbSession
from bot.enums.moderationActionType import ModerationActionType
from bot.repository.memberModerationHistoryRepository import MemberModerationHistoryRepository


class KickService:
    def createKickHistory(self, actionByUserId, targetUserId, reason):
        historyData = {
            "action_by_user_id": actionByUserId,
            "target_user_id": targetUserId,
            "action_type": ModerationActionType.KICK.value,
            "reason": reason,
            "duration_minutes": None,
        }

        with getDbSession() as session:
            memberModerationHistoryRepository = MemberModerationHistoryRepository(session)
            history = memberModerationHistoryRepository.create(historyData)
            session.commit()
            return history