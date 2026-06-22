from io import BytesIO
from math import ceil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from bot.helper.numberFormatHelper import formatNumber
from bot.config.database import getDbSession
from bot.repository.farmMarketListingRepository import FarmMarketListingRepository
from bot.services.assetImageService import assetImageService


class FarmMarketShopRenderService:
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

    def renderMemberShopPageToBuffer(
        self,
        sellerUserId: int,
        memberDisplayName: str,
        page: int = 1,
    ):
        with getDbSession() as session:
            farmMarketListingRepository = FarmMarketListingRepository(session)

            totalItemCount = farmMarketListingRepository.countOpenListingsBySellerUserId(
                sellerUserId,
            )
            totalPage = self.calculateTotalPage(totalItemCount)
            currentPage = self.normalizePage(page, totalPage)

            marketListings = farmMarketListingRepository.findOpenListingsBySellerUserIdAndPage(
                sellerUserId,
                currentPage,
                self.PER_PAGE,
            )

            image = self.renderMarketShopImage(
                title=f"Shop của {memberDisplayName}",
                marketListings=marketListings,
                currentPage=currentPage,
                totalPage=totalPage,
            )

        return {
            "buffer": self.convertImageToBuffer(image),
            "currentPage": currentPage,
            "totalPage": totalPage,
        }

    def renderMarketShopImage(
        self,
        title: str,
        marketListings,
        currentPage: int,
        totalPage: int,
    ):
        baseImage = assetImageService.getImage(self.BACKGROUND_KEY)

        self.renderTitle(baseImage, title)
        self.renderPageText(baseImage, currentPage, totalPage)

        for index, marketListing in enumerate(marketListings):
            if index >= len(self.SLOT_POSITIONS):
                break

            self.renderMarketListing(baseImage, marketListing, index)

        return baseImage

    def renderMarketListing(self, baseImage: Image.Image, marketListing, index: int):
        slotX, slotY = self.SLOT_POSITIONS[index]

        item = marketListing.item

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
            text=f"ID: {marketListing.id}",
            centerX=slotX + self.SLOT_WIDTH // 2,
            y=slotY + self.ITEM_ID_OFFSET_Y,
            fontSize=self.ITEM_ID_FONT_SIZE,
        )

        self.renderQuantityInfo(
            baseImage,
            quantity=marketListing.quantity,
            slotX=slotX,
            y=slotY + self.QUANTITY_OFFSET_Y,
        )

        self.renderPriceInfo(
            baseImage,
            price=marketListing.price,
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
            text=f"SL: {formatNumber(quantity)}",
            x=slotX + self.QUANTITY_TEXT_OFFSET_X,
            y=y - 2,
            fontSize=self.QUANTITY_FONT_SIZE,
        )

    def renderPriceInfo(
        self,
        baseImage: Image.Image,
        price: int,
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
            text=formatNumber(price),
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
