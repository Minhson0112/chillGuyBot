from datetime import datetime, timezone

from bot.config.database import getDbSession
from bot.repository.memberRepository import MemberRepository
from bot.repository.chatRepository import ChatRepository
from bot.services.farm.farmInitializeService import FarmInitializeService


class MemberSyncService:
    def __init__(self):
        self.farmInitializeService = FarmInitializeService()

    def buildMemberData(self, discordMember):
        joinedAt = (
            discordMember.joined_at.replace(tzinfo=None)
            if discordMember.joined_at
            else datetime.now(timezone.utc).replace(tzinfo=None)
        )

        return {
            "user_id": discordMember.id,
            "global_name": discordMember.global_name,
            "username": discordMember.name,
            "nick": discordMember.nick,
            "date_of_birth": None,
            "joined_at": joinedAt,
            "leave_at": None,
            "is_bot": discordMember.bot,
            "join_count": 1,
            "warning_count": 0,
        }

    def syncMember(self, session, discordMember):
        memberRepository = MemberRepository(session)
        chatRepository = ChatRepository(session)
        memberData = self.buildMemberData(discordMember)

        member, isCreated = memberRepository.upsertOnGuildSync(discordMember.id, memberData)
        if isCreated:
            chatRepository.createIfNotExists(member.user_id)
            self.farmInitializeService.initializeFarmForMember(
                session=session,
                userId=member.user_id,
                isBot=member.is_bot,
            )

    def syncDiscordMember(self, discordMember):
        with getDbSession() as session:
            self.syncMember(session, discordMember)
            session.commit()

    async def syncGuildMembers(self, guild):
        syncedCount = 0

        with getDbSession() as session:
            async for discordMember in guild.fetch_members(limit=None):
                self.syncMember(session, discordMember)
                syncedCount += 1

            session.commit()

        return syncedCount
