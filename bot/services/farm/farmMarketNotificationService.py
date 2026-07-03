import discord

from bot.config.channel import FARM_NOTIFICATION_CHANNEL_ID
from bot.config.emoji import FARM_GAME_EMOJI
from bot.helper.discordResolverHelper import resolveChannel
from bot.helper.numberFormatHelper import formatNumber


class FarmMarketNotificationService:
    async def sendMemberPurchaseNotification(self, bot, notificationData):
        if notificationData is None:
            return

        notificationChannel = await resolveChannel(
            bot,
            FARM_NOTIFICATION_CHANNEL_ID,
            discord.TextChannel,
        )

        if notificationChannel is None:
            return

        chillCoinEmoji = FARM_GAME_EMOJI["chill_coin"]
        buyerDisplayName = discord.utils.escape_markdown(
            notificationData["buyerDisplayName"],
        )
        bonusText = (
            f"Trong đó bonus: **{formatNumber(notificationData['sellerBonus'])}** "
            f"{chillCoinEmoji}."
        )

        if notificationData["isBonusLimitReached"]:
            bonusText += (
                f" Bạn đã chạm giới hạn bonus market "
                f"**{formatNumber(notificationData['dailyBonusLimit'])}** "
                f"{chillCoinEmoji} trong ngày."
            )

        await notificationChannel.send(
            content=(
                f"<@{notificationData['sellerUserId']}>\n"
                f"**{buyerDisplayName}** đã mua "
                f"**{notificationData['quantity']}** {notificationData['itemText']} "
                f"trong shop của bạn.\n"
                f"Giá người mua trả: "
                f"**{formatNumber(notificationData['listingPrice'])}** {chillCoinEmoji}\n"
                f"Bạn nhận được: "
                f"**{formatNumber(notificationData['sellerPayout'])}** {chillCoinEmoji}.\n"
                f"{bonusText}"
            ),
            allowed_mentions=discord.AllowedMentions(
                users=[discord.Object(id=notificationData["sellerUserId"])],
                roles=False,
                everyone=False,
            ),
        )
