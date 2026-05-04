from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from bot.config.database import getDbSession
from bot.repository.farmTrainEventHistoryRepository import FarmTrainEventHistoryRepository
from bot.services.assetImageService import assetImageService


class FarmTrainRankingRenderService:
    BACKGROUND_KEY = "trainRankingsScreen"

    FONT_PATH = Path("bot/assets/fonts/arial.ttf")

    NAME_FONT_SIZE = 34
    COUNT_FONT_SIZE = 38
    MIN_FONT_SIZE = 20

    TEXT_FILL = (255, 220, 120, 255)
    STROKE_FILL = (55, 25, 5, 255)

    ROW_CENTER_Y_LIST = [
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

    NAME_X = 225
    NAME_MAX_WIDTH = 120

    COUNT_RIGHT_X = 835
    COUNT_MAX_WIDTH = 120

    def __init__(self, bot):
        self.bot = bot

    async def renderTopTrainByMonthToBuffer(
        self,
        guild,
        year: int,
        month: int,
    ):
        with getDbSession() as session:
            farmTrainEventHistoryRepository = FarmTrainEventHistoryRepository(session)

            rankings = farmTrainEventHistoryRepository.findTop10CompletedByMonth(
                year=year,
                month=month,
            )

            rankingRows = []

            for ranking in rankings:
                userId = ranking.user_id
                completedCount = ranking.completed_count

                rankingRows.append({
                    "userId": userId,
                    "completedCount": completedCount,
                })

        for rankingRow in rankingRows:
            rankingRow["memberDisplayName"] = await self.resolveMemberDisplayName(
                guild=guild,
                userId=rankingRow["userId"],
            )

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
            if index >= len(self.ROW_CENTER_Y_LIST):
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
        centerY = self.ROW_CENTER_Y_LIST[rowIndex]

        self.renderMemberName(
            baseImage=baseImage,
            memberDisplayName=rankingRow["memberDisplayName"],
            centerY=centerY,
        )

        self.renderCompletedCount(
            baseImage=baseImage,
            completedCount=rankingRow["completedCount"],
            centerY=centerY,
        )

    def renderMemberName(
        self,
        baseImage: Image.Image,
        memberDisplayName: str,
        centerY: int,
    ):
        self.drawEllipsisTextCenterY(
            baseImage=baseImage,
            text=memberDisplayName,
            x=self.NAME_X,
            centerY=centerY,
            maxWidth=self.NAME_MAX_WIDTH,
            fontSize=self.NAME_FONT_SIZE,
        )

    def renderCompletedCount(
        self,
        baseImage: Image.Image,
        completedCount: int,
        centerY: int,
    ):
        self.drawRightFitTextCenterY(
            baseImage=baseImage,
            text=self.formatNumber(completedCount),
            rightX=self.COUNT_RIGHT_X,
            centerY=centerY,
            maxWidth=self.COUNT_MAX_WIDTH,
            fontSize=self.COUNT_FONT_SIZE,
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

    def drawEllipsisTextCenterY(
        self,
        baseImage: Image.Image,
        text: str,
        x: int,
        centerY: int,
        maxWidth: int,
        fontSize: int,
    ):
        draw = ImageDraw.Draw(baseImage)
        font = ImageFont.truetype(str(self.FONT_PATH), fontSize)

        displayText = self.truncateTextToFit(
            draw=draw,
            text=text,
            maxWidth=maxWidth,
            font=font,
        )

        textHeight = self.getTextHeight(draw, displayText, font)
        y = centerY - textHeight // 2 - 2

        draw.text(
            (x, y),
            displayText,
            font=font,
            fill=self.TEXT_FILL,
            stroke_width=2,
            stroke_fill=self.STROKE_FILL,
        )

    def truncateTextToFit(
        self,
        draw: ImageDraw.ImageDraw,
        text: str,
        maxWidth: int,
        font: ImageFont.FreeTypeFont,
    ):
        if text is None:
            return ""

        if self.getTextWidth(draw, text, font) <= maxWidth:
            return text

        ellipsis = "..."
        ellipsisWidth = self.getTextWidth(draw, ellipsis, font)

        if ellipsisWidth >= maxWidth:
            return ellipsis

        result = ""

        for char in text:
            nextText = result + char

            if self.getTextWidth(draw, nextText, font) + ellipsisWidth > maxWidth:
                break

            result = nextText

        return result + ellipsis

    def drawRightFitTextCenterY(
        self,
        baseImage: Image.Image,
        text: str,
        rightX: int,
        centerY: int,
        maxWidth: int,
        fontSize: int,
    ):
        draw = ImageDraw.Draw(baseImage)
        font = self.getFitFont(draw, text, maxWidth, fontSize)

        textWidth = self.getTextWidth(draw, text, font)
        textHeight = self.getTextHeight(draw, text, font)

        x = rightX - textWidth
        y = centerY - textHeight // 2 - 2

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

        while currentFontSize >= self.MIN_FONT_SIZE:
            font = ImageFont.truetype(str(self.FONT_PATH), currentFontSize)
            textWidth = self.getTextWidth(draw, text, font)

            if textWidth <= maxWidth:
                return font

            currentFontSize -= 1

        return ImageFont.truetype(str(self.FONT_PATH), self.MIN_FONT_SIZE)

    def getTextWidth(
        self,
        draw: ImageDraw.ImageDraw,
        text: str,
        font: ImageFont.FreeTypeFont,
    ):
        bbox = draw.textbbox((0, 0), text, font=font)

        return bbox[2] - bbox[0]

    def getTextHeight(
        self,
        draw: ImageDraw.ImageDraw,
        text: str,
        font: ImageFont.FreeTypeFont,
    ):
        bbox = draw.textbbox((0, 0), text, font=font)

        return bbox[3] - bbox[1]

    def formatNumber(self, number: int):
        return f"{number:,}"

    def convertImageToBuffer(self, image: Image.Image):
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        buffer.seek(0)

        return buffer