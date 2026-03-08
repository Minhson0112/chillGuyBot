import discord
from discord import app_commands

from bot.config.config import CHILL_STATION_GUILD_ID


def guildOnly():
    async def predicate(interaction: discord.Interaction) -> bool:
        if interaction.guild is None:
            raise app_commands.CheckFailure("Lệnh này chỉ dùng được trong server.")

        return True

    return app_commands.check(predicate)


def chillStationOnly():
    async def predicate(interaction: discord.Interaction) -> bool:
        if interaction.guild is None:
            raise app_commands.CheckFailure("Lệnh này chỉ dùng được trong server.")

        if interaction.guild.id != CHILL_STATION_GUILD_ID:
            raise app_commands.CheckFailure("Lệnh này chỉ dùng được trong Chill Station.")

        return True

    return app_commands.check(predicate)