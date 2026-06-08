import discord

from bot.config.emoji import COWONCCY, WING_L, WING_R


class LottoEventMessageService:
    def buildLottoEventEmbed(self, guild: discord.Guild, lottoEvent):
        embed = discord.Embed(
            title=f"{WING_L} {lottoEvent.name} {WING_R}",
            description=(
                f"- Giá mỗi vé lotto: **{lottoEvent.ticket_price_cowoncy:,}** {COWONCCY}\n"
                f"- Hạn mua vé: **{lottoEvent.buy_deadline.strftime('%Y-%m-%d %H:%M')}**\n"
                f"- Ngày tổ chức event: **{lottoEvent.draw_at.strftime('%Y-%m-%d %H:%M')}**"
            ),
            color=discord.Color.gold(),
        )

        if guild.icon is not None:
            embed.set_thumbnail(url=guild.icon.url)

        embed.timestamp = lottoEvent.draw_at
        embed.set_footer(text="Thời gian quay thưởng")

        return embed
