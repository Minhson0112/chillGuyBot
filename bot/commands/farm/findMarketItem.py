import discord
from discord.ext import commands

from bot.helper.numberFormatHelper import formatNumber
from bot.config.emoji import FARM_GAME_EMOJI
from bot.services.farm.farmMarketSearchService import FarmMarketSearchService


class FindMarketItemView(discord.ui.View):
    def __init__(
        self,
        authorId: int,
        itemId: int,
        itemText: str,
    ):
        super().__init__(timeout=60)

        self.authorId = authorId
        self.itemId = itemId
        self.itemText = itemText
        self.isConfirmed = False
        self.farmMarketSearchService = FarmMarketSearchService()

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id != self.authorId:
            await interaction.response.send_message(
                "Bạn không thể xác nhận tìm kiếm của người khác.",
                ephemeral=True,
            )
            return False

        return True

    @discord.ui.button(label="Xác nhận tìm kiếm", emoji="✅", style=discord.ButtonStyle.success)
    async def confirmButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.isConfirmed:
            await interaction.response.send_message(
                "Lượt tìm kiếm này đã được xử lý.",
                ephemeral=True,
            )
            return

        self.isConfirmed = True
        self.disableButtons()

        try:
            searchResult = self.farmMarketSearchService.searchFirstListing(
                searcherUserId=interaction.user.id,
                itemId=self.itemId,
            )

            if not searchResult["success"]:
                await interaction.response.edit_message(
                    content=searchResult["message"],
                    embed=None,
                    view=self,
                    allowed_mentions=discord.AllowedMentions.none(),
                )
                return

            embed = self.buildFoundEmbed(searchResult["result"])

            await interaction.response.edit_message(
                content=None,
                embed=embed,
                view=self,
                allowed_mentions=discord.AllowedMentions.none(),
            )

        except Exception as e:
            print(f"Find market item confirm error: {e}")
            await interaction.response.edit_message(
                content="Đã xảy ra lỗi khi tìm shop bán món đồ này.",
                embed=None,
                view=self,
            )

    def disableButtons(self):
        for child in self.children:
            child.disabled = True

    def buildFoundEmbed(self, result):
        chillCoinEmoji = FARM_GAME_EMOJI["chill_coin"]

        embed = discord.Embed(
            title="Đã tìm thấy shop phù hợp",
            description=(
                f"Farm đầu tiên tìm thấy: **Farm của {result['sellerDisplayName']}**\n"
                f"Chủ farm: <@{result['sellerUserId']}>"
            ),
            color=discord.Color.green(),
        )

        embed.add_field(
            name="Món đang bán",
            value=result["itemText"],
            inline=True,
        )

        embed.add_field(
            name="Số lượng",
            value=f"**{formatNumber(result['quantity'])}**",
            inline=True,
        )

        embed.add_field(
            name="Giá bán",
            value=f"**{formatNumber(result['price'])}** {chillCoinEmoji}",
            inline=True,
        )

        embed.add_field(
            name="ID món hàng",
            value=f"`{result['listingId']}`",
            inline=True,
        )

        embed.add_field(
            name="Cách mua",
            value=f"`cg buyshop {result['listingId']}`",
            inline=True,
        )

        embed.add_field(
            name="Phí tìm kiếm",
            value=f"**{formatNumber(result['searchCost'])}** {chillCoinEmoji}",
            inline=True,
        )

        return embed



class FindMarketItem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.farmMarketSearchService = FarmMarketSearchService()

    @commands.command(name="tim")
    async def findMarketItem(self, ctx, *, itemName: str = None):
        if itemName is None:
            await ctx.reply("Cách dùng: `cg tim <tên món đồ>`")
            return

        try:
            findItemResult = self.farmMarketSearchService.findItemByName(itemName)

            if not findItemResult["success"]:
                await ctx.reply(findItemResult["message"])
                return

            chillCoinEmoji = FARM_GAME_EMOJI["chill_coin"]

            embed = discord.Embed(
                title="Xác nhận tìm kiếm shop",
                description=(
                    f"Có phải bạn muốn tìm món đồ: {findItemResult['itemText']} không?\n"
                    f"Giá tìm kiếm: **{formatNumber(findItemResult['searchCost'])}** {chillCoinEmoji}\n\n"
                    f"Nếu không có farm nào đang bán món này, bạn sẽ không mất phí."
                ),
                color=discord.Color.gold(),
            )

            embed.set_footer(text="Bấm xác nhận để bắt đầu tìm kiếm.")

            view = FindMarketItemView(
                authorId=ctx.author.id,
                itemId=findItemResult["item"]["id"],
                itemText=findItemResult["itemText"],
            )

            await ctx.reply(
                embed=embed,
                view=view,
                allowed_mentions=discord.AllowedMentions.none(),
            )

        except Exception as e:
            print(f"Find market item error: {e}")
            await ctx.reply("Đã xảy ra lỗi khi tìm món đồ trong shop.")



async def setup(bot):
    await bot.add_cog(FindMarketItem(bot))
