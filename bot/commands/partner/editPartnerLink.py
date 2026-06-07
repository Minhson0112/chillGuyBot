import discord
from discord import app_commands
from discord.ext import commands

from bot.enums.moderationActionType import ModerationActionType
from bot.services.partner.editPartnerLinkService import EditPartnerLinkService
from bot.validation.modPermissionValidation import hasModerationPermission


class EditPartnerLink(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.editPartnerLinkService = EditPartnerLinkService()

    @app_commands.command(name="editpnlink", description="Sửa link mời của server partner")
    @app_commands.describe(
        partner_id="ID của partner cần sửa link",
        invite_link="Link mời mới của server partner",
    )
    @hasModerationPermission(ModerationActionType.PN)
    async def editpnlink(
        self,
        interaction: discord.Interaction,
        partner_id: int,
        invite_link: str,
    ):
        if interaction.guild is None:
            await interaction.response.send_message("Lệnh này chỉ dùng được trong server.")
            return

        await interaction.response.defer()

        result = await self.editPartnerLinkService.editPartnerLink(
            bot=self.bot,
            interaction=interaction,
            partnerId=partner_id,
            inviteLink=invite_link,
        )

        await interaction.followup.send(result)


async def setup(bot):
    await bot.add_cog(EditPartnerLink(bot))
