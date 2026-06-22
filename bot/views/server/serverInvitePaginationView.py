import math

import discord

from bot.config.decoration import FOOTER_DECORATION_IMG_URL


class ServerInvitePaginationView(discord.ui.View):
    def __init__(
        self,
        invites,
        authorId: int,
        currentPage: int = 1,
        perPage: int = 10,
    ):
        super().__init__(timeout=180)

        self.invites = invites
        self.authorId = authorId
        self.perPage = perPage
        self.totalPages = max(1, math.ceil(len(invites) / perPage))
        self.currentPage = max(1, min(currentPage, self.totalPages))

        self.updateButtonState()

    def buildEmbed(self, guild: discord.Guild | None):
        embed = discord.Embed(
            title="Danh Sách Invite Server",
            description=f"Tổng số invite đã ghi nhận: **{len(self.invites)}**",
            color=discord.Color.blue(),
        )

        startIndex = (self.currentPage - 1) * self.perPage
        endIndex = startIndex + self.perPage
        pageInvites = self.invites[startIndex:endIndex]

        if len(pageInvites) == 0:
            embed.add_field(
                name="Không có dữ liệu",
                value="Hiện tại chưa có invite nào được ghi nhận.",
                inline=False,
            )
        else:
            lines = []

            for invite in pageInvites:
                inviterText = (
                    f"<@{invite.inviter_user_id}>"
                    if invite.inviter_user_id is not None
                    else "`Không rõ`"
                )
                createdAtText = self.formatDatetime(invite.discord_created_at)

                lines.append(
                    f"{inviterText} - `{invite.invite_code}` - "
                    f"Đã dùng **{self.formatNumber(invite.uses)}** - "
                    f"`{self.formatStatus(invite.status)}` - {createdAtText}"
                )

            embed.add_field(
                name="Người tạo - invite code - số lượng đã dùng - trạng thái - ngày tạo",
                value="\n".join(lines),
                inline=False,
            )

        if guild is not None and guild.icon is not None:
            embed.set_thumbnail(url=guild.icon.url)

        embed.set_image(url=FOOTER_DECORATION_IMG_URL)
        embed.set_footer(text=f"Trang {self.currentPage}/{self.totalPages}")

        return embed

    def updateButtonState(self):
        self.previousButton.disabled = self.currentPage <= 1
        self.nextButton.disabled = self.currentPage >= self.totalPages

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id != self.authorId:
            await interaction.response.send_message(
                "Chỉ người dùng lệnh này mới có thể chuyển trang danh sách invite.",
                ephemeral=True,
            )
            return False

        return True

    @discord.ui.button(label="Trước", emoji="⬅️", style=discord.ButtonStyle.secondary)
    async def previousButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.currentPage -= 1
        self.updateButtonState()

        await interaction.response.edit_message(
            embed=self.buildEmbed(interaction.guild),
            view=self,
        )

    @discord.ui.button(label="Tiếp", emoji="➡️", style=discord.ButtonStyle.secondary)
    async def nextButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.currentPage += 1
        self.updateButtonState()

        await interaction.response.edit_message(
            embed=self.buildEmbed(interaction.guild),
            view=self,
        )

    def formatDatetime(self, value):
        if value is None:
            return "`Không rõ`"

        return value.strftime("%d/%m/%Y %H:%M")

    def formatNumber(self, value):
        return f"{int(value or 0):,}".replace(",", ".")

    def formatStatus(self, status):
        statusMap = {
            "active": "Đang hoạt động",
            "expired": "Hết hạn",
            "deleted": "Đã xoá",
            "unknown": "Không rõ",
        }

        return statusMap.get(status, status)
