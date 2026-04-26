import discord
from discord.ext import commands

from bot.services.farm.farmHarvestService import FarmHarvestService
from bot.services.farm.farmRenderService import FarmRenderService
from bot.services.farm.farmWaterService import FarmWaterService


class MyFarmView(discord.ui.View):
    def __init__(self, bot, authorId: int, memberDisplayName: str):
        super().__init__(timeout=600)

        self.bot = bot
        self.authorId = authorId
        self.memberDisplayName = memberDisplayName
        self.farmRenderService = FarmRenderService(bot)
        self.farmHarvestService = FarmHarvestService()
        self.farmWaterService = FarmWaterService()

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id != self.authorId:
            await interaction.response.send_message(
                "Bạn không thể thao tác farm của người khác.",
                ephemeral=True,
            )
            return False

        return True

    @discord.ui.button(label="Làm mới", emoji="🔄", style=discord.ButtonStyle.secondary)
    async def refreshButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.refreshFarmMessage(interaction)

    @discord.ui.button(label="Tưới nước", emoji="💧", style=discord.ButtonStyle.primary)
    async def waterButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            waterResult = self.farmWaterService.waterCrop(self.authorId)

            if not waterResult["success"]:
                await interaction.response.send_message(
                    waterResult["message"],
                    ephemeral=True,
                )
                return

            await self.refreshFarmMessage(
                interaction=interaction,
                extraMessage=waterResult["message"],
            )

        except Exception as e:
            print(f"Water farm error: {e}")
            await interaction.response.send_message(
                "Đã xảy ra lỗi khi tưới nước.",
                ephemeral=True,
            )

    @discord.ui.button(label="Thu hoạch", emoji="🌾", style=discord.ButtonStyle.success)
    async def harvestButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            harvestResult = self.farmHarvestService.harvestCrop(self.authorId)

            if not harvestResult["success"]:
                await interaction.response.send_message(
                    harvestResult["message"],
                    ephemeral=True,
                )
                return

            await self.refreshFarmMessage(
                interaction=interaction,
                extraMessage=harvestResult["message"],
            )

        except Exception as e:
            print(f"Harvest farm error: {e}")
            await interaction.response.send_message(
                "Đã xảy ra lỗi khi thu hoạch.",
                ephemeral=True,
            )

    async def refreshFarmMessage(
        self,
        interaction: discord.Interaction,
        extraMessage: str = None,
    ):
        renderResult = await self.farmRenderService.renderFarmByMemberId(self.authorId)

        file = discord.File(
            renderResult["buffer"],
            filename="my_farm.png",
        )

        embed = self.buildFarmEmbed(renderResult["embedData"])

        if extraMessage is not None:
            embed.description = extraMessage

        embed.set_image(url="attachment://my_farm.png")

        await interaction.response.edit_message(
            embed=embed,
            attachments=[file],
            view=self,
        )

    def buildFarmEmbed(self, embedData):
        embed = discord.Embed(
            title=f"Farm của {self.memberDisplayName}",
            color=discord.Color.green(),
        )

        embed.add_field(
            name="Cây đang trồng",
            value=embedData["cropText"],
            inline=True,
        )

        embed.add_field(
            name="Thu hoạch trong",
            value=embedData["remainingTimeText"],
            inline=True,
        )

        embed.add_field(
            name="Trạng thái đất",
            value=embedData["landStatusText"],
            inline=True,
        )

        embed.add_field(
            name="Sâu bệnh",
            value=embedData["pestStatusText"],
            inline=True,
        )

        return embed


class MyFarmCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.farmRenderService = FarmRenderService(bot)

    @commands.command(name="myfarm")
    async def myFarm(self, ctx):
        try:
            renderResult = await self.farmRenderService.renderFarmByMemberId(ctx.author.id)

            file = discord.File(
                renderResult["buffer"],
                filename="my_farm.png",
            )

            view = MyFarmView(
                bot=self.bot,
                authorId=ctx.author.id,
                memberDisplayName=ctx.author.display_name,
            )

            embed = view.buildFarmEmbed(renderResult["embedData"])
            embed.set_image(url="attachment://my_farm.png")

            await ctx.reply(
                embed=embed,
                file=file,
                view=view,
            )

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