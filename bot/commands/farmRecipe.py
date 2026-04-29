import discord
from discord.ext import commands

from bot.services.farm.farmRecipeRenderService import FarmRecipeRenderService


class FarmRecipePaginationView(discord.ui.View):
    def __init__(
        self,
        currentPage: int,
        totalPage: int,
    ):
        super().__init__(timeout=600)

        self.currentPage = currentPage
        self.totalPage = totalPage
        self.farmRecipeRenderService = FarmRecipeRenderService()

        self.updateButtonState()

    def updateButtonState(self):
        self.previousButton.disabled = self.currentPage <= 1
        self.nextButton.disabled = self.currentPage >= self.totalPage

    @discord.ui.button(label="Trước", emoji="⬅️", style=discord.ButtonStyle.secondary)
    async def previousButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.currentPage > 1:
            self.currentPage -= 1

        await self.refreshRecipeMessage(interaction)

    @discord.ui.button(label="Tiếp", emoji="➡️", style=discord.ButtonStyle.secondary)
    async def nextButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.currentPage < self.totalPage:
            self.currentPage += 1

        await self.refreshRecipeMessage(interaction)

    async def refreshRecipeMessage(self, interaction: discord.Interaction):
        renderResult = self.farmRecipeRenderService.renderRecipePageToBuffer(
            page=self.currentPage,
        )

        self.currentPage = renderResult["currentPage"]
        self.totalPage = renderResult["totalPage"]

        self.updateButtonState()

        file = discord.File(
            renderResult["buffer"],
            filename="recipes.png",
        )

        await interaction.response.edit_message(
            attachments=[file],
            view=self,
        )


class FarmRecipeCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.farmRecipeRenderService = FarmRecipeRenderService()

    @commands.command(name="rec")
    async def recipes(self, ctx):
        try:
            renderResult = self.farmRecipeRenderService.renderRecipePageToBuffer(page=1)

            file = discord.File(
                renderResult["buffer"],
                filename="recipes.png",
            )

            view = FarmRecipePaginationView(
                currentPage=renderResult["currentPage"],
                totalPage=renderResult["totalPage"],
            )

            await ctx.reply(
                file=file,
                view=view,
            )

        except FileNotFoundError as e:
            print(f"Recipe asset file not found: {e}")
            await ctx.reply("Không tìm thấy ảnh asset để render công thức nấu ăn.")

        except Exception as e:
            print(f"Render recipe error: {e}")
            await ctx.reply("Đã xảy ra lỗi khi render công thức nấu ăn.")


async def setup(bot):
    await bot.add_cog(FarmRecipeCommand(bot))