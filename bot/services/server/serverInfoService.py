from bot.config.database import getDbSession
from bot.repository.memberRepository import MemberRepository


class ServerInfoService:
    def getServerInfo(self, guild):
        with getDbSession() as session:
            memberRepository = MemberRepository(session)
            maxHistoricalMemberCount = memberRepository.countAllMembers()
            permissionCounts = memberRepository.countMembersByPermission()

        return {
            "serverName": guild.name,
            "createdAt": guild.created_at,
            "memberCount": guild.member_count or 0,
            "maxHistoricalMemberCount": maxHistoricalMemberCount,
            "botCount": sum(1 for member in guild.members if member.bot),
            "adminCount": permissionCounts["adminCount"],
            "modCount": permissionCounts["modCount"],
            "staffCount": permissionCounts["staffCount"],
            "boostCount": guild.premium_subscription_count or 0,
        }
