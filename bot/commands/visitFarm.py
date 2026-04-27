import discord
from discord.ext import commands

from bot.services.farm.farmRenderService import FarmRenderService


class VisitFarmCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.farmRenderService = FarmRenderService(bot)

    @commands.command(name="visit")
    async def visitFarm(self, ctx, member: discord.Member = None):
        if member is None:
            await ctx.reply("Cách dùng: `cg visit @user`")
            return

        if member.bot:
            await ctx.reply("Bot không có nông trại để ghé thăm.")
            return

        try:
            renderResult = await self.farmRenderService.renderFarmByMemberId(member.id)

            file = discord.File(
                renderResult["buffer"],
                filename="visit_farm.png",
            )

            embed = self.buildVisitFarmEmbed(
                memberDisplayName=member.display_name,
                embedData=renderResult["embedData"],
            )

            embed.set_image(url="attachment://visit_farm.png")

            await ctx.reply(
                embed=embed,
                file=file,
            )

        except ValueError:
            await ctx.reply(f"{member.display_name} chưa có nông trại.")

        except FileNotFoundError as e:
            print(f"Visit farm asset file not found: {e}")
            await ctx.reply("Không tìm thấy ảnh asset để render farm.")

        except Exception as e:
            print(f"Visit farm error: {e}")
            await ctx.reply("Đã xảy ra lỗi khi ghé thăm farm.")

    def buildVisitFarmEmbed(
        self,
        memberDisplayName: str,
        embedData,
    ):
        embed = discord.Embed(
            title=f"Farm của {memberDisplayName}",
            description="Thông tin cây trồng hiện tại",
            color=discord.Color.green(),
        )

        embed.add_field(
            name="Cây đang trồng",
            value=embedData["cropText"],
            inline=True,
        )

        embed.add_field(
            name="Thu hoạch trong 🌾",
            value=embedData["remainingTimeText"],
            inline=True,
        )

        embed.add_field(
            name="Trạng thái đất 💧",
            value=embedData["landStatusText"],
            inline=True,
        )

        embed.add_field(
            name="Sâu bệnh <:bug:1498089075867914281>",
            value=embedData["pestStatusText"],
            inline=True,
        )

        return embed


async def setup(bot):
    await bot.add_cog(VisitFarmCommand(bot))