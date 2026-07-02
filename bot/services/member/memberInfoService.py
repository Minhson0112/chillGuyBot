from datetime import datetime

from bot.cache.chatCountCache import chatCountCache
from bot.cache.memberDailyActivityCache import memberDailyActivityCache
from bot.cache.voiceSessionCache import voiceSessionCache
from bot.config.database import getDbSession
from bot.config.roles import GENDER_ROLES
from bot.repository.chatRepository import ChatRepository
from bot.repository.farmRepository import FarmRepository
from bot.repository.memberDailyActivityRepository import MemberDailyActivityRepository
from bot.repository.memberModerationHistoryRepository import MemberModerationHistoryRepository
from bot.repository.memberRepository import MemberRepository


class MemberInfoService:
    def getMemberInfo(self, discordMember):
        userId = discordMember.id

        with getDbSession() as session:
            memberRepository = MemberRepository(session)
            memberModerationHistoryRepository = MemberModerationHistoryRepository(session)
            chatRepository = ChatRepository(session)
            memberDailyActivityRepository = MemberDailyActivityRepository(session)
            farmRepository = FarmRepository(session)

            member = memberRepository.findByUserId(userId)
            if member is None:
                return None

            muteCount = memberModerationHistoryRepository.countMuteByTargetUserId(userId)
            chat = chatRepository.findByUserId(userId)
            farm = farmRepository.findByUserId(userId)
            totalVoiceSeconds = memberDailyActivityRepository.getTotalVoiceSecondsByUserId(
                userId,
            )

        pendingChatCount = chatCountCache.get(userId, {}).get("total_chat_count", 0)
        pendingVoiceSeconds = sum(
            activityData.get("voice_seconds", 0)
            for (cachedUserId, _), activityData in memberDailyActivityCache.items()
            if cachedUserId == userId
        )

        voiceSession = voiceSessionCache.get(userId)
        currentVoiceSeconds = 0

        if voiceSession is not None:
            joinedAt = voiceSession["joined_at"]
            now = datetime.now(joinedAt.tzinfo) if joinedAt.tzinfo else datetime.now()
            currentVoiceSeconds = max(int((now - joinedAt).total_seconds()), 0)

        return {
            "member": member,
            "nickname": discordMember.display_name,
            "genderLabel": self.getGenderLabel(discordMember),
            "muteCount": muteCount,
            "totalChatCount": (chat.total_chat_count if chat else 0) + pendingChatCount,
            "totalVoiceSeconds": totalVoiceSeconds + pendingVoiceSeconds + currentVoiceSeconds,
            "farmLevel": farm.farm_level if farm else None,
        }

    def getGenderLabel(self, discordMember):
        memberRoleIds = {role.id for role in discordMember.roles}

        for genderConfig in GENDER_ROLES.values():
            if genderConfig["roleId"] in memberRoleIds:
                return genderConfig["label"]

        return "Chưa xác định"
