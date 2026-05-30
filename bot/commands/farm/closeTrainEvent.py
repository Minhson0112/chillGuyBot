import discord
from discord import app_commands
from discord.ext import commands

from bot.config.userId import OWNER_ID
from bot.services.farm.farmTrainEventCloseService import FarmTrainEventCloseService


class CloseTrainEvent(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.farmTrainEventCloseService = FarmTrainEventCloseService()

    @app_commands.command(
        name="closetrainevent",
        description="Đóng sự kiện tàu hỏa đang mở",
    )
    @app_commands.describe(
        event_id="ID của sự kiện tàu hỏa cần đóng",
    )
    async def closeTrainEvent(
        self,
        interaction: discord.Interaction,
        event_id: int,
    ):
        if interaction.user.id != OWNER_ID:
            await interaction.response.send_message(
                "Bạn không có quyền đóng sự kiện tàu hỏa.",
                ephemeral=True,
            )
            return

        await interaction.response.defer(thinking=True)

        try:
            result = self.farmTrainEventCloseService.closeTrainEvent(
                trainEventId=event_id,
            )

            await interaction.followup.send(result["message"])

        except Exception as e:
            print(f"Close train event error: {e}")
            await interaction.followup.send("Đã xảy ra lỗi khi đóng sự kiện tàu hỏa.")


async def setup(bot):
    await bot.add_cog(CloseTrainEvent(bot))