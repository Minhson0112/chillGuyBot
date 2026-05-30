import discord
from discord import app_commands
from discord.ext import commands

from bot.config.database import getDbSession
from bot.repository.autoResponderRepository import AutoResponderRepository
from bot.services.autoResponder.deleteAutoResponseService import DeleteAutoResponseService
from bot.validation.guildValidation import chillStationOnly


class DeleteAutoResponse(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.deleteAutoResponseService = DeleteAutoResponseService()

    @app_commands.command(name="deleteautoresponse", description="Xóa auto response theo key")
    @app_commands.describe(
        msg_key="Key cần xóa",
    )
    @chillStationOnly()
    async def deleteAutoResponse(
        self,
        interaction: discord.Interaction,
        msg_key: str,
    ):
        msgKey = msg_key.strip().lower()
        if not msgKey:
            await interaction.response.send_message("msg_key không được để trống.")
            return

        with getDbSession() as session:
            autoResponderRepository = AutoResponderRepository(session)
            autoResponder = autoResponderRepository.findByMsgKey(msgKey)

        if autoResponder is None:
            await interaction.response.send_message("Không tìm thấy auto response với key này.")
            return

        isOwnerServer = interaction.guild.owner_id == interaction.user.id
        isOwnerKey = autoResponder.user_id == interaction.user.id

        if not isOwnerKey and not isOwnerServer:
            await interaction.response.send_message(
                "Bạn chỉ có thể xóa key của chính mình hoặc phải là owner server.",
            )
            return

        await interaction.response.defer()

        deletedAutoResponder = self.deleteAutoResponseService.deleteByMsgKey(msgKey)
        if deletedAutoResponder is None:
            await interaction.followup.send("Không tìm thấy auto response để xóa.")
            return

        embed = discord.Embed(
            title="Xóa auto response thành công",
            description="Đã xóa rule auto response.",
        )
        embed.add_field(
            name="Người xóa",
            value=interaction.user.mention,
            inline=False,
        )
        embed.add_field(
            name="Key",
            value=msgKey,
            inline=False,
        )
        embed.add_field(
            name="Người tạo key",
            value=f"<@{deletedAutoResponder.user_id}>",
            inline=False,
        )

        await interaction.followup.send(
            embed=embed
        )

    @deleteAutoResponse.autocomplete("msg_key")
    async def msgKeyAutocomplete(
        self,
        interaction: discord.Interaction,
        current: str,
    ):
        if interaction.guild is None:
            return []

        currentLower = current.lower()

        with getDbSession() as session:
            autoResponderRepository = AutoResponderRepository(session)
            autoResponders = autoResponderRepository.getAll()

        isOwnerServer = interaction.guild.owner_id == interaction.user.id

        choices = []
        for autoResponder in autoResponders:
            canDelete = autoResponder.user_id == interaction.user.id or isOwnerServer
            if not canDelete:
                continue

            msgKey = autoResponder.msg_key
            if currentLower and currentLower not in msgKey.lower():
                continue

            choices.append(app_commands.Choice(name=msgKey, value=msgKey))

            if len(choices) >= 25:
                break

        return choices

async def setup(bot):
    await bot.add_cog(DeleteAutoResponse(bot))