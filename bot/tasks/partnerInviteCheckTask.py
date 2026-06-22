import discord
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from discord.ext import commands

from bot.helper.discordResolverHelper import resolveChannel
from bot.config.channel import BOT_NOTIFICATION_CHANNEL_ID, PARTNER_CHANNEL_ID, TICKET_CHANNEL_ID
from bot.services.partner.partnerInviteCheckService import PartnerInviteCheckService


class PartnerInviteCheckTask(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.partnerInviteCheckService = PartnerInviteCheckService()
        self.scheduler = AsyncIOScheduler(timezone="Asia/Ho_Chi_Minh")

        self.scheduler.add_job(
            self.runPartnerInviteCheckJob,
            CronTrigger(
                hour=11,
                minute=0,
                second=0,
                timezone="Asia/Ho_Chi_Minh",
            ),
            id="partnerInviteCheckJob",
            replace_existing=True,
            max_instances=1,
        )

        self.scheduler.start()

    async def runPartnerInviteCheckJob(self):
        await self.bot.wait_until_ready()

        try:
            invalidPartners = await self.partnerInviteCheckService.findInvalidActivePartnerInvites(self.bot)
            notificationChannel = await resolveChannel(self.bot, BOT_NOTIFICATION_CHANNEL_ID, discord.TextChannel)

            if notificationChannel is None:
                print("Partner invite check job error: notification channel not found")
                return

            for partner in invalidPartners:
                await notificationChannel.send(
                    content=self.buildNotificationMessage(partner),
                    allowed_mentions=discord.AllowedMentions(
                        users=True,
                        roles=False,
                        everyone=False,
                    ),
                )

            print(f"Partner invite check job found {len(invalidPartners)} invalid partner invites")
        except Exception as e:
            print(f"Partner invite check job error: {e}")

    def buildNotificationMessage(self, partner):
        return (
            f"<@{partner['representativeUserId']}>\n"
            f"Chào Người đại diện của server {partner['guildName']}, "
            f"có vẻ như link mời của server của bạn ở <#{PARTNER_CHANNEL_ID}> đã hết hạn, "
            f"vui lòng <#{TICKET_CHANNEL_ID}> để cập nhật lại link nhé."
        )

    def cog_unload(self):
        if self.scheduler.running:
            self.scheduler.shutdown()


async def setup(bot):
    await bot.add_cog(PartnerInviteCheckTask(bot))
