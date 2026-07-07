import discord
from discord import app_commands
from discord.ext import commands

from bot.services.member.memberInfoImageService import MemberInfoImageService
from bot.services.member.memberInfoService import MemberInfoService
from bot.validation.guildValidation import chillStationOnly


class MemberInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.memberInfoService = MemberInfoService()
        self.memberInfoImageService = MemberInfoImageService()

    @app_commands.command(name="memberinfo", description="Xem thông tin member")
    @app_commands.describe(target="Member cần xem thông tin")
    @chillStationOnly()
    async def memberInfo(
        self,
        interaction: discord.Interaction,
        target: discord.Member,
    ):
        await interaction.response.defer()

        memberInfo = self.memberInfoService.getMemberInfo(target)

        if memberInfo is None:
            await interaction.followup.send(
                "Không tìm thấy thông tin member trong database.")
            return

        await self.fillPartnerDisplayName(interaction.guild, memberInfo)

        imageBuffer = await self.memberInfoImageService.buildMemberInfoImage(
            target,
            memberInfo,
        )
        file = discord.File(
            fp=imageBuffer,
            filename="member_info.png",
        )

        await interaction.followup.send(file=file)

    async def fillPartnerDisplayName(self, guild, memberInfo):
        partnerUserId = memberInfo.get("partnerUserId")

        if partnerUserId is None or guild is None:
            return

        partnerMember = guild.get_member(partnerUserId)

        if partnerMember is None:
            try:
                partnerMember = await guild.fetch_member(partnerUserId)
            except (discord.NotFound, discord.HTTPException):
                return

        memberInfo["partnerName"] = partnerMember.display_name


async def setup(bot):
    await bot.add_cog(MemberInfo(bot))
