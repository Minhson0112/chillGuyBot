from discord.ext import commands

from bot.config.database import getDbSession
from bot.config.emoji import FARM_GAME_EMOJI
from bot.repository.shopItemRepository import ShopItemRepository


class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="info")
    async def info(
        self,
        ctx: commands.Context,
        shopItemId: int = None,
    ):
        if ctx.guild is None:
            return

        if shopItemId is None:
            await ctx.reply(
                f"Hãy nhập ID item trong shop.\n"
                f"Ví dụ: `cg info 12`"
            )
            return

        with getDbSession() as session:
            shopItemRepository = ShopItemRepository(session)

            shopItem = shopItemRepository.findByIdWithItem(shopItemId)

            if shopItem is None or shopItem.item is None:
                await ctx.reply(
                    f"Không tìm thấy item trong shop với ID **{shopItemId}**."
                )
                return

            item = shopItem.item
            itemText = self.buildItemText(item)
            description = item.description or "Món đồ này chưa có mô tả."

            await ctx.reply(
                f"{itemText}\n"
                f"{description}"
            )

    def buildItemText(self, item):
        itemEmoji = FARM_GAME_EMOJI.get(item.icon_image_key)

        if itemEmoji is None:
            return f"**{item.name}**"

        return f"{itemEmoji} **{item.name}**"


async def setup(bot):
    await bot.add_cog(Info(bot))