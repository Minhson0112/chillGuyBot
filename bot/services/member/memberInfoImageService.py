from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

from bot.helper.numberFormatHelper import formatNumber
from bot.helper.timeFormatHelper import formatHoursMinutesSeconds
from bot.services.asset.assetImageService import assetImageService


class MemberInfoImageService:
    FONT_PATH = Path("bot/assets/fonts/arial.ttf")

    AVATAR_BOX = (112, 230, 542, 610)
    AVATAR_RADIUS = 12

    NICKNAME_BOX = (148, 675, 507, 721)
    PARTNER_NAME_BOX = (126, 823, 530, 887)

    VALUE_BOX_LEFT = 1135
    VALUE_BOX_RIGHT = 1518
    VALUE_ROW_CENTERS = [280, 350, 419, 499, 569, 637, 705, 771, 837]

    TEXT_COLOR = (48, 31, 17, 255)
    NICKNAME_COLOR = (218, 154, 76, 255)
    NICKNAME_STROKE_COLOR = (35, 20, 10, 255)

    async def buildMemberInfoImage(self, discordMember, memberInfo):
        image = assetImageService.getImage("memberInfo")
        avatarImage = await self.getMemberAvatarImage(discordMember)

        self.pasteMemberAvatar(image, avatarImage)
        self.drawMemberInfo(image, memberInfo)

        buffer = BytesIO()
        image.save(buffer, format="PNG")
        buffer.seek(0)

        return buffer

    async def getMemberAvatarImage(self, discordMember):
        avatarAsset = discordMember.display_avatar.replace(
            size=512,
            format="png",
            static_format="png",
        )
        avatarBytes = await avatarAsset.read()

        return Image.open(BytesIO(avatarBytes)).convert("RGBA")

    def pasteMemberAvatar(self, image, avatarImage):
        left, top, right, bottom = self.AVATAR_BOX
        avatarSize = (right - left, bottom - top)
        fittedAvatar = ImageOps.fit(
            avatarImage,
            avatarSize,
            method=Image.Resampling.LANCZOS,
        )

        mask = Image.new("L", avatarSize, 0)
        maskDraw = ImageDraw.Draw(mask)
        maskDraw.rounded_rectangle(
            (0, 0, avatarSize[0] - 1, avatarSize[1] - 1),
            radius=self.AVATAR_RADIUS,
            fill=255,
        )

        image.paste(fittedAvatar, (left, top), mask)

    def drawMemberInfo(self, image, memberInfo):
        member = memberInfo["member"]
        draw = ImageDraw.Draw(image)

        dateOfBirth = (
            member.date_of_birth.strftime("%d/%m/%Y")
            if member.date_of_birth
            else "Chưa có"
        )
        joinedAt = (
            member.joined_at.strftime("%d/%m/%Y")
            if member.joined_at
            else "Chưa có"
        )

        values = {
            0: dateOfBirth,
            1: memberInfo["genderLabel"],
            2: joinedAt,
            3: formatNumber(memberInfo["muteCount"]),
            4: formatNumber(member.warning_count),
            5: formatNumber(memberInfo["totalChatCount"]),
            6: formatHoursMinutesSeconds(memberInfo["totalVoiceSeconds"]),
            7: memberInfo["marriageStatus"],
            8: str(memberInfo["farmLevel"]) if memberInfo["farmLevel"] else "Chưa có",
        }

        nicknameFont = self.getFitFont(
            draw,
            memberInfo["nickname"],
            28,
            self.NICKNAME_BOX[2] - self.NICKNAME_BOX[0],
            20,
        )
        self.drawCenteredText(
            draw,
            self.NICKNAME_BOX,
            memberInfo["nickname"],
            nicknameFont,
            self.NICKNAME_COLOR,
            strokeWidth=2,
            strokeFill=self.NICKNAME_STROKE_COLOR,
        )

        partnerNameFont = self.getFitFont(
            draw,
            memberInfo["partnerName"],
            28,
            self.PARTNER_NAME_BOX[2] - self.PARTNER_NAME_BOX[0],
            20,
        )
        self.drawCenteredText(
            draw,
            self.PARTNER_NAME_BOX,
            memberInfo["partnerName"],
            partnerNameFont,
            self.NICKNAME_COLOR,
            strokeWidth=2,
            strokeFill=self.NICKNAME_STROKE_COLOR,
        )

        for rowIndex, value in values.items():
            valueBox = (
                self.VALUE_BOX_LEFT,
                self.VALUE_ROW_CENTERS[rowIndex] - 27,
                self.VALUE_BOX_RIGHT,
                self.VALUE_ROW_CENTERS[rowIndex] + 27,
            )
            valueFont = self.getFitFont(
                draw,
                value,
                32,
                self.VALUE_BOX_RIGHT - self.VALUE_BOX_LEFT,
                22,
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

    def drawCenteredText(
        self,
        draw,
        box,
        text,
        font,
        fill,
        strokeWidth=0,
        strokeFill=None,
    ):
        left, top, right, bottom = box
        textBox = draw.textbbox((0, 0), text, font=font, stroke_width=strokeWidth)
        textWidth = textBox[2] - textBox[0]
        textHeight = textBox[3] - textBox[1]

        x = left + ((right - left) - textWidth) / 2 - textBox[0]
        y = top + ((bottom - top) - textHeight) / 2 - textBox[1]

        draw.text(
            (x, y),
            text,
            font=font,
            fill=fill,
            stroke_width=strokeWidth,
            stroke_fill=strokeFill,
        )
