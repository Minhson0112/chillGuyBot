from datetime import datetime
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from bot.config.database import getDbSession
from bot.config.farmLevel import FARM_MAX_LEVEL, FARM_LEVEL_REQUIRED_EXP
from bot.repository.farmRepository import FarmRepository
from bot.services.assetImageService import assetImageService


class FarmRenderService:
    def __init__(self, bot):
        self.bot = bot

    FONT_PATH = Path("bot/assets/fonts/arial.ttf")

    AVATAR_X = 10
    AVATAR_Y = 10
    AVATAR_SIZE = 130

    STATUS_ICON_SIZE = 52
    STATUS_FONT_SIZE = 42

    COIN_ICON_X = 150
    COIN_ICON_Y = 20
    COIN_TEXT_X = 215
    COIN_TEXT_Y = 26

    LEVEL_ICON_X = 150
    LEVEL_ICON_Y = 82
    LEVEL_TEXT_X = 215
    LEVEL_TEXT_Y = 88

    EXP_ICON_X = 430
    EXP_ICON_Y = 28
    EXP_ICON_SIZE = 46

    EXP_BAR_X = 490
    EXP_BAR_Y = 35
    EXP_BAR_WIDTH = 360
    EXP_BAR_HEIGHT = 32

    EXP_TEXT_X = 630
    EXP_TEXT_Y = 37
    EXP_FONT_SIZE = 22

    EXP_BAR_BACKGROUND_FILL = (45, 35, 35, 220)
    EXP_BAR_FILL = (90, 200, 255, 255)
    EXP_BAR_BORDER_FILL = (255, 255, 255, 255)

    LAND_WET_IMAGE_KEY = "farm_land_wet"
    LAND_DRY_IMAGE_KEY = "farm_land_dry"

    LAND_SCALE = 6
    TRAIN_SCALE = 1

    FARM_START_X = 530
    FARM_START_Y = 550

    TRAIN_X = 1430
    TRAIN_Y = 150

    MAX_PLOT_COUNT = 16

    LAND_GRID_POSITIONS = [
        (0, 0), (1, 0), (2, 0), (3, 0),
        (0, 1), (1, 1), (2, 1), (3, 1),
        (0, 2), (1, 2), (2, 2), (3, 2),
        (0, 3), (1, 3), (2, 3), (3, 3),
    ]

    async def renderFarmByMemberId(self, memberId: int):
        with getDbSession() as session:
            farmRepository = FarmRepository(session)
            farm = farmRepository.findByUserIdWithRenderData(memberId)

            if farm is None:
                raise ValueError(f"Farm not found for member id: {memberId}")

            image = self.renderFarmImage(farm)

        avatarImage = await self.getMemberAvatarImage(memberId)

        if avatarImage is not None:
            self.pasteMemberAvatar(image, avatarImage)

        return self.convertImageToBuffer(image)

    def renderFarmImage(self, farm):
        baseImage = assetImageService.getImage(farm.base_image_key)

        cropArea = farm.cropArea

        landImageKey = self.resolveLandImageKey(cropArea)
        landImage = assetImageService.getImage(landImageKey)
        landImage = self.resizeByScale(landImage, self.LAND_SCALE)

        if cropArea is not None:
            unlockedGridPositions = self.getUnlockedGridPositions(cropArea.unlocked_plot_count)

            self.pasteTilesByGrid(
                baseImage,
                landImage,
                unlockedGridPositions,
                startX=self.FARM_START_X,
                startY=self.FARM_START_Y,
            )

            if cropArea.crop_id is not None and cropArea.planted_at is not None:
                cropStage = self.resolveCurrentCropStage(cropArea)

                if cropStage is not None:
                    plantImage = assetImageService.getImage(cropStage.image_key)
                    plantImage = self.resizeByScale(plantImage, cropStage.render_scale)

                    self.pastePlantByGrid(
                        baseImage,
                        plantImage,
                        landImage,
                        unlockedGridPositions,
                        startX=self.FARM_START_X,
                        startY=self.FARM_START_Y,
                        offsetX=0,
                        offsetY=cropStage.render_offset_y,
                    )

        if farm.chickenCoop is not None:
            self.renderChickens(baseImage, farm.chickenCoop)

        if farm.cowShed is not None:
            self.renderCow(baseImage, farm.cowShed)

        if farm.is_train_event:
            trainImage = assetImageService.getImage("train")
            trainImage = self.resizeByScale(trainImage, self.TRAIN_SCALE)
            self.pasteSprite(baseImage, trainImage, x=self.TRAIN_X, y=self.TRAIN_Y)

        self.renderFarmStatusInfo(baseImage, farm)

        return baseImage

    def resolveLandImageKey(self, cropArea):
        if cropArea is not None and cropArea.is_dry:
            return self.LAND_DRY_IMAGE_KEY

        return self.LAND_WET_IMAGE_KEY

    def getUnlockedGridPositions(self, unlockedPlotCount: int):
        if unlockedPlotCount <= 0:
            return []

        plotCount = min(unlockedPlotCount, self.MAX_PLOT_COUNT)

        return self.LAND_GRID_POSITIONS[:plotCount]

    def renderChickens(self, baseImage: Image.Image, chickenCoop):
        if chickenCoop.chicken_count >= 1 and chickenCoop.chicken_1_image_key is not None:
            chickenImage = assetImageService.getImage(chickenCoop.chicken_1_image_key)
            chickenImage = self.resizeByScale(chickenImage, chickenCoop.render_scale)

            self.pasteSprite(
                baseImage,
                chickenImage,
                x=chickenCoop.chicken_1_x,
                y=chickenCoop.chicken_1_y,
            )

        if chickenCoop.chicken_count >= 2 and chickenCoop.chicken_2_image_key is not None:
            chickenImage = assetImageService.getImage(chickenCoop.chicken_2_image_key)
            chickenImage = self.resizeByScale(chickenImage, chickenCoop.render_scale)

            self.pasteSprite(
                baseImage,
                chickenImage,
                x=chickenCoop.chicken_2_x,
                y=chickenCoop.chicken_2_y,
            )

    def renderCow(self, baseImage: Image.Image, cowShed):
        if cowShed.cow_count < 1:
            return

        if cowShed.cow_image_key is None:
            return

        cowImage = assetImageService.getImage(cowShed.cow_image_key)
        cowImage = self.resizeByScale(cowImage, cowShed.render_scale)

        self.pasteSprite(
            baseImage,
            cowImage,
            x=cowShed.cow_x,
            y=cowShed.cow_y,
        )

    def resolveCurrentCropStage(self, cropArea):
        if cropArea.crop is None:
            return None

        cropStages = sorted(
            cropArea.crop.growthStages,
            key=lambda cropStage: cropStage.stage_start_seconds,
        )

        if not cropStages:
            return None

        elapsedSeconds = self.calculateElapsedGrowthSeconds(cropArea)
        currentStage = cropStages[0]

        for cropStage in cropStages:
            if elapsedSeconds >= cropStage.stage_start_seconds:
                currentStage = cropStage
            else:
                break

        return currentStage

    def calculateElapsedGrowthSeconds(self, cropArea):
        now = datetime.now()
        elapsedSeconds = int((now - cropArea.planted_at).total_seconds())

        elapsedSeconds -= cropArea.total_dry_seconds
        elapsedSeconds -= cropArea.total_pest_seconds

        if cropArea.is_dry and cropArea.dryness_started_at is not None:
            elapsedSeconds -= int((now - cropArea.dryness_started_at).total_seconds())

        if cropArea.is_pest_infected and cropArea.pest_started_at is not None:
            elapsedSeconds -= int((now - cropArea.pest_started_at).total_seconds())

        return max(elapsedSeconds, 0)

    def renderFarmStatusInfo(self, baseImage: Image.Image, farm):
        self.renderChillCoinInfo(baseImage, farm)
        self.renderFarmLevelInfo(baseImage, farm)
        self.renderFarmExpInfo(baseImage, farm)

    def renderChillCoinInfo(self, baseImage: Image.Image, farm):
        coinIcon = assetImageService.getImage("currency_chill_coin")
        coinIcon = coinIcon.resize(
            (self.STATUS_ICON_SIZE, self.STATUS_ICON_SIZE),
            Image.LANCZOS,
        )

        self.pasteSprite(
            baseImage,
            coinIcon,
            x=self.COIN_ICON_X,
            y=self.COIN_ICON_Y,
        )

        chillCoin = 0

        if farm.member is not None:
            chillCoin = farm.member.chill_coin

        self.drawStatusText(
            baseImage,
            text=self.formatNumber(chillCoin),
            x=self.COIN_TEXT_X,
            y=self.COIN_TEXT_Y,
        )

    def renderFarmLevelInfo(self, baseImage: Image.Image, farm):
        levelIcon = assetImageService.getImage("level")
        levelIcon = levelIcon.resize(
            (self.STATUS_ICON_SIZE, self.STATUS_ICON_SIZE),
            Image.LANCZOS,
        )

        self.pasteSprite(
            baseImage,
            levelIcon,
            x=self.LEVEL_ICON_X,
            y=self.LEVEL_ICON_Y,
        )

        self.drawStatusText(
            baseImage,
            text=str(farm.farm_level),
            x=self.LEVEL_TEXT_X,
            y=self.LEVEL_TEXT_Y,
        )

    def renderFarmExpInfo(self, baseImage: Image.Image, farm):
        expIcon = assetImageService.getImage("exp")
        expIcon = expIcon.resize(
            (self.EXP_ICON_SIZE, self.EXP_ICON_SIZE),
            Image.LANCZOS,
        )

        self.pasteSprite(
            baseImage,
            expIcon,
            x=self.EXP_ICON_X,
            y=self.EXP_ICON_Y,
        )

        currentExp = max(farm.farm_exp, 0)
        requiredExp = self.getRequiredExpForNextLevel(farm.farm_level)

        if requiredExp is None:
            progressRate = 1
            expText = "MAX"
        else:
            currentExp = min(currentExp, requiredExp)
            progressRate = currentExp / requiredExp
            expText = f"{self.formatNumber(currentExp)}/{self.formatNumber(requiredExp)}"

        self.drawExpBar(baseImage, progressRate)

        self.drawTextWithFontSize(
            baseImage,
            text=expText,
            x=self.EXP_TEXT_X,
            y=self.EXP_TEXT_Y,
            fontSize=self.EXP_FONT_SIZE,
        )

    def drawExpBar(self, baseImage: Image.Image, progressRate: float):
        draw = ImageDraw.Draw(baseImage)

        progressRate = max(0, min(progressRate, 1))
        filledWidth = int(self.EXP_BAR_WIDTH * progressRate)

        barLeft = self.EXP_BAR_X
        barTop = self.EXP_BAR_Y
        barRight = self.EXP_BAR_X + self.EXP_BAR_WIDTH
        barBottom = self.EXP_BAR_Y + self.EXP_BAR_HEIGHT

        draw.rounded_rectangle(
            (barLeft, barTop, barRight, barBottom),
            radius=8,
            fill=self.EXP_BAR_BACKGROUND_FILL,
            outline=self.EXP_BAR_BORDER_FILL,
            width=2,
        )

        if filledWidth > 0:
            draw.rounded_rectangle(
                (
                    barLeft,
                    barTop,
                    barLeft + filledWidth,
                    barBottom,
                ),
                radius=8,
                fill=self.EXP_BAR_FILL,
            )

    def getRequiredExpForNextLevel(self, currentLevel: int):
        if currentLevel >= FARM_MAX_LEVEL:
            return None

        nextLevel = currentLevel + 1

        return FARM_LEVEL_REQUIRED_EXP.get(nextLevel)

    def resizeByScale(self, image: Image.Image, scale: float):
        width = int(image.width * scale)
        height = int(image.height * scale)

        return image.resize((width, height), Image.NEAREST)

    def pasteTilesByGrid(
        self,
        baseImg: Image.Image,
        tileImg: Image.Image,
        gridPositions: list[tuple[int, int]],
        startX: int,
        startY: int,
    ):
        tileW, tileH = tileImg.size

        for gridX, gridY in gridPositions:
            x = startX + gridX * tileW
            y = startY + gridY * tileH
            baseImg.paste(tileImg, (x, y), tileImg)

    def pastePlantByGrid(
        self,
        baseImg: Image.Image,
        plantImg: Image.Image,
        landImg: Image.Image,
        gridPositions: list[tuple[int, int]],
        startX: int,
        startY: int,
        offsetX: int = 0,
        offsetY: int = 0,
    ):
        tileW, tileH = landImg.size
        plantW, plantH = plantImg.size

        for gridX, gridY in gridPositions:
            landX = startX + gridX * tileW
            landY = startY + gridY * tileH

            x = landX + (tileW - plantW) // 2 + offsetX
            y = landY + (tileH - plantH) // 2 + offsetY

            baseImg.paste(plantImg, (x, y), plantImg)

    def pasteSprite(
        self,
        baseImg: Image.Image,
        spriteImg: Image.Image,
        x: int,
        y: int,
    ):
        if x is None or y is None:
            return

        baseImg.paste(spriteImg, (x, y), spriteImg)

    async def getMemberAvatarImage(self, memberId: int):
        user = self.bot.get_user(memberId)

        if user is None:
            user = await self.bot.fetch_user(memberId)

        avatarAsset = user.display_avatar.replace(size=256, static_format="png")
        avatarBytes = await avatarAsset.read()

        return Image.open(BytesIO(avatarBytes)).convert("RGBA")

    def pasteMemberAvatar(self, baseImage: Image.Image, avatarImage: Image.Image):
        avatarImage = avatarImage.resize((self.AVATAR_SIZE, self.AVATAR_SIZE), Image.LANCZOS)

        baseImage.paste(
            avatarImage,
            (self.AVATAR_X, self.AVATAR_Y),
            avatarImage,
        )

    def drawStatusText(
        self,
        baseImage: Image.Image,
        text: str,
        x: int,
        y: int,
    ):
        self.drawTextWithFontSize(
            baseImage,
            text=text,
            x=x,
            y=y,
            fontSize=self.STATUS_FONT_SIZE,
            strokeWidth=3,
        )

    def drawTextWithFontSize(
        self,
        baseImage: Image.Image,
        text: str,
        x: int,
        y: int,
        fontSize: int,
        strokeWidth: int = 2,
    ):
        draw = ImageDraw.Draw(baseImage)
        font = ImageFont.truetype(str(self.FONT_PATH), fontSize)

        draw.text(
            (x, y),
            text,
            font=font,
            fill=(255, 255, 255, 255),
            stroke_width=strokeWidth,
            stroke_fill=(0, 0, 0, 255),
        )

    def formatNumber(self, number: int):
        return f"{number:,}"

    def convertImageToBuffer(self, image: Image.Image):
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        buffer.seek(0)

        return buffer