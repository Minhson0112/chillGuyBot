from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

from bot.helper.numberFormatHelper import formatNumber
from bot.services.asset.assetImageService import assetImageService


class ServerInfoImageService:
    FONT_PATH = Path("bot/assets/fonts/arial.ttf")

    SERVER_ICON_BOX = (148, 408, 578, 838)
    SERVER_ICON_RADIUS = 18

    SERVER_NAME_BOX = (903, 407, 1215, 468)
    VALUE_BOX_LEFT = 1032
    VALUE_BOX_RIGHT = 1275
    VALUE_ROW_CENTERS = [519, 573, 625, 676, 728, 780, 833, 884]

    TEXT_COLOR = (67, 42, 24, 255)

    async def buildServerInfoImage(self, guild, serverInfo):
        image = assetImageService.getImage("serverInfo")
        serverIconImage = await self.getServerIconImage(guild)

        if serverIconImage is not None:
            self.pasteServerIcon(image, serverIconImage)

        self.drawServerInfo(image, serverInfo)

        buffer = BytesIO()
        image.save(buffer, format="PNG")
        buffer.seek(0)

        return buffer

    async def getServerIconImage(self, guild):
        if guild.icon is None:
            return None

        iconAsset = guild.icon.replace(
            size=512,
            format="png",
            static_format="png",
        )
        iconBytes = await iconAsset.read()

        return Image.open(BytesIO(iconBytes)).convert("RGBA")

    def pasteServerIcon(self, image, serverIconImage):
        left, top, right, bottom = self.SERVER_ICON_BOX
        iconSize = (right - left, bottom - top)
        fittedIcon = ImageOps.fit(
            serverIconImage,
            iconSize,
            method=Image.Resampling.LANCZOS,
        )

        mask = Image.new("L", iconSize, 0)
        maskDraw = ImageDraw.Draw(mask)
        maskDraw.rounded_rectangle(
            (0, 0, iconSize[0] - 1, iconSize[1] - 1),
            radius=self.SERVER_ICON_RADIUS,
            fill=255,
        )

        image.paste(fittedIcon, (left, top), mask)

    def drawServerInfo(self, image, serverInfo):
        draw = ImageDraw.Draw(image)
        createdAt = serverInfo["createdAt"].strftime("%d/%m/%Y")
        values = [
            createdAt,
            formatNumber(serverInfo["memberCount"]),
            formatNumber(serverInfo["maxHistoricalMemberCount"]),
            formatNumber(serverInfo["botCount"]),
            formatNumber(serverInfo["adminCount"]),
            formatNumber(serverInfo["modCount"]),
            formatNumber(serverInfo["staffCount"]),
            formatNumber(serverInfo["boostCount"]),
        ]

        serverNameFont = self.getFitFont(
            draw,
            serverInfo["serverName"],
            34,
            self.SERVER_NAME_BOX[2] - self.SERVER_NAME_BOX[0],
            22,
        )
        self.drawCenteredText(
            draw,
            self.SERVER_NAME_BOX,
            serverInfo["serverName"],
            serverNameFont,
            self.TEXT_COLOR,
        )

        for rowCenter, value in zip(self.VALUE_ROW_CENTERS, values):
            valueBox = (
                self.VALUE_BOX_LEFT,
                rowCenter - 24,
                self.VALUE_BOX_RIGHT,
                rowCenter + 24,
            )
            valueFont = self.getFitFont(
                draw,
                value,
                28,
                self.VALUE_BOX_RIGHT - self.VALUE_BOX_LEFT,
                20,
            )
            self.drawCenteredText(
                draw,
                valueBox,
                value,
                valueFont,
                self.TEXT_COLOR,
            )

    def getFitFont(self, draw, text, fontSize, maxWidth, minFontSize):
        currentFontSize = fontSize

        while currentFontSize >= minFontSize:
            font = ImageFont.truetype(str(self.FONT_PATH), currentFontSize)
            textBox = draw.textbbox((0, 0), text, font=font)

            if textBox[2] - textBox[0] <= maxWidth:
                return font

            currentFontSize -= 2

        return ImageFont.truetype(str(self.FONT_PATH), minFontSize)

    def drawCenteredText(self, draw, box, text, font, fill):
        left, top, right, bottom = box
        textBox = draw.textbbox((0, 0), text, font=font)
        textWidth = textBox[2] - textBox[0]
        textHeight = textBox[3] - textBox[1]

        x = left + ((right - left) - textWidth) / 2 - textBox[0]
        y = top + ((bottom - top) - textHeight) / 2 - textBox[1]

        draw.text((x, y), text, font=font, fill=fill)
