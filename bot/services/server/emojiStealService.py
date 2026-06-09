import re

import aiohttp
import discord


class EmojiStealService:
    EMOJI_PATTERN = re.compile(r"^<(a?):([A-Za-z0-9_]+):(\d{15,22})>$")
    EMOJI_NAME_PATTERN = re.compile(r"^[A-Za-z0-9_]{2,32}$")
    MAX_EMOJI_IMAGE_SIZE = 256 * 1024

    def parseCustomEmoji(self, emoji: str):
        match = self.EMOJI_PATTERN.match(emoji.strip())

        if match is None:
            raise ValueError("Emoji không hợp lệ. Hãy dùng custom emoji dạng `<:name:id>` hoặc `<a:name:id>`.")

        return {
            "isAnimated": match.group(1) == "a",
            "emojiId": match.group(3),
        }

    def validateEmojiName(self, emojiName: str):
        if self.EMOJI_NAME_PATTERN.match(emojiName) is None:
            raise ValueError("Tên emoji phải dài 2-32 ký tự và chỉ gồm chữ, số hoặc dấu gạch dưới.")

    def buildEmojiUrl(self, emojiData):
        extension = "gif" if emojiData["isAnimated"] else "png"
        return f"https://cdn.discordapp.com/emojis/{emojiData['emojiId']}.{extension}"

    async def fetchEmojiImage(self, emojiUrl: str):
        async with aiohttp.ClientSession() as session:
            async with session.get(emojiUrl) as response:
                if response.status != 200:
                    raise ValueError("Không thể tải ảnh emoji từ Discord CDN.")

                imageBytes = await response.read()

        if len(imageBytes) > self.MAX_EMOJI_IMAGE_SIZE:
            raise ValueError("Ảnh emoji vượt quá giới hạn 256KB của Discord.")

        return imageBytes

    async def stealEmoji(
        self,
        guild: discord.Guild,
        emoji: str,
        emojiName: str,
        reason: str,
    ) -> discord.Emoji:
        normalizedEmojiName = emojiName.strip()
        self.validateEmojiName(normalizedEmojiName)
        emojiData = self.parseCustomEmoji(emoji)
        emojiUrl = self.buildEmojiUrl(emojiData)
        imageBytes = await self.fetchEmojiImage(emojiUrl)

        return await guild.create_custom_emoji(
            name=normalizedEmojiName,
            image=imageBytes,
            reason=reason,
        )
