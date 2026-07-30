import discord
from discord import app_commands

from bot.config.userId import CAN_ADD_WORD_ID_LIST


def canAddWord():
    async def predicate(interaction: discord.Interaction) -> bool:
        if interaction.user.id not in CAN_ADD_WORD_ID_LIST:
            raise app_commands.CheckFailure("bạn không có quyền dùng lệnh này.")

        return True
    return app_commands.check(predicate)