import discord
from discord import app_commands
from discord.ext import commands

from bot.config.emoji import LOGO
from bot.enums.moderationActionType import ModerationActionType
from bot.services.lotto.createLottoEventService import CreateLottoEventService
from bot.validation.guildValidation import guildOnly
from bot.validation.modPermissionValidation import hasModerationPermission


class CreateLottoEventCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.createLottoEventService = CreateLottoEventService()

    @app_commands.command(
        name="createlottoevent",
        description="Tạo event quay thưởng lotto",
    )
    @app_commands.describe(
        name="Tên event lotto",
        ticket_price="Giá cowoncy cho mỗi vé lotto",
        buy_deadline="Ngày hết hạn mua vé, format YYYY-MM-DD HH:mm",
        draw_at="Ngày quay thưởng, format YYYY-MM-DD HH:mm",
    )
    @guildOnly()
    @hasModerationPermission(ModerationActionType.EVENT)
    async def createLottoEvent(
        self,
        interaction: discord.Interaction,
        name: str,
        ticket_price: int,
        buy_deadline: str,
        draw_at: str,
    ):
        await interaction.response.defer(ephemeral=True)

        result = self.createLottoEventService.createLottoEvent(
            name=name,
            ticketPriceCowoncy=ticket_price,
            buyDeadlineText=buy_deadline,
            drawAtText=draw_at,
        )

        if not result["success"]:
            await interaction.followup.send(
                f"{LOGO} {result['message']}",
                ephemeral=True,
            )
            return

        await interaction.followup.send(
            f"{LOGO} {result['message']}\n"
            f"Tên event: **{result['name']}**\n"
            f"Giá mỗi vé: **{result['ticketPriceCowoncy']:,}** cowoncy\n"
            f"Hết hạn mua vé: **{result['buyDeadline'].strftime('%Y-%m-%d %H:%M')}**\n"
            f"Ngày quay thưởng: **{result['drawAt'].strftime('%Y-%m-%d %H:%M')}**",
            ephemeral=True,
        )


async def setup(bot):
    await bot.add_cog(CreateLottoEventCommand(bot))
