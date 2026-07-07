import discord
from discord.ext import commands

from bot.services.serverItem.serverUserInventoryService import ServerUserInventoryService


class InventoryCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.serverUserInventoryService = ServerUserInventoryService()

    @commands.command(name="inv")
    async def inventory(self, ctx: commands.Context):
        if ctx.guild is None:
            return

        try:
            inventoryResult = self.serverUserInventoryService.getInventoryMessage(
                userId=ctx.author.id,
            )

            if not inventoryResult["success"]:
                await ctx.reply(
                    inventoryResult["message"],
                    mention_author=False,
                )
                return

            await ctx.reply(
                embed=self.buildInventoryEmbed(
                    member=ctx.author,
                    inventoryText=inventoryResult["message"],
                ),
                mention_author=False,
            )
        except Exception as e:
            print(f"Show server item inventory error: {e}")
            await ctx.reply(
                "Đã xảy ra lỗi khi mở kho server item.",
                mention_author=False,
            )

    def buildInventoryEmbed(
        self,
        member: discord.Member,
        inventoryText: str,
    ):
        embed = discord.Embed(
            title="Kho server item",
            description=inventoryText,
            color=discord.Color.pink(),
        )
        embed.set_author(
            name=member.display_name,
            icon_url=member.display_avatar.url,
        )

        return embed


async def setup(bot):
    await bot.add_cog(InventoryCommand(bot))
