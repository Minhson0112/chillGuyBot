from bot.config.database import getDbSession
from bot.repository.memberModerationHistoryRepository import MemberModerationHistoryRepository
from bot.repository.memberRepository import MemberRepository


class MemberInfoService:
    def getMemberInfo(self, userId):
        with getDbSession() as session:
            memberRepository = MemberRepository(session)
            memberModerationHistoryRepository = MemberModerationHistoryRepository(session)

            member = memberRepository.findByUserId(userId)
            if member is None:
                return None

            muteCount = memberModerationHistoryRepository.countMuteByTargetUserId(userId)

            return {
                "member": member,
                "mute_count": muteCount,
            }