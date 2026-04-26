from pathlib import Path

from PIL import Image

from bot.config.imagePaths import ASSET_IMAGE_PATHS


class AssetImageService:
    def __init__(self):
        self.cache = {}

    def preloadAssets(self):
        missingAssets = []

        for imageKey, imagePath in ASSET_IMAGE_PATHS.items():
            path = Path(imagePath)

            if not path.exists():
                missingAssets.append(f"{imageKey}: {imagePath}")
                continue

            self.cache[imageKey] = Image.open(path).convert("RGBA")

        if missingAssets:
            missingText = "\n".join(missingAssets)
            raise FileNotFoundError(f"Missing asset images:\n{missingText}")

        print(f"✅ đã load {len(self.cache)} asset images")

    def getImage(self, imageKey: str):
        image = self.cache.get(imageKey)

        if image is None:
            raise ValueError(f"Asset image not found: {imageKey}")

        return image.copy()

    def hasImage(self, imageKey: str):
        return imageKey in self.cache

    def getLoadedCount(self):
        return len(self.cache)


assetImageService = AssetImageService()