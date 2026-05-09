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
from bot.views.farm.myFarmShopPaginationView import MyFarmShopPaginationView
from bot.services.farm.farmInventoryRenderService import FarmInventoryRenderService
from bot.views.farm.mySiloPaginationView import MySiloPaginationView
from bot.services.farm.farmInventoryRenderService import FarmInventoryRenderService
from bot.views.farm.myBarnPaginationView import MyBarnPaginationView
from bot.services.farm.farmShopRenderService import FarmShopRenderService
from bot.views.farm.farmNpcShopPaginationView import FarmNpcShopPaginationView
from bot.services.farm.farmRecipeRenderService import FarmRecipeRenderService
from bot.views.farm.farmRecipePaginationView import FarmRecipePaginationView
from bot.repository.userInventoryRepository import UserInventoryRepository
from bot.views.farm.plantSeedSelectView import PlantSeedSelectView
from bot.config.database import getDbSession


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
        self.farmInventoryRenderService = FarmInventoryRenderService()
        self.farmInventoryRenderService = FarmInventoryRenderService()
        self.farmShopRenderService = FarmShopRenderService()
        self.farmRecipeRenderService = FarmRecipeRenderService()

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id != self.authorId:
            await interaction.response.send_message(
                "Bạn không thể thao tác farm của người khác.",
                ephemeral=True,
            )
            return False

        return True

    @discord.ui.button(label="Làm mới", emoji="<:reload:1501945504546689095>", style=discord.ButtonStyle.secondary)
    async def refreshButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.refreshFarmMessage(interaction)

    @discord.ui.button(label="Trồng cây", emoji="🌱", style=discord.ButtonStyle.success)
    async def plantCropButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            seedOptions = self.findSeedOptions()

            if not seedOptions:
                await interaction.response.send_message(
                    "Bạn không có hạt giống nào trong silo. hãy bấm nút **<:store:1501945501883568331> Shop NPC** để mua hạt giống.",
                    ephemeral=True,
                )
                return

            view = PlantSeedSelectView(
                authorId=self.authorId,
                seedOptions=seedOptions,
            )

            await interaction.response.send_message(
                content="Các hạt giống 🌱 bên dưới là các hạt giống trong silo của bạn.<:silo:1501945517880639498>",
                view=view,
                ephemeral=True,
            )

        except Exception as e:
            print(f"Open plant seed select error: {e}")
            await interaction.response.send_message(
                "Đã xảy ra lỗi khi mở danh sách hạt giống.",
                ephemeral=True,
            )

    @discord.ui.button(label="Tưới nước", emoji="<:watering:1501945506018885743>", style=discord.ButtonStyle.primary)
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

    @discord.ui.button(label="Bắt sâu", emoji="<:bug:1498089075867914281>", style=discord.ButtonStyle.danger)
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

    @discord.ui.button(label="Thu hoạch", emoji="<:harvest:1501945507277438997>", style=discord.ButtonStyle.success)
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

    @discord.ui.button(label="Cho gà ăn", emoji="<:feeding_chicken:1501945509152030860>", style=discord.ButtonStyle.primary)
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

    @discord.ui.button(label="Cho bò ăn", emoji="<:feed_cow:1501945511241060352>", style=discord.ButtonStyle.primary)
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
    
    @discord.ui.button(label="Lấy trứng", emoji="<:easteregg:1501945513157853345>", style=discord.ButtonStyle.success)
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

    @discord.ui.button(label="Vắt sữa", emoji="<:milking:1501945514651025510>", style=discord.ButtonStyle.success)
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

    @discord.ui.button(label="Câu cá", emoji="<:fishing:1501945516378816563>", style=discord.ButtonStyle.secondary)
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
        
    @discord.ui.button(label="Xem silo", emoji="<:silo:1501945517880639498>", style=discord.ButtonStyle.secondary)
    async def viewMySiloButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            renderResult = self.farmInventoryRenderService.renderSiloPageToBuffer(
                userId=self.authorId,
                memberDisplayName=self.memberDisplayName,
                page=1,
            )

            file = discord.File(
                renderResult["buffer"],
                filename="my_silo.png",
            )

            view = MySiloPaginationView(
                authorId=self.authorId,
                memberDisplayName=self.memberDisplayName,
                currentPage=renderResult["currentPage"],
                totalPage=renderResult["totalPage"],
            )

            await interaction.response.send_message(
                file=file,
                view=view,
                ephemeral=True,
            )

        except FileNotFoundError as e:
            print(f"Silo asset file not found: {e}")
            await interaction.response.send_message(
                "Không tìm thấy ảnh asset để render silo.",
                ephemeral=True,
            )

        except Exception as e:
            print(f"Render my silo error: {e}")
            await interaction.response.send_message(
                "Đã xảy ra lỗi khi xem silo của bạn.",
                ephemeral=True,
            )

    @discord.ui.button(label="Xem barn", emoji="<:barn:1501945519680000041>", style=discord.ButtonStyle.secondary)
    async def viewMyBarnButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            renderResult = self.farmInventoryRenderService.renderBarnPageToBuffer(
                userId=self.authorId,
                memberDisplayName=self.memberDisplayName,
                page=1,
            )

            file = discord.File(
                renderResult["buffer"],
                filename="my_barn.png",
            )

            view = MyBarnPaginationView(
                authorId=self.authorId,
                memberDisplayName=self.memberDisplayName,
                currentPage=renderResult["currentPage"],
                totalPage=renderResult["totalPage"],
            )

            await interaction.response.send_message(
                file=file,
                view=view,
                ephemeral=True,
            )

        except FileNotFoundError as e:
            print(f"Barn asset file not found: {e}")
            await interaction.response.send_message(
                "Không tìm thấy ảnh asset để render barn.",
                ephemeral=True,
            )

        except Exception as e:
            print(f"Render my barn error: {e}")
            await interaction.response.send_message(
                "Đã xảy ra lỗi khi xem barn của bạn.",
                ephemeral=True,
            )

    @discord.ui.button(label="Shop NPC", emoji="<:store:1501945501883568331>", style=discord.ButtonStyle.secondary)
    async def viewNpcShopButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            renderResult = self.farmShopRenderService.renderShopPageToBuffer(
                page=1,
            )

            file = discord.File(
                renderResult["buffer"],
                filename="farm_shop.png",
            )

            view = FarmNpcShopPaginationView(
                authorId=self.authorId,
                currentPage=renderResult["currentPage"],
                totalPage=renderResult["totalPage"],
            )

            await interaction.response.send_message(
                file=file,
                view=view,
                ephemeral=True,
            )

        except FileNotFoundError as e:
            print(f"Farm NPC shop asset file not found: {e}")
            await interaction.response.send_message(
                "Không tìm thấy ảnh asset để render shop NPC.",
                ephemeral=True,
            )

        except Exception as e:
            print(f"Render farm NPC shop error: {e}")
            await interaction.response.send_message(
                "Đã xảy ra lỗi khi xem shop NPC.",
                ephemeral=True,
            )
    
    @discord.ui.button(label="Xem shop của bạn", emoji="<:producemarket:1501945503133208737>", style=discord.ButtonStyle.secondary)
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

    @discord.ui.button(label="Công thức cooking", emoji="<:cooking:1501948950377267221>", style=discord.ButtonStyle.secondary)
    async def viewRecipeButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            renderResult = self.farmRecipeRenderService.renderRecipePageToBuffer(
                page=1,
            )

            file = discord.File(
                renderResult["buffer"],
                filename="recipes.png",
            )

            view = FarmRecipePaginationView(
                authorId=self.authorId,
                currentPage=renderResult["currentPage"],
                totalPage=renderResult["totalPage"],
            )

            await interaction.response.send_message(
                file=file,
                view=view,
                ephemeral=True,
            )

        except FileNotFoundError as e:
            print(f"Recipe asset file not found: {e}")
            await interaction.response.send_message(
                "Không tìm thấy ảnh asset để render công thức nấu ăn.",
                ephemeral=True,
            )

        except Exception as e:
            print(f"Render recipe error: {e}")
            await interaction.response.send_message(
                "Đã xảy ra lỗi khi xem công thức nấu ăn.",
                ephemeral=True,
            )

    @discord.ui.button(label="Nhận đồ ăn", emoji="<:food:1501945500558164128>", style=discord.ButtonStyle.success)
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

    @discord.ui.button(label="+ Ô đất", emoji="<:farmland_wet:1501946998105047241>", style=discord.ButtonStyle.secondary)
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

    def findSeedOptions(self):
        with getDbSession() as session:
            userInventoryRepository = UserInventoryRepository(session)

            seedRows = userInventoryRepository.findSeedItemsByUserId(
                userId=self.authorId,
                limit=25,
            )

            seedOptions = []

            for seedInventory, totalGrowthSeconds in seedRows:
                item = seedInventory.item

                if item is None:
                    continue

                seedOptions.append({
                    "userInventoryId": seedInventory.id,
                    "itemName": item.name,
                    "iconImageKey": item.icon_image_key,
                    "quantity": seedInventory.quantity,
                    "growthTimeText": self.formatGrowthTime(totalGrowthSeconds),
                })

            return seedOptions
        
    def formatGrowthTime(self, totalGrowthSeconds: int):
        if totalGrowthSeconds is None:
            return "-"

        minutes = totalGrowthSeconds // 60
        seconds = totalGrowthSeconds % 60

        return f"{minutes}:{seconds:02d}"

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

        embed = self.buildFarmEmbed(renderResult["embedData"], extraMessage)

        embed.set_image(url="attachment://my_farm.png")

        await interaction.response.edit_message(
            embed=embed,
            attachments=[file],
            view=self,
        )

    def buildFarmEmbed(self, embedData, extraMessage: str = None):
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
            name="------------------------------------------",
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
        name="------------------------------------------",
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
            name="------------------------------------------",
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
            name="------------------------------------------",
            value="**Sự kiện tàu hỏa 🚂**",
            inline=False,
        )

        embed.add_field(
            name="Trạng thái",
            value=embedData["trainEventText"],
            inline=False,
        )

        if extraMessage is not None:
            embed.add_field(
                name="------------------------------------------",
                value=extraMessage,
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