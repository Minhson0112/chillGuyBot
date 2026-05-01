import discord
from discord.ext import commands

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
        self.memberVoiceActivityService.handleVoiceStateUpdate(member, before, after)


async def setup(bot):
    await bot.add_cog(VoiceStateUpdateEvent(bot))