from io import BytesIO

from PIL import ImageDraw, ImageFont

from bot.helper.timeFormatHelper import formatHoursMinutesSeconds
from bot.services.assetImageService import assetImageService


class MemberVoiceRankingImageService:
    FONT_PATH = "bot/assets/fonts/arial.ttf"

    ROW_CENTER_Y_LIST = [
        525,
        615,
        717,
        800,
        895,
        978,
        1065,
        1163,
        1255,
        1342,
    ]

    NAME_BOX_LEFT = 350
    NAME_BOX_RIGHT = 600

    TIME_BOX_LEFT = 850
    TIME_BOX_RIGHT = 960

    TEXT_COLOR = (255, 221, 130, 255)
    STROKE_COLOR = (58, 31, 10, 255)

    def __init__(self, bot):
        self.bot = bot

    async def buildRankingImage(self, topMembers, guild):
        image = assetImageService.getImage("voiceRankingsScreen")
        draw = ImageDraw.Draw(image)

        for index, member in enumerate(topMembers):
            rowCenterY = self.ROW_CENTER_Y_LIST[index]

            displayName = await self.resolveMemberDisplayName(guild, member.user_id)
            displayName = self.truncateText(displayName, 24)

            voiceTime = formatHoursMinutesSeconds(int(member.voice_seconds))

            nameBox = (
                self.NAME_BOX_LEFT,
                rowCenterY - 45,
                self.NAME_BOX_RIGHT,
                rowCenterY + 45,
            )

            timeBox = (
                self.TIME_BOX_LEFT,
                rowCenterY - 45,
                self.TIME_BOX_RIGHT,
                rowCenterY + 45,
            )

            nameFont = self.getFitFont(
                draw,
                displayName,
                44,
                self.NAME_BOX_RIGHT - self.NAME_BOX_LEFT,
            )

            timeFont = self.getFitFont(
                draw,
                voiceTime,
                40,
                self.TIME_BOX_RIGHT - self.TIME_BOX_LEFT,
            )

            self.drawCenteredText(draw, nameBox, displayName, nameFont)
            self.drawCenteredText(draw, timeBox, voiceTime, timeFont)

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
