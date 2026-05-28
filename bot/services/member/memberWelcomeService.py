import random

import discord

from bot.config.channel import MAIN_CHAT_CHANNEL_ID, WELCOME_CHANNEL_ID
from bot.config.decoration import WELCOME_DECORATION_IMG_URL
from bot.config.emoji import BLUEMOON, FLOWER, LOGO, STRING, SUN, WELCOME, WING_L, WING_R
from bot.config.roles import INTERSHIP_ROLE_ID, MODERATOR_ROLE_ID, STAFF_ROLE_ID

WELCOME_MESSAGES = [
    "chúc bạn một ngày vui vẻ",
    "chúc bạn có thật nhiều niềm vui ở đây",
    "mong bạn sẽ thấy thật thoải mái ở Chill Station",
    "chúc bạn hôm nay gặp toàn điều dễ thương",
    "hy vọng bạn sẽ có những phút giây thật chill",
    "chúc bạn làm quen được nhiều người bạn mới",
]

MAIN_CHAT_WELCOME_MESSAGES = [
    "Chúc bạn có một ngày tuyệt vời",
    "Chúc bạn luôn thấy vui khi ghé Chill Station",
    "Mong bạn sẽ có thật nhiều khoảnh khắc dễ thương ở đây",
    "Chúc bạn làm quen được nhiều người bạn mới",
    "Hy vọng hôm nay của bạn sẽ thật nhẹ nhàng và vui vẻ",
    "Chúc bạn có một hành trình thật chill cùng mọi người",
]


class MemberWelcomeService:
    async def handleMemberWelcome(self, member: discord.Member):
        await self.sendWelcomeMessage(member)
        await self.sendMainChatWelcomeMessage(member)

    async def sendWelcomeMessage(self, member: discord.Member):
        welcomeChannel = await self.resolveTextChannel(member.guild, WELCOME_CHANNEL_ID)
        if welcomeChannel is None:
            return

        welcomeMessage = random.choice(WELCOME_MESSAGES)
        await welcomeChannel.send(
            f"{STRING} Chào mừng {member.mention} đã cập bến\n"
            f"{LOGO}\n"
            f"{SUN} {welcomeMessage} {FLOWER}"
        )

    async def sendMainChatWelcomeMessage(self, member: discord.Member):
        mainChatChannel = await self.resolveTextChannel(member.guild, MAIN_CHAT_CHANNEL_ID)
        if mainChatChannel is None:
            return

        welcomeMessage = random.choice(MAIN_CHAT_WELCOME_MESSAGES)
        embed = discord.Embed(
            title=f"{WING_L} Welcome To Chill Station {WING_R}",
            description=(
                f"{WELCOME} Chào mừng {member.mention} {WELCOME} tới với\n"
                f"# {LOGO}\n\n"
                f"{SUN} Hãy pick role ở https://discord.com/channels/1356994231918530690/1357332039858393110 để chúng ta hiểu nhau hơn.\n"
                f"{SUN} Say hi với mọi người ở https://discord.com/channels/1356994231918530690/1356994232857923827 nào.\n\n"
                f"{STRING} {welcomeMessage} {BLUEMOON}"
            ),
            color=discord.Color.green(),
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_image(url=WELCOME_DECORATION_IMG_URL)

        await mainChatChannel.send(
            content=(
                f"<@&{MODERATOR_ROLE_ID}> <@&{STAFF_ROLE_ID}> <@&{INTERSHIP_ROLE_ID}> "
                "Ra đón thành viên mới nào."
            ),
            embed=embed,
        )

    async def resolveTextChannel(self, guild: discord.Guild, channelId: int):
        channel = guild.get_channel(channelId)
        if channel is None:
            try:
                channel = await guild.fetch_channel(channelId)
            except discord.HTTPException:
                return None

        if not isinstance(channel, discord.TextChannel):
            return None

        return channel

