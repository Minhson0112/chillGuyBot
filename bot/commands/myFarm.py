import discord
from discord.ext import commands

from bot.services.farm.farmRenderService import FarmRenderService


class MyFarmRefreshView(discord.ui.View):
    def __init__(self, bot, authorId: int):
        super().__init__(timeout=600)

        self.bot = bot
        self.authorId = authorId
        self.farmRenderService = FarmRenderService(bot)

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id != self.authorId:
            await interaction.response.send_message(
                "Bạn không thể làm mới farm của người khác.",
                ephemeral=True,
            )
            return False

        return True

    @discord.ui.button(label="Làm mới", emoji="🔄", style=discord.ButtonStyle.secondary)
    async def refreshButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            buffer = await self.farmRenderService.renderFarmByMemberId(self.authorId)

            file = discord.File(buffer, filename="my_farm.png")

            await interaction.response.edit_message(
                attachments=[file],
                view=self,
            )

        except ValueError:
            await interaction.response.send_message(
                "Bạn chưa có nông trại. Hãy liên hệ quản trị viên để khởi tạo farm.",
                ephemeral=True,
            )

        except FileNotFoundError as e:
            print(f"Farm asset file not found: {e}")
            await interaction.response.send_message(
                "Không tìm thấy ảnh asset để render farm.",
                ephemeral=True,
            )

        except Exception as e:
            print(f"Refresh farm error: {e}")
            await interaction.response.send_message(
                "Đã xảy ra lỗi khi làm mới farm.",
                ephemeral=True,
            )


class MyFarmCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.farmRenderService = FarmRenderService(bot)

    @commands.command(name="myfarm")
    async def myFarm(self, ctx):
        try:
            buffer = await self.farmRenderService.renderFarmByMemberId(ctx.author.id)

            file = discord.File(buffer, filename="my_farm.png")

            view = MyFarmRefreshView(
                bot=self.bot,
                authorId=ctx.author.id,
            )

            await ctx.reply(file=file, view=view)

        except ValueError:
            await ctx.reply("Bạn chưa có nông trại. Hãy liên hệ quản trị viên để khởi tạo farm.")

        except FileNotFoundError as e:
            print(f"Farm asset file not found: {e}")
            await ctx.reply("Không tìm thấy ảnh asset để render farm.")

        except Exception as e:
            print(f"Render farm error: {e}")
            await ctx.reply("Đã xảy ra lỗi khi render farm.")


async def setup(bot):
    await bot.add_cog(MyFarmCommand(bot))