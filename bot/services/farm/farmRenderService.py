from datetime import datetime
from io import BytesIO

from PIL import Image
from urllib.request import urlopen

from bot.config.database import getDbSession
from bot.repository.farmRepository import FarmRepository
from bot.services.assetImageService import assetImageService


class FarmRenderService:
    def __init__(self, bot):
        self.bot = bot
    
    AVATAR_X = 40
    AVATAR_Y = 40
    AVATAR_SIZE = 96
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
        avatarUrl = str(avatarAsset.url)

        with urlopen(avatarUrl) as response:
            avatarBytes = response.read()

        return Image.open(BytesIO(avatarBytes)).convert("RGBA")
    
    def pasteMemberAvatar(self, baseImage: Image.Image, avatarImage: Image.Image):
        avatarImage = avatarImage.resize((self.AVATAR_SIZE, self.AVATAR_SIZE), Image.LANCZOS)

        baseImage.paste(
            avatarImage,
            (self.AVATAR_X, self.AVATAR_Y),
            avatarImage,
        )

    def convertImageToBuffer(self, image: Image.Image):
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        buffer.seek(0)

        return buffer