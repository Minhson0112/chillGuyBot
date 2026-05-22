import discord
from discord import app_commands
from discord.ext import commands

from bot.config.emoji import FARM_GAME_EMOJI, LOGO
from bot.services.exchange.chillCoinExchangeCowoncyService import ChillCoinExchangeCowoncyService
from bot.validation.guildValidation import guildOnly
from bot.validation.isOwnerValidation import isOwner


class ExchangeCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.chillCoinExchangeCowoncyService = ChillCoinExchangeCowoncyService()

    @app_commands.command(name="exchange", description="Đổi chill coin của user sang cowoncy")
    @app_commands.default_permissions(administrator=True)
    @app_commands.describe(
        user="User muốn đổi chill coin sang cowoncy",
        chill_coin="Số chill coin muốn đổi",
    )
    @guildOnly()
    @isOwner()
    async def exchange(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        chill_coin: int,
    ):
        await interaction.response.defer(ephemeral=False)

        result = self.chillCoinExchangeCowoncyService.exchange(
            senderUserId=interaction.user.id,
            receiverUserId=user.id,
            chillCoinAmount=chill_coin,
        )

        if not result["success"]:
            await interaction.followup.send(result["message"], ephemeral=False)
            return

        chillCoinEmoji = FARM_GAME_EMOJI["chill_coin"]

        await interaction.followup.send(
            (
                f"{LOGO} Đã trừ **{result['chillCoinAmount']:,}** {chillCoinEmoji} "
                f"trong tài khoản của {user.mention}.\n"
                f"Bạn hãy chuyển cho user **{result['cowoncyAmount']:,}** <:OwO:1503021935724859473> cowoncy."
            ),
            ephemeral=False,
        )


async def setup(bot):
    await bot.add_cog(ExchangeCommand(bot))
