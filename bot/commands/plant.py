from discord.ext import commands

from bot.services.farm.farmPlantService import FarmPlantService

class PlantCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.farmPlantService = FarmPlantService()

    @commands.command(name="plant")
    async def plant(self, ctx, userInventoryId: int = None):
        if userInventoryId is None:
            await ctx.reply("Cách dùng: `cg plant <id_seed_trong_silo>`")
            return

        result = self.farmPlantService.plantCrop(
            userId=ctx.author.id,
            userInventoryId=userInventoryId,
        )

        await ctx.reply(result["message"])

async def setup(bot):
    await bot.add_cog(PlantCommand(bot))