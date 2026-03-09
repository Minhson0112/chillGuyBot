from datetime import datetime, timezone

from bot.config.database import getDbSession
from bot.repository.memberRepository import MemberRepository
from bot.repository.chatRepository import ChatRepository


class MemberJoinService:
    def handleMemberJoin(self, discordMember):
        joinedAt = (
            discordMember.joined_at.replace(tzinfo=None)
            if discordMember.joined_at
            else datetime.now(timezone.utc).replace(tzinfo=None)
        )

        memberData = {
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

        with getDbSession() as session:
            memberRepository = MemberRepository(session)
            chatRepository = ChatRepository(session)

            memberRepository.upsertOnJoin(discordMember.id, memberData)
            chatRepository.createIfNotExists(discordMember.id)

            session.commit()