from discord.ext import commands

from bot.config.database import getDbSession
from bot.helper.farmItemHelper import buildItemText
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
            itemText = buildItemText(item)
            description = item.description or "Món đồ này chưa có mô tả."

            await ctx.reply(
                f"{itemText}\n"
                f"{description}"
            )
