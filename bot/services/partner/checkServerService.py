import discord

from bot.config.database import getDbSession
from bot.config.config import NUMBER_OF_MEMBER_REQUIRED_FOR_PN
from bot.repository.partnerRepository import PartnerRepository


class CheckServerService:
    async def checkServer(self, bot: discord.Client, inviteLink: str) -> str:
        try:
            invite = await bot.fetch_invite(inviteLink, with_counts=True)
        except discord.NotFound:
            return "Link mời không tồn tại hoặc đã hết hạn."
        except discord.HTTPException:
            return "Không thể lấy thông tin server từ link mời."

        if invite.guild is None:
            return "Không thể lấy thông tin guild từ link mời."

        guildId = invite.guild.id
        guildName = invite.guild.name
        memberCount = invite.approximate_member_count or 0

        with getDbSession() as dbSession:
            partnerRepository = PartnerRepository(dbSession)
            partner = partnerRepository.findByGuildId(guildId)

        resultLines = [
            f"Tên server: {guildName}",
            f"Tổng thành viên: {memberCount}",
        ]

        if memberCount < NUMBER_OF_MEMBER_REQUIRED_FOR_PN:
            resultLines.append("Server này chưa đủ thành viên quy định.")
            return "\n".join(resultLines)

        if partner is not None:
            resultLines.append("Server này đã tồn tại trong danh sách partner.")
            return "\n".join(resultLines)

        resultLines.append(f"Server {guildName} thoả mãn các điều kiện để làm partner.")
        return "\n".join(resultLines)