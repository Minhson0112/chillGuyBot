import discord
from discord.ext import commands

from bot.services.farm.farmHarvestService import FarmHarvestService
from bot.services.farm.farmRenderService import FarmRenderService
from bot.services.farm.farmWaterService import FarmWaterService
from bot.services.farm.farmPestRemoveService import FarmPestRemoveService
from bot.services.farm.farmChickenFeedService import FarmChickenFeedService
from bot.services.farm.farmChickenEggCollectService import FarmChickenEggCollectService
from bot.services.farm.farmCowFeedService import FarmCowFeedService
from bot.services.farm.farmCowMilkCollectService import FarmCowMilkCollectService
from bot.services.farm.farmFishingService import FarmFishingService
from bot.services.farm.farmMarketShopRenderService import FarmMarketShopRenderService
from bot.services.farm.farmPlotUnlockService import FarmPlotUnlockService
from bot.services.farm.farmKitchenCollectService import FarmKitchenCollectService
from bot.services.farm.farmTrainEventQueueService import FarmTrainEventQueueService


class MyFarmShopPaginationView(discord.ui.View):
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

        embed = self.buildShopEmbed()
        embed.set_image(url="attachment://my_shop.png")

        await interaction.response.edit_message(
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

class MyFarmView(discord.ui.View):
    def __init__(self, bot, authorId: int, memberDisplayName: str):
        super().__init__(timeout=600)

        self.bot = bot
        self.authorId = authorId
        self.memberDisplayName = memberDisplayName
        self.farmRenderService = FarmRenderService(bot)
        self.farmHarvestService = FarmHarvestService()
        self.farmWaterService = FarmWaterService()
        self.farmPestRemoveService = FarmPestRemoveService()
        self.farmChickenFeedService = FarmChickenFeedService()
        self.farmChickenEggCollectService = FarmChickenEggCollectService()
        self.farmCowFeedService = FarmCowFeedService()
        self.farmCowMilkCollectService = FarmCowMilkCollectService()
        self.farmFishingService = FarmFishingService()
        self.farmMarketShopRenderService = FarmMarketShopRenderService()
        self.farmPlotUnlockService = FarmPlotUnlockService()
        self.farmKitchenCollectService = FarmKitchenCollectService()
        self.farmTrainEventQueueService = FarmTrainEventQueueService()
        
        

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

    @discord.ui.button(label="Bắt sâu", emoji="🐛", style=discord.ButtonStyle.danger)
    async def removePestButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            pestResult = self.farmPestRemoveService.removePest(self.authorId)

            if not pestResult["success"]:
                await interaction.response.send_message(
                    pestResult["message"],
                    ephemeral=True,
                )
                return

            await self.refreshFarmMessage(
                interaction=interaction,
                extraMessage=pestResult["message"],
            )

        except Exception as e:
            print(f"Remove pest farm error: {e}")
            await interaction.response.send_message(
                "Đã xảy ra lỗi khi bắt sâu.",
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

    @discord.ui.button(label="Cho gà ăn", emoji="🐔", style=discord.ButtonStyle.primary)
    async def feedChickenButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            feedResult = self.farmChickenFeedService.feedChicken(self.authorId)

            if not feedResult["success"]:
                await interaction.response.send_message(
                    feedResult["message"],
                    ephemeral=True,
                )
                return

            await self.refreshFarmMessage(
                interaction=interaction,
                extraMessage=feedResult["message"],
            )

        except Exception as e:
            print(f"Feed chicken error: {e}")
            await interaction.response.send_message(
                "Đã xảy ra lỗi khi cho gà ăn.",
                ephemeral=True,
            )

    @discord.ui.button(label="Cho bò ăn", emoji="🐄", style=discord.ButtonStyle.primary)
    async def feedCowButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            feedResult = self.farmCowFeedService.feedCow(self.authorId)

            if not feedResult["success"]:
                await interaction.response.send_message(
                    feedResult["message"],
                    ephemeral=True,
                )
                return

            await self.refreshFarmMessage(
                interaction=interaction,
                extraMessage=feedResult["message"],
            )

        except Exception as e:
            print(f"Feed cow error: {e}")
            await interaction.response.send_message(
                "Đã xảy ra lỗi khi cho bò ăn.",
                ephemeral=True,
            )
    
    @discord.ui.button(label="Lấy trứng", emoji="🥚", style=discord.ButtonStyle.success)
    async def collectEggButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            collectResult = self.farmChickenEggCollectService.collectEgg(self.authorId)

            if not collectResult["success"]:
                await interaction.response.send_message(
                    collectResult["message"],
                    ephemeral=True,
                )
                return

            await self.refreshFarmMessage(
                interaction=interaction,
                extraMessage=collectResult["message"],
            )

        except Exception as e:
            print(f"Collect egg error: {e}")
            await interaction.response.send_message(
                "Đã xảy ra lỗi khi lấy trứng.",
                ephemeral=True,
            )

    @discord.ui.button(label="Vắt sữa", emoji="🥛", style=discord.ButtonStyle.success)
    async def collectMilkButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            collectResult = self.farmCowMilkCollectService.collectMilk(self.authorId)

            if not collectResult["success"]:
                await interaction.response.send_message(
                    collectResult["message"],
                    ephemeral=True,
                )
                return

            await self.refreshFarmMessage(
                interaction=interaction,
                extraMessage=collectResult["message"],
            )

        except Exception as e:
            print(f"Collect milk error: {e}")
            await interaction.response.send_message(
                "Đã xảy ra lỗi khi vắt sữa.",
                ephemeral=True,
            )

    @discord.ui.button(label="Câu cá", emoji="🎣", style=discord.ButtonStyle.secondary)
    async def fishingButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            fishingResult = self.farmFishingService.fish(self.authorId)

            if not fishingResult["success"]:
                await interaction.response.send_message(
                    fishingResult["message"],
                    ephemeral=True,
                )
                return

            await self.refreshFarmMessage(
                interaction=interaction,
                extraMessage=fishingResult["message"],
            )

        except Exception as e:
            print(f"Fishing error: {e}")
            await interaction.response.send_message(
                "Đã xảy ra lỗi khi câu cá.",
                ephemeral=True,
            )
    
    @discord.ui.button(label="Xem shop của bạn", emoji="🛒", style=discord.ButtonStyle.secondary)
    async def viewMyShopButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            renderResult = self.farmMarketShopRenderService.renderMemberShopPageToBuffer(
                sellerUserId=self.authorId,
                memberDisplayName=self.memberDisplayName,
                page=1,
            )

            file = discord.File(
                renderResult["buffer"],
                filename="my_shop.png",
            )

            view = MyFarmShopPaginationView(
                sellerUserId=self.authorId,
                sellerDisplayName=self.memberDisplayName,
                currentPage=renderResult["currentPage"],
                totalPage=renderResult["totalPage"],
            )

            embed = view.buildShopEmbed()
            embed.set_image(url="attachment://my_shop.png")

            await interaction.response.send_message(
                embed=embed,
                file=file,
                view=view,
                ephemeral=True,
            )

        except FileNotFoundError as e:
            print(f"My shop asset file not found: {e}")
            await interaction.response.send_message(
                "Không tìm thấy ảnh asset để render shop.",
                ephemeral=True,
            )

        except Exception as e:
            print(f"Render my shop error: {e}")
            await interaction.response.send_message(
                "Đã xảy ra lỗi khi xem shop của bạn.",
                ephemeral=True,
            )

    @discord.ui.button(label="Nhận đồ ăn", emoji="🍱", style=discord.ButtonStyle.success)
    async def collectFoodButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            collectResult = self.farmKitchenCollectService.collectFood(self.authorId)

            if not collectResult["success"]:
                await interaction.response.send_message(
                    collectResult["message"],
                    ephemeral=True,
                )
                return

            await self.refreshFarmMessage(
                interaction=interaction,
                extraMessage=collectResult["message"],
            )

        except Exception as e:
            print(f"Collect food error: {e}")
            await interaction.response.send_message(
                "Đã xảy ra lỗi khi nhận đồ ăn.",
                ephemeral=True,
            )

    @discord.ui.button(label="Xếp hàng", emoji="🚂", style=discord.ButtonStyle.primary)
    async def trainEventQueueButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            trainResult = self.farmTrainEventQueueService.queueTrain(self.authorId)

            if not trainResult["success"]:
                await interaction.response.send_message(
                    trainResult["message"],
                    ephemeral=True,
                )
                return

            await self.refreshFarmMessage(
                interaction=interaction,
                extraMessage=trainResult["message"],
            )

        except Exception as e:
            print(f"Train event queue error: {e}")
            await interaction.response.send_message(
                "Đã xảy ra lỗi khi xếp hàng lên tàu hỏa.",
                ephemeral=True,
            )

    @discord.ui.button(label="+ Ô đất", emoji="🧱", style=discord.ButtonStyle.secondary)
    async def unlockPlotButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            unlockResult = self.farmPlotUnlockService.unlockPlot(self.authorId)

            if not unlockResult["success"]:
                await interaction.response.send_message(
                    unlockResult["message"],
                    ephemeral=True,
                )
                return

            await self.refreshFarmMessage(
                interaction=interaction,
                extraMessage=unlockResult["message"],
            )

        except Exception as e:
            print(f"Unlock farm plot error: {e}")
            await interaction.response.send_message(
                "Đã xảy ra lỗi khi mở ô đất.",
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
            name="Thu hoạch trong ⏱️",
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

        embed.add_field(
            name="--------------------------------------------------------",
            value="**Trạng thái chuồng gà <:chicken_left:1495565972692537415>**",
            inline=False,
        )

        embed.add_field(
            name="Gà đói",
            value=embedData["chickenHungryText"],
            inline=True,
        )

        embed.add_field(
            name="Lấy trứng <:Egg:1495565393463349318>",
            value=embedData["eggCollectText"],
            inline=True,
        )

        embed.add_field(
        name="--------------------------------------------------------",
        value="**Trạng thái chuồng bò <:cow_left:1495566015164317747>**",
        inline=False,
    )

        embed.add_field(
            name="Bò đói",
            value=embedData["cowHungryText"],
            inline=True,
        )

        embed.add_field(
            name="Vắt sữa <:Milk:1495567020601774263>",
            value=embedData["milkCollectText"],
            inline=True,
        )

        embed.add_field(
            name="--------------------------------------------------------",
            value="**Trạng thái nhà bếp 🍳**",
            inline=False,
        )

        embed.add_field(
            name="Món đang nấu",
            value=embedData["kitchenFoodText"],
            inline=True,
        )

        embed.add_field(
            name="Số lượng",
            value=embedData["kitchenQuantityText"],
            inline=True,
        )

        embed.add_field(
            name="Thời gian còn lại ⏱️",
            value=embedData["kitchenRemainingTimeText"],
            inline=True,
        )

        embed.add_field(
            name="--------------------------------------------------------",
            value="**Sự kiện tàu hỏa 🚂**",
            inline=False,
        )

        embed.add_field(
            name="Trạng thái",
            value=embedData["trainEventText"],
            inline=False,
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