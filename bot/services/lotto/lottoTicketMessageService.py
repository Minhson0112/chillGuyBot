import discord

from bot.config.decoration import FOOTER_DECORATION_IMG_URL
from bot.config.emoji import BLUEMOON, STRING


class LottoTicketMessageService:
    def buildTicketListEmbed(
        self,
        member: discord.Member,
        title: str,
        tickets: list[list[int]],
    ):
        ticketLines = [
            f"- Vé {index + 1} : {' | '.join(str(number) for number in ticket)}"
            for index, ticket in enumerate(tickets)
        ]

        embed = discord.Embed(
            title=title,
            description="\n".join(ticketLines),
            color=discord.Color.green(),
        )

        embed.set_author(
            name=member.display_name,
            icon_url=member.display_avatar.url,
        )
        embed.set_image(url=FOOTER_DECORATION_IMG_URL)
        embed.set_footer(text="hãy dùng cg mylotto để check lại các vé của bạn")

        return embed

    def buildLottoPaymentCompletedEmbed(
        self,
        member: discord.Member,
        tickets: list[list[int]],
    ):
        return self.buildTicketListEmbed(
            member=member,
            title=f"{STRING} Mua vé lotto thành công {BLUEMOON}",
            tickets=tickets,
        )
