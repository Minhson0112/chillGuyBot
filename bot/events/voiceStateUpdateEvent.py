import discord
from discord.ext import commands

from bot.config.channel import FARM_NOTIFICATION_CHANNEL_ID
from bot.services.memberActivity.memberVoiceActivityService import MemberVoiceActivityService


class VoiceStateUpdateEvent(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.memberVoiceActivityService = MemberVoiceActivityService()

    @commands.Cog.listener()
    async def on_voice_state_update(
        self,
        member: discord.Member,
        before: discord.VoiceState,
        after: discord.VoiceState,
    ):
        dailyTaskMessage = self.memberVoiceActivityService.handleVoiceStateUpdate(
            member,
            before,
            after,
        )

        if dailyTaskMessage is None:
            return

        try:
            notificationChannel = await self.resolveNotificationChannel()

            if notificationChannel is None:
                return

            await notificationChannel.send(
                content=f"{member.mention}\n{dailyTaskMessage}",
                allowed_mentions=discord.AllowedMentions(
                    users=True,
                    roles=False,
                    everyone=False,
                ),
            )
        except Exception as e:
            print(f"Send voice daily task message error: {e}")

    async def resolveNotificationChannel(self):
        channel = self.bot.get_channel(FARM_NOTIFICATION_CHANNEL_ID)

        if channel is not None:
            return channel

        try:
            channel = await self.bot.fetch_channel(FARM_NOTIFICATION_CHANNEL_ID)
        except discord.NotFound:
            return None
        except discord.Forbidden:
            return None
        except discord.HTTPException:
            return None

        if not isinstance(channel, discord.TextChannel):
            return None

        return channel


async def setup(bot):
    await bot.add_cog(VoiceStateUpdateEvent(bot))
