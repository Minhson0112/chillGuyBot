import discord

from bot.services.farm.farmAchievementService import FarmAchievementService


class FarmAchievementPaginationView(discord.ui.View):
    def __init__(
        self,
        authorId: int,
        currentPage: int,
        totalPage: int,
    ):
        super().__init__(timeout=600)

        self.authorId = authorId
        self.currentPage = currentPage
        self.totalPage = totalPage
        self.farmAchievementService = FarmAchievementService()

        self.updateButtonState()

    def updateButtonState(self):
        self.previousButton.disabled = self.currentPage <= 1
        self.nextButton.disabled = self.currentPage >= self.totalPage

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id != self.authorId:
            await interaction.response.send_message(
                "Bạn không thể điều khiển bảng thành tựu của người khác.",
                ephemeral=True,
            )
            return False

        return True

    @discord.ui.button(label="Trước", emoji="⬅️", style=discord.ButtonStyle.secondary)
    async def previousButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.currentPage > 1:
            self.currentPage -= 1

        await self.refreshAchievementMessage(interaction)

    @discord.ui.button(label="Nhận thưởng", emoji="🎁", style=discord.ButtonStyle.success)
    async def claimButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()

        previewResult = self.farmAchievementService.previewClaimPage(
            userId=self.authorId,
            page=self.currentPage,
        )

        if not previewResult["success"]:
            await interaction.followup.send(
                previewResult["message"],
                ephemeral=True,
            )
            await self.editAchievementMessage(interaction)
            return

        roleIds = previewResult["roleIds"]

        for roleId in roleIds:
            role = interaction.guild.get_role(roleId) if interaction.guild else None

            if role is None:
                await interaction.followup.send(
                    f"Không tìm thấy role reward `{roleId}` trong server.",
                    ephemeral=True,
                )
                await self.editAchievementMessage(interaction)
                return

            if role not in interaction.user.roles:
                try:
                    await interaction.user.add_roles(
                        role,
                        reason="Farm achievement reward",
                    )
                except discord.Forbidden:
                    await interaction.followup.send(
                        f"Bot không đủ quyền để cấp role <@&{roleId}>.",
                        ephemeral=True,
                    )
                    await self.editAchievementMessage(interaction)
                    return
                except discord.HTTPException:
                    await interaction.followup.send(
                        f"Không thể cấp role <@&{roleId}> lúc này.",
                        ephemeral=True,
                    )
                    await self.editAchievementMessage(interaction)
                    return

        claimResult = self.farmAchievementService.claimPage(
            userId=self.authorId,
            page=self.currentPage,
        )

        await interaction.followup.send(
            claimResult["message"],
            ephemeral=True,
        )
        await self.editAchievementMessage(interaction)

    @discord.ui.button(label="Tiếp", emoji="➡️", style=discord.ButtonStyle.secondary)
    async def nextButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.currentPage < self.totalPage:
            self.currentPage += 1

        await self.refreshAchievementMessage(interaction)

    async def refreshAchievementMessage(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await self.editAchievementMessage(interaction)

    async def editAchievementMessage(self, interaction: discord.Interaction):
        pageResult = self.farmAchievementService.getAchievementPage(
            userId=self.authorId,
            page=self.currentPage,
        )

        if not pageResult["success"]:
            await interaction.edit_original_response(
                content=pageResult["message"],
                embed=None,
                view=None,
            )
            return

        self.currentPage = pageResult["currentPage"]
        self.totalPage = pageResult["totalPage"]
        self.updateButtonState()

        embed = buildFarmAchievementEmbed(pageResult)

        await interaction.edit_original_response(
            content=None,
            embed=embed,
            view=self,
        )


def buildFarmAchievementEmbed(pageResult):
    embed = discord.Embed(
        title=f"Thành tựu Farm - {pageResult['categoryName']}",
        description=pageResult["categoryDescription"] or None,
        color=discord.Color.green(),
    )

    for achievement in pageResult["achievements"]:
        if achievement["isRewardClaimed"]:
            statusText = "Đã nhận"
        elif achievement["isCompleted"]:
            statusText = "Hoàn thành, chưa nhận"
        else:
            statusText = "Chưa hoàn thành"

        embed.add_field(
            name=achievement["name"],
            value=(
                f"Tiến độ: **{achievement['progressText']}**\n"
                f"Phần thưởng: {achievement['rewardText']}\n"
                f"Trạng thái: {statusText}"
            ),
            inline=False,
        )

    embed.set_footer(
        text=f"Trang {pageResult['currentPage']}/{pageResult['totalPage']}",
    )

    return embed
