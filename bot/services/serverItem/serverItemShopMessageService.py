import discord

from bot.config.database import getDbSession
from bot.config.emoji import CHILL_COIN, COWONCCY, LOVE
from bot.config.imagePaths import ASSET_IMAGE_PATHS
from bot.helper.numberFormatHelper import formatNumber
from bot.repository.serverItemMasterRepository import ServerItemMasterRepository


class ServerItemShopMessageService:
    SHOP_COLOR = 0xFF8AC6

    async def sendShopMessage(self, ctx):
        serverItems = self.findShopItems()

        if not serverItems:
            await ctx.reply("Hiện chưa có item nào trong love shop.")
            return

        embeds = []
        files = []

        for serverItem in serverItems:
            imagePath = self.findItemImagePath(serverItem)
            imageFileName = f"{serverItem.icon_image_key}.png"

            files.append(discord.File(imagePath, filename=imageFileName))
            embeds.append(self.buildItemEmbed(serverItem, imageFileName))

        await ctx.send(
            embeds=embeds,
            files=files,
            view=self.buildShopView(serverItems),
        )

    def findShopItems(self):
        with getDbSession() as session:
            serverItemMasterRepository = ServerItemMasterRepository(session)
            return serverItemMasterRepository.findAll()

    def buildItemEmbed(self, serverItem, imageFileName: str):
        embed = discord.Embed(
            title=serverItem.name,
            description=(
                f"Giá cowoncy: **{formatNumber(serverItem.price_cowoncy)}** {COWONCCY}\n"
                f"Giá chillcoin: **{formatNumber(serverItem.price_chill_coin)}** {CHILL_COIN}\n"
                f"Điểm thân mật: **{formatNumber(serverItem.intimacy_points)}** {LOVE}"
            ),
            color=self.SHOP_COLOR,
        )
        embed.set_image(url=f"attachment://{imageFileName}")
        return embed

    def buildShopView(self, serverItems):
        view = discord.ui.View(timeout=None)

        for serverItem in serverItems:
            view.add_item(discord.ui.Button(
                label=f"Mua {serverItem.name}",
                style=discord.ButtonStyle.primary,
                disabled=True,
            ))

        return view

    def findItemImagePath(self, serverItem):
        imagePath = ASSET_IMAGE_PATHS.get(serverItem.icon_image_key)

        if imagePath is None:
            raise ValueError(f"Server item image path not found: {serverItem.icon_image_key}")

        return imagePath
