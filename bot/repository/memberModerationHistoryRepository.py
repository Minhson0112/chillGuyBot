from sqlalchemy import func
from bot.models.memberModerationHistory import MemberModerationHistory
from bot.enums.moderationActionType import ModerationActionType


class MemberModerationHistoryRepository:
    def __init__(self, session):
        self.session = session

    def create(self, historyData):
        history = MemberModerationHistory(**historyData)
        self.session.add(history)
        self.session.flush()
        return history

    def countMuteByTargetUserId(self, targetUserId):
        return self.session.query(func.count(MemberModerationHistory.id_member_moderation_history)).filter(
            MemberModerationHistory.target_user_id == targetUserId,
            MemberModerationHistory.action_type == ModerationActionType.MUTE.value,
        ).scalar()