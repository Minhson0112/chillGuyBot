from datetime import datetime
import math

import discord
from discord import app_commands
from discord.ext import commands

from bot.config.config import NOTIFICATION_CHANNEL_ID
from bot.config.database import getDbSession
from bot.enums.moderationActionType import ModerationActionType
from bot.repository.musicEventRepository import MusicEventRepository
from bot.services.musicEvent.musicEventService import MusicEventService
from bot.validation.guildValidation import chillStationOnly
from bot.validation.modPermissionValidation import hasModerationPermission


class RegisterMusicEventModal(discord.ui.Modal, title="Đăng kí bài hát"):
    songNames = discord.ui.TextInput(
        label="Tên bài hát, viết cách nhau bởi dấu ,",
        placeholder="Ví dụ: bài hát a, bài hát b, bài hát c",
        required=True,
        max_length=1000,
    )

    def __init__(self, musicEventId: int):
        super().__init__()
        self.musicEventId = musicEventId

    async def on_submit(self, interaction: discord.Interaction):
        if interaction.guild is None:
            await interaction.response.send_message(
                "Lệnh này chỉ dùng được trong server.",
                ephemeral=True,
            )
            return

        with getDbSession() as dbSession:
            musicEventService = MusicEventService(dbSession)
            result = musicEventService.registerSongs(
                userId=interaction.user.id,
                musicEventId=self.musicEventId,
                rawSongNames=str(self.songNames),
            )

        if not result["success"]:
            await interaction.response.send_message(
                result["message"],
                ephemeral=True,
            )
            return

        role = interaction.guild.get_role(result["musicEvent"].role_id)
        if role is not None and isinstance(interaction.user, discord.Member):
            try:
                await interaction.user.add_roles(role, reason="Registered music event")
            except discord.Forbidden:
                await interaction.response.send_message(
                    "Đăng kí thành công nhưng bot không có quyền cấp role.",
                    ephemeral=True,
                )
                return
            except discord.HTTPException:
                await interaction.response.send_message(
                    "Đăng kí thành công nhưng không thể cấp role lúc này.",
                    ephemeral=True,
                )
                return

        registeredSongNames = [entry.song_name for entry in result["musicEventEntries"]]

        await interaction.response.send_message(
            "\n".join(
                [
                    f"Đăng kí thành công cho event: {result['musicEvent'].event_name}",
                    f"Danh sách bài hát: {', '.join(registeredSongNames)}",
                    f"Số người đăng kí hiện tại: {result['musicEvent'].participant_count}",
                ]
            ),
            ephemeral=True,
        )


class ParticipantPaginationView(discord.ui.View):
    def __init__(self, musicEventId: int, musicEventName: str, participants: list[dict], pageSize: int = 3):
        super().__init__(timeout=180)
        self.musicEventId = musicEventId
        self.musicEventName = musicEventName
        self.participants = participants
        self.pageSize = pageSize
        self.currentPage = 0
        self.totalPages = max(1, math.ceil(len(participants) / pageSize))
        self.updateButtonState()

    def buildEmbed(self):
        embed = discord.Embed(
            title=f"Người tham gia - {self.musicEventName}",
            color=discord.Color.blurple(),
        )

        if not self.participants:
            embed.description = "Hiện tại chưa có ai đăng kí."
            embed.set_footer(text="Trang 1/1")
            return embed

        startIndex = self.currentPage * self.pageSize
        endIndex = startIndex + self.pageSize
        pageParticipants = self.participants[startIndex:endIndex]

        for index, participant in enumerate(pageParticipants):
            songLines = "\n".join(
                [f"- {songName}" for songName in participant["songNames"]]
            )

            embed.add_field(
                name=f"Người tham gia {startIndex + index + 1}",
                value=f"<@{participant['userId']}>\n{songLines if songLines else 'Chưa có bài hát'}",
                inline=False,
            )

        embed.set_footer(text=f"Trang {self.currentPage + 1}/{self.totalPages}")
        return embed

    def updateButtonState(self):
        self.previousButton.disabled = self.currentPage <= 0
        self.nextButton.disabled = self.currentPage >= self.totalPages - 1

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.secondary)
    async def previousButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.currentPage -= 1
        self.updateButtonState()
        await interaction.response.edit_message(
            embed=self.buildEmbed(),
            view=self,
        )

    @discord.ui.button(label="Next", style=discord.ButtonStyle.secondary)
    async def nextButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.currentPage += 1
        self.updateButtonState()
        await interaction.response.edit_message(
            embed=self.buildEmbed(),
            view=self,
        )


