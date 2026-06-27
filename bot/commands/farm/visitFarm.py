import discord
from discord.ext import commands

from bot.services.farm.farmMarketShopRenderService import FarmMarketShopRenderService
from bot.services.farm.farmRenderService import FarmRenderService


class MemberShopPaginationView(discord.ui.View):
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

    async def refreshShopMessage(self, interaction: discord.Interaction):
        await interaction.response.defer()

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
            filename="member_shop.png",
        )

        embed = self.buildShopEmbed()
        embed.set_image(url="attachment://member_shop.png")

        await interaction.edit_original_response(
            embed=embed,
            attachments=[file],
            view=self,
        )

    def buildShopEmbed(self):
        return discord.Embed(
            title=f"Shop của {self.sellerDisplayName}",
            description=(
                "Dùng `cg buyshop <id>` để mua món hàng trong shop này.\n"
                f"Trang **{self.currentPage} / {self.totalPage}**"
            ),
            color=discord.Color.gold(),
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


class VisitFarmView(discord.ui.View):
    def __init__(
        self,
        bot,
        visitedUserId: int,
        visitedDisplayName: str,
    ):
        super().__init__(timeout=600)

        self.bot = bot
        self.visitedUserId = visitedUserId
        self.visitedDisplayName = visitedDisplayName
        self.farmMarketShopRenderService = FarmMarketShopRenderService()

    @discord.ui.button(label="Xem shop", emoji="🛒", style=discord.ButtonStyle.primary)
    async def viewShopButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()

        try:
            renderResult = self.farmMarketShopRenderService.renderMemberShopPageToBuffer(
                sellerUserId=self.visitedUserId,
                memberDisplayName=self.visitedDisplayName,
                page=1,
            )

            file = discord.File(
                renderResult["buffer"],
                filename="member_shop.png",
            )

            view = MemberShopPaginationView(
                sellerUserId=self.visitedUserId,
                sellerDisplayName=self.visitedDisplayName,
                currentPage=renderResult["currentPage"],
                totalPage=renderResult["totalPage"],
            )

            embed = view.buildShopEmbed()
            embed.set_image(url="attachment://member_shop.png")

            await interaction.followup.send(
                embed=embed,
                file=file,
                view=view,
                ephemeral=True,
            )

        except FileNotFoundError as e:
            print(f"Visit shop asset file not found: {e}")
            await interaction.followup.send(
                "Không tìm thấy ảnh asset để render shop.",
                ephemeral=True,
            )

        except Exception as e:
            print(f"Visit shop render error: {e}")
            await interaction.followup.send(
                "Đã xảy ra lỗi khi xem shop.",
                ephemeral=True,
            )


class VisitFarmCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.farmRenderService = FarmRenderService(bot)

    @commands.command(name="visit")
    async def visitFarm(self, ctx, member: discord.Member = None):
        if member is None:
            await ctx.reply("Cách dùng: `cg visit @user`")
            return

        if member.bot:
            await ctx.reply("Bot không có nông trại để ghé thăm.")
            return

        try:
            renderResult = await self.farmRenderService.renderFarmByMemberId(
                member.id,
                includePrivateInfo=False,
            )

            file = discord.File(
                renderResult["buffer"],
                filename="visit_farm.png",
            )

            embed = self.buildVisitFarmEmbed(
                memberDisplayName=member.display_name,
                embedData=renderResult["embedData"],
            )

            embed.set_image(url="attachment://visit_farm.png")

            view = VisitFarmView(
                bot=self.bot,
                visitedUserId=member.id,
                visitedDisplayName=member.display_name,
            )

            await ctx.reply(
                embed=embed,
                file=file,
                view=view,
            )

        except ValueError:
            await ctx.reply(f"{member.display_name} chưa có nông trại.")

        except FileNotFoundError as e:
            print(f"Visit farm asset file not found: {e}")
            await ctx.reply("Không tìm thấy ảnh asset để render farm.")

        except Exception as e:
            print(f"Visit farm error: {e}")
            await ctx.reply("Đã xảy ra lỗi khi ghé thăm farm.")

    def buildVisitFarmEmbed(
        self,
        memberDisplayName: str,
        embedData,
    ):
        embed = discord.Embed(
            title=f"Farm của {memberDisplayName}",
            description="Thông tin cây trồng hiện tại",
            color=discord.Color.green(),
        )

        embed.add_field(
            name="Cây đang trồng",
            value=embedData["cropText"],
            inline=True,
        )

        embed.add_field(
            name="Thu hoạch trong 🌾",
            value=embedData["remainingTimeText"],
            inline=True,
        )

        embed.add_field(
            name="Trạng thái đất 💧",
            value=embedData["landStatusText"],
            inline=True,
        )

        embed.add_field(
            name="Sâu bệnh <:bug:1498089075867914281>",
            value=embedData["pestStatusText"],
            inline=True,
        )

        return embed


async def setup(bot):
    await bot.add_cog(VisitFarmCommand(bot))
