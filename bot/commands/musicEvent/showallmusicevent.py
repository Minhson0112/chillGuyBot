import math

import discord
from discord import app_commands
from discord.ext import commands

from bot.config.database import getDbSession
from bot.services.musicEvent.musicEventService import MusicEventService


class ShowAllMusicEventView(discord.ui.View):
    def __init__(self, events, pageSize: int = 3):
        super().__init__(timeout=180)
        self.events = events
        self.pageSize = pageSize
        self.currentPage = 0
        self.totalPages = max(1, math.ceil(len(events) / pageSize))
        self.updateButtonState()

    def buildEmbed(self):
        embed = discord.Embed(
            title="Danh sách music event",
            color=discord.Color.blurple(),
        )

        if not self.events:
            embed.description = "Hiện tại chưa có music event nào."
            embed.set_footer(text="Trang 1/1")
            return embed

        startIndex = self.currentPage * self.pageSize
        endIndex = startIndex + self.pageSize
        pageEvents = self.events[startIndex:endIndex]

        for musicEvent in pageEvents:
            statusText = "Open" if musicEvent.is_available else "Closed"
            embed.add_field(
                name=f"ID {musicEvent.id} - {musicEvent.event_name}",
                value=(
                    f"Trạng thái: {statusText}\n"
                    f"Số người đăng kí: {musicEvent.participant_count}\n"
                    f"Hết hạn đăng kí: {musicEvent.expired_at.strftime('%Y-%m-%d %H:%M')}"
                ),
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
        await interaction.response.edit_message(embed=self.buildEmbed(), view=self)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.secondary)
    async def nextButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.currentPage += 1
        self.updateButtonState()
        await interaction.response.edit_message(embed=self.buildEmbed(), view=self)


class ShowAllMusicEvent(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="showallmusicevent",
        description="Hiển thị tất cả music event",
    )
    async def showAllMusicEvent(self, interaction: discord.Interaction):
        with getDbSession() as session:
            musicEventService = MusicEventService(session)
            events = musicEventService.getAllMusicEvents()

        view = ShowAllMusicEventView(events=events, pageSize=3)

        await interaction.response.send_message(
            embed=view.buildEmbed(),
            view=view
        )


async def setup(bot):
    await bot.add_cog(ShowAllMusicEvent(bot))
