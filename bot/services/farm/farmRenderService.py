from datetime import datetime, timedelta
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from bot.config.database import getDbSession
from bot.config.emoji import FARM_GAME_EMOJI
from bot.config.farmLevel import FARM_MAX_LEVEL, FARM_LEVEL_REQUIRED_EXP
from bot.repository.farmRepository import FarmRepository
from bot.repository.farmTrainEventRepository import FarmTrainEventRepository
from bot.enums.toolStatus import ToolStatus
from bot.enums.toolType import ToolType
from bot.repository.farmToolEquipmentRepository import FarmToolEquipmentRepository
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

    EXP_ICON_X = 530
    EXP_ICON_Y = 13
    EXP_ICON_SIZE = 46

    EXP_BAR_X = 590
    EXP_BAR_Y = 20
    EXP_BAR_WIDTH = 360
    EXP_BAR_HEIGHT = 32

    EXP_TEXT_X = 730
    EXP_TEXT_Y = 25
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

    CHICKEN_HUNGRY_INTERVAL_MINUTES = 30
    EGG_COLLECT_INTERVAL_MINUTES = 10

    COW_HUNGRY_INTERVAL_MINUTES = 30
    MILK_COLLECT_INTERVAL_MINUTES = 15

    LAND_GRID_POSITIONS = [
        (0, 0), (1, 0), (2, 0), (3, 0),
        (0, 1), (1, 1), (2, 1), (3, 1),
        (0, 2), (1, 2), (2, 2), (3, 2),
        (0, 3), (1, 3), (2, 3), (3, 3),
    ]

    HOT_BAR_IMAGE_KEY = "hot_bar"

    HOT_BAR_X = 620
    HOT_BAR_Y = 940
    HOT_BAR_SCALE_DIVISOR = 3

    HOT_BAR_SLOT_COUNT = 4
    HOT_BAR_INNER_WIDTH_RATE = 0.95

    HOT_BAR_TOOL_WIDTH_RATE = 0.50
    HOT_BAR_TOOL_HEIGHT_RATE = 0.40
    HOT_BAR_TOOL_Y_RATE = 0.35

    TOOL_DURABILITY_BAR_HEIGHT = 5
    TOOL_DURABILITY_BAR_OFFSET_Y = 4
    TOOL_DURABILITY_BAR_WIDTH_RATE = 0.85

    TOOL_DURABILITY_BAR_BACKGROUND_FILL = (60, 45, 35, 220)
    TOOL_DURABILITY_BAR_FILL = (80, 220, 90, 240)
    TOOL_DURABILITY_BAR_BORDER_FILL = (255, 255, 255, 180)

    HOT_BAR_TOOL_ORDER = [
        ToolType.FISHING_ROD.value,
        ToolType.SICKLE.value,
        ToolType.WATERING_CAN.value,
        ToolType.MILK_PAIL.value,
    ]

    async def renderFarmByMemberId(self, memberId: int):
        with getDbSession() as session:
            farmRepository = FarmRepository(session)
            farmTrainEventRepository = FarmTrainEventRepository(session)
            farmToolEquipmentRepository = FarmToolEquipmentRepository(session)
            

            farm = farmRepository.findByUserIdWithRenderData(memberId)

            if farm is None:
                raise ValueError(f"Farm not found for member id: {memberId}")

            trainEvent = None

            if farm.is_train_event:
                trainEvent = farmTrainEventRepository.findOpeningEventWithItem()
            
            toolEquipments = farmToolEquipmentRepository.findByFarmIdWithToolData(farm.id)

            image = self.renderFarmImage(farm, toolEquipments)
            embedData = self.buildFarmEmbedData(farm, trainEvent)

        avatarImage = await self.getMemberAvatarImage(memberId)

        if avatarImage is not None:
            self.pasteMemberAvatar(image, avatarImage)

        return {
            "buffer": self.convertImageToBuffer(image),
            "embedData": embedData,
        }

    def renderFarmImage(self, farm, toolEquipments=None):
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
        
        self.renderToolHotBar(baseImage, toolEquipments)

        self.renderFarmStatusInfo(baseImage, farm)

        return baseImage

    def buildFarmEmbedData(self, farm, trainEvent=None):
        cropAreaData = self.buildCropAreaEmbedData(farm.cropArea)
        chickenCoopData = self.buildChickenCoopEmbedData(farm.chickenCoop)
        cowShedData = self.buildCowShedEmbedData(farm.cowShed)
        kitchenData = self.buildKitchenEmbedData(farm.kitchen)
        trainEventData = self.buildTrainEventEmbedData(farm, trainEvent)

        return {
            "cropText": cropAreaData["cropText"],
            "remainingTimeText": cropAreaData["remainingTimeText"],
            "landStatusText": cropAreaData["landStatusText"],
            "pestStatusText": cropAreaData["pestStatusText"],
            "chickenHungryText": chickenCoopData["chickenHungryText"],
            "eggCollectText": chickenCoopData["eggCollectText"],
            "cowHungryText": cowShedData["cowHungryText"],
            "milkCollectText": cowShedData["milkCollectText"],
            "kitchenFoodText": kitchenData["kitchenFoodText"],
            "kitchenQuantityText": kitchenData["kitchenQuantityText"],
            "kitchenRemainingTimeText": kitchenData["kitchenRemainingTimeText"],
            "trainEventText": trainEventData["trainEventText"],
        }

    def buildCropAreaEmbedData(self, cropArea):
        if cropArea is None:
            return {
                "cropText": "Chưa có khu đất",
                "remainingTimeText": "-",
                "landStatusText": "-",
                "pestStatusText": "-",
            }

        cropText = "Chưa trồng cây"
        remainingTimeText = "-"
        landStatusText = "Khô" if cropArea.is_dry else "Ướt"
        pestStatusText = "Có" if cropArea.is_pest_infected else "Không"

        if cropArea.crop is not None:
            crop = cropArea.crop
            cropEmoji = ""

            if crop.cropItem is not None:
                cropEmoji = FARM_GAME_EMOJI.get(crop.cropItem.icon_image_key, "")

            cropText = f"{cropEmoji} **{crop.name}**".strip()
            remainingTimeText = self.buildRemainingHarvestTimeText(cropArea)

        return {
            "cropText": cropText,
            "remainingTimeText": remainingTimeText,
            "landStatusText": landStatusText,
            "pestStatusText": pestStatusText,
        }

    def buildRemainingHarvestTimeText(self, cropArea):
        if cropArea.harvestable_at is None:
            return "-"

        now = datetime.now()
        remainingSeconds = int((cropArea.harvestable_at - now).total_seconds())

        if remainingSeconds <= 0:
            return "Có thể thu hoạch"

        return self.formatRemainingTime(remainingSeconds)

    def buildChickenCoopEmbedData(self, chickenCoop):
        if chickenCoop is None:
            return {
                "chickenHungryText": "Chưa có chuồng gà",
                "eggCollectText": "-",
            }

        if chickenCoop.chicken_count <= 0:
            return {
                "chickenHungryText": "Chưa nuôi gà",
                "eggCollectText": "-",
            }

        return {
            "chickenHungryText": self.buildChickenHungryText(chickenCoop),
            "eggCollectText": self.buildEggCollectText(chickenCoop),
        }

    def buildChickenHungryText(self, chickenCoop):
        if chickenCoop.last_fed_at is None:
            return "Đang đói"

        now = datetime.now()
        hungryAt = chickenCoop.last_fed_at + timedelta(minutes=self.CHICKEN_HUNGRY_INTERVAL_MINUTES)
        remainingSeconds = int((hungryAt - now).total_seconds())

        if remainingSeconds <= 0:
            return "Đang đói"

        return f"Chưa đói - còn {self.formatRemainingTime(remainingSeconds)}"

    def buildEggCollectText(self, chickenCoop):
        if chickenCoop.last_collected_egg_at is None:
            return "Có thể lấy"

        now = datetime.now()
        collectableAt = chickenCoop.last_collected_egg_at + timedelta(minutes=self.EGG_COLLECT_INTERVAL_MINUTES)
        remainingSeconds = int((collectableAt - now).total_seconds())

        if remainingSeconds <= 0:
            return "Có thể lấy"

        return f"Còn {self.formatRemainingTime(remainingSeconds)}"

    def buildCowShedEmbedData(self, cowShed):
        if cowShed is None:
            return {
                "cowHungryText": "Chưa có chuồng bò",
                "milkCollectText": "-",
            }

        if cowShed.cow_count <= 0:
            return {
                "cowHungryText": "Chưa nuôi bò",
                "milkCollectText": "-",
            }

        return {
            "cowHungryText": self.buildCowHungryText(cowShed),
            "milkCollectText": self.buildMilkCollectText(cowShed),
        }

    def buildCowHungryText(self, cowShed):
        if cowShed.last_fed_at is None:
            return "Đang đói"

        now = datetime.now()
        hungryAt = cowShed.last_fed_at + timedelta(minutes=self.COW_HUNGRY_INTERVAL_MINUTES)
        remainingSeconds = int((hungryAt - now).total_seconds())

        if remainingSeconds <= 0:
            return "Đang đói"

        return f"Chưa đói - còn {self.formatRemainingTime(remainingSeconds)}"

    def buildMilkCollectText(self, cowShed):
        if cowShed.last_collected_milk_at is None:
            return "Có thể vắt"

        now = datetime.now()
        collectableAt = cowShed.last_collected_milk_at + timedelta(minutes=self.MILK_COLLECT_INTERVAL_MINUTES)
        remainingSeconds = int((collectableAt - now).total_seconds())

        if remainingSeconds <= 0:
            return "Có thể vắt"

        return f"Còn {self.formatRemainingTime(remainingSeconds)}"

    def formatRemainingTime(self, remainingSeconds: int):
        minutes = remainingSeconds // 60
        seconds = remainingSeconds % 60

        return f"{minutes}:{seconds:02d}"

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
        if chickenCoop.chicken_count >= 1:
            chickenImage = assetImageService.getImage("chicken_1_image_key")
            chickenImage = self.resizeByScale(chickenImage, chickenCoop.render_scale)

            self.pasteSprite(
                baseImage,
                chickenImage,
                x=chickenCoop.chicken_1_x,
                y=chickenCoop.chicken_1_y,
            )

        if chickenCoop.chicken_count >= 2:
            chickenImage = assetImageService.getImage("chicken_2_image_key")
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

        cowImage = assetImageService.getImage("cow_image_key")
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

        return max(elapsedSeconds, 0)

    def buildKitchenEmbedData(self, kitchen):
        if kitchen is None:
            return {
                "kitchenFoodText": "Chưa có nhà bếp",
                "kitchenQuantityText": "-",
                "kitchenRemainingTimeText": "-",
            }

        if kitchen.status == "idle" or kitchen.current_recipe_id is None:
            return {
                "kitchenFoodText": "Đang trống",
                "kitchenQuantityText": "-",
                "kitchenRemainingTimeText": "-",
            }

        currentRecipe = kitchen.currentRecipe

        if currentRecipe is None or currentRecipe.resultItem is None:
            return {
                "kitchenFoodText": "Dữ liệu món ăn không hợp lệ",
                "kitchenQuantityText": "-",
                "kitchenRemainingTimeText": "-",
            }

        resultItem = currentRecipe.resultItem
        itemEmoji = FARM_GAME_EMOJI.get(resultItem.icon_image_key, "")
        kitchenFoodText = f"{itemEmoji} **{resultItem.name}**".strip()

        return {
            "kitchenFoodText": kitchenFoodText,
            "kitchenQuantityText": self.formatNumber(kitchen.cooking_quantity),
            "kitchenRemainingTimeText": self.buildKitchenRemainingTimeText(kitchen),
        }

    def buildKitchenRemainingTimeText(self, kitchen):
        if kitchen.finished_at is None:
            return "-"

        now = datetime.now()
        remainingSeconds = int((kitchen.finished_at - now).total_seconds())

        if remainingSeconds <= 0:
            return "Có thể nhận món"

        return self.formatRemainingTime(remainingSeconds)

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

    def buildTrainEventEmbedData(self, farm, trainEvent):
        if not farm.is_train_event:
            return {
                "trainEventText": "Tàu đang ở ga Chill Station, sẽ cập bến farm của bạn sớm thôi.",
            }

        if trainEvent is None or trainEvent.requiredItem is None:
            return {
                "trainEventText": "Tàu hỏa đang cập bến, nhưng chưa tìm thấy dữ liệu yêu cầu.",
            }

        requiredItem = trainEvent.requiredItem
        itemEmoji = FARM_GAME_EMOJI.get(requiredItem.icon_image_key, "")
        chillCoinEmoji = FARM_GAME_EMOJI["chill_coin"]
        expEmoji = FARM_GAME_EMOJI["exp"]

        return {
            "trainEventText": (
                f"Tàu hỏa yêu cầu **{self.formatNumber(trainEvent.required_quantity)}** "
                f"{itemEmoji} **{requiredItem.name}**, "
                f"phần thưởng **{self.formatNumber(trainEvent.reward_chill_coin)}** {chillCoinEmoji} "
                f"**{self.formatNumber(trainEvent.reward_exp)}** {expEmoji}"
            ),
        }

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
    

    def renderToolHotBar(self, baseImage: Image.Image, toolEquipments):
        hotBarImage = assetImageService.getImage(self.HOT_BAR_IMAGE_KEY)
        hotBarImage = hotBarImage.resize(
            (
                hotBarImage.width // self.HOT_BAR_SCALE_DIVISOR,
                hotBarImage.height // self.HOT_BAR_SCALE_DIVISOR,
            ),
            Image.NEAREST,
        )

        equippedToolByType = self.buildEquippedToolByType(toolEquipments)

        for slotIndex, toolType in enumerate(self.HOT_BAR_TOOL_ORDER):
            userTool = equippedToolByType.get(toolType)

            if userTool is None:
                continue

            self.pasteToolToHotBar(
                hotBarImage=hotBarImage,
                userTool=userTool,
                slotIndex=slotIndex,
                slotCount=self.HOT_BAR_SLOT_COUNT,
            )

        self.pasteSprite(
            baseImage,
            hotBarImage,
            x=self.HOT_BAR_X,
            y=self.HOT_BAR_Y,
        )

    def buildEquippedToolByType(self, toolEquipments):
        equippedToolByType = {}

        if not toolEquipments:
            return equippedToolByType

        for equipment in toolEquipments:
            userTool = equipment.user_tool

            if userTool is None:
                continue

            if userTool.status == ToolStatus.BROKEN.value:
                continue

            if userTool.current_durability <= 0:
                continue

            toolTemplate = userTool.tool_template

            if toolTemplate is None:
                continue

            toolType = toolTemplate.tool_type

            if toolType not in self.HOT_BAR_TOOL_ORDER:
                continue

            equippedToolByType[toolType] = userTool

        return equippedToolByType

    def pasteToolToHotBar(
        self,
        hotBarImage: Image.Image,
        userTool,
        slotIndex: int,
        slotCount: int,
    ):
        item = userTool.item
        toolTemplate = userTool.tool_template

        if item is None or toolTemplate is None:
            return

        toolImage = assetImageService.getImage(item.icon_image_key)

        innerWidth = int(hotBarImage.width * self.HOT_BAR_INNER_WIDTH_RATE)
        startX = (hotBarImage.width - innerWidth) // 2

        slotWidth = innerWidth // slotCount
        slotLeft = startX + slotIndex * slotWidth
        slotCenterX = slotLeft + slotWidth // 2

        maxToolWidth = int(slotWidth * self.HOT_BAR_TOOL_WIDTH_RATE)
        maxToolHeight = int(hotBarImage.height * self.HOT_BAR_TOOL_HEIGHT_RATE)

        toolImage = self.resizeSpriteToFit(
            toolImage,
            maxToolWidth,
            maxToolHeight,
        )

        toolX = slotCenterX - toolImage.width // 2
        toolY = int(hotBarImage.height * self.HOT_BAR_TOOL_Y_RATE)

        hotBarImage.paste(toolImage, (toolX, toolY), toolImage)

        self.drawToolDurabilityBar(
            hotBarImage=hotBarImage,
            slotCenterX=slotCenterX,
            toolImage=toolImage,
            toolY=toolY,
            currentDurability=userTool.current_durability,
            maxDurability=toolTemplate.max_durability,
        )

    def drawToolDurabilityBar(
        self,
        hotBarImage: Image.Image,
        slotCenterX: int,
        toolImage: Image.Image,
        toolY: int,
        currentDurability: int,
        maxDurability: int,
    ):
        if maxDurability <= 0:
            return

        draw = ImageDraw.Draw(hotBarImage)

        durabilityRate = currentDurability / maxDurability
        durabilityRate = max(0, min(1, durabilityRate))

        barWidth = int(toolImage.width * self.TOOL_DURABILITY_BAR_WIDTH_RATE)
        barHeight = self.TOOL_DURABILITY_BAR_HEIGHT

        barX = slotCenterX - barWidth // 2
        barY = toolY - barHeight - self.TOOL_DURABILITY_BAR_OFFSET_Y

        fillWidth = int(barWidth * durabilityRate)

        draw.rectangle(
            (barX, barY, barX + barWidth, barY + barHeight),
            fill=self.TOOL_DURABILITY_BAR_BACKGROUND_FILL,
        )

        draw.rectangle(
            (barX, barY, barX + fillWidth, barY + barHeight),
            fill=self.TOOL_DURABILITY_BAR_FILL,
        )

        draw.rectangle(
            (barX, barY, barX + barWidth, barY + barHeight),
            outline=self.TOOL_DURABILITY_BAR_BORDER_FILL,
            width=1,
        )

    def resizeSpriteToFit(
        self,
        spriteImage: Image.Image,
        maxWidth: int,
        maxHeight: int,
    ):
        scale = min(maxWidth / spriteImage.width, maxHeight / spriteImage.height)

        width = int(spriteImage.width * scale)
        height = int(spriteImage.height * scale)

        return spriteImage.resize((width, height), Image.NEAREST)

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

        avatarAsset = user.display_avatar.replace(
            size=256,
            format="png",
            static_format="png",
        )

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