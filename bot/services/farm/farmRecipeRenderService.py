from io import BytesIO
from math import ceil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from bot.config.database import getDbSession
from bot.repository.foodRecipeRepository import FoodRecipeRepository
from bot.services.assetImageService import assetImageService


class FarmRecipeRenderService:
    BACKGROUND_KEY = "recipesScreen"
    COIN_ICON_KEY = "currency_chill_coin"
    LEVEL_ICON_KEY = "level"
    CLOCK_ICON_KEY = "clock"

    FONT_PATH = Path("bot/assets/fonts/arial.ttf")

    PER_PAGE = 5

    TITLE_TEXT = "Công thức nấu ăn"

    TITLE_X = 770
    TITLE_Y = 70

    PAGE_TEXT_X = 765
    PAGE_TEXT_Y = 955

    ROW_START_X = 95
    ROW_TEXT_Y_LIST = [
        250,
        400,
        550,
        700,
        850,
    ]

    INFO_RIGHT_X = 1425

    ITEM_ICON_SIZE = 42
    INFO_ICON_SIZE = 34

    TITLE_FONT_SIZE = 46
    PAGE_FONT_SIZE = 26
    LINE_FONT_SIZE = 26

    TEXT_FILL = (255, 235, 180, 255)
    STROKE_FILL = (60, 25, 5, 255)

    INLINE_GAP = 14
    ICON_TEXT_GAP = 8

    ITEM_ICON_OFFSET_Y = -7
    INFO_ICON_OFFSET_Y = -4

    def renderRecipePageToBuffer(self, page: int = 1):
        with getDbSession() as session:
            foodRecipeRepository = FoodRecipeRepository(session)

            totalRecipeCount = foodRecipeRepository.countActiveRecipes()
            totalPage = self.calculateTotalPage(totalRecipeCount)
            currentPage = self.normalizePage(page, totalPage)

            recipes = foodRecipeRepository.findActiveRecipesByPage(
                currentPage,
                self.PER_PAGE,
            )

            image = self.renderRecipeImage(
                recipes=recipes,
                currentPage=currentPage,
                totalPage=totalPage,
            )

        return {
            "buffer": self.convertImageToBuffer(image),
            "currentPage": currentPage,
            "totalPage": totalPage,
        }

    def renderRecipeImage(
        self,
        recipes,
        currentPage: int,
        totalPage: int,
    ):
        baseImage = assetImageService.getImage(self.BACKGROUND_KEY).copy()

        self.renderTitle(baseImage)
        self.renderPageText(baseImage, currentPage, totalPage)

        for index, recipe in enumerate(recipes):
            if index >= len(self.ROW_TEXT_Y_LIST):
                break

            self.renderRecipeLine(
                baseImage=baseImage,
                recipe=recipe,
                y=self.ROW_TEXT_Y_LIST[index],
            )

        return baseImage

    def renderRecipeLine(
        self,
        baseImage: Image.Image,
        recipe,
        y: int,
    ):
        resultItem = recipe.resultItem

        if resultItem is None:
            return

        draw = ImageDraw.Draw(baseImage)
        font = ImageFont.truetype(str(self.FONT_PATH), self.LINE_FONT_SIZE)

        self.renderRecipeFormula(
            baseImage=baseImage,
            draw=draw,
            font=font,
            recipe=recipe,
            y=y,
        )

        self.renderRecipeInfoRight(
            baseImage=baseImage,
            draw=draw,
            font=font,
            recipe=recipe,
            resultItem=resultItem,
            y=y,
        )

    def renderRecipeFormula(
        self,
        baseImage: Image.Image,
        draw: ImageDraw.ImageDraw,
        font: ImageFont.FreeTypeFont,
        recipe,
        y: int,
    ):
        resultItem = recipe.resultItem
        x = self.ROW_START_X

        x = self.drawInlineText(
            draw=draw,
            text=f"id:{resultItem.id}",
            x=x,
            y=y,
            font=font,
        )

        x = self.drawInlineText(
            draw=draw,
            text=resultItem.name,
            x=x,
            y=y,
            font=font,
        )

        x = self.drawInlineIcon(
            baseImage=baseImage,
            imageKey=resultItem.icon_image_key,
            x=x,
            y=y + self.ITEM_ICON_OFFSET_Y,
            size=self.ITEM_ICON_SIZE,
            resizeType=Image.NEAREST,
        )

        x = self.drawInlineText(
            draw=draw,
            text="=",
            x=x,
            y=y,
            font=font,
        )

        self.renderIngredientsInline(
            baseImage=baseImage,
            draw=draw,
            font=font,
            ingredients=recipe.ingredients,
            x=x,
            y=y,
        )

    def renderRecipeInfoRight(
        self,
        baseImage: Image.Image,
        draw: ImageDraw.ImageDraw,
        font: ImageFont.FreeTypeFont,
        recipe,
        resultItem,
        y: int,
    ):
        infoWidth = self.calculateRecipeInfoWidth(
            draw=draw,
            font=font,
            priceText=self.formatPrice(resultItem.sell_price),
            levelText=str(recipe.required_farm_level),
            timeText=self.formatCookingTime(recipe.cooking_seconds),
        )

        x = self.INFO_RIGHT_X - infoWidth

        x = self.drawInlineIcon(
            baseImage=baseImage,
            imageKey=self.COIN_ICON_KEY,
            x=x,
            y=y + self.INFO_ICON_OFFSET_Y,
            size=self.INFO_ICON_SIZE,
            resizeType=Image.LANCZOS,
        )

        x = self.drawInlineText(
            draw=draw,
            text=self.formatPrice(resultItem.sell_price),
            x=x,
            y=y,
            font=font,
        )

        x = self.drawInlineIcon(
            baseImage=baseImage,
            imageKey=self.LEVEL_ICON_KEY,
            x=x,
            y=y + self.INFO_ICON_OFFSET_Y,
            size=self.INFO_ICON_SIZE,
            resizeType=Image.LANCZOS,
        )

        x = self.drawInlineText(
            draw=draw,
            text=str(recipe.required_farm_level),
            x=x,
            y=y,
            font=font,
        )

        x = self.drawInlineIcon(
            baseImage=baseImage,
            imageKey=self.CLOCK_ICON_KEY,
            x=x,
            y=y + self.INFO_ICON_OFFSET_Y,
            size=self.INFO_ICON_SIZE,
            resizeType=Image.LANCZOS,
        )

        self.drawInlineText(
            draw=draw,
            text=self.formatCookingTime(recipe.cooking_seconds),
            x=x,
            y=y,
            font=font,
        )

    def calculateRecipeInfoWidth(
        self,
        draw: ImageDraw.ImageDraw,
        font: ImageFont.FreeTypeFont,
        priceText: str,
        levelText: str,
        timeText: str,
    ):
        return (
            self.INFO_ICON_SIZE
            + self.ICON_TEXT_GAP
            + self.getTextWidth(draw, priceText, font)
            + self.INLINE_GAP
            + self.INFO_ICON_SIZE
            + self.ICON_TEXT_GAP
            + self.getTextWidth(draw, levelText, font)
            + self.INLINE_GAP
            + self.INFO_ICON_SIZE
            + self.ICON_TEXT_GAP
            + self.getTextWidth(draw, timeText, font)
        )

    def renderIngredientsInline(
        self,
        baseImage: Image.Image,
        draw: ImageDraw.ImageDraw,
        font: ImageFont.FreeTypeFont,
        ingredients,
        x: int,
        y: int,
    ):
        sortedIngredients = sorted(
            ingredients,
            key=lambda ingredient: ingredient.id,
        )

        for index, ingredient in enumerate(sortedIngredients):
            item = ingredient.item

            if item is None:
                continue

            if index > 0:
                x = self.drawInlineText(
                    draw=draw,
                    text="+",
                    x=x,
                    y=y,
                    font=font,
                )

            x = self.drawInlineText(
                draw=draw,
                text=f"{ingredient.quantity} {item.name}",
                x=x,
                y=y,
                font=font,
            )

            x = self.drawInlineIcon(
                baseImage=baseImage,
                imageKey=item.icon_image_key,
                x=x,
                y=y + self.ITEM_ICON_OFFSET_Y,
                size=self.ITEM_ICON_SIZE,
                resizeType=Image.NEAREST,
            )

        return x

    def drawInlineText(
        self,
        draw: ImageDraw.ImageDraw,
        text: str,
        x: int,
        y: int,
        font: ImageFont.FreeTypeFont,
    ):
        draw.text(
            (x, y),
            text,
            font=font,
            fill=self.TEXT_FILL,
            stroke_width=2,
            stroke_fill=self.STROKE_FILL,
        )

        return x + self.getTextWidth(draw, text, font) + self.INLINE_GAP

    def drawInlineIcon(
        self,
        baseImage: Image.Image,
        imageKey: str,
        x: int,
        y: int,
        size: int,
        resizeType,
    ):
        iconImage = assetImageService.getImage(imageKey)
        iconImage = iconImage.resize((size, size), resizeType)

        self.pasteSprite(
            baseImage,
            iconImage,
            x,
            y,
        )

        return x + size + self.ICON_TEXT_GAP

    def getTextWidth(
        self,
        draw: ImageDraw.ImageDraw,
        text: str,
        font: ImageFont.FreeTypeFont,
    ):
        bbox = draw.textbbox((0, 0), text, font=font)

        return bbox[2] - bbox[0]

    def renderTitle(self, baseImage: Image.Image):
        self.drawCenteredText(
            baseImage,
            text=self.TITLE_TEXT,
            centerX=self.TITLE_X,
            y=self.TITLE_Y,
            fontSize=self.TITLE_FONT_SIZE,
        )

    def renderPageText(
        self,
        baseImage: Image.Image,
        currentPage: int,
        totalPage: int,
    ):
        self.drawCenteredText(
            baseImage,
            text=f"{currentPage}/{totalPage}",
            centerX=self.PAGE_TEXT_X,
            y=self.PAGE_TEXT_Y,
            fontSize=self.PAGE_FONT_SIZE,
        )

    def pasteSprite(
        self,
        baseImg: Image.Image,
        spriteImg: Image.Image,
        x: int,
        y: int,
    ):
        baseImg.paste(spriteImg, (x, y), spriteImg)

    def drawCenteredText(
        self,
        baseImage: Image.Image,
        text: str,
        centerX: int,
        y: int,
        fontSize: int,
    ):
        draw = ImageDraw.Draw(baseImage)
        font = ImageFont.truetype(str(self.FONT_PATH), fontSize)

        textWidth = self.getTextWidth(draw, text, font)
        x = centerX - textWidth // 2

        draw.text(
            (x, y),
            text,
            font=font,
            fill=self.TEXT_FILL,
            stroke_width=2,
            stroke_fill=self.STROKE_FILL,
        )

    def calculateTotalPage(self, totalItemCount: int):
        if totalItemCount <= 0:
            return 1

        return ceil(totalItemCount / self.PER_PAGE)

    def normalizePage(self, page: int, totalPage: int):
        if page < 1:
            return 1

        if page > totalPage:
            return totalPage

        return page

    def formatPrice(self, price):
        if price is None:
            return "-"

        return f"{price:,}"

    def formatCookingTime(self, cookingSeconds: int):
        minutes = cookingSeconds // 60
        seconds = cookingSeconds % 60

        if minutes <= 0:
            return f"{seconds}s"

        if seconds <= 0:
            return f"{minutes}m"

        return f"{minutes}m{seconds:02d}s"

    def convertImageToBuffer(self, image: Image.Image):
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        buffer.seek(0)

        return buffer