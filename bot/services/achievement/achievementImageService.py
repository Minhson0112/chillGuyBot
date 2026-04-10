from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


class AchievementImageService:
    def __init__(self):
        baseDir = Path(__file__).resolve().parents[2]
        self.imagePath = baseDir / "assets" / "images" / "achievements" / "chillStation.png"
        self.fontPath = "arial.ttf"
        self.textColor = (219, 222, 225, 255)
        self.fontSize = 32
        self.onlinePos = (556, 1124)
        self.memberPos = (870, 1124)

        self.baseImage = None
        self.font = None

        self.preload()

    def preload(self):
        self.baseImage = Image.open(self.imagePath).convert("RGBA")
        self.font = ImageFont.truetype(self.fontPath, self.fontSize)

    def buildAchievementImage(self, onlineCount: int, memberCount: int):
        image = self.baseImage.copy()
        draw = ImageDraw.Draw(image)

        onlineText = f"{onlineCount:,} Trực tuyến"
        memberText = f"{memberCount:,} Thành viên"

        draw.text(self.onlinePos, onlineText, font=self.font, fill=self.textColor)
        draw.text(self.memberPos, memberText, font=self.font, fill=self.textColor)

        buffer = BytesIO()
        image.save(buffer, format="PNG")
        buffer.seek(0)

        return buffer