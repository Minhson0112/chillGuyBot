import math

import discord


class AutoResponderPaginationView(discord.ui.View):
    def __init__(self, autoResponders, perPage=5):
        super().__init__(timeout=180)
        self.autoResponders = autoResponders
        self.perPage = perPage
        self.currentPage = 0
        self.totalPages = max(1, math.ceil(len(autoResponders) / perPage))
        self.updateButtonState()

    def buildEmbed(self):
        embed = discord.Embed(
            title="Danh sách auto response",
            description=f"Tổng số key: {len(self.autoResponders)}",
        )

        start = self.currentPage * self.perPage
        end = start + self.perPage
        pageItems = self.autoResponders[start:end]

        if not pageItems:
            embed.add_field(
                name="Không có dữ liệu",
                value="Chưa có auto response nào.",
                inline=False,
            )
        else:
            for autoResponder in pageItems:
                embed.add_field(
                    name=autoResponder.msg_key,
                    value=(
                        f"Người tạo: <@{autoResponder.user_id}>\n"
                        f"Global: {'Có' if autoResponder.is_global else 'Không'}\n"
                        f"Template: {autoResponder.msg_link}"
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