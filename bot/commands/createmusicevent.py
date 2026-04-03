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
        eventName="Tên event",
        expiredAt="Ngày hết hạn đăng ký, format: YYYY-MM-DD HH:MM",
        roleId="ID role sẽ được cấp khi member đăng kí event",
    )
    @chillStationOnly()
    @hasModerationPermission(ModerationActionType.EVENT)
    async def createMusicEvent(
        self,
        interaction: discord.Interaction,
        eventName: str,
        expiredAt: str,
        roleId: str,
    ):
        try:
            expiredAtDatetime = datetime.strptime(expiredAt, "%Y-%m-%d %H:%M")
        except ValueError:
            await interaction.response.send_message(
                "Ngày hết hạn đăng ký không đúng định dạng. Hãy dùng dạng YYYY-MM-DD HH:MM"
            )
            return

        try:
            roleIdInt = int(roleId)
        except ValueError:
            await interaction.response.send_message(
                "roleId không hợp lệ."
            )
            return

        with getDbSession() as dbSession:
            musicEventRepository = MusicEventRepository(dbSession)
            musicEvent = musicEventRepository.create(
                eventName=eventName,
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