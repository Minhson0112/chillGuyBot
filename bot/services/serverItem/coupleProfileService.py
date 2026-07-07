from datetime import datetime
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

from bot.config.database import getDbSession
from bot.config.imagePaths import ASSET_IMAGE_PATHS
from bot.helper.numberFormatHelper import formatNumber
from bot.helper.timeFormatHelper import formatHoursMinutesSeconds
from bot.repository.coupleDailyVoiceActivityRepository import CoupleDailyVoiceActivityRepository
from bot.repository.coupleRepository import CoupleRepository
from bot.repository.serverItemGiftHistoryRepository import ServerItemGiftHistoryRepository
from bot.services.asset.assetImageService import assetImageService


class CoupleProfileService:
    FONT_PATH = Path("bot/assets/fonts/arial.ttf")

    USER_1_AVATAR_BOX = (307, 148, 694, 525)
    USER_2_AVATAR_BOX = (1080, 148, 1467, 525)
    AVATAR_RADIUS = 12

    USER_1_NAME_BOX = (370, 560, 680, 616)
    USER_2_NAME_BOX = (1144, 560, 1454, 616)

    RING_BOX = (820, 285, 954, 419)

    INTIMACY_VALUE_BOX = (214, 750, 437, 792)
    TOGETHER_DAYS_VALUE_BOX = (616, 749, 855, 792)
    GIFT_COUNT_VALUE_BOX = (1028, 749, 1251, 792)
    VOICE_TIME_VALUE_BOX = (1438, 749, 1679, 792)

    TEXT_COLOR = (255, 247, 232, 255)
    TEXT_STROKE_COLOR = (80, 35, 55, 255)
    NAME_COLOR = (255, 244, 224, 255)

    def getCoupleProfile(self, userId: int):
        with getDbSession() as session:
            coupleRepository = CoupleRepository(session)
            giftHistoryRepository = ServerItemGiftHistoryRepository(session)
            voiceActivityRepository = CoupleDailyVoiceActivityRepository(session)

            couple = coupleRepository.findActiveByUserId(userId)

            if couple is None:
                return {
                    "success": False,
                    "message": "Bạn hiện không có mối quan hệ nào.",
                }

            giftHistoryCount = giftHistoryRepository.countGiftHistoriesBetweenUsers(
                user1Id=couple.user_1_id,
                user2Id=couple.user_2_id,
            )
            totalVoiceSeconds = voiceActivityRepository.getTotalVoiceSecondsByCoupleId(couple.id)
            ringImageKey = couple.ringItem.icon_image_key if couple.ringItem is not None else None

            return {
                "success": True,
                "couple": {
                    "id": couple.id,
                    "user1Id": couple.user_1_id,
                    "user2Id": couple.user_2_id,
                    "intimacyPoints": couple.intimacy_points,
                    "createdAt": couple.created_at,
                    "ringImageKey": ringImageKey,
                    "giftHistoryCount": giftHistoryCount,
                    "totalVoiceSeconds": totalVoiceSeconds,
                },
            }

    async def buildCoupleProfileImage(
        self,
        user1,
        user2,
        coupleProfile,
    ):
        image = self.getBaseImage()
        user1AvatarImage = await self.getUserAvatarImage(user1)
        user2AvatarImage = await self.getUserAvatarImage(user2)

        self.pasteAvatar(image, user1AvatarImage, self.USER_1_AVATAR_BOX)
        self.pasteAvatar(image, user2AvatarImage, self.USER_2_AVATAR_BOX)
        self.pasteRingImage(image, coupleProfile.get("ringImageKey"))
        self.drawCoupleInfo(image, user1, user2, coupleProfile)

        buffer = BytesIO()
        image.save(buffer, format="PNG")
        buffer.seek(0)

        return buffer

    async def getUserAvatarImage(self, user):
        avatarAsset = user.display_avatar.replace(
            size=512,
            format="png",
            static_format="png",
        )
        avatarBytes = await avatarAsset.read()

        return Image.open(BytesIO(avatarBytes)).convert("RGBA")

    def getBaseImage(self):
        if assetImageService.hasImage("couple_banner"):
            return assetImageService.getImage("couple_banner")

        return Image.open(ASSET_IMAGE_PATHS["couple_banner"]).convert("RGBA")

    def pasteAvatar(self, image, avatarImage, avatarBox):
        left, top, right, bottom = avatarBox
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

    def pasteRingImage(self, image, ringImageKey):
        if ringImageKey is None:
            return

        ringImage = self.getAssetImage(ringImageKey)

        if ringImage is None:
            return

        left, top, right, bottom = self.RING_BOX
        ringSize = (right - left, bottom - top)
        ringImage.thumbnail(ringSize, Image.Resampling.LANCZOS)
        pasteX = left + (ringSize[0] - ringImage.width) // 2
        pasteY = top + (ringSize[1] - ringImage.height) // 2

        image.paste(ringImage, (pasteX, pasteY), ringImage)

    def getAssetImage(self, imageKey: str):
        if assetImageService.hasImage(imageKey):
            return assetImageService.getImage(imageKey)

        imagePath = ASSET_IMAGE_PATHS.get(imageKey)

        if imagePath is None:
            return None

        path = Path(imagePath)

        if not path.exists():
            return None

        return Image.open(path).convert("RGBA")

    def drawCoupleInfo(self, image, user1, user2, coupleProfile):
        draw = ImageDraw.Draw(image)
        nameFont = self.getFitFont(draw, user1.display_name, 34, 300, 22)
        self.drawCenteredText(
            draw,
            self.USER_1_NAME_BOX,
            user1.display_name,
            nameFont,
            self.NAME_COLOR,
            strokeWidth=2,
            strokeFill=self.TEXT_STROKE_COLOR,
        )

        nameFont = self.getFitFont(draw, user2.display_name, 34, 300, 22)
        self.drawCenteredText(
            draw,
            self.USER_2_NAME_BOX,
            user2.display_name,
            nameFont,
            self.NAME_COLOR,
            strokeWidth=2,
            strokeFill=self.TEXT_STROKE_COLOR,
        )

        togetherDays = self.getTogetherDays(coupleProfile.get("createdAt"))
        values = [
            (self.INTIMACY_VALUE_BOX, formatNumber(coupleProfile.get("intimacyPoints"))),
            (self.TOGETHER_DAYS_VALUE_BOX, f"{formatNumber(togetherDays)} ngày"),
            (self.GIFT_COUNT_VALUE_BOX, formatNumber(coupleProfile.get("giftHistoryCount"))),
            (
                self.VOICE_TIME_VALUE_BOX,
                formatHoursMinutesSeconds(int(coupleProfile.get("totalVoiceSeconds") or 0)),
            ),
        ]

        for box, value in values:
            valueFont = self.getFitFont(draw, value, 30, box[2] - box[0], 20)
            self.drawCenteredText(
                draw,
                box,
                value,
                valueFont,
                self.TEXT_COLOR,
                strokeWidth=2,
                strokeFill=self.TEXT_STROKE_COLOR,
            )

    def getTogetherDays(self, createdAt):
        if createdAt is None:
            return 0

        return max((datetime.now() - createdAt).days, 0)

    def getFitFont(self, draw, text, fontSize, maxWidth, minFontSize):
        currentFontSize = fontSize

        while currentFontSize >= minFontSize:
            font = ImageFont.truetype(str(self.FONT_PATH), currentFontSize)
            textBox = draw.textbbox((0, 0), str(text), font=font)

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
        textBox = draw.textbbox((0, 0), str(text), font=font, stroke_width=strokeWidth)
        textWidth = textBox[2] - textBox[0]
        textHeight = textBox[3] - textBox[1]

        x = left + ((right - left) - textWidth) / 2 - textBox[0]
        y = top + ((bottom - top) - textHeight) / 2 - textBox[1]

        draw.text(
            (x, y),
            str(text),
            font=font,
            fill=fill,
            stroke_width=strokeWidth,
            stroke_fill=strokeFill,
        )
