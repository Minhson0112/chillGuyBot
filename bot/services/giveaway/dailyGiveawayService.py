from datetime import datetime, timedelta, timezone

import discord

from bot.config.channel import DAILY_GIVEAWAY_CHANNEL_ID
from bot.config.roles import GIVEAWAY_ROLE_ID
from bot.enums.giveawayType import GiveawayType
from bot.services.giveaway.createGiveawayService import CreateGiveawayService
from bot.services.giveaway.giveawayMessageService import GiveawayMessageService
from bot.services.giveaway.giveawaySchedulerService import giveawaySchedulerService
from bot.views.giveawayJoinButtonView import GiveawayJoinButtonView


class DailyGiveawayService:
    GMT7 = timezone(timedelta(hours=7))
    REWARD_COWONCY = 300000
    WINNER_COUNT = 1
    DURATION_SECONDS = 36000

    def __init__(self):
        self.createGiveawayService = CreateGiveawayService()
        self.giveawayMessageService = GiveawayMessageService()

    async def createDailyGiveaway(self, bot):
        if bot.user is None:
            print("Daily giveaway skipped: bot user is None")
            return

        channel = await self.resolveDailyGiveawayChannel(bot)

        if channel is None:
            print("Daily giveaway skipped: daily giveaway channel not found")
            return

        result = self.createGiveawayService.createGiveaway(
            title=self.buildDailyGiveawayTitle(),
            giveawayType=GiveawayType.COWONCY.value,
            reward=self.REWARD_COWONCY,
            winnerCount=self.WINNER_COUNT,
            durationSeconds=self.DURATION_SECONDS,
            channelId=DAILY_GIVEAWAY_CHANNEL_ID,
            createdByUserId=bot.user.id,
        )

        if not result["success"]:
            print(f"Daily giveaway failed: {result['message']}")
            return

        giveawayId = result["giveawayId"]
        embed = self.giveawayMessageService.buildGiveawayEmbedById(
            giveawayId=giveawayId,
            guild=channel.guild,
        )

        if embed is None:
            print(f"Daily giveaway failed: cannot build embed, giveawayId={giveawayId}")
            return

        giveawayMessage = await channel.send(
            content=(
                f"<@&{GIVEAWAY_ROLE_ID}> "
                "<a:CS_blueblink:1507030291640881203> Chúc các bạn ngày mới vui vẻ cùng Chill Station <a:CS_bluemoon:1507030292811091999>"
            ),
            embed=embed,
            view=GiveawayJoinButtonView(giveawayId),
            allowed_mentions=discord.AllowedMentions(
                users=False,
                roles=True,
                everyone=False,
            ),
        )

        self.createGiveawayService.updateGiveawayMessageId(
            giveawayId=giveawayId,
            messageId=giveawayMessage.id,
        )
        giveawaySchedulerService.reloadSchedule()

        print(f"Daily giveaway created: giveawayId={giveawayId}")

    def buildDailyGiveawayTitle(self):
        now = datetime.now(self.GMT7)
        dateText = now.strftime("%d/%m/%Y")

        return f"GA daily ngày {dateText}"

    async def resolveDailyGiveawayChannel(self, bot):
        channel = bot.get_channel(DAILY_GIVEAWAY_CHANNEL_ID)

        if channel is None:
            try:
                channel = await bot.fetch_channel(DAILY_GIVEAWAY_CHANNEL_ID)
            except discord.NotFound:
                return None
            except discord.Forbidden:
                return None
            except discord.HTTPException:
                return None

        if not isinstance(channel, discord.TextChannel):
            return None

        return channel
