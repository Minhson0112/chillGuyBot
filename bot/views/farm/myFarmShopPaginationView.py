import discord

from bot.helper.numberFormatHelper import formatNumber
from bot.config.database import getDbSession
from bot.config.emoji import FARM_GAME_EMOJI
from bot.helper.farmItemHelper import buildItemText
from bot.repository.farmMarketListingRepository import FarmMarketListingRepository
from bot.services.farm.farmMarketShopRenderService import FarmMarketShopRenderService


class MyFarmShopPaginationView(discord.ui.View):
    HISTORY_LIMIT = 10

    def __init__(
        self,
        sellerUserId: int,
        sellerDisplayName: str,
        currentPage: int,
        totalPage: int,
    ):
        super().__init__(timeout=600)

        self.sellerUserId = sellerUserId
        self.sellerDisplayName = sellerDisplayName
        self.currentPage = currentPage
        self.totalPage = totalPage
        self.farmMarketShopRenderService = FarmMarketShopRenderService()

        self.updateButtonState()

    def updateButtonState(self):
        self.previousButton.disabled = self.currentPage <= 1
        self.nextButton.disabled = self.currentPage >= self.totalPage

    @discord.ui.button(label="Lịch sử mua hàng", emoji="🧾", style=discord.ButtonStyle.primary)
    async def historyButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = self.buildPurchaseHistoryEmbed()

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True,
            allowed_mentions=discord.AllowedMentions.none(),
        )

    @discord.ui.button(label="Trước", emoji="⬅️", style=discord.ButtonStyle.secondary)
    async def previousButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.currentPage > 1:
            self.currentPage -= 1

        await self.refreshShopMessage(interaction)

    @discord.ui.button(label="Tiếp", emoji="➡️", style=discord.ButtonStyle.secondary)
    async def nextButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.currentPage < self.totalPage:
            self.currentPage += 1

        await self.refreshShopMessage(interaction)

    async def refreshShopMessage(self, interaction: discord.Interaction):
        renderResult = self.farmMarketShopRenderService.renderMemberShopPageToBuffer(
            sellerUserId=self.sellerUserId,
            memberDisplayName=self.sellerDisplayName,
            page=self.currentPage,
        )

        self.currentPage = renderResult["currentPage"]
        self.totalPage = renderResult["totalPage"]

        self.updateButtonState()

        file = discord.File(
            renderResult["buffer"],
            filename="my_shop.png",
        )

        await interaction.response.edit_message(
            content=self.buildShopContent(),
            attachments=[file],
            view=self,
            embed=None,
        )

    def buildShopContent(self):
        return (
            f"**Shop của {self.sellerDisplayName}**\n"
            "Dùng `cg buyshop <id>` để mua món hàng trong shop này.\n"
            f"Trang **{self.currentPage} / {self.totalPage}**"
        )

    def buildPurchaseHistoryEmbed(self):
        with getDbSession() as session:
            farmMarketListingRepository = FarmMarketListingRepository(session)

            soldListings = farmMarketListingRepository.findSoldListingsBySellerUserId(
                sellerUserId=self.sellerUserId,
                limit=self.HISTORY_LIMIT,
            )

        embed = discord.Embed(
            title=f"Lịch sử mua hàng tại shop của {self.sellerDisplayName}",
            color=discord.Color.gold(),
        )

        if not soldListings:
            embed.description = "Shop này chưa có lịch sử mua hàng."
            return embed

        for listing in soldListings:
            itemText = buildItemText(listing.item, "**Không rõ item**")
            buyerText = self.buildBuyerText(listing.buyer_user_id)
            soldAtText = self.formatSoldAt(listing.sold_at)
            chillCoinEmoji = FARM_GAME_EMOJI["chill_coin"]

            embed.add_field(
                name=f"#{listing.id} - {itemText}",
                value=(
                    f"Số lượng: **{formatNumber(listing.quantity)}**\n"
                    f"Giá: **{formatNumber(listing.price)}** {chillCoinEmoji}\n"
                    f"Người mua: {buyerText}\n"
                    f"Thời gian mua: **{soldAtText}**"
                ),
                inline=False,
            )

        return embed

    def buildBuyerText(self, buyerUserId):
        if buyerUserId is None:
            return "Không rõ"

        return f"<@{buyerUserId}>"

    def formatSoldAt(self, soldAt):
        if soldAt is None:
            return "-"

        return soldAt.strftime("%Y-%m-%d %H:%M")
