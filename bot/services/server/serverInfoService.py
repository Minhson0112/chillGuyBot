import discord

from bot.config.database import getDbSession
from bot.repository.chatRepository import ChatRepository
from bot.repository.memberRepository import MemberRepository


class ServerInfoService:
    def buildServerInfoEmbed(self, guild: discord.Guild) -> discord.Embed:
        createdAt = guild.created_at.strftime("%Y-%m-%d %H:%M:%S UTC")
        memberCount = guild.member_count or 0
        botCount = sum(1 for member in guild.members if member.bot)

        with getDbSession() as session:
            memberRepository = MemberRepository(session)
            chatRepository = ChatRepository(session)

            maxHistoricalMemberCount = memberRepository.countAllMembers()
            topChat = chatRepository.findTopChatMember()

        if topChat is None or topChat.member is None:
            topChatMemberDisplay = "Chưa có dữ liệu"
        else:
            topChatMemberId = topChat.member.user_id
            topChatMemberDisplay = f"<@{topChatMemberId}> ({topChat.total_chat_count})"

        embed = discord.Embed(
            title="Server Info",
            description="Thông tin tổng quan của server",
        )

        if guild.icon is not None:
            embed.set_thumbnail(url=guild.icon.url)

        embed.add_field(name="Tên guild", value=guild.name, inline=False)
        embed.add_field(name="Ngày thành lập guild", value=createdAt, inline=False)
        embed.add_field(name="Số lượng thành viên", value=str(memberCount), inline=True)
        embed.add_field(name="Số lượng bot", value=str(botCount), inline=True)
        embed.add_field(
            name="Số lượng thành viên nhiều nhất từng có",
            value=str(maxHistoricalMemberCount),
            inline=False
        )
        embed.add_field(
            name="Thành viên chat nhiều nhất lịch sử",
            value=topChatMemberDisplay,
            inline=False
        )

        return embed