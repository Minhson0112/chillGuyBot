from io import BytesIO
from math import ceil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from bot.config.database import getDbSession
from bot.repository.userInventoryRepository import UserInventoryRepository
from bot.services.assetImageService import assetImageService


class FarmInventoryRenderService:
    BACKGROUND_KEY = "shopScreen"
    CHILL_COIN_ICON_KEY = "currency_chill_coin"

    FONT_PATH = Path("bot/assets/fonts/arial.ttf")

    PER_PAGE = 20

    TITLE_X = 770
    TITLE_Y = 70

    PAGE_TEXT_X = 765
    PAGE_TEXT_Y = 955

    ITEM_ICON_SIZE = 72
    SMALL_ICON_SIZE = 24

    ITEM_NAME_FONT_SIZE = 24
    ITEM_ID_FONT_SIZE = 24
    QUANTITY_FONT_SIZE = 22
    PRICE_FONT_SIZE = 22
    TITLE_FONT_SIZE = 44
    PAGE_FONT_SIZE = 26

    TEXT_FILL = (255, 235, 180, 255)
    STROKE_FILL = (60, 25, 5, 255)

    SLOT_POSITIONS = [
        (70, 185), (355, 185), (640, 185), (925, 185), (1210, 185),
        (70, 375), (355, 375), (640, 375), (925, 375), (1210, 375),
        (70, 560), (355, 560), (640, 560), (925, 560), (1210, 560),
        (70, 745), (355, 745), (640, 745), (925, 745), (1210, 745),
    ]

    SLOT_WIDTH = 245
    SLOT_HEIGHT = 160

    ITEM_NAME_OFFSET_Y = 10
    ITEM_ICON_OFFSET_Y = 40
    ITEM_ID_OFFSET_Y = 110
    QUANTITY_OFFSET_Y = 140
    PRICE_OFFSET_Y = 140

    QUANTITY_TEXT_OFFSET_X = 55

    PRICE_ICON_OFFSET_X = 150
    PRICE_TEXT_OFFSET_X = 178

    ITEM_NAME_MAX_LENGTH = 25
    TITLE_MAX_LENGTH = 24

    def renderSiloPageToBuffer(
        self,
        userId: int,
        memberDisplayName: str,
        page: int = 1,
    ):
        with getDbSession() as session:
            userInventoryRepository = UserInventoryRepository(session)

            totalItemCount = userInventoryRepository.countSiloItemsByUserId(userId)
            totalPage = self.calculateTotalPage(totalItemCount)
            currentPage = self.normalizePage(page, totalPage)

            inventoryItems = userInventoryRepository.findSiloItemsByUserIdAndPage(
                userId,
                currentPage,
                self.PER_PAGE,
            )

            image = self.renderInventoryImage(
                title=f"Silo của {memberDisplayName}",
                inventoryItems=inventoryItems,
                currentPage=currentPage,
                totalPage=totalPage,
            )

        return {
            "buffer": self.convertImageToBuffer(image),
            "currentPage": currentPage,
            "totalPage": totalPage,
        }

    def renderBarnPageToBuffer(
        self,
        userId: int,
        memberDisplayName: str,
        page: int = 1,
    ):
        with getDbSession() as session:
            userInventoryRepository = UserInventoryRepository(session)

            totalItemCount = userInventoryRepository.countBarnItemsByUserId(userId)
            totalPage = self.calculateTotalPage(totalItemCount)
            currentPage = self.normalizePage(page, totalPage)

            inventoryItems = userInventoryRepository.findBarnItemsByUserIdAndPage(
                userId,
                currentPage,
                self.PER_PAGE,
            )

            image = self.renderInventoryImage(
                title=f"Barn của {memberDisplayName}",
                inventoryItems=inventoryItems,
                currentPage=currentPage,
                totalPage=totalPage,
            )

        return {
            "buffer": self.convertImageToBuffer(image),
            "currentPage": currentPage,
            "totalPage": totalPage,
        }

    def renderInventoryImage(
        self,
        title: str,
        inventoryItems,
        currentPage: int,
        totalPage: int,
    ):
        baseImage = assetImageService.getImage(self.BACKGROUND_KEY)

        self.renderTitle(baseImage, title)
        self.renderPageText(baseImage, currentPage, totalPage)

        for index, userInventory in enumerate(inventoryItems):
            if index >= len(self.SLOT_POSITIONS):
                break

            self.renderInventoryItem(baseImage, userInventory, index)

        return baseImage

    def renderInventoryItem(self, baseImage: Image.Image, userInventory, index: int):
        slotX, slotY = self.SLOT_POSITIONS[index]

        item = userInventory.item

        if item is None:
            return

        self.renderItemName(baseImage, item.name, slotX, slotY)

        itemIcon = assetImageService.getImage(item.icon_image_key)
        itemIcon = self.resizeItemIcon(itemIcon)

        iconX = slotX + (self.SLOT_WIDTH - itemIcon.width) // 2
        iconY = slotY + self.ITEM_ICON_OFFSET_Y

        self.pasteSprite(baseImage, itemIcon, iconX, iconY)

        self.drawCenteredText(
            baseImage,
            text=f"ID: {userInventory.id}",
            centerX=slotX + self.SLOT_WIDTH // 2,
            y=slotY + self.ITEM_ID_OFFSET_Y,
            fontSize=self.ITEM_ID_FONT_SIZE,
        )

        self.renderQuantityInfo(
            baseImage,
            quantity=userInventory.quantity,
            slotX=slotX,
            y=slotY + self.QUANTITY_OFFSET_Y,
        )

        if item.is_sellable:
            self.renderSellPriceInfo(
                baseImage,
                sellPrice=item.sell_price,
                slotX=slotX,
                y=slotY + self.PRICE_OFFSET_Y,
            )

    def renderItemName(
        self,
        baseImage: Image.Image,
        itemName: str,
        slotX: int,
        slotY: int,
    ):
        self.drawCenteredText(
            baseImage,
            text=self.truncateText(itemName, self.ITEM_NAME_MAX_LENGTH),
            centerX=slotX + self.SLOT_WIDTH // 2,
            y=slotY + self.ITEM_NAME_OFFSET_Y,
            fontSize=self.ITEM_NAME_FONT_SIZE,
        )

    def renderQuantityInfo(
        self,
        baseImage: Image.Image,
        quantity: int,
        slotX: int,
        y: int,
    ):
        self.drawText(
            baseImage,
            text=f"SL: {self.formatNumber(quantity)}",
            x=slotX + self.QUANTITY_TEXT_OFFSET_X,
            y=y - 2,
            fontSize=self.QUANTITY_FONT_SIZE,
        )

    def renderSellPriceInfo(
        self,
        baseImage: Image.Image,
        sellPrice: int,
        slotX: int,
        y: int,
    ):
        coinIcon = assetImageService.getImage(self.CHILL_COIN_ICON_KEY)
        coinIcon = coinIcon.resize(
            (self.SMALL_ICON_SIZE, self.SMALL_ICON_SIZE),
            Image.LANCZOS,
        )

        iconX = slotX + self.PRICE_ICON_OFFSET_X
        textX = slotX + self.PRICE_TEXT_OFFSET_X

        self.pasteSprite(baseImage, coinIcon, iconX, y)

        self.drawText(
            baseImage,
            text=self.formatNumber(sellPrice),
            x=textX,
            y=y - 2,
            fontSize=self.PRICE_FONT_SIZE,
        )

    def renderTitle(
        self,
        baseImage: Image.Image,
        title: str,
    ):
        self.drawCenteredText(
            baseImage,
            text=self.truncateText(title, self.TITLE_MAX_LENGTH),
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

    def resizeItemIcon(self, image: Image.Image):
        return image.resize(
            (self.ITEM_ICON_SIZE, self.ITEM_ICON_SIZE),
            Image.NEAREST,
        )

    def pasteSprite(
        self,
        baseImg: Image.Image,
        spriteImg: Image.Image,
        x: int,
        y: int,
    ):
        baseImg.paste(spriteImg, (x, y), spriteImg)

    def drawText(
        self,
        baseImage: Image.Image,
        text: str,
        x: int,
        y: int,
        fontSize: int,
    ):
        draw = ImageDraw.Draw(baseImage)
        font = ImageFont.truetype(str(self.FONT_PATH), fontSize)

        draw.text(
            (x, y),
            text,
            font=font,
            fill=self.TEXT_FILL,
            stroke_width=2,
            stroke_fill=self.STROKE_FILL,
        )

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

        bbox = draw.textbbox((0, 0), text, font=font)
        textWidth = bbox[2] - bbox[0]

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

    def formatNumber(self, number: int):
        return f"{number:,}"

    def truncateText(self, text: str, maxLength: int):
        if text is None:
            return ""

        if len(text) <= maxLength:
            return text

        return text[:maxLength - 3] + "..."

    def convertImageToBuffer(self, image: Image.Image):
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        buffer.seek(0)

        return buffer