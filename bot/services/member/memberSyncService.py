from datetime import datetime, timezone

from bot.config.database import getDbSession
from bot.repository.memberRepository import MemberRepository
from bot.repository.chatRepository import ChatRepository


class MemberSyncService:
    def syncGuildMembers(self, guild):
        syncedCount = 0

        with getDbSession() as session:
            memberRepository = MemberRepository(session)
            chatRepository = ChatRepository(session)

            for discordMember in guild.members:
                memberData = {
                    "user_id": discordMember.id,
                    "global_name": discordMember.global_name,
                    "username": discordMember.name,
                    "nick": discordMember.nick,
                    "date_of_birth": None,
                    "joined_at": (
                        discordMember.joined_at.replace(tzinfo=None)
                        if discordMember.joined_at
                        else datetime.now(timezone.utc).replace(tzinfo=None)
                    ),
                    "leave_at": None,
                    "is_bot": discordMember.bot,
                    "join_count": 1,
                    "warning_count": 0,
                }

                memberRepository.upsertByUserId(discordMember.id, memberData)

                chat = chatRepository.findByUserId(discordMember.id)
                if chat is None:
                    chatRepository.create({
                        "user_id": discordMember.id,
                        "total_chat_count": 0,
                        "level_chat_count": 0,
                    })

                syncedCount += 1

            session.commit()

        return syncedCount