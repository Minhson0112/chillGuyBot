from datetime import datetime, timedelta, timezone

import discord

from bot.config.channel import GIVEAWAY_FOR_DONATOR_CHANNEL_ID
from bot.config.database import getDbSession
from bot.config.roles import GIVEAWAY_ROLE_ID
from bot.enums.giveawayType import GiveawayType
from bot.repository.owoDonateHistoryRepository import OwoDonateHistoryRepository
from bot.services.donate.monthlyDonatorRoleService import MonthlyDonatorRoleService
from bot.services.giveaway.createGiveawayService import CreateGiveawayService
from bot.services.giveaway.giveawayMessageService import GiveawayMessageService
from bot.services.giveaway.giveawaySchedulerService import giveawaySchedulerService
from bot.views.giveaway.giveawayJoinButtonView import GiveawayJoinButtonView


class MonthlyDonatorGiveawayService:
    GMT7 = timezone(timedelta(hours=7))
    WINNER_COUNT = 1
    DURATION_SECONDS = 36000

    def __init__(self):
        self.createGiveawayService = CreateGiveawayService()
        self.giveawayMessageService = GiveawayMessageService()
        self.monthlyDonatorRoleService = MonthlyDonatorRoleService()

    async def createMonthlyDonatorGiveaway(self, bot):
        if bot.user is None:
            print("Monthly donator giveaway skipped: bot user is None")
            return

        channel = await self.resolveGiveawayChannel(bot)

        if channel is None:
            print("Monthly donator giveaway skipped: giveaway channel not found")
            return

        now = datetime.now(self.GMT7)
        totalDonate = self.getTotalDonateByMonth(now.year, now.month)

        if totalDonate <= 1:
            print(
                f"Monthly donator giveaway skipped: total donate {totalDonate:,} cowoncy"
            )
            return

        limitRole = self.findCurrentMonthDonatorRole(channel.guild)

        if limitRole is None:
            print("Monthly donator giveaway skipped: monthly donator role not found")
            return

        reward = totalDonate // 2
        result = self.createGiveawayService.createGiveaway(
            title=self.buildMonthlyDonatorGiveawayTitle(now.year, now.month),
            giveawayType=GiveawayType.COWONCY.value,
            reward=reward,
            winnerCount=self.WINNER_COUNT,
            durationSeconds=self.DURATION_SECONDS,
            channelId=GIVEAWAY_FOR_DONATOR_CHANNEL_ID,
            createdByUserId=bot.user.id,
            limitRoleId=limitRole.id,
        )

        if not result["success"]:
            print(f"Monthly donator giveaway failed: {result['message']}")
            return

        giveawayId = result["giveawayId"]
        embed = self.giveawayMessageService.buildGiveawayEmbedById(
            giveawayId=giveawayId,
            guild=channel.guild,
        )

        if embed is None:
            print(f"Monthly donator giveaway failed: cannot build embed, giveawayId={giveawayId}")
            return

        giveawayMessage = await channel.send(
            content=(
                f"<@&{GIVEAWAY_ROLE_ID}> <@&{limitRole.id}> "
                "<a:CS_blueblink:1507030291640881203> Giveaway dành cho những donator tuyệt vời của Chill Station, chúc các bạn một tháng mới thật bùng nổ. <a:CS_bluemoon:1507030292811091999>"
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

        print(f"Monthly donator giveaway created: giveawayId={giveawayId}")

    def getTotalDonateByMonth(self, year: int, month: int):
        with getDbSession() as session:
            owoDonateHistoryRepository = OwoDonateHistoryRepository(session)
            return owoDonateHistoryRepository.getTotalDonateByMonth(year, month)

    def findCurrentMonthDonatorRole(self, guild: discord.Guild):
        roleName = self.monthlyDonatorRoleService.buildCurrentMonthRoleName()
        return discord.utils.get(guild.roles, name=roleName)

    def buildMonthlyDonatorGiveawayTitle(self, year: int, month: int):
        return f"GA for donator {year}/{month:02d}"

    async def resolveGiveawayChannel(self, bot):
        channel = bot.get_channel(GIVEAWAY_FOR_DONATOR_CHANNEL_ID)

        if channel is None:
            try:
                channel = await bot.fetch_channel(GIVEAWAY_FOR_DONATOR_CHANNEL_ID)
            except discord.NotFound:
                return None
            except discord.Forbidden:
                return None
            except discord.HTTPException:
                return None

        if not isinstance(channel, discord.TextChannel):
            return None

        return channel
