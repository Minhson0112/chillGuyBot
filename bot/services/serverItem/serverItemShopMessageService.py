import discord
from discord.http import Route
from discord import utils

from bot.config.database import getDbSession
from bot.config.emoji import CHILL_COIN, COWONCCY, LOVE
from bot.config.imagePaths import ASSET_IMAGE_PATHS
from bot.enums.discordComponentType import DiscordComponentType
from bot.helper.numberFormatHelper import formatNumber
from bot.repository.serverItemMasterRepository import ServerItemMasterRepository


class ServerItemShopMessageService:
    COMPONENTS_V2_FLAG = 1 << 15
    CUSTOM_ID_PREFIX = "server_item_buy"
    CONTAINER_ACCENT_COLOR = 0xFF8AC6

    async def sendShopMessage(self, ctx):
        serverItems = self.findShopItems()
        files = self.buildItemFiles(serverItems)
        payload = {
            "flags": self.COMPONENTS_V2_FLAG,
            "allowed_mentions": {
                "parse": [],
            },
            "attachments": self.buildAttachmentPayloads(files),
            "components": [
                {
                    "type": DiscordComponentType.CONTAINER,
                    "accent_color": self.CONTAINER_ACCENT_COLOR,
                    "components": self.buildShopComponents(serverItems),
                },
            ],
        }

        try:
            await ctx.bot.http.request(
                Route(
                    "POST",
                    "/channels/{channel_id}/messages",
                    channel_id=ctx.channel.id,
                ),
                files=files,
                form=self.buildMultipartPayload(payload, files),
            )
        finally:
            for file in files:
                file.close()

    def findShopItems(self):
        with getDbSession() as session:
            serverItemMasterRepository = ServerItemMasterRepository(session)
            return serverItemMasterRepository.findAll()

    def buildShopComponents(self, serverItems):
        components = [
            {
                "type": DiscordComponentType.TEXT_DISPLAY,
                "content": (
                    "# Love Shop\n"
                    "Mua quà và nhẫn để tăng điểm thân mật."
                ),
            },
            {
                "type": DiscordComponentType.SEPARATOR,
            },
        ]

        if not serverItems:
            components.append({
                "type": DiscordComponentType.TEXT_DISPLAY,
                "content": "Hiện chưa có item nào trong love shop.",
            })
            return components

        for index, serverItem in enumerate(serverItems):
            components.extend(self.buildItemComponents(serverItem))

            if index < len(serverItems) - 1:
                components.append({
                    "type": DiscordComponentType.SEPARATOR,
                })

        return components

    def buildItemComponents(self, serverItem):
        imageFileName = self.buildImageFileName(serverItem)

        return [
            {
                "type": DiscordComponentType.TEXT_DISPLAY,
                "content": (
                    f"## {serverItem.name}\n"
                    f"**Giá cowoncy:** **{formatNumber(serverItem.price_cowoncy)}** {COWONCCY}\n"
                    f"**Giá chillcoin:** **{formatNumber(serverItem.price_chill_coin)}** {CHILL_COIN}\n"
                    f"**Điểm thân mật:** **{formatNumber(serverItem.intimacy_points)}** {LOVE}"
                ),
            },
            {
                "type": DiscordComponentType.MEDIA_GALLERY,
                "items": [
                    {
                        "media": {
                            "url": f"attachment://{imageFileName}",
                        },
                        "description": f"Server item {serverItem.name}",
                    },
                ],
            },
            {
                "type": DiscordComponentType.ACTION_ROW,
                "components": [
                    {
                        "type": DiscordComponentType.BUTTON,
                        "style": 3,
                        "label": f"Mua {serverItem.name}",
                        "custom_id": self.buildBuyCustomId(serverItem.id),
                        "disabled": True,
                    },
                ],
            },
        ]

    def buildItemFiles(self, serverItems):
        files = []

        for serverItem in serverItems:
            imagePath = self.findItemImagePath(serverItem)
            files.append(discord.File(
                imagePath,
                filename=self.buildImageFileName(serverItem),
            ))

        return files

    def buildAttachmentPayloads(self, files):
        return [
            file.to_dict(index)
            for index, file in enumerate(files)
        ]

    def buildMultipartPayload(self, payload, files):
        multipart = [
            {
                "name": "payload_json",
                "value": utils._to_json(payload),
            },
        ]

        for index, file in enumerate(files):
            multipart.append({
                "name": f"files[{index}]",
                "value": file.fp,
                "filename": file.filename,
                "content_type": "application/octet-stream",
            })

        return multipart

    def findItemImagePath(self, serverItem):
        imagePath = ASSET_IMAGE_PATHS.get(serverItem.icon_image_key)

        if imagePath is None:
            raise ValueError(f"Server item image path not found: {serverItem.icon_image_key}")

        return imagePath

    def buildImageFileName(self, serverItem):
        return f"{serverItem.icon_image_key}.png"

    def buildBuyCustomId(self, serverItemId: int):
        return f"{self.CUSTOM_ID_PREFIX}:{serverItemId}"
