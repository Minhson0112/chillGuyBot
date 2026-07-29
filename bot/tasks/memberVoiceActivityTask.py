import discord
from discord.ext import commands, tasks

from bot.config.channel import FARM_NOTIFICATION_CHANNEL_ID
from bot.helper.discordResolverHelper import resolveChannel
from bot.services.memberActivity.memberVoiceActivityService import MemberVoiceActivityService


class MemberVoiceActivityTask(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.memberVoiceActivityService = MemberVoiceActivityService()
        self.trackMemberVoiceActivity.start()

    def cog_unload(self):
        self.trackMemberVoiceActivity.cancel()

    @tasks.loop(minutes=1)
    async def trackMemberVoiceActivity(self):
        completedTaskMessages = self.memberVoiceActivityService.trackCurrentVoiceSessions(
            self.bot.guilds,
        )

        for userId, member, dailyTaskMessage in completedTaskMessages:
            await self.sendDailyTaskMessage(userId, member, dailyTaskMessage)

    async def sendDailyTaskMessage(self, userId, member, dailyTaskMessage):
        if dailyTaskMessage is None:
            return

        try:
            notificationChannel = await resolveChannel(
                self.bot,
                FARM_NOTIFICATION_CHANNEL_ID,
                discord.TextChannel,
            )

            if notificationChannel is None:
                return

            mention = member.mention if member is not None else f"<@{userId}>"

            await notificationChannel.send(
                content=f"{mention}\n{dailyTaskMessage}",
                allowed_mentions=discord.AllowedMentions(
                    users=True,
                    roles=False,
                    everyone=False,
                ),
            )
        except Exception as e:
            print(f"Send voice daily task message error: {e}")

    @trackMemberVoiceActivity.before_loop
    async def beforeTrackMemberVoiceActivity(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(MemberVoiceActivityTask(bot))
