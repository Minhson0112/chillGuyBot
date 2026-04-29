import discord
from discord import app_commands
from discord.ext import commands

from bot.config.userId import OWNER_ID
from bot.services.farm.farmTrainEventCreateService import FarmTrainEventCreateService


class CreateTrainEvent(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.farmTrainEventCreateService = FarmTrainEventCreateService()

    @app_commands.command(
        name="createtrainevent",
        description="Tạo sự kiện tàu hỏa cho toàn server",
    )
    @app_commands.describe(
        item_id="ID của item trong bảng items",
        quantity="Số lượng item tàu yêu cầu",
        chill_coin="Số chill coin thưởng khi hoàn thành",
        exp="Số EXP farm thưởng khi hoàn thành",
    )
    async def createTrainEvent(
        self,
        interaction: discord.Interaction,
        item_id: int,
        quantity: int,
        chill_coin: int,
        exp: int,
    ):
        if interaction.user.id != OWNER_ID:
            await interaction.response.send_message(
                "Bạn không có quyền tạo sự kiện tàu hỏa.",
                ephemeral=True,
            )
            return

        await interaction.response.defer(thinking=True)

        try:
            result = self.farmTrainEventCreateService.createTrainEvent(
                requiredItemId=item_id,
                requiredQuantity=quantity,
                rewardChillCoin=chill_coin,
                rewardExp=exp,
                createdByUserId=interaction.user.id,
            )

            await interaction.followup.send(result["message"])

        except Exception as e:
            print(f"Create train event error: {e}")
            await interaction.followup.send("Đã xảy ra lỗi khi tạo sự kiện tàu hỏa.")


async def setup(bot):
    await bot.add_cog(CreateTrainEvent(bot))