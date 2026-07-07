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
from bot.repository.coupleRepository import CoupleRepository


class MemberInfoService:
    def getMemberInfo(self, discordMember):
        userId = discordMember.id

        with getDbSession() as session:
            memberRepository = MemberRepository(session)
            memberModerationHistoryRepository = MemberModerationHistoryRepository(session)
            chatRepository = ChatRepository(session)
            memberDailyActivityRepository = MemberDailyActivityRepository(session)
            farmRepository = FarmRepository(session)
            coupleRepository = CoupleRepository(session)

            member = memberRepository.findByUserId(userId)
            if member is None:
                return None

            muteCount = memberModerationHistoryRepository.countMuteByTargetUserId(userId)
            chat = chatRepository.findByUserId(userId)
            farm = farmRepository.findByUserId(userId)
            totalVoiceSeconds = memberDailyActivityRepository.getTotalVoiceSecondsByUserId(
                userId,
            )
            couple = coupleRepository.findActiveByUserId(userId)

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

        partnerUserId = None
        partnerName = "Không có"
        marriageStatus = "Không"

        if couple is not None:
            partnerUserId = couple.user_2_id if couple.user_1_id == userId else couple.user_1_id
            partnerMember = discordMember.guild.get_member(partnerUserId)
            partnerName = partnerMember.display_name if partnerMember is not None else f"<@{partnerUserId}>"
            marriageStatus = "Có"

        return {
            "member": member,
            "nickname": discordMember.display_name,
            "genderLabel": self.getGenderLabel(discordMember),
            "muteCount": muteCount,
            "totalChatCount": (chat.total_chat_count if chat else 0) + pendingChatCount,
            "totalVoiceSeconds": totalVoiceSeconds + pendingVoiceSeconds + currentVoiceSeconds,
            "farmLevel": farm.farm_level if farm else None,
            "partnerUserId": partnerUserId,
            "partnerName": partnerName,
            "marriageStatus": marriageStatus,
        }

    def getGenderLabel(self, discordMember):
        memberRoleIds = {role.id for role in discordMember.roles}

        for genderConfig in GENDER_ROLES.values():
            if genderConfig["roleId"] in memberRoleIds:
                return genderConfig["label"]

        return "Chưa xác định"
