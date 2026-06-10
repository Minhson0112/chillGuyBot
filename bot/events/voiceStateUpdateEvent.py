import discord
from discord.ext import commands

from bot.config.channel import CREATE_VOICE_CHANNEL_ID, FARM_NOTIFICATION_CHANNEL_ID
from bot.config.emoji import LOGO
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
        if member.bot:
            return

        await self.sendVoiceChannelJoinMessage(member, before, after)
        await self.sendVoiceChannelLeaveMessage(member, before, after)

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

    async def sendVoiceChannelJoinMessage(
        self,
        member: discord.Member,
        before: discord.VoiceState,
        after: discord.VoiceState,
    ):
        if after.channel is None:
            return

        if before.channel is not None and before.channel.id == after.channel.id:
            return

        if not isinstance(after.channel, discord.VoiceChannel):
            return

        if after.channel.id == CREATE_VOICE_CHANNEL_ID:
            return

        try:
            await after.channel.send(
                content=(
                    f"# {LOGO}\n"
                    f"Chào mừng hành khách {member.display_name} đã lên chuyến tàu {after.channel.name}."
                ),
                allowed_mentions=discord.AllowedMentions(
                    users=False,
                    roles=False,
                    everyone=False,
                ),
            )
        except discord.Forbidden:
            return
        except discord.HTTPException:
            return

    async def sendVoiceChannelLeaveMessage(
        self,
        member: discord.Member,
        before: discord.VoiceState,
        after: discord.VoiceState,
    ):
        if before.channel is None:
            return

        if after.channel is not None and after.channel.id == before.channel.id:
            return

        if not isinstance(before.channel, discord.VoiceChannel):
            return

        if before.channel.id == CREATE_VOICE_CHANNEL_ID:
            return

        try:
            await before.channel.send(
                content=(
                    f"# {LOGO}\n"
                    f"{member.display_name} đã nhảy khỏi chuyến tàu {before.channel.name}, hẹn gặp lại."
                ),
                allowed_mentions=discord.AllowedMentions(
                    users=False,
                    roles=False,
                    everyone=False,
                ),
            )
        except discord.Forbidden:
            return
        except discord.HTTPException:
            return


async def setup(bot):
    await bot.add_cog(VoiceStateUpdateEvent(bot))
