import discord

from bot.helper.numberFormatHelper import formatNumber
from bot.services.serverItem.proposalService import ProposalService


class ProposalRingSelect(discord.ui.Select):
    def __init__(self, ringOptions):
        options = []

        for ringOption in ringOptions:
            options.append(discord.SelectOption(
                label=ringOption["itemName"][:100],
                value=str(ringOption["inventoryId"]),
                description=f"Điểm thân mật: {formatNumber(ringOption['intimacyPoints'])}"[:100],
                emoji=ringOption["itemEmoji"],
            ))

        super().__init__(
            placeholder="Chọn nhẫn để cầu hôn",
            min_values=1,
            max_values=1,
            options=options[:25],
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        view = self.view
        ringInventoryId = int(self.values[0])
        ringOption = view.findRingOption(ringInventoryId)

        if ringOption is None:
            await interaction.edit_original_response(
                content="Nhẫn được chọn không hợp lệ.",
                view=None,
            )
            return

        proposalResponseView = ProposalResponseView(
            proposerId=view.proposerId,
            targetId=view.targetMember.id,
            ringInventoryId=ringInventoryId,
        )
        proposalMessage = await interaction.channel.send(
            content=view.targetMember.mention,
            embed=proposalResponseView.buildPendingEmbed(
                proposer=interaction.user,
                target=view.targetMember,
                ringOption=ringOption,
            ),
            view=proposalResponseView,
            allowed_mentions=discord.AllowedMentions(
                users=True,
                roles=False,
                everyone=False,
            ),
        )
        proposalResponseView.message = proposalMessage

        await interaction.edit_original_response(
            content="Đã gửi lời cầu hôn.",
            view=None,
        )


class ProposalRingSelectView(discord.ui.View):
    def __init__(
        self,
        proposerId: int,
        targetMember: discord.Member,
        ringOptions,
    ):
        super().__init__(timeout=180)
        self.proposerId = proposerId
        self.targetMember = targetMember
        self.ringOptions = ringOptions
        self.add_item(ProposalRingSelect(ringOptions))

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id != self.proposerId:
            await interaction.response.send_message(
                "Bạn không thể chọn nhẫn thay người khác.",
                ephemeral=True,
            )
            return False

        return True

    def findRingOption(self, ringInventoryId: int):
        for ringOption in self.ringOptions:
            if ringOption["inventoryId"] == ringInventoryId:
                return ringOption

        return None


class ProposalResponseView(discord.ui.View):
    def __init__(
        self,
        proposerId: int,
        targetId: int,
        ringInventoryId: int,
    ):
        super().__init__(timeout=60)
        self.proposerId = proposerId
        self.targetId = targetId
        self.ringInventoryId = ringInventoryId
        self.proposalService = ProposalService()
        self.message = None

    @discord.ui.button(label="Đồng ý", style=discord.ButtonStyle.success)
    async def acceptButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        result = self.proposalService.acceptProposal(
            proposerUserId=self.proposerId,
            targetUserId=self.targetId,
            ringInventoryId=self.ringInventoryId,
        )
        self.disableAllItems()

        if not result["success"]:
            await interaction.response.edit_message(
                embed=self.buildFailedEmbed(result["message"]),
                view=self,
            )
            return

        await interaction.response.edit_message(
            embed=self.buildAcceptedEmbed(
                proposer=interaction.guild.get_member(self.proposerId),
                target=interaction.user,
                result=result,
            ),
            view=self,
        )

    @discord.ui.button(label="Không đồng ý", style=discord.ButtonStyle.danger)
    async def declineButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.disableAllItems()

        await interaction.response.edit_message(
            embed=self.buildDeclinedEmbed(),
            view=self,
        )

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id != self.targetId:
            await interaction.response.send_message(
                "Chỉ người được cầu hôn mới có thể phản hồi.",
                ephemeral=True,
            )
            return False

        return True

    async def on_timeout(self):
        self.disableAllItems()

        if self.message is not None:
            await self.message.edit(
                embed=self.buildTimeoutEmbed(),
                view=self,
            )

    def disableAllItems(self):
        for item in self.children:
            item.disabled = True

    def buildPendingEmbed(self, proposer, target, ringOption):
        embed = discord.Embed(
            title="Lời cầu hôn",
            description=(
                f"{target.mention} ơi, {proposer.mention} đã cầu hôn bạn bằng "
                f"{self.buildRingText(ringOption['itemName'], ringOption['itemEmoji'])}.\n"
                "Bạn đồng ý chứ?"
            ),
            color=discord.Color.pink(),
        )
        embed.add_field(
            name="Điểm thân mật",
            value=f"**{formatNumber(ringOption['intimacyPoints'])}**",
            inline=False,
        )
        return embed

    def buildAcceptedEmbed(self, proposer, target, result: dict):
        proposerMention = f"<@{self.proposerId}>" if proposer is None else proposer.mention
        embed = discord.Embed(
            title="Cầu hôn thành công",
            description=(
                f"{target.mention} đã đồng ý lời cầu hôn của {proposerMention}.\n"
                f"Nhẫn: {self.buildRingText(result['ringName'], result['ringEmoji'])}\n"
                f"Điểm thân mật hiện tại: **{formatNumber(result['intimacyPoints'])}**"
            ),
            color=discord.Color.green(),
        )
        return embed

    def buildDeclinedEmbed(self):
        embed = discord.Embed(
            title="Lời cầu hôn đã bị từ chối",
            description="Không có gì xảy ra.",
            color=discord.Color.orange(),
        )
        return embed

    def buildTimeoutEmbed(self):
        embed = discord.Embed(
            title="Lời cầu hôn đã hết hạn",
            description="Không có phản hồi trong 60 giây.",
            color=discord.Color.light_grey(),
        )
        return embed

    def buildFailedEmbed(self, message: str):
        embed = discord.Embed(
            title="Cầu hôn thất bại",
            description=message,
            color=discord.Color.red(),
        )
        return embed

    def buildRingText(self, ringName: str, ringEmoji: str | None):
        if ringEmoji is None:
            return f"**{ringName}**"

        return f"{ringEmoji} **{ringName}**"
