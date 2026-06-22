import traceback
from datetime import timezone
import math

import discord

from bot.config.emoji import JOIN_BUTTON
from bot.helper.discordTimestampHelper import formatShortDateTime
from bot.services.giveaway.giveawayMessageService import GiveawayMessageService


GIVEAWAY_JOIN_BUTTON_CUSTOM_ID_PREFIX = "giveaway_join"
GIVEAWAY_PARTICIPANT_BUTTON_CUSTOM_ID_PREFIX = "giveaway_participants"
GIVEAWAY_PARTICIPANT_PAGE_SIZE = 10


class GiveawayJoinButtonView(discord.ui.View):
    def __init__(self, giveawayId: int):
        super().__init__(timeout=None)
        self.giveawayId = giveawayId
        self.add_item(GiveawayJoinButton(giveawayId))
        self.add_item(GiveawayParticipantButton(giveawayId))

    async def on_error(self, interaction: discord.Interaction, error: Exception, item):
        traceback.print_exception(type(error), error, error.__traceback__)

        if interaction.response.is_done():
            await interaction.followup.send(
                "Đã xảy ra lỗi khi tham gia giveaway.",
                ephemeral=True,
            )
            return

        await interaction.response.send_message(
            "Đã xảy ra lỗi khi tham gia giveaway.",
            ephemeral=True,
        )


class GiveawayJoinButton(discord.ui.Button):
    def __init__(self, giveawayId: int):
        super().__init__(
            label="Tham gia",
            style=discord.ButtonStyle.primary,
            emoji=JOIN_BUTTON,
            custom_id=f"{GIVEAWAY_JOIN_BUTTON_CUSTOM_ID_PREFIX}:{giveawayId}",
        )
        self.giveawayId = giveawayId
        self.giveawayMessageService = GiveawayMessageService()

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        if interaction.guild is None:
            await interaction.followup.send(
                "Bạn chỉ có thể tham gia giveaway trong server.",
                ephemeral=True,
            )
            return

        userRoleIds = []
        if isinstance(interaction.user, discord.Member):
            userRoleIds = [role.id for role in interaction.user.roles]

        result = self.giveawayMessageService.joinGiveaway(
            giveawayId=self.giveawayId,
            userId=interaction.user.id,
            userRoleIds=userRoleIds,
        )

        if not result["success"]:
            await interaction.followup.send(
                result["message"],
                ephemeral=True,
            )
            return

        embed = self.giveawayMessageService.buildGiveawayEmbedById(
            giveawayId=self.giveawayId,
            guild=interaction.guild,
        )

        if embed is not None and interaction.message is not None:
            await interaction.message.edit(
                embed=embed,
                view=GiveawayJoinButtonView(self.giveawayId),
            )

        await interaction.followup.send(
            result["message"],
            ephemeral=True,
        )


class GiveawayParticipantButton(discord.ui.Button):
    def __init__(self, giveawayId: int):
        super().__init__(
            label="Xem người tham gia",
            style=discord.ButtonStyle.secondary,
            custom_id=f"{GIVEAWAY_PARTICIPANT_BUTTON_CUSTOM_ID_PREFIX}:{giveawayId}",
        )
        self.giveawayId = giveawayId
        self.giveawayMessageService = GiveawayMessageService()

    async def callback(self, interaction: discord.Interaction):
        participants = self.giveawayMessageService.findActiveParticipants(self.giveawayId)
        view = GiveawayParticipantPaginationView(
            giveawayId=self.giveawayId,
            participants=participants,
        )

        await interaction.response.send_message(
            embed=view.buildEmbed(),
            view=view,
            ephemeral=True,
        )


class GiveawayParticipantPaginationView(discord.ui.View):
    def __init__(
        self,
        giveawayId: int,
        participants: list[dict],
    ):
        super().__init__(timeout=180)
        self.giveawayId = giveawayId
        self.participants = participants
        self.currentPage = 0
        self.totalPages = max(1, math.ceil(len(participants) / GIVEAWAY_PARTICIPANT_PAGE_SIZE))
        self.updateButtonState()

    def buildEmbed(self):
        embed = discord.Embed(
            title="Danh sách người tham gia giveaway",
            color=discord.Color.gold(),
        )

        startIndex = self.currentPage * GIVEAWAY_PARTICIPANT_PAGE_SIZE
        endIndex = startIndex + GIVEAWAY_PARTICIPANT_PAGE_SIZE
        pageParticipants = self.participants[startIndex:endIndex]

        if len(pageParticipants) == 0:
            embed.description = "Chưa có người tham gia giveaway này."
        else:
            lines = [
                self.buildParticipantLine(participant)
                for participant in pageParticipants
            ]
            embed.description = "\n".join(lines)

        embed.set_footer(
            text=f"Trang {self.currentPage + 1}/{self.totalPages} | {len(self.participants)} người tham gia"
        )

        return embed

    def buildParticipantLine(self, participant: dict):
        joinedAt = participant["joinedAt"]

        if joinedAt.tzinfo is None:
            joinedAt = joinedAt.replace(tzinfo=timezone.utc)

        joinedAtText = formatShortDateTime(joinedAt)

        return f"- <@{participant['userId']}> tham gia lúc {joinedAtText}"

    def updateButtonState(self):
        self.previousButton.disabled = self.currentPage <= 0
        self.nextButton.disabled = self.currentPage >= self.totalPages - 1

    @discord.ui.button(label="Trước", emoji="⬅️", style=discord.ButtonStyle.secondary)
    async def previousButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.currentPage -= 1
        self.updateButtonState()

        await interaction.response.edit_message(
            embed=self.buildEmbed(),
            view=self,
        )

    @discord.ui.button(label="Tiếp", emoji="➡️", style=discord.ButtonStyle.secondary)
    async def nextButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.currentPage += 1
        self.updateButtonState()

        await interaction.response.edit_message(
            embed=self.buildEmbed(),
            view=self,
        )
