from datetime import datetime
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from bot.config.database import getDbSession
from bot.repository.fishingHistoryRepository import FishingHistoryRepository
from bot.services.assetImageService import assetImageService


class FarmFishingRankingRenderService:
    BACKGROUND_KEY = "fishingRankingsScreen"

    FONT_PATH = Path("bot/assets/fonts/arial.ttf")

    NAME_FONT_SIZE = 34
    FISH_FONT_SIZE = 32
    WEIGHT_FONT_SIZE = 36

    TEXT_FILL = (255, 220, 120, 255)
    STROKE_FILL = (55, 25, 5, 255)

    FISH_ICON_SIZE = 52

    ROW_Y_LIST = [
        500,
        600,
        695,
        795,
        890,
        980,
        1072,
        1163,
        1257,
        1347,
    ]

    NAME_X = 260
    NAME_MAX_WIDTH = 460

    FISH_ICON_X = 590
    FISH_TEXT_X = 655
    FISH_MAX_WIDTH = 260

    WEIGHT_RIGHT_X = 970
    WEIGHT_MAX_WIDTH = 220

    def __init__(self, bot):
        self.bot = bot

    async def renderTopFishingByMonthToBuffer(
        self,
        guild,
        year: int,
        month: int,
    ):
        with getDbSession() as session:
            fishingHistoryRepository = FishingHistoryRepository(session)
            rankings = fishingHistoryRepository.findTop10ByMonth(
                year=year,
                month=month,
            )

            rankingRows = []

            for fishingHistory in rankings:
                memberDisplayName = await self.resolveMemberDisplayName(
                    guild=guild,
                    userId=fishingHistory.user_id,
                )

                rankingRows.append({
                    "memberDisplayName": memberDisplayName,
                    "item": fishingHistory.item,
                    "weightKg": fishingHistory.weight_kg,
                })

            image = self.renderRankingImage(rankingRows)

        return {
            "buffer": self.convertImageToBuffer(image),
            "rankingCount": len(rankingRows),
            "year": year,
            "month": month,
        }

    def renderRankingImage(self, rankingRows):
        baseImage = assetImageService.getImage(self.BACKGROUND_KEY).copy()

        for index, rankingRow in enumerate(rankingRows):
            if index >= len(self.ROW_Y_LIST):
                break

            self.renderRankingRow(
                baseImage=baseImage,
                rankingRow=rankingRow,
                rowIndex=index,
            )

        return baseImage

    def renderRankingRow(
        self,
        baseImage: Image.Image,
        rankingRow,
        rowIndex: int,
    ):
        y = self.ROW_Y_LIST[rowIndex]

        self.renderMemberName(
            baseImage=baseImage,
            memberDisplayName=rankingRow["memberDisplayName"],
            y=y,
        )

        self.renderFishInfo(
            baseImage=baseImage,
            item=rankingRow["item"],
            y=y,
        )

        self.renderWeight(
            baseImage=baseImage,
            weightKg=rankingRow["weightKg"],
            y=y,
        )

    def renderMemberName(
        self,
        baseImage: Image.Image,
        memberDisplayName: str,
        y: int,
    ):
        self.drawFitText(
            baseImage=baseImage,
            text=memberDisplayName,
            x=self.NAME_X,
            y=y,
            maxWidth=self.NAME_MAX_WIDTH,
            fontSize=self.NAME_FONT_SIZE,
        )

    def renderFishInfo(
        self,
        baseImage: Image.Image,
        item,
        y: int,
    ):
        if item is None:
            return

        fishIcon = assetImageService.getImage(item.icon_image_key)
        fishIcon = fishIcon.resize(
            (self.FISH_ICON_SIZE, self.FISH_ICON_SIZE),
            Image.NEAREST,
        )

        iconY = y - 10

        self.pasteSprite(
            baseImage,
            fishIcon,
            self.FISH_ICON_X,
            iconY,
        )

        self.drawFitText(
            baseImage=baseImage,
            text=item.name,
            x=self.FISH_TEXT_X,
            y=y,
            maxWidth=self.FISH_MAX_WIDTH,
            fontSize=self.FISH_FONT_SIZE,
        )

    def renderWeight(
        self,
        baseImage: Image.Image,
        weightKg,
        y: int,
    ):
        weightText = self.formatWeight(weightKg)

        self.drawRightFitText(
            baseImage=baseImage,
            text=weightText,
            rightX=self.WEIGHT_RIGHT_X,
            y=y,
            maxWidth=self.WEIGHT_MAX_WIDTH,
            fontSize=self.WEIGHT_FONT_SIZE,
        )

    async def resolveMemberDisplayName(
        self,
        guild,
        userId: int,
    ):
        if guild is not None:
            guildMember = guild.get_member(userId)

            if guildMember is not None:
                return guildMember.display_name

        user = self.bot.get_user(userId)

        if user is None:
            try:
                user = await self.bot.fetch_user(userId)
            except Exception:
                user = None

        if user is not None:
            return user.display_name

        return str(userId)

    def drawFitText(
        self,
        baseImage: Image.Image,
        text: str,
        x: int,
        y: int,
        maxWidth: int,
        fontSize: int,
    ):
        draw = ImageDraw.Draw(baseImage)
        font = self.getFitFont(draw, text, maxWidth, fontSize)

        draw.text(
            (x, y),
            text,
            font=font,
            fill=self.TEXT_FILL,
            stroke_width=2,
            stroke_fill=self.STROKE_FILL,
        )

    def drawRightFitText(
        self,
        baseImage: Image.Image,
        text: str,
        rightX: int,
        y: int,
        maxWidth: int,
        fontSize: int,
    ):
        draw = ImageDraw.Draw(baseImage)
        font = self.getFitFont(draw, text, maxWidth, fontSize)

        textWidth = self.getTextWidth(draw, text, font)
        x = rightX - textWidth

        draw.text(
            (x, y),
            text,
            font=font,
            fill=self.TEXT_FILL,
            stroke_width=2,
            stroke_fill=self.STROKE_FILL,
        )

    def getFitFont(
        self,
        draw: ImageDraw.ImageDraw,
        text: str,
        maxWidth: int,
        fontSize: int,
    ):
        currentFontSize = fontSize

        while currentFontSize >= 18:
            font = ImageFont.truetype(str(self.FONT_PATH), currentFontSize)
            textWidth = self.getTextWidth(draw, text, font)

            if textWidth <= maxWidth:
                return font

            currentFontSize -= 1

        return ImageFont.truetype(str(self.FONT_PATH), 18)

    def getTextWidth(
        self,
        draw: ImageDraw.ImageDraw,
        text: str,
        font: ImageFont.FreeTypeFont,
    ):
        bbox = draw.textbbox((0, 0), text, font=font)

        return bbox[2] - bbox[0]

    def pasteSprite(
        self,
        baseImg: Image.Image,
        spriteImg: Image.Image,
        x: int,
        y: int,
    ):
        baseImg.paste(spriteImg, (x, y), spriteImg)

    def formatWeight(self, weightKg):
        return f"{float(weightKg):.2f}"

    def convertImageToBuffer(self, image: Image.Image):
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        buffer.seek(0)

        return buffer