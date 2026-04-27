import discord
from discord.ext import commands

from bot.services.farm.farmMarketShopRenderService import FarmMarketShopRenderService
from bot.services.farm.farmRenderService import FarmRenderService


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

            embed = discord.Embed(
                title=f"Shop của {self.visitedDisplayName}",
                description=(
                    "Dùng `cg buyshop <id>` để mua món hàng trong shop này.\n"
                    f"Trang **{renderResult['currentPage']} / {renderResult['totalPage']}**"
                ),
                color=discord.Color.gold(),
            )
            embed.set_image(url="attachment://member_shop.png")

            await interaction.response.send_message(
                embed=embed,
                file=file,
                ephemeral=True,
            )

        except FileNotFoundError as e:
            print(f"Visit shop asset file not found: {e}")
            await interaction.response.send_message(
                "Không tìm thấy ảnh asset để render shop.",
                ephemeral=True,
            )

        except Exception as e:
            print(f"Visit shop render error: {e}")
            await interaction.response.send_message(
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
            renderResult = await self.farmRenderService.renderFarmByMemberId(member.id)

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