class JoinMusicEventButton(discord.ui.Button):
    def __init__(self, musicEventId: int):
        super().__init__(
            label="Join",
            style=discord.ButtonStyle.primary,
            custom_id=f"join_music_event:{musicEventId}",
        )
        self.musicEventId = musicEventId

    async def callback(self, interaction: discord.Interaction):
        with getDbSession() as dbSession:
            musicEventRepository = MusicEventRepository(dbSession)
            musicEvent = musicEventRepository.findById(self.musicEventId)

        if musicEvent is None:
            await interaction.response.send_message(
                "Event không tồn tại.",
                ephemeral=True,
            )
            return

        if not musicEvent.is_available:
            await interaction.response.send_message(
                "Event đã đóng đăng kí.",
                ephemeral=True,
            )
            return

        if musicEvent.expired_at <= datetime.now():
            await interaction.response.send_message(
                "Event đã hết hạn đăng kí.",
                ephemeral=True,
            )
            return

        await interaction.response.send_modal(
            RegisterMusicEventModal(self.musicEventId)
        )


class ShowParticipantsButton(discord.ui.Button):
    def __init__(self, musicEventId: int):
        super().__init__(
            label="Xem người tham gia",
            style=discord.ButtonStyle.secondary,
            custom_id=f"show_music_event_participants:{musicEventId}",
        )
        self.musicEventId = musicEventId

    async def callback(self, interaction: discord.Interaction):
        with getDbSession() as dbSession:
            musicEventService = MusicEventService(dbSession)
            result = musicEventService.getParticipants(self.musicEventId)

        if not result["success"]:
            await interaction.response.send_message(
                result["message"],
                ephemeral=True,
            )
            return

        view = ParticipantPaginationView(
            musicEventId=self.musicEventId,
            musicEventName=result["musicEvent"].event_name,
            participants=result["participants"],
            pageSize=3,
        )

        await interaction.response.send_message(
            embed=view.buildEmbed(),
            view=view,
            ephemeral=True,
        )


class JoinMusicEventView(discord.ui.View):
    def __init__(self, musicEventId: int):
        super().__init__(timeout=None)
        self.add_item(JoinMusicEventButton(musicEventId))
        self.add_item(ShowParticipantsButton(musicEventId))


class OpenMusicEvent(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="openmusicevent",
        description="Mở music event lên kênh thông báo",
    )
    @app_commands.describe(
        id="ID của event trong music_event",
    )
    @chillStationOnly()
    @hasModerationPermission(ModerationActionType.EVENT)
    async def openMusicEvent(
        self,
        interaction: discord.Interaction,
        id: int,
    ):
        if interaction.guild is None:
            await interaction.response.send_message(
                "Lệnh này chỉ dùng được trong server.",
                ephemeral=True,
            )
            return

        with getDbSession() as dbSession:
            musicEventRepository = MusicEventRepository(dbSession)
            musicEvent = musicEventRepository.findById(id)

        if musicEvent is None:
            await interaction.response.send_message(
                "Không tìm thấy music event.",
                ephemeral=True,
            )
            return

        notificationChannel = interaction.guild.get_channel(NOTIFICATION_CHANNEL_ID)
        if notificationChannel is None:
            try:
                notificationChannel = await self.bot.fetch_channel(NOTIFICATION_CHANNEL_ID)
            except discord.NotFound:
                await interaction.response.send_message(
                    "Không tìm thấy kênh Notification.",
                    ephemeral=True,
                )
                return
            except discord.Forbidden:
                await interaction.response.send_message(
                    "Bot không có quyền truy cập kênh Notification.",
                    ephemeral=True,
                )
                return
            except discord.HTTPException:
                await interaction.response.send_message(
                    "Không thể lấy thông tin kênh Notification.",
                    ephemeral=True,
                )
                return

        if not isinstance(notificationChannel, discord.TextChannel):
            await interaction.response.send_message(
                "Notification channel không phải text channel.",
                ephemeral=True,
            )
            return

        embed = discord.Embed(
            title="Music Event",
            color=discord.Color.blurple(),
        )
        embed.add_field(
            name="Tên sự kiện",
            value=musicEvent.event_name,
            inline=False,
        )
        embed.add_field(
            name="Thời hạn đăng kí",
            value=musicEvent.expired_at.strftime("%Y-%m-%d %H:%M"),
            inline=False,
        )

        await notificationChannel.send(
            embed=embed,
            view=JoinMusicEventView(musicEvent.id),
        )

        await interaction.response.send_message(
            f"Đã gửi music event lên kênh <#{NOTIFICATION_CHANNEL_ID}>.",
        )


async def setup(bot):
    await bot.add_cog(OpenMusicEvent(bot))