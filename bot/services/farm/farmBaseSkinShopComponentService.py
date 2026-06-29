from discord.http import Route

from bot.config.database import getDbSession
from bot.config.emoji import FARM_GAME_EMOJI
from bot.config.imagePaths import ASSET_IMAGE_URLS
from bot.enums.discordComponentType import DiscordComponentType
from bot.helper.numberFormatHelper import formatNumber
from bot.repository.baseSkinMasterRepository import BaseSkinMasterRepository


class FarmBaseSkinShopComponentService:
    COMPONENTS_V2_FLAG = 1 << 15
    CUSTOM_ID_PREFIX = "farm_skin_buy"
    DEFAULT_BASE_SKIN_CODE = "base"
    CONTAINER_ACCENT_COLOR = 0x57A7FF

    def __init__(self, bot):
        self.bot = bot

    async def sendShopMessage(self, ctx):
        baseSkins = self.findShopBaseSkins()
        payload = {
            "flags": self.COMPONENTS_V2_FLAG,
            "allowed_mentions": {
                "parse": [],
            },
            "components": [
                {
                    "type": DiscordComponentType.CONTAINER,
                    "accent_color": self.CONTAINER_ACCENT_COLOR,
                    "components": self.buildShopComponents(baseSkins),
                },
            ],
        }

        await ctx.bot.http.request(
            Route(
                "POST",
                "/channels/{channel_id}/messages",
                channel_id=ctx.channel.id,
            ),
            json=payload,
        )

    def findShopBaseSkins(self):
        with getDbSession() as session:
            baseSkinMasterRepository = BaseSkinMasterRepository(session)
            baseSkins = baseSkinMasterRepository.findAll()

            return [
                baseSkin
                for baseSkin in baseSkins
                if baseSkin.code != self.DEFAULT_BASE_SKIN_CODE
            ]

    def buildShopComponents(self, baseSkins):
        components = [
            {
                "type": DiscordComponentType.TEXT_DISPLAY,
                "content": (
                    "# Shop Base Skin\n"
                    "Thay đổi diện mạo nông trại bằng những base skin đặc biệt."
                ),
            },
            {
                "type": DiscordComponentType.SEPARATOR,
            },
        ]

        if not baseSkins:
            components.append({
                "type": DiscordComponentType.TEXT_DISPLAY,
                "content": "Hiện chưa có base skin nào trong shop.",
            })
            return components

        for index, baseSkin in enumerate(baseSkins):
            components.extend(self.buildBaseSkinComponents(baseSkin))

            if index < len(baseSkins) - 1:
                components.append({
                    "type": DiscordComponentType.SEPARATOR,
                })

        components.extend([
            {
                "type": DiscordComponentType.SEPARATOR,
            },
            {
                "type": DiscordComponentType.TEXT_DISPLAY,
                "content": "-# Bạn cũng có thể dùng `cg buyskin <id>` để mua skin.",
            },
        ])

        return components

    def buildBaseSkinComponents(self, baseSkin):
        imageUrl = ASSET_IMAGE_URLS.get(baseSkin.base_image_key)

        if imageUrl is None:
            raise ValueError(
                f"Base skin image URL not found: {baseSkin.base_image_key}",
            )

        chillCoinEmoji = FARM_GAME_EMOJI["chill_coin"]
        saleStatus = "Đang mở bán" if baseSkin.is_active else "Chưa mở bán"
        buttonStyle = 3 if baseSkin.is_active else 2
        buttonLabel = f"Mua {baseSkin.name}" if baseSkin.is_active else "Chưa mở bán"

        return [
            {
                "type": DiscordComponentType.TEXT_DISPLAY,
                "content": (
                    f"## {baseSkin.name}\n"
                    f"**ID:** `{baseSkin.id}`\n"
                    f"**Giá:** **{formatNumber(baseSkin.buy_price)}** {chillCoinEmoji}\n"
                    f"**Farm level yêu cầu:** **{baseSkin.required_farm_level}**\n"
                    f"**Trạng thái:** **{saleStatus}**"
                ),
            },
            {
                "type": DiscordComponentType.MEDIA_GALLERY,
                "items": [
                    {
                        "media": {
                            "url": imageUrl,
                        },
                        "description": f"Base skin {baseSkin.name}",
                    },
                ],
            },
            {
                "type": DiscordComponentType.ACTION_ROW,
                "components": [
                    {
                        "type": DiscordComponentType.BUTTON,
                        "style": buttonStyle,
                        "label": buttonLabel,
                        "custom_id": self.buildBuyCustomId(baseSkin.id),
                        "disabled": not baseSkin.is_active,
                    },
                ],
            },
        ]

    def buildBuyCustomId(self, baseSkinId: int):
        return f"{self.CUSTOM_ID_PREFIX}:{baseSkinId}"
