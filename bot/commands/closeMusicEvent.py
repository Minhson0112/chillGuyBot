import discord
from discord import app_commands
from discord.ext import commands

from bot.config.database import getDbSession
from bot.enums.moderationActionType import ModerationActionType
from bot.repository.musicEventRepository import MusicEventRepository
from bot.validation.guildValidation import chillStationOnly
from bot.validation.modPermissionValidation import hasModerationPermission


class CloseMusicEvent(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="closemusicevent",
        description="Đóng music event và xóa role của event",
    )
    @app_commands.describe(
        event_id="ID của event âm nhạc",
    )
    @chillStationOnly()
    @hasModerationPermission(ModerationActionType.EVENT)
    async def closeMusicEvent(
        self,
        interaction: discord.Interaction,
        event_id: int,
    ):
        if interaction.guild is None:
            await interaction.response.send_message(
                "Lệnh này chỉ dùng được trong server.",
                ephemeral=True,
            )
            return

        with getDbSession() as dbSession:
            musicEventRepository = MusicEventRepository(dbSession)
            musicEvent = musicEventRepository.findById(event_id)

            if musicEvent is None:
                await interaction.response.send_message(
                    "Không tìm thấy music event.",
                    ephemeral=True,
                )
                return

            role = interaction.guild.get_role(musicEvent.role_id)
            if role is None:
                try:
                    fetchedRole = await interaction.guild.fetch_roles()
                    role = next((item for item in fetchedRole if item.id == musicEvent.role_id), None)
                except discord.Forbidden:
                    await interaction.response.send_message(
                        "Bot không có quyền lấy danh sách role.",
                        ephemeral=True,
                    )
                    return
                except discord.HTTPException:
                    await interaction.response.send_message(
                        "Không thể lấy thông tin role của event.",
                        ephemeral=True,
                    )
                    return

            musicEventRepository.closeEvent(musicEvent)

            if role is not None:
                try:
                    await role.delete(reason=f"Close music event {musicEvent.id}")
                except discord.Forbidden:
                    await interaction.response.send_message(
                        "Đã đóng event trong DB nhưng bot không có quyền xóa role.",
                        ephemeral=True,
                    )
                    dbSession.commit()
                    return
                except discord.HTTPException:
                    await interaction.response.send_message(
                        "Đã đóng event trong DB nhưng không thể xóa role lúc này.",
                        ephemeral=True,
                    )
                    dbSession.commit()
                    return

            dbSession.commit()

        await interaction.response.send_message(
            "\n".join(
                [
                    "Đã đóng music event thành công.",
                    f"eventId: {musicEvent.id}",
                    f"eventName: {musicEvent.event_name}",
                ]
            ),
        )

async def setup(bot):
    await bot.add_cog(CloseMusicEvent(bot))