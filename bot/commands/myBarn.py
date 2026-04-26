import discord
from discord.ext import commands

from bot.services.farm.farmInventoryRenderService import FarmInventoryRenderService


class MyBarnPaginationView(discord.ui.View):
    def __init__(
        self,
        authorId: int,
        memberDisplayName: str,
        currentPage: int,
        totalPage: int,
    ):
        super().__init__(timeout=180)

        self.authorId = authorId
        self.memberDisplayName = memberDisplayName
        self.currentPage = currentPage
        self.totalPage = totalPage
        self.farmInventoryRenderService = FarmInventoryRenderService()

        self.updateButtonState()

    def updateButtonState(self):
        self.previousButton.disabled = self.currentPage <= 1
        self.nextButton.disabled = self.currentPage >= self.totalPage

    async def updateBarnMessage(self, interaction: discord.Interaction):
        renderResult = self.farmInventoryRenderService.renderBarnPageToBuffer(
            userId=self.authorId,
            memberDisplayName=self.memberDisplayName,
            page=self.currentPage,
        )

        self.currentPage = renderResult["currentPage"]
        self.totalPage = renderResult["totalPage"]

        self.updateButtonState()

        file = discord.File(
            renderResult["buffer"],
            filename="my_barn.png",
        )

        await interaction.response.edit_message(
            attachments=[file],
            view=self,
        )

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id != self.authorId:
            await interaction.response.send_message(
                "Bạn không thể điều khiển barn của người khác.",
                ephemeral=True,
            )
            return False

        return True

    @discord.ui.button(label="Trước", emoji="⬅️", style=discord.ButtonStyle.secondary)
    async def previousButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.currentPage -= 1
        await self.updateBarnMessage(interaction)

    @discord.ui.button(label="Tiếp", emoji="➡️", style=discord.ButtonStyle.secondary)
    async def nextButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.currentPage += 1
        await self.updateBarnMessage(interaction)


class MyBarnCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.farmInventoryRenderService = FarmInventoryRenderService()

    @commands.command(name="mybarn")
    async def myBarn(self, ctx, page: int = 1):
        try:
            renderResult = self.farmInventoryRenderService.renderBarnPageToBuffer(
                userId=ctx.author.id,
                memberDisplayName=ctx.author.display_name,
                page=page,
            )

            file = discord.File(
                renderResult["buffer"],
                filename="my_barn.png",
            )

            view = MyBarnPaginationView(
                authorId=ctx.author.id,
                memberDisplayName=ctx.author.display_name,
                currentPage=renderResult["currentPage"],
                totalPage=renderResult["totalPage"],
            )

            await ctx.reply(file=file, view=view)

        except FileNotFoundError as e:
            print(f"Barn asset file not found: {e}")
            await ctx.reply("Không tìm thấy ảnh asset để render barn.")

        except Exception as e:
            print(f"Render barn error: {e}")
            await ctx.reply("Đã xảy ra lỗi khi render barn.")


async def setup(bot):
    await bot.add_cog(MyBarnCommand(bot))