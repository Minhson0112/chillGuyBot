from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

from bot.helper.numberFormatHelper import formatNumber
from bot.services.asset.assetImageService import assetImageService


class DailyTaskImageService:
    FONT_PATH = Path("bot/assets/fonts/arial.ttf")

    DATE_BOX = (510, 215, 775, 268)
    TASK_NAME_POSITIONS = [
        (247, 339),
        (247, 540),
        (247, 741),
        (247, 939),
        (247, 1142),
    ]
    TASK_DESCRIPTION_POSITIONS = [
        (247, 378),
        (247, 579),
        (247, 780),
        (247, 978),
        (247, 1181),
    ]
    TASK_TEXT_RIGHT = 780

    PROGRESS_BOXES = [
        (219, 439, 769, 459),
        (219, 638, 769, 658),
        (219, 843, 769, 863),
        (219, 1040, 769, 1060),
        (219, 1243, 769, 1263),
    ]
    PROGRESS_COLOR = (65, 142, 210, 255)
    PROGRESS_TEXT_COLOR = (49, 45, 37, 255)

    REWARD_BOX_LEFT = 808
    REWARD_BOX_RIGHT = 922
    REWARD_ROW_CENTERS = [
        (396, 436),
        (589, 629),
        (790, 830),
        (990, 1030),
        (1190, 1230),
    ]
    REWARD_ICON_SIZE = 28
    REWARD_GAP = 7

    TEXT_COLOR = (87, 57, 32, 255)

    def buildDailyTaskImage(self, imageData):
        image = assetImageService.getImage("dailyTask")
        draw = ImageDraw.Draw(image)
        chillCoinIcon = assetImageService.getImage("currency_chill_coin")
        expIcon = assetImageService.getImage("exp")

        self.drawDate(draw, imageData["taskDate"])

        taskLayouts = zip(
            self.TASK_NAME_POSITIONS,
            self.TASK_DESCRIPTION_POSITIONS,
            self.PROGRESS_BOXES,
            self.REWARD_ROW_CENTERS,
            imageData["tasks"],
        )

        for taskLayout in taskLayouts:
            (
                taskNamePosition,
                descriptionPosition,
                progressBox,
                rewardRowCenters,
                taskData,
            ) = taskLayout
            self.drawTask(
                draw,
                taskNamePosition,
                descriptionPosition,
                progressBox,
                taskData,
            )
            self.drawRewards(
                image,
                draw,
                rewardRowCenters,
                taskData,
                chillCoinIcon,
                expIcon,
            )

        buffer = BytesIO()
        image.save(buffer, format="PNG")
        buffer.seek(0)

        return buffer

    def drawDate(self, draw, taskDate):
        dateText = taskDate.strftime("%d/%m/%Y")
        font = ImageFont.truetype(str(self.FONT_PATH), 28)
        self.drawCenteredText(draw, self.DATE_BOX, dateText, font, self.TEXT_COLOR)

    def drawTask(
        self,
        draw,
        taskNamePosition,
        descriptionPosition,
        progressBox,
        taskData,
    ):
        taskName = taskData["taskName"]
        description = taskData["description"]
        textWidth = self.TASK_TEXT_RIGHT - taskNamePosition[0]
        taskNameFont = self.getFitFont(draw, taskName, 27, textWidth, 20)
        descriptionFont = self.getFitFont(draw, description, 22, textWidth, 17)

        draw.text(
            taskNamePosition,
            taskName,
            font=taskNameFont,
            fill=self.TEXT_COLOR,
        )
        draw.text(
            descriptionPosition,
            description,
            font=descriptionFont,
            fill=self.TEXT_COLOR,
        )

        self.drawProgressBar(draw, progressBox, taskData)

    def drawProgressBar(self, draw, progressBox, taskData):
        progressLeft, progressTop, progressRight, progressBottom = progressBox
        progressHeight = progressBottom - progressTop
        requiredValue = taskData["requiredValue"]

        if requiredValue > 0:
            progressRate = min(max(taskData["progressValue"] / requiredValue, 0), 1)
            progressWidth = int(
                (progressRight - progressLeft) * progressRate
            )

            if progressWidth > 0:
                draw.rounded_rectangle(
                    (
                        progressLeft,
                        progressTop,
                        progressLeft + progressWidth,
                        progressBottom,
                    ),
                    radius=progressHeight // 2,
                    fill=self.PROGRESS_COLOR,
                )

        progressFont = ImageFont.truetype(str(self.FONT_PATH), 18)
        self.drawCenteredText(
            draw,
            progressBox,
            taskData["progressText"],
            progressFont,
            self.PROGRESS_TEXT_COLOR,
        )

    def drawRewards(
        self,
        image,
        draw,
        rewardRowCenters,
        taskData,
        chillCoinIcon,
        expIcon,
    ):
        rewardRows = [
            (chillCoinIcon, formatNumber(taskData["rewardChillCoin"])),
            (expIcon, formatNumber(taskData["rewardExp"])),
        ]
        rewardFont = ImageFont.truetype(str(self.FONT_PATH), 22)

        for rowCenter, rewardRow in zip(rewardRowCenters, rewardRows):
            icon, value = rewardRow
            iconTop = rowCenter - self.REWARD_ICON_SIZE // 2
            fittedIcon = ImageOps.contain(
                icon,
                (self.REWARD_ICON_SIZE, self.REWARD_ICON_SIZE),
                method=Image.Resampling.LANCZOS,
            )
            valueFont = self.getFitFont(
                draw,
                value,
                rewardFont.size,
                self.REWARD_BOX_RIGHT - self.REWARD_BOX_LEFT - self.REWARD_ICON_SIZE,
                16,
            )
            valueBox = draw.textbbox((0, 0), value, font=valueFont)
            valueWidth = valueBox[2] - valueBox[0]
            groupWidth = fittedIcon.width + self.REWARD_GAP + valueWidth
            groupLeft = self.REWARD_BOX_LEFT + (
                (self.REWARD_BOX_RIGHT - self.REWARD_BOX_LEFT) - groupWidth
            ) // 2
            iconLeft = groupLeft
            image.alpha_composite(fittedIcon, (iconLeft, iconTop))

            valueX = iconLeft + fittedIcon.width + self.REWARD_GAP - valueBox[0]
            valueY = rowCenter - (
                (valueBox[3] - valueBox[1]) / 2
            ) - valueBox[1]
            draw.text(
                (valueX, valueY),
                value,
                font=valueFont,
                fill=self.TEXT_COLOR,
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
