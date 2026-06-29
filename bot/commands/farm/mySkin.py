import discord
from discord.ext import commands

from bot.services.farm.farmBaseSkinInventoryService import FarmBaseSkinInventoryService


class MySkinCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.farmBaseSkinInventoryService = FarmBaseSkinInventoryService()

    @commands.command(name="myskin")
    async def mySkin(self, ctx):
        try:
            baseSkinInventories = self.farmBaseSkinInventoryService.getMemberBaseSkins(
                ctx.author.id,
            )

            embed = self.buildEmbed(ctx.author, baseSkinInventories)

            await ctx.reply(
                embed=embed,
                mention_author=False,
            )

        except Exception as e:
            print(f"Show base skin inventory error: {e}")
            await ctx.reply("Đã xảy ra lỗi khi xem kho base skin.")

    def buildEmbed(self, member, baseSkinInventories):
        embed = discord.Embed(
            title=f"Kho Base Skin • {member.display_name}",
            description=(
                "Bộ sưu tập base skin dành cho nông trại của bạn.\n"
                f"**Tổng số skin:** `{len(baseSkinInventories)}`"
            ),
            color=discord.Color.from_rgb(87, 167, 255),
        )

        embed.set_author(
            name=member.display_name,
            icon_url=member.display_avatar.url,
        )

        if not baseSkinInventories:
            embed.add_field(
                name="Kho skin đang trống",
                value="Bạn chưa sở hữu base skin nào.",
                inline=False,
            )
        else:
            for inventory in baseSkinInventories:
                baseSkin = inventory.baseSkin

                if baseSkin is None:
                    continue

                statusText = "Đang sử dụng" if inventory.is_using else "Chưa sử dụng"
                statusIcon = "●" if inventory.is_using else "○"

                embed.add_field(
                    name=f"{statusIcon} {baseSkin.name}",
                    value=(
                        f"**ID:** `{inventory.id}`\n"
                        f"**Trạng thái:** {statusText}"
                    ),
                    inline=True,
                )

        embed.set_footer(
            text="Dùng lệnh cg useskin {id} để dùng base skin mà bạn muốn",
        )

        return embed


async def setup(bot):
    await bot.add_cog(MySkinCommand(bot))
