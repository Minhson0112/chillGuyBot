from bot.config.database import getDbSession
from bot.enums.moderationActionType import ModerationActionType
from bot.repository.memberModerationHistoryRepository import MemberModerationHistoryRepository


class MuteService:
    def createMuteHistory(self, actionByUserId, targetUserId, reason, durationMinutes):
        historyData = {
            "action_by_user_id": actionByUserId,
            "target_user_id": targetUserId,
            "action_type": ModerationActionType.MUTE.value,
            "reason": reason,
            "duration_minutes": durationMinutes,
        }

        with getDbSession() as session:
            memberModerationHistoryRepository = MemberModerationHistoryRepository(session)
            history = memberModerationHistoryRepository.create(historyData)
            session.commit()
            return history