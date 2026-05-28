from discord.ext import commands

from bot.services.giveaway.giveawaySchedulerService import giveawaySchedulerService


class GiveawayDrawTask(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.isStarted = False

    def cog_unload(self):
        giveawaySchedulerService.shutdown()

    @commands.Cog.listener()
    async def on_ready(self):
        if self.isStarted:
            return

        giveawaySchedulerService.start(self.bot)
        self.isStarted = True


async def setup(bot):
    await bot.add_cog(GiveawayDrawTask(bot))
