import math

import discord


class PartnerListPaginationView(discord.ui.View):
    def __init__(
        self,
        partners,
        authorId: int,
        perPage: int = 10,
    ):
        super().__init__(timeout=180)
        self.partners = partners
        self.authorId = authorId
        self.perPage = perPage
        self.currentPage = 0
        self.totalPages = max(1, math.ceil(len(partners) / perPage))
        self.updateButtonState()

    def buildEmbed(self):
        embed = discord.Embed(
            title="Danh sách server partner",
            description=f"Tổng số PN: {len(self.partners)}",
            color=discord.Color.blue(),
        )

        start = self.currentPage * self.perPage
        end = start + self.perPage
        pagePartners = self.partners[start:end]

        if not pagePartners:
            embed.add_field(
                name="Không có dữ liệu",
                value="Hiện chưa có server partner nào.",
                inline=False,
            )
        else:
            for partner in pagePartners:
                embed.add_field(
                    name=f"ID: {partner['id']}",
                    value=(
                        f"- Tên server: {partner['guildName']}\n"
                        f"- Người đại diện: <@{partner['representativeUserId']}>\n"
                        f"- Trạng thái: {partner['status']}"
                    ),
                    inline=False,
                )

        embed.set_footer(text=f"Trang {self.currentPage + 1}/{self.totalPages}")

        return embed

    def updateButtonState(self):
        self.previousButton.disabled = self.currentPage <= 0
        self.nextButton.disabled = self.currentPage >= self.totalPages - 1

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id != self.authorId:
            await interaction.response.send_message(
                "Chỉ người dùng lệnh showpn mới có thể chuyển trang danh sách này.",
            )
            return False

        return True

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
