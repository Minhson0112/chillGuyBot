import discord
from discord import app_commands
from discord.ext import commands

from bot.services.serverItem.proposalService import ProposalService
from bot.views.serverItem.proposalView import ProposalRingSelectView


class ProposeCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.proposalService = ProposalService()

    @app_commands.command(name="propose", description="Cầu hôn một member bằng nhẫn trong kho")
    @app_commands.describe(member="Người bạn muốn cầu hôn")
    async def propose(self, interaction: discord.Interaction, member: discord.Member):
        if interaction.guild is None:
            await interaction.response.send_message(
                "Lệnh này chỉ dùng được trong server.",
                ephemeral=True,
            )
            return

        if member.bot:
            await interaction.response.send_message(
                "Bạn không thể cầu hôn bot.",
                ephemeral=True,
            )
            return

        if member.id == interaction.user.id:
            await interaction.response.send_message(
                "Bạn không thể tự cầu hôn chính mình.",
                ephemeral=True,
            )
            return

        proposalMemberValidationResult = self.proposalService.validateProposalMembers(
            proposerUserId=interaction.user.id,
            targetUserId=member.id,
        )

        if not proposalMemberValidationResult["success"]:
            await interaction.response.send_message(
                proposalMemberValidationResult["message"],
                ephemeral=True,
            )
            return

        ringOptions = self.proposalService.findAvailableRingOptions(interaction.user.id)

        if not ringOptions:
            await interaction.response.send_message(
                "Bạn không có nhẫn để cầu hôn. Hãy xem shop bằng lệnh `cg loveshop`.",
                ephemeral=True,
            )
            return

        await interaction.response.send_message(
            "Vui lòng chọn nhẫn để cầu hôn.",
            view=ProposalRingSelectView(
                proposerId=interaction.user.id,
                targetMember=member,
                ringOptions=ringOptions,
            ),
            ephemeral=True,
        )


async def setup(bot):
    await bot.add_cog(ProposeCommand(bot))
