from datetime import datetime

import discord
from discord import app_commands
from discord.ext import commands

from bot.config.database import getDbSession
from bot.repository.musicEventRepository import MusicEventRepository
from bot.enums.moderationActionType import ModerationActionType
from bot.validation.guildValidation import chillStationOnly
from bot.validation.modPermissionValidation import hasModerationPermission


class CreateMusicEvent(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="createmusicevent",
        description="Tạo music event mới",
    )
    @app_commands.describe(
        event_name="Tên event",
        expired_at="Ngày hết hạn đăng ký, format: YYYY-MM-DD HH:MM",
        role_id="ID role sẽ được cấp khi member đăng kí event",
    )
    @chillStationOnly()
    @hasModerationPermission(ModerationActionType.EVENT)
    async def createMusicEvent(
        self,
        interaction: discord.Interaction,
        event_name: str,
        expired_at: str,
        role_id: str,
    ):
        try:
            expiredAtDatetime = datetime.strptime(expired_at, "%Y-%m-%d %H:%M")
        except ValueError:
            await interaction.response.send_message(
                "Ngày hết hạn đăng ký không đúng định dạng. Hãy dùng dạng YYYY-MM-DD HH:MM"
            )
            return

        try:
            roleIdInt = int(role_id)
        except ValueError:
            await interaction.response.send_message(
                "roleId không hợp lệ."
            )
            return

        with getDbSession() as dbSession:
            musicEventRepository = MusicEventRepository(dbSession)
            musicEvent = musicEventRepository.create(
                eventName=event_name,
                roleId=roleIdInt,
                expiredAt=expiredAtDatetime,
            )
            dbSession.commit()

        await interaction.response.send_message(
            "\n".join(
                [
                    "Tạo music event thành công.",
                    f"id: {musicEvent.id}",
                    f"eventName: {musicEvent.event_name}",
                    f"expiredAt: {musicEvent.expired_at}",
                ]
            )
        )


async def setup(bot):
    await bot.add_cog(CreateMusicEvent(bot))