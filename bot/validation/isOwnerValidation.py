import discord
from discord import app_commands

from bot.config.userId import OWNER_ID


def isOwner():
    async def predicate(interaction: discord.Interaction) -> bool:
        if interaction.user.id != OWNER_ID:
            raise app_commands.CheckFailure("bạn không có quyền dùng lệnh này.")

        return True
    return app_commands.check(predicate)