import discord
from discord import app_commands

from bot.config.channel import MOD_COMMAND_CHANNEL_ID


def modChannelOnly():
    async def predicate(interaction: discord.Interaction) -> bool:
        if interaction.channel is None:
            raise app_commands.CheckFailure("Không xác định được kênh thực hiện lệnh.")

        if interaction.channel.id != MOD_COMMAND_CHANNEL_ID:
            raise app_commands.CheckFailure("Lệnh moderation chỉ được dùng trong kênh được chỉ định.")

        return True

    return app_commands.check(predicate)