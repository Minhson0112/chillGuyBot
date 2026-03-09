from datetime import datetime, timezone

from bot.config.database import getDbSession
from bot.repository.memberRepository import MemberRepository


class MemberLeaveService:
    def handleMemberLeave(self, discordMember):
        leaveAt = datetime.now(timezone.utc).replace(tzinfo=None)

        with getDbSession() as session:
            memberRepository = MemberRepository(session)
            memberRepository.updateLeaveAt(discordMember.id, leaveAt)
            session.commit()