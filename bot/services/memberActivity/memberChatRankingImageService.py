from io import BytesIO

from PIL import ImageDraw, ImageFont

from bot.services.assetImageService import assetImageService


class MemberChatRankingImageService:
    FONT_PATH = "bot/assets/fonts/arial.ttf"

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

    NAME_BOX_LEFT = 360
    NAME_BOX_RIGHT = 1050

    COUNT_BOX_LEFT = 1190
    COUNT_BOX_RIGHT = 1500

    TEXT_COLOR = (255, 221, 130, 255)
    STROKE_COLOR = (58, 31, 10, 255)

    def __init__(self, bot):
        self.bot = bot

    async def buildRankingImage(self, topMembers, guild):
        image = assetImageService.getImage("chatRankingsScreen")
        draw = ImageDraw.Draw(image)

        for index, member in enumerate(topMembers):
            rowCenterY = self.ROW_CENTER_Y_LIST[index]

            displayName = await self.resolveMemberDisplayName(guild, member.user_id)
            displayName = self.truncateText(displayName, 24)

            chatCount = self.formatNumber(member.level_chat_count)

            nameBox = (
                self.NAME_BOX_LEFT,
                rowCenterY - 45,
                self.NAME_BOX_RIGHT,
                rowCenterY + 45,
            )

            countBox = (
                self.COUNT_BOX_LEFT,
                rowCenterY - 45,
                self.COUNT_BOX_RIGHT,
                rowCenterY + 45,
            )

            nameFont = self.getFitFont(
                draw,
                displayName,
                44,
                self.NAME_BOX_RIGHT - self.NAME_BOX_LEFT,
            )

            countFont = self.getFitFont(
                draw,
                chatCount,
                44,
                self.COUNT_BOX_RIGHT - self.COUNT_BOX_LEFT,
            )

            self.drawCenteredText(draw, nameBox, displayName, nameFont)
            self.drawCenteredText(draw, countBox, chatCount, countFont)

        buffer = BytesIO()
        image.save(buffer, format="PNG")
        buffer.seek(0)

        return buffer

    async def resolveMemberDisplayName(self, guild, userId: int):
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

    def truncateText(self, text, maxLength):
        if len(text) > maxLength:
            return f"{text[:maxLength - 3]}..."

        return text

    def formatNumber(self, value):
        return f"{int(value):,}".replace(",", ".")

    def getFont(self, fontSize):
        try:
            return ImageFont.truetype(self.FONT_PATH, fontSize)
        except OSError:
            return ImageFont.load_default()

    def getFitFont(self, draw, text, fontSize, maxWidth):
        currentFontSize = fontSize

        while currentFontSize >= 26:
            font = self.getFont(currentFontSize)
            bbox = draw.textbbox((0, 0), text, font=font)
            textWidth = bbox[2] - bbox[0]

            if textWidth <= maxWidth:
                return font

            currentFontSize -= 2

        return self.getFont(26)

    def drawCenteredText(self, draw, box, text, font):
        left, top, right, bottom = box

        bbox = draw.textbbox((0, 0), text, font=font)
        textWidth = bbox[2] - bbox[0]
        textHeight = bbox[3] - bbox[1]

        x = left + ((right - left) - textWidth) / 2
        y = top + ((bottom - top) - textHeight) / 2 - 4

        draw.text(
            (x, y),
            text,
            font=font,
            fill=self.TEXT_COLOR,
            stroke_width=3,
            stroke_fill=self.STROKE_COLOR,
        